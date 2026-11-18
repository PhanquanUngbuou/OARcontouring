"""DICOM node chạy trong mạng bệnh viện.

Luồng:
  CT-sim --(C-STORE CT)--> node này --(phân vùng)--> RTSTRUCT --(C-STORE)--> Monaco

CT-sim vẫn đẩy ảnh sang Monaco như cũ; chỉ cần thêm node này làm đích thứ hai.
Node nhận đủ series (không có lát mới trong `settle_seconds` giây) thì chạy
pipeline và gửi RTSTRUCT sang Monaco (nếu đã cấu hình).

Có thể chọn vùng giải phẫu theo AE title mà CT-sim gọi tới, ví dụ cấu hình
trên CT-sim 2 đích: OAR_HN (đầu cổ) và OAR_AUTO (tự nhận diện).

Không ghi thông tin bệnh nhân vào log: series chỉ được nhắc bằng mã băm ngắn.
"""

from __future__ import annotations

import hashlib
import logging
import queue
import shutil
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path

from pydicom import dcmread
from pynetdicom import AE, evt
from pynetdicom.sop_class import CTImageStorage, RTStructureSetStorage, Verification

from .pipeline import run_pipeline
from .segment import Segmenter

log = logging.getLogger(__name__)


def short_id(uid: str) -> str:
    return hashlib.sha256(uid.encode()).hexdigest()[:10]


@dataclass
class Destination:
    host: str
    port: int
    ae_title: str


@dataclass
class NodeConfig:
    ae_title: str = "OAR_AI"
    port: int = 11112
    work_dir: Path = Path("./oar_work")
    settle_seconds: float = 60.0
    ae_site: dict[str, str] = field(default_factory=dict)  # AE title được gọi -> vùng
    default_site: str = "auto"
    forward: Destination | None = None
    keep_images: bool = False


def send_rtstruct(path: Path, dest: Destination, calling_ae: str) -> None:
    ae = AE(ae_title=calling_ae)
    ae.add_requested_context(RTStructureSetStorage)
    assoc = ae.associate(dest.host, dest.port, ae_title=dest.ae_title)
    if not assoc.is_established:
        raise ConnectionError(f"Không kết nối được {dest.ae_title}@{dest.host}:{dest.port}")
    try:
        status = assoc.send_c_store(dcmread(path))
        if not status or status.Status != 0x0000:
            raise RuntimeError(f"Đích từ chối RTSTRUCT, status={getattr(status, 'Status', None)}")
    finally:
        assoc.release()


class OarNode:
    def __init__(self, config: NodeConfig, segmenter: Segmenter):
        self.cfg = config
        self.segmenter = segmenter
        self.incoming = config.work_dir / "incoming"
        self.output = config.work_dir / "rtstruct"
        self.failed = config.work_dir / "failed"
        for d in (self.incoming, self.output, self.failed):
            d.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._pending: dict[Path, tuple[float, str]] = {}  # thư mục series -> (lần nhận cuối, vùng)
        self._jobs: queue.Queue[tuple[Path, str]] = queue.Queue()
        self._stop = threading.Event()
        self._server = None
        self._threads: list[threading.Thread] = []
        self.processed: list[Path] = []  # RTSTRUCT đã tạo (dùng cho test/giám sát)

    # ---------------------------------------------------------------- nhận
    def _on_store(self, event):
        ds = event.dataset
        ds.file_meta = event.file_meta
        if getattr(ds, "Modality", "") != "CT":
            return 0x0000  # nhận nhưng bỏ qua
        called = event.assoc.acceptor.ae_title.strip()
        site = self.cfg.ae_site.get(called, self.cfg.default_site)
        series_dir = self.incoming / short_id(ds.SeriesInstanceUID)
        series_dir.mkdir(exist_ok=True)
        ds.save_as(series_dir / f"{short_id(ds.SOPInstanceUID)}.dcm", enforce_file_format=True)
        with self._lock:
            self._pending[series_dir] = (time.monotonic(), site)
        return 0x0000

    def _watch(self):
        while not self._stop.wait(1.0):
            now = time.monotonic()
            with self._lock:
                ready = [(d, s) for d, (t, s) in self._pending.items() if now - t >= self.cfg.settle_seconds]
                for d, _ in ready:
                    del self._pending[d]
            for job in ready:
                self._jobs.put(job)

    # ---------------------------------------------------------------- xử lý
    def _work(self):
        while not self._stop.is_set():
            try:
                series_dir, site = self._jobs.get(timeout=0.5)
            except queue.Empty:
                continue
            self.process(series_dir, site)

    def process(self, series_dir: Path, site: str) -> Path | None:
        sid = series_dir.name
        out = self.output / f"RS_{sid}.dcm"
        try:
            log.info("Series %s: bắt đầu phân vùng (vùng=%s)", sid, site)
            t0 = time.monotonic()
            report = run_pipeline(series_dir, out, self.segmenter, site=site)
            log.info("Series %s: xong sau %.0fs, %d cấu trúc", sid, time.monotonic() - t0, len(report.written))
            if self.cfg.forward:
                send_rtstruct(out, self.cfg.forward, self.cfg.ae_title)
                log.info("Series %s: đã gửi RTSTRUCT tới %s", sid, self.cfg.forward.ae_title)
            if not self.cfg.keep_images:
                shutil.rmtree(series_dir, ignore_errors=True)
            self.processed.append(out)
            return out
        except Exception:
            log.exception("Series %s: lỗi, chuyển sang thư mục failed/", sid)
            shutil.move(str(series_dir), str(self.failed / sid))
            return None

    # ---------------------------------------------------------------- vòng đời
    def start(self, block: bool = True):
        ae = AE(ae_title=self.cfg.ae_title)
        ae.require_called_aet = False  # cho phép nhiều AE title (OAR_HN, OAR_AUTO, ...)
        ae.add_supported_context(CTImageStorage)
        ae.add_supported_context(Verification)  # C-ECHO để test kết nối từ CT-sim
        for target in (self._watch, self._work):
            t = threading.Thread(target=target, daemon=True)
            t.start()
            self._threads.append(t)
        log.info("OAR node lắng nghe cổng %d, AE %s", self.cfg.port, self.cfg.ae_title)
        self._server = ae.start_server(
            ("0.0.0.0", self.cfg.port), block=block,
            evt_handlers=[(evt.EVT_C_STORE, self._on_store)],
        )
        return self._server

    def stop(self):
        self._stop.set()
        if self._server is not None:
            self._server.shutdown()
        for t in self._threads:
            t.join(timeout=5)
