"""App giao diện web chạy CỤC BỘ (chỉ 127.0.0.1): chọn CT, khoanh OAR, xem contour, tải RTSTRUCT.

Mở bằng `oar-contour app` hoặc bấm đúp "QuanContour.app" trên Mac.
Ảnh không rời khỏi máy: trình duyệt gửi file tới chính máy này, không qua Internet.
"""

from __future__ import annotations

import io
import json
import logging
import re
import shutil
import subprocess
import sys
import threading
import time
import traceback
import uuid
import webbrowser
from dataclasses import dataclass, field
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

import numpy as np

log = logging.getLogger(__name__)

DEVICE_LABEL = {"gpu": "GPU NVIDIA", "mps": "chip đồ hoạ Apple", "cpu": "CPU",
                "cpu_fallback": "CPU (chip đồ hoạ lỗi, đã chuyển sang CPU)"}

WEB_DIR = Path(__file__).parent / "web"
DEFAULT_PORT = 8765
WINDOWS = {"soft": (40, 400), "lung": (-600, 1500), "bone": (400, 1800)}
SAFE_NAME = re.compile(r"[^A-Za-z0-9._-]")


def guess_accelerator() -> str:
    """Đoán nhanh máy có bộ tăng tốc không (không import PyTorch để app nhẹ)."""
    import platform

    if sys.platform == "darwin" and platform.machine() == "arm64":
        return "mps"
    if shutil.which("nvidia-smi") or Path(r"C:\Windows\System32\nvidia-smi.exe").exists():
        return "gpu"
    return "cpu"


# ------------------------------------------------------------------ dữ liệu xem ảnh
@dataclass
class ViewerData:
    """CT (HU) và mask theo thứ tự rt_utils: (rows, cols, slices), lát tăng dần về phía đầu."""
    vol: np.ndarray
    spacing: tuple[float, float, float]  # row_mm, col_mm, slice_mm
    masks: dict[str, tuple[tuple[slice, slice, slice], np.ndarray]]  # tên -> (bbox, mask con)
    colors: dict[str, tuple[int, int, int]]
    undo: list = field(default_factory=list)  # (tên, trục, lát, mặt cắt cũ) để hoàn tác
    dirty: bool = False  # có chỉnh sửa chưa lưu

    @classmethod
    def load(cls, ct_dir: Path, rtstruct: Path) -> "ViewerData":
        from pydicom import dcmread
        from rt_utils import RTStructBuilder

        rt = RTStructBuilder.create_from(str(ct_dir), str(rtstruct))
        s0 = rt.series_data[0]
        slope = float(getattr(s0, "RescaleSlope", 1))
        inter = float(getattr(s0, "RescaleIntercept", 0))
        vol = np.stack([s.pixel_array for s in rt.series_data], -1).astype(np.float32) * slope + inter
        vol = np.clip(vol, -1024, 3071).astype(np.int16)
        row_mm, col_mm = (float(v) for v in s0.PixelSpacing)
        if len(rt.series_data) > 1:
            p0 = np.array(rt.series_data[0].ImagePositionPatient, float)
            p1 = np.array(rt.series_data[1].ImagePositionPatient, float)
            z_mm = float(np.linalg.norm(p1 - p0)) or 1.0
        else:
            z_mm = float(getattr(s0, "SliceThickness", 1.0))
        rs = dcmread(str(rtstruct))
        names = {r.ROINumber: r.ROIName for r in rs.StructureSetROISequence}
        colors = {names[c.ReferencedROINumber]: tuple(int(v) for v in c.ROIDisplayColor)
                  for c in rs.ROIContourSequence}
        masks = {}
        for name in colors:
            m = rt.get_roi_mask_by_name(name)
            idx = np.nonzero(m)
            if not idx[0].size:
                continue
            bbox = tuple(slice(int(i.min()), int(i.max()) + 1) for i in idx)
            masks[name] = (bbox, m[bbox].copy())
        return cls(vol, (row_mm, col_mm, z_mm), masks, colors)

    def shape(self, axis: str) -> int:
        return {"axial": self.vol.shape[2], "coronal": self.vol.shape[0], "sagittal": self.vol.shape[1]}[axis]

    def _mask_slice(self, name: str, axis: str, i: int) -> np.ndarray | None:
        bbox, sub = self.masks[name]
        ax = {"axial": 2, "coronal": 0, "sagittal": 1}[axis]
        if not bbox[ax].start <= i < bbox[ax].stop:
            return None
        full = np.zeros(self._plane_shape(axis), bool)
        local = i - bbox[ax].start
        if axis == "axial":
            full[bbox[0], bbox[1]] = sub[:, :, local]
        elif axis == "coronal":
            full[bbox[1], bbox[2]] = sub[local, :, :]
        else:
            full[bbox[0], bbox[2]] = sub[:, local, :]
        return self._orient(full, axis)

    def _plane_shape(self, axis):
        r, c, n = self.vol.shape
        return {"axial": (r, c), "coronal": (c, n), "sagittal": (r, n)}[axis]

    @staticmethod
    def _orient(plane: np.ndarray, axis: str) -> np.ndarray:
        """Hướng hiển thị: axial giữ nguyên; coronal/sagittal dựng trục z đứng, đầu ở trên."""
        return plane if axis == "axial" else plane.T[::-1]

    def geometry(self) -> dict:
        """Kích thước (pixel) và cỡ pixel (mm) của ảnh hiển thị theo từng trục."""
        r, c, n = self.vol.shape
        row_mm, col_mm, z_mm = self.spacing
        return {
            "axial": {"w": c, "h": r, "px_w": col_mm, "px_h": row_mm},
            "coronal": {"w": c, "h": n, "px_w": col_mm, "px_h": z_mm},
            "sagittal": {"w": r, "h": n, "px_w": row_mm, "px_h": z_mm},
        }

    def ct_png(self, axis: str, i: int, window: str) -> bytes:
        """Ảnh CT (đã chỉnh cửa sổ) đúng độ phân giải gốc; trình duyệt tự phóng mượt khi zoom."""
        from PIL import Image

        i = int(np.clip(i, 0, self.shape(axis) - 1))
        if axis == "axial":
            img = self.vol[:, :, i]
        elif axis == "coronal":
            img = self.vol[i, :, :]
        else:
            img = self.vol[:, i, :]
        level, width = WINDOWS.get(window, WINDOWS["soft"])
        gray = np.clip((img.astype(np.float32) - (level - width / 2)) / width * 255, 0, 255).astype(np.uint8)
        buf = io.BytesIO()
        Image.fromarray(np.ascontiguousarray(self._orient(gray, axis))).save(buf, "PNG", compress_level=1)
        return buf.getvalue()

    def contours(self, axis: str, i: int) -> dict:
        """Đường viền từng cơ quan trên lát i, toạ độ pixel hiển thị (pixel (c, r) chiếm [c, c+1]).

        Lấy biên trên lưới phóng 2 lần nên đường viền nằm sát mép voxel (lệch <= 1/4 voxel).
        """
        import cv2

        i = int(np.clip(i, 0, self.shape(axis) - 1))
        out = {}
        for name in self.masks:
            m = self._mask_slice(name, axis, i)
            if m is None or not m.any():
                continue
            up = np.kron(m.astype(np.uint8), np.ones((2, 2), np.uint8))
            found, _ = cv2.findContours(up, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
            polys = []
            for c in found:
                pts = c.reshape(-1, 2).astype(np.float32)
                if len(pts) < 3:
                    continue
                polys.append(np.round((pts + 0.5) / 2.0, 2).tolist())
            if polys:
                out[name] = polys
        return out

    # ---------------------------------------------------------- chỉnh sửa contour
    def _full_bbox(self):
        r, c, n = self.vol.shape
        return (slice(0, r), slice(0, c), slice(0, n))

    def _full(self, name: str) -> np.ndarray:
        bbox, sub = self.masks[name]
        fb = self._full_bbox()
        if bbox != fb:
            full = np.zeros(self.vol.shape, bool)
            full[bbox] = sub
            self.masks[name] = (fb, full)
        return self.masks[name][1]

    def add_structure(self, name: str, color: tuple[int, int, int]):
        self.masks[name] = (self._full_bbox(), np.zeros(self.vol.shape, bool))
        self.colors[name] = color
        self.dirty = True

    @staticmethod
    def _plane(m: np.ndarray, axis: str, i: int) -> np.ndarray:
        return m[:, :, i] if axis == "axial" else m[i, :, :] if axis == "coronal" else m[:, i, :]

    def _set_plane(self, m: np.ndarray, axis: str, i: int, disp: np.ndarray):
        plane = disp if axis == "axial" else disp[::-1].T  # ngược lại với _orient
        if axis == "axial":
            m[:, :, i] = plane
        elif axis == "coronal":
            m[i, :, :] = plane
        else:
            m[:, i, :] = plane

    def edit(self, name: str, axis: str, i: int, op: str, points: list, radius_mm: float):
        """Vẽ thêm (op="add") hoặc xoá (op="erase") theo nét bút trên mặt cắt đang hiển thị.

        points: toạ độ pixel hiển thị (pixel (c, r) chiếm [c, c+1]); bút tròn bán kính radius_mm (theo mm thật).
        Vẽ thêm một vòng kín thì phần bên trong tự được tô kín."""
        import cv2
        from scipy import ndimage

        if name not in self.masks:
            raise ValueError("Không có cấu trúc này")
        i = int(np.clip(i, 0, self.shape(axis) - 1))
        m = self._full(name)
        disp = self._orient(self._plane(m, axis, i), axis).copy()
        g = self.geometry()[axis]
        rx, ry = max(0.6, radius_mm / g["px_w"]), max(0.6, radius_mm / g["px_h"])
        pts = [(float(x) - 0.5, float(y) - 0.5) for x, y in points] or []
        dense = []
        for a, b in zip(pts, pts[1:] + pts[-1:]):
            d = max(abs(b[0] - a[0]) / rx, abs(b[1] - a[1]) / ry)
            k = max(1, int(np.ceil(d * 3)))
            dense += [(a[0] + (b[0] - a[0]) * t / k, a[1] + (b[1] - a[1]) * t / k) for t in range(k)]
        dense += pts[-1:]
        canvas = np.zeros(disp.shape, np.uint8)
        for x, y in dense:
            cv2.ellipse(canvas, (int(round(x * 16)), int(round(y * 16))), (int(round(rx * 16)), int(round(ry * 16))),
                        0, 0, 360, 1, -1, lineType=cv2.LINE_8, shift=4)
        stroke = canvas.astype(bool)
        new = (disp | stroke) if op == "add" else (disp & ~stroke)
        if op == "add":
            new = ndimage.binary_fill_holes(new)
        self.undo.append((name, axis, i, disp))
        del self.undo[:-100]
        self._set_plane(m, axis, i, new)
        self.dirty = True
        return i

    def undo_last(self):
        if not self.undo:
            return None
        name, axis, i, disp = self.undo.pop()
        if name in self.masks:
            self._set_plane(self._full(name), axis, i, disp)
        self.dirty = True
        return {"name": name, "axis": axis, "i": i}

    def full_mask(self, name: str) -> np.ndarray:
        bbox, sub = self.masks[name]
        full = np.zeros(self.vol.shape, bool)
        full[bbox] = sub
        return full

    def write_rtstruct(self, ct_dir: Path, out_path: Path):
        from rt_utils import RTStructBuilder

        rt = RTStructBuilder.create_new(dicom_series_path=str(ct_dir))
        for name in self.masks:
            full = self.full_mask(name)
            if full.any():
                rt.add_roi(mask=full, color=list(self.colors[name]), name=name, description="Approved in QuanContour",
                           roi_generation_algorithm=2, roi_interpreted_type="ORGAN")
        rt.set_series_description("OAR approved")
        rt.ds.StructureSetLabel = "OAR_DUYET"
        rt.ds.StructureSetName = "OAR_DUYET"
        rt.save(str(out_path))

    def centers(self) -> dict[str, dict[str, int]]:
        """Lát giữa của từng cơ quan theo từng trục, để bấm vào tên là nhảy tới."""
        out = {}
        for name, (bbox, _) in self.masks.items():
            out[name] = {"coronal": (bbox[0].start + bbox[0].stop) // 2,
                         "sagittal": (bbox[1].start + bbox[1].stop) // 2,
                         "axial": (bbox[2].start + bbox[2].stop) // 2}
        return out


# ------------------------------------------------------------------ công việc
@dataclass
class Job:
    id: str
    dir: Path
    site: str = "auto"
    fast: bool = False
    demo: bool = False
    device: str = "auto"  # lựa chọn: auto | cpu
    presets: dict = field(default_factory=dict)  # danh sách cơ quan theo vùng lúc tạo ca
    protocol: str = ""  # id phác đồ (vị trí u); rỗng = chọn theo vùng giải phẫu
    intent: str = ""  # curative | palliative
    names: list = field(default_factory=list)  # danh sách OAR cố định của ca (theo phác đồ)
    refine_parotid: bool = False  # hiệu chỉnh tuyến mang tai (thử nghiệm)
    approved: bool = False  # bác sĩ đã sửa & lưu bản duyệt (dữ liệu huấn luyện)
    source: str = ""  # tên thư mục ca nguồn (khoanh hàng loạt)
    # tiến trình
    plan: list = field(default_factory=list)  # [(tên bước, trọng số)]
    step: int = 0
    step_started: float = 0.0
    model_started: float = 0.0
    spu: float = 60.0  # giây cho 1 đơn vị trọng số (ước lượng theo máy, tự học sau mỗi ca)
    device_used: str = ""  # thực tế: gpu | mps | cpu (+ ghi chú nếu chuyển CPU)
    saved_elapsed: int = 0
    status: str = "uploading"  # uploading | queued | running | done | error
    message: str = ""
    started: float = 0.0
    finished: float = 0.0
    n_files: int = 0
    result: dict = field(default_factory=dict)
    error: str = ""
    viewer: ViewerData | None = None

    @property
    def ct_dir(self) -> Path:
        return self.dir / "ct"

    @property
    def rtstruct(self) -> Path:
        return self.dir / "RS_AI_OAR.dcm"

    def run_spec(self) -> dict | None:
        """Danh sách OAR cố định + OAR bác sĩ tự vẽ (khi chọn theo phác đồ)."""
        if not self.protocol:
            return None
        from .protocols import PROTOCOL_BY_ID

        return {"names": list(self.names), "manual": [], "label": self.label(), "refine_parotid": self.refine_parotid}

    def label(self) -> str:
        if not self.protocol:
            return ""
        from .protocols import INTENTS, PROTOCOL_BY_ID

        if self.protocol == "custom":
            return f"Tự chọn OAR · {INTENTS.get(self.intent, '').lower()}"
        p = PROTOCOL_BY_ID.get(self.protocol)
        return f"{p.name if p else self.protocol} · {INTENTS.get(self.intent, '').lower()}"

    def progress(self) -> tuple[int, int | None]:
        """(% hoàn thành, số giây còn lại dự kiến)."""
        if self.status == "done":
            return 100, 0
        if self.status != "running":
            return 0, None
        if not self.plan:  # đang đọc ảnh / định vị vùng chụp: nhích dần tới ~8%
            el = time.time() - self.started if self.started else 0
            return int(min(8, 1 + 7 * el / max(5.0, 0.35 * self.spu))), None
        now = time.time()
        total = sum(w for _, w in self.plan) or 1.0
        i = min(self.step, len(self.plan) - 1)
        done = sum(w for _, w in self.plan[:i])
        cur = self.plan[i][1]
        expected = cur * self.spu
        el = now - self.step_started
        frac = min(0.95, el / expected) if expected > 0 else 0.0
        got = done + frac * cur
        spu = self.spu
        if got > 0.3 and self.model_started:  # chạy chậm/nhanh hơn dự kiến -> điều chỉnh
            spu = 0.5 * self.spu + 0.5 * (now - self.model_started) / got
        remaining = max(0.0, (total - got) * spu) + 5
        return int(3 + 94 * got / total), int(remaining)

    def public(self) -> dict:
        elapsed = (self.finished or time.time()) - self.started if self.started else self.saved_elapsed
        pct, eta = self.progress()
        return {"id": self.id, "status": self.status, "message": self.message, "site": self.site,
                "percent": pct, "eta": eta, "approved": self.approved,
                "dirty": bool(self.viewer and self.viewer.dirty),
                "step_label": self.plan[min(self.step, len(self.plan) - 1)][0] if self.plan else "",
                "fast": self.fast, "demo": self.demo, "elapsed": round(elapsed),
                "device": self.device, "device_used": self.device_used,
                "protocol": self.protocol, "intent": self.intent, "label": self.label(), "source": self.source, "n_files": self.n_files,
                "result": self.result, "error": self.error, "folder": str(self.dir)}


def pick_ct_series(upload_dir: Path, ct_dir: Path) -> tuple[int, int]:
    """Chọn series CT nhiều lát nhất trong các file đã tải lên. Trả về (số lát, số series bỏ qua)."""
    from pydicom import dcmread

    groups: dict[str, list[Path]] = {}
    for f in upload_dir.rglob("*"):
        if not f.is_file():
            continue
        try:
            ds = dcmread(f, stop_before_pixels=True, force=True)
            if getattr(ds, "Modality", "") != "CT" or "ImagePositionPatient" not in ds:
                continue
            groups.setdefault(str(ds.SeriesInstanceUID), []).append(f)
        except Exception:
            continue
    if not groups:
        raise ValueError("Không tìm thấy ảnh CT DICOM trong thư mục đã chọn.")
    best = max(groups.values(), key=len)
    ct_dir.mkdir(parents=True, exist_ok=True)
    for k, f in enumerate(best):
        shutil.move(str(f), ct_dir / f"ct_{k:04d}.dcm")
    shutil.rmtree(upload_dir, ignore_errors=True)
    return len(best), len(groups) - 1


class JobManager:
    def __init__(self, root: Path, segmenter_factory=None, isolate: bool = False):
        """segmenter_factory(device) -> Segmenter; device là "gpu" | "mps" | "cpu".
        isolate=True: mỗi ca chạy trong tiến trình riêng (app thật), segmenter_factory bỏ qua."""
        self.isolate = isolate
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        self.jobs: dict[str, Job] = {}
        self._segmenter_factory = segmenter_factory
        self._segmenters: dict[str, object] = {}
        self._run_lock = threading.Lock()  # mỗi lúc chạy 1 ca (nặng CPU/GPU)
        self._load_history()

    def _load_history(self):
        for meta in sorted(self.root.glob("*/job.json")):
            try:
                data = json.loads(meta.read_text(encoding="utf-8"))
                job = Job(id=data["id"], dir=meta.parent, site=data.get("site", "auto"),
                          fast=data.get("fast", False), demo=data.get("demo", False), status="done",
                          message="Hoàn tất", result=data.get("result", {}), n_files=data.get("n_files", 0),
                          device=data.get("device", "auto"), device_used=data.get("device_used", ""),
                          saved_elapsed=int(data.get("elapsed", 0)),
                          protocol=data.get("protocol", ""), intent=data.get("intent", ""),
                          approved=(meta.parent / "RS_DUYET.dcm").exists(), source=data.get("source", ""))
                if job.rtstruct.exists() and job.ct_dir.exists():
                    self.jobs[job.id] = job
            except Exception:
                continue

    # -------- danh sách cơ quan theo vùng (bác sĩ chọn trong app), lưu ở <thư mục kết quả>/settings.json
    @property
    def _settings_path(self) -> Path:
        return self.root / "settings.json"

    def presets(self) -> dict[str, list[str]]:
        from .structures import DEFAULT_PRESETS

        saved = {}
        try:
            saved = json.loads(self._settings_path.read_text(encoding="utf-8")).get("presets", {})
        except Exception:
            pass
        return {site: list(saved.get(site, names)) for site, names in DEFAULT_PRESETS.items()}

    def save_preset(self, site: str, names: list[str] | None):
        """names=None: về mặc định."""
        from .catalog import catalog
        from .structures import DEFAULT_PRESETS

        if site not in DEFAULT_PRESETS:
            raise ValueError("Vùng không hợp lệ")
        data = {}
        try:
            data = json.loads(self._settings_path.read_text(encoding="utf-8"))
        except Exception:
            pass
        presets = data.setdefault("presets", {})
        if names is None:
            presets.pop(site, None)
        else:
            cat = catalog()
            clean = [n for n in dict.fromkeys(names) if n in cat]
            if not clean:
                raise ValueError("Cần chọn ít nhất 1 cơ quan")
            presets[site] = clean
        self._settings_path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")

    def _settings(self) -> dict:
        try:
            return json.loads(self._settings_path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def protocol_names(self) -> dict[str, dict[str, list[str]]]:
        """Danh sách OAR theo phác đồ: mặc định đã được khoa chỉnh (nếu có), không thì mặc định của app."""
        from .protocols import PROTOCOLS, default_names, expand

        saved = self._settings().get("protocols", {})
        out = {}
        for p in PROTOCOLS:
            out[p.id] = {}
            for intent in ("curative", "palliative"):
                names = saved.get(p.id, {}).get(intent)
                out[p.id][intent] = expand(names) if names else default_names(p.id, intent)
        return out

    def save_protocol(self, pid: str, intent: str, names: list[str] | None):
        from .protocols import PROTOCOL_BY_ID, expand

        if pid not in PROTOCOL_BY_ID or intent not in ("curative", "palliative"):
            raise ValueError("Phác đồ không hợp lệ")
        data = self._settings()
        entry = data.setdefault("protocols", {}).setdefault(pid, {})
        if names is None:
            entry.pop(intent, None)
        else:
            clean = expand(names)
            if not clean:
                raise ValueError("Cần chọn ít nhất 1 cơ quan")
            entry[intent] = clean
        self._settings_path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")

    def create(self, site: str, fast: bool, demo: bool, device: str = "auto", protocol: str = "",
               intent: str = "", names: list[str] | None = None, refine_parotid: bool = False) -> Job:
        jid = datetime.now().strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:4]
        job = Job(id=jid, dir=self.root / jid, site=site, fast=fast, demo=demo,
                  device=device if device in ("auto", "cpu") else "auto", presets=self.presets())
        if protocol == "custom":  # trường hợp khác: bác sĩ tự chọn OAR
            from .protocols import expand

            job.protocol, job.intent = "custom", intent if intent in ("curative", "palliative") else "curative"
            job.names = expand(names or [])
            if not job.names:
                raise ValueError("Chưa chọn OAR nào")
        elif protocol:
            from .protocols import PROTOCOL_BY_ID, expand

            if protocol not in PROTOCOL_BY_ID or intent not in ("curative", "palliative"):
                raise ValueError("Phác đồ không hợp lệ")
            job.protocol, job.intent = protocol, intent
            job.names = expand(names) if names else self.protocol_names()[protocol][intent]
            if not job.names:
                raise ValueError("Danh sách cơ quan trống")
        job.refine_parotid = bool(refine_parotid) and bool(job.protocol)
        (job.dir / "upload").mkdir(parents=True)
        self.jobs[jid] = job
        return job

    def start(self, job: Job):
        job.status, job.message = "queued", "Đang chờ ca trước chạy xong"
        threading.Thread(target=self._run, args=(job,), daemon=True).start()

    def _run(self, job: Job):
        with self._run_lock:
            job.status, job.started = "running", time.time()
            key = self._speed_key(job)
            job.spu = float(self._settings().get("speed", {}).get(key, self.SPEED_DEFAULT[key]))

            def say(msg):
                job.message = msg

            try:
                if job.demo:
                    from .demo import download_sample, nifti_to_dicom_series

                    say("Tải ảnh CT mẫu công khai")
                    nifti = download_sample(self.root / "_sample" / "example_ct.nii.gz")
                    nifti_to_dicom_series(nifti, job.ct_dir)
                    shutil.rmtree(job.dir / "upload", ignore_errors=True)
                    job.n_files = len(list(job.ct_dir.glob("*.dcm")))
                else:
                    say("Lọc series CT trong thư mục đã chọn")
                    n, skipped = pick_ct_series(job.dir / "upload", job.ct_dir)
                    job.n_files = n
                    if skipped:
                        say(f"Dùng series CT {n} lát, bỏ qua {skipped} series khác")
                if self.isolate:
                    job.result, job.device_used = self._segment_in_subprocess(job, say)
                else:
                    job.result, job.device_used = _segment(
                        job.ct_dir, job.rtstruct, job.site, job.device, job.fast, say, self._get_segmenter,
                        job.presets, job.run_spec(), lambda k, p: self._on_event(job, k, p))
                self._learn_speed(job)
                say("Chuẩn bị ảnh để xem")
                self._drop_viewers()
                job.viewer = ViewerData.load(job.ct_dir, job.rtstruct)
                job.status, job.message = "done", "Hoàn tất"
                (job.dir / "job.json").write_text(json.dumps(
                    {"id": job.id, "site": job.site, "fast": job.fast, "demo": job.demo,
                     "n_files": job.n_files, "result": job.result, "device": job.device,
                     "device_used": job.device_used, "elapsed": round(time.time() - job.started),
                     "protocol": job.protocol, "intent": job.intent},
                    ensure_ascii=False), encoding="utf-8")
            except Exception as e:
                log.error("Ca %s lỗi:\n%s", job.id, traceback.format_exc())
                job.status, job.error = "error", str(e) or e.__class__.__name__
                job.message = "Lỗi"
            finally:
                job.finished = time.time()

    SPEED_DEFAULT = {"gpu:full": 10, "gpu:fast": 5, "mps:full": 90, "mps:fast": 25,
                     "cpu:full": 240, "cpu:fast": 45}

    def _speed_key(self, job: Job) -> str:
        dev = guess_accelerator() if job.device == "auto" else "cpu"
        return f"{dev}:{'fast' if job.fast else 'full'}"

    def _on_event(self, job: Job, kind: str, payload):
        now = time.time()
        if kind == "plan":
            job.plan = [tuple(x) for x in payload]
            job.step, job.step_started, job.model_started = 2, now, now
            job.spu = float(self._settings().get("speed", {}).get(self._speed_key(job),
                                                                  self.SPEED_DEFAULT[self._speed_key(job)]))
        elif kind == "step":
            job.step, job.step_started = int(payload), now

    def _learn_speed(self, job: Job):
        """Ghi lại tốc độ thật của máy để lần sau ước tính thời gian chính xác hơn."""
        if not job.plan or not job.model_started:
            return
        total = sum(w for _, w in job.plan)
        if total <= 0:
            return
        measured = (time.time() - job.model_started) / total
        data = self._settings()
        speed = data.setdefault("speed", {})
        key = self._speed_key(job)
        old = speed.get(key, self.SPEED_DEFAULT[key])
        speed[key] = round(0.5 * old + 0.5 * measured, 1)
        try:
            self._settings_path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        except OSError:
            pass

    def _get_segmenter(self, dev: str):
        seg = self._segmenters.get(dev)
        if seg is None:
            seg = self._segmenters[dev] = self._segmenter_factory(dev)
        return seg

    def _segment_in_subprocess(self, job: Job, say) -> tuple[dict, str]:
        """Chạy model trong tiến trình riêng: xong ca là trả lại toàn bộ RAM (PyTorch, model)."""
        import multiprocessing as mp

        ctx = mp.get_context("spawn")
        q = ctx.Queue()
        proc = ctx.Process(target=_segment_worker, daemon=False,
                           args=(str(job.ct_dir), str(job.rtstruct), job.site, job.device, job.fast, q,
                                 job.presets, job.run_spec()))
        proc.start()
        try:
            while True:
                try:
                    kind, payload = q.get(timeout=1.0)
                except Exception:  # queue.Empty
                    if not proc.is_alive():
                        raise RuntimeError(
                            "Tiến trình khoanh bị dừng đột ngột (thường do máy hết RAM). "
                            "Hãy đóng bớt ứng dụng (Chrome, Zalo…) rồi chạy lại.")
                    continue
                if kind == "msg":
                    say(payload)
                elif kind in ("plan", "step"):
                    self._on_event(job, kind, payload)
                elif kind == "done":
                    return payload["result"], payload["device_used"]
                elif kind == "error":
                    raise RuntimeError(payload)
        finally:
            proc.join(timeout=30)
            if proc.is_alive():
                proc.kill()

    def _drop_viewers(self):
        """Chỉ giữ ảnh của 1 ca trong RAM (trừ ca đang sửa dở chưa lưu)."""
        for j in self.jobs.values():
            if j.viewer is not None and not j.viewer.dirty:
                j.viewer = None

    def viewer(self, job: Job) -> ViewerData:
        if job.viewer is None:
            self._drop_viewers()
            rs = job.dir / "RS_DUYET.dcm"
            job.viewer = ViewerData.load(job.ct_dir, rs if rs.exists() else job.rtstruct)
        return job.viewer

    def checklist(self, job: Job) -> dict | None:
        """Bộ cấu trúc chuẩn của kho dữ liệu (theo phác đồ): đã có / còn thiếu trong ca này."""
        from .protocols import TRAINING_SETS

        req = TRAINING_SETS.get(job.protocol)
        if not req:
            return None
        v = self.viewer(job)
        present = [n for n in req if n in v.masks and v.masks[n][1].any()]
        return {"set": job.protocol, "required": req, "present": present,
                "missing": [n for n in req if n not in present]}

    def approve(self, job: Job) -> dict:
        """Lưu bản bác sĩ đã duyệt: RTSTRUCT mới + thống kê so với bản tự động -> kho dữ liệu huấn luyện."""
        from .evaluate import dice

        v = self.viewer(job)
        out = job.dir / "RS_DUYET.dcm"
        v.write_rtstruct(job.ct_dir, out)
        orig = ViewerData.load(job.ct_dir, job.rtstruct)
        cc = float(np.prod(v.spacing)) / 1000.0
        stats = []
        for name in v.masks:
            e = v.full_mask(name)
            if name in orig.masks:
                o = orig.full_mask(name)
                d = dice(o, e)
                stats.append({"name": name, "dice": round(d, 3), "edited": d < 0.999,
                              "cc_auto": round(float(o.sum()) * cc, 1), "cc_approved": round(float(e.sum()) * cc, 1)})
            elif e.any():
                stats.append({"name": name, "dice": None, "edited": True, "new": True, "cc_auto": 0,
                              "cc_approved": round(float(e.sum()) * cc, 1)})
        del orig
        chk = self.checklist(job)
        (job.dir / "duyet.json").write_text(json.dumps(
            {"id": job.id, "label": job.label(), "protocol": job.protocol, "stats": stats,
             "missing": chk["missing"] if chk else [],
             "time": datetime.now().isoformat(timespec="seconds")}, ensure_ascii=False, indent=1), encoding="utf-8")
        v.dirty = False
        v.undo.clear()
        job.approved = True
        return {"stats": stats, "missing": chk["missing"] if chk else []}

    # ---------------------------------------------------------- dọn dẹp & xuất dữ liệu
    def _deletable(self) -> list[Job]:
        """Ca chưa duyệt, đã xong hoặc lỗi, không đang sửa dở."""
        return [j for j in self.jobs.values()
                if not j.approved and j.status in ("done", "error")
                and not (j.viewer is not None and j.viewer.dirty)]

    @staticmethod
    def _size_mb(path: Path) -> float:
        return sum(f.stat().st_size for f in path.rglob("*") if f.is_file()) / 1e6 if path.exists() else 0.0

    def cleanup_preview(self) -> dict:
        jobs = self._deletable()
        return {"count": len(jobs), "mb": round(sum(self._size_mb(j.dir) for j in jobs))}

    def cleanup(self) -> dict:
        jobs = self._deletable()
        mb = sum(self._size_mb(j.dir) for j in jobs)
        for j in jobs:
            shutil.rmtree(j.dir, ignore_errors=True)
            self.jobs.pop(j.id, None)
        return {"deleted": len(jobs), "mb": round(mb)}

    def export_dataset(self, out_dir: Path | None = None) -> dict:
        """Xuất các ca đã duyệt dạng ẩn danh: ảnh CT + nhãn từng cấu trúc (NIfTI), mã ca ngẫu nhiên.

        NIfTI chỉ chứa ảnh và hình học (kích thước, khoảng cách điểm ảnh), không có tên/mã bệnh nhân, ngày chụp.
        Bảng đối chiếu mã ca <-> ca gốc lưu ở <thư mục kết quả>/_export_map.json, KHÔNG nằm trong thư mục xuất."""
        import SimpleITK as sitk
        from rt_utils import RTStructBuilder

        from .segment import load_ct_series

        out_dir = Path(out_dir or Path.home() / "QuanContour_XuatAnDanh")
        out_dir.mkdir(parents=True, exist_ok=True)
        map_path = self.root / "_export_map.json"
        try:
            mapping = json.loads(map_path.read_text(encoding="utf-8"))
        except Exception:
            mapping = {}
        exported, summary = 0, {}
        for job in sorted(self.jobs.values(), key=lambda j: j.id):
            rs = job.dir / "RS_DUYET.dcm"
            if not job.approved or not rs.exists():
                continue
            code = mapping.get(job.id) or f"case_{uuid.uuid4().hex[:8]}"
            mapping[job.id] = code
            cdir = out_dir / code
            done_flag = cdir / "meta.json"
            if done_flag.exists() and done_flag.stat().st_mtime >= rs.stat().st_mtime:
                names = json.loads(done_flag.read_text(encoding="utf-8")).get("structures", [])
            else:
                image = load_ct_series(job.ct_dir)
                rt = RTStructBuilder.create_from(str(job.ct_dir), str(rs))
                slice_index = [int(round(image.TransformPhysicalPointToContinuousIndex(
                    [float(v) for v in ds.ImagePositionPatient])[2])) for ds in rt.series_data]
                (cdir / "labels").mkdir(parents=True, exist_ok=True)
                sitk.WriteImage(image, str(cdir / "ct.nii.gz"), useCompression=True)
                names = []
                for name in rt.get_roi_names():
                    m = rt.get_roi_mask_by_name(name)  # (rows, cols, n) theo thứ tự rt_utils
                    arr = np.zeros(image.GetSize()[::-1], np.uint8)
                    for n_, k in enumerate(slice_index):
                        arr[k] = m[:, :, n_]
                    if not arr.any():
                        continue
                    lab = sitk.GetImageFromArray(arr)
                    lab.CopyInformation(image)
                    safe = re.sub(r"[^A-Za-z0-9_]", "_", name)
                    sitk.WriteImage(lab, str(cdir / "labels" / f"{safe}.nii.gz"), useCompression=True)
                    names.append(safe)
                stats = {}
                try:
                    stats = {st["name"]: st for st in json.loads((job.dir / "duyet.json").read_text(encoding="utf-8")).get("stats", [])}
                except Exception:
                    pass
                done_flag.write_text(json.dumps({
                    "code": code, "protocol": job.protocol, "intent": job.intent, "structures": names,
                    "spacing_mm": list(image.GetSpacing()), "size": list(image.GetSize()),
                    "agreement_auto_vs_approved": {n: stats[n].get("dice") for n in names if n in stats},
                }, ensure_ascii=False, indent=1), encoding="utf-8")
            exported += 1
            for n in names:
                summary[n] = summary.get(n, 0) + 1
        map_path.write_text(json.dumps(mapping, indent=1), encoding="utf-8")
        (out_dir / "dataset.json").write_text(json.dumps(
            {"cases": exported, "structures": dict(sorted(summary.items())),
             "note": "Du lieu da an danh (khong ten/ma benh nhan, khong ngay chup). Chi dung cho nghien cuu da duoc phe duyet."},
            ensure_ascii=False, indent=1), encoding="utf-8")
        return {"cases": exported, "folder": str(out_dir)}

    def dataset(self) -> dict:
        """Tổng hợp kho dữ liệu đã duyệt: số ca, mỗi cấu trúc phải sửa bao nhiêu."""
        per: dict[str, dict] = {}
        n = 0
        for f in sorted(self.root.glob("*/duyet.json")):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
            except Exception:
                continue
            n += 1
            for st in data.get("stats", []):
                p = per.setdefault(st["name"], {"name": st["name"], "cases": 0, "edited": 0, "new": 0, "dices": []})
                p["cases"] += 1
                p["edited"] += bool(st.get("edited"))
                p["new"] += bool(st.get("new"))
                if st.get("dice") is not None:
                    p["dices"].append(st["dice"])
        rows = []
        for p in per.values():
            d = p.pop("dices")
            p["mean_dice"] = round(float(np.mean(d)), 3) if d else None
            rows.append(p)
        rows.sort(key=lambda r: (r["mean_dice"] if r["mean_dice"] is not None else -1))
        return {"cases": n, "structures": rows}


def _segment(ct_dir, rtstruct, site, device_pref, fast, say, get_segmenter, presets=None,
             spec=None, event=None) -> tuple[dict, str]:
    from .pipeline import run_pipeline
    from .segment import pick_device

    dev = pick_device() if device_pref == "auto" else "cpu"
    seg = get_segmenter(dev)
    seg.fast = fast
    used = getattr(seg, "device", dev)
    spec = spec or {}
    report = run_pipeline(ct_dir, rtstruct, seg, site=site, presets=presets or None,
                          names=spec.get("names"), manual=spec.get("manual"), label=spec.get("label"),
                          refine_parotid=bool(spec.get("refine_parotid")),
                          on_plan=(lambda p: event("plan", p)) if event else None,
                          on_step=(lambda i: event("step", i)) if event else None,
                          progress=say)
    if getattr(seg, "fell_back", False) and dev == "mps":
        used = "cpu_fallback"
    result = {
        "sites": report.sites,
        "structures": [{"name": n, "cc": round(v, 1)} for n, v in report.written.items()],
        "skipped": report.skipped_empty,
        "not_covered": report.not_covered,
        "notes": report.notes,
    }
    return result, used


def _segment_worker(ct_dir, rtstruct, site, device_pref, fast, q, presets=None, spec=None):
    """Chạy trong tiến trình con (spawn)."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    logging.getLogger("pydicom").setLevel(logging.ERROR)
    try:
        from .segment import TotalSegmentatorRunner

        result, used = _segment(Path(ct_dir), Path(rtstruct), site, device_pref, fast,
                                lambda m: q.put(("msg", m)),
                                lambda dev: TotalSegmentatorRunner(device=dev), presets, spec,
                                lambda k, p: q.put((k, p)))
        q.put(("done", {"result": result, "device_used": used}))
    except Exception as e:
        logging.error("Lỗi khi khoanh:\n%s", traceback.format_exc())
        q.put(("error", str(e) or e.__class__.__name__))


# ------------------------------------------------------------------ HTTP
def make_handler(manager: JobManager, server_ref: dict):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):  # không ghi URL (có thể chứa tên file) vào log
            pass

        # -- tiện ích
        def _send(self, code, body: bytes, ctype="application/json", extra=None):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            for k, v in (extra or {}).items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(body)

        def _json(self, obj, code=200):
            self._send(code, json.dumps(obj, ensure_ascii=False).encode())

        def _body(self) -> bytes:
            n = int(self.headers.get("Content-Length", 0))
            return self.rfile.read(n) if n else b""

        def _job(self, jid) -> Job | None:
            job = manager.jobs.get(jid)
            if job is None:
                self._json({"error": "Không tìm thấy ca"}, 404)
            return job

        def _local_only(self) -> bool:
            # chặn trang web khác gọi vào app (CSRF): chỉ nhận request từ chính giao diện app
            origin = self.headers.get("Origin")
            host = self.headers.get("Host", "")
            if origin and urlparse(origin).netloc != host:
                self._json({"error": "forbidden"}, 403)
                return False
            if not (host.startswith("127.0.0.1:") or host.startswith("localhost:")):
                self._json({"error": "forbidden"}, 403)
                return False
            return True

        # -- GET
        def do_GET(self):
            if not self._local_only():
                return
            url = urlparse(self.path)
            q = parse_qs(url.query)
            parts = [p for p in url.path.split("/") if p]
            if not parts:
                return self._send(200, (WEB_DIR / "index.html").read_bytes(), "text/html; charset=utf-8")
            if parts == ["api", "catalog"]:
                from .catalog import ANATOMY_ORDER, GROUPS, GROUP_OF, TASKS, catalog
                from .structures import DEFAULT_PRESETS, SITE_NAMES
                from .ts_labels import TOTAL_PART_OF

                cat = catalog()
                items = [{"name": n, "task": st.task, "group": GROUP_OF.get(n, "Khác"), "color": st.color,
                          "parts": sorted({TOTAL_PART_OF[l] for l in st.labels if st.task == "total"
                                           and l in TOTAL_PART_OF})}
                         for n, st in cat.items()]
                from .protocols import INTENTS, PROTOCOLS, default_names

                protocols = [{"id": p.id, "group": p.group, "name": p.name, "manual": list(p.manual),
                              "note": p.note, "region": p.region,
                              "defaults": {i: default_names(p.id, i) for i in ("curative", "palliative")}}
                             for p in PROTOCOLS]
                return self._json({"items": items, "groups": GROUPS, "sites": SITE_NAMES,
                                   "tasks": {t: v for t, v in TASKS.items()},
                                   "presets": manager.presets(), "defaults": DEFAULT_PRESETS,
                                   "protocols": protocols, "protocol_names": manager.protocol_names(),
                                   "intents": INTENTS, "anatomy": ANATOMY_ORDER,
                                   "parotid_landmarks": __import__("oar_contour.parotid_refine",
                                                                   fromlist=["x"]).LANDMARK_NAMES})
            if parts == ["api", "dataset"]:
                return self._json(manager.dataset())
            if parts == ["api", "cleanup"]:
                return self._json(manager.cleanup_preview())
            if parts == ["api", "info"]:
                acc = guess_accelerator()
                sp = manager._settings().get("speed", {})
                spu = {m: sp.get(f"{acc}:{m}", JobManager.SPEED_DEFAULT[f"{acc}:{m}"]) for m in ("full", "fast")}
                return self._json({"accelerator": acc, "sec_per_unit": spu})
            if parts == ["api", "jobs"]:
                jobs = sorted(manager.jobs.values(), key=lambda j: j.id, reverse=True)
                return self._json([j.public() for j in jobs])
            if len(parts) >= 3 and parts[:2] == ["api", "jobs"]:
                job = self._job(parts[2])
                if job is None:
                    return
                if len(parts) == 3:
                    return self._json(job.public())
                if job.status != "done":
                    return self._json({"error": "Ca chưa xong"}, 409)
                what = parts[3]
                if what == "volume":
                    v = manager.viewer(job)
                    return self._json({
                        "sizes": {a: v.shape(a) for a in ("axial", "coronal", "sagittal")},
                        "colors": {n: v.colors[n] for n in v.masks},
                        "centers": v.centers(),
                        "geom": v.geometry(),
                    })
                if what == "slice":
                    v = manager.viewer(job)
                    axis = q.get("axis", ["axial"])[0]
                    if axis not in ("axial", "coronal", "sagittal"):
                        return self._json({"error": "axis"}, 400)
                    png = v.ct_png(axis, int(q.get("i", ["0"])[0]), q.get("w", ["soft"])[0])
                    return self._send(200, png, "image/png")
                if what == "contours":
                    v = manager.viewer(job)
                    axis = q.get("axis", ["axial"])[0]
                    if axis not in ("axial", "coronal", "sagittal"):
                        return self._json({"error": "axis"}, 400)
                    return self._json(v.contours(axis, int(q.get("i", ["0"])[0])))
                if what == "checklist":
                    return self._json(manager.checklist(job) or {})
                if what == "rtstruct":
                    approved = job.dir / "RS_DUYET.dcm"
                    use_approved = approved.exists() and q.get("version", ["duyet"])[0] != "goc"
                    f, nm = (approved, f"RS_DUYET_{job.id}.dcm") if use_approved else (job.rtstruct, f"RS_AI_OAR_{job.id}.dcm")
                    return self._send(200, f.read_bytes(), "application/dicom",
                                      {"Content-Disposition": f'attachment; filename="{nm}"'})
            self._json({"error": "not found"}, 404)

        # -- POST / PUT
        def do_POST(self):
            if not self._local_only():
                return
            parts = [p for p in urlparse(self.path).path.split("/") if p]
            if parts == ["api", "jobs"]:
                data = json.loads(self._body() or b"{}")
                site = data.get("site", "auto")
                if site != "auto":
                    from .structures import structures_for

                    try:
                        structures_for(site.split(","))
                    except ValueError as e:
                        return self._json({"error": str(e)}, 400)
                try:
                    job = manager.create(site, bool(data.get("fast")), bool(data.get("demo")),
                                         str(data.get("device", "auto")), str(data.get("protocol") or ""),
                                         str(data.get("intent") or ""), data.get("names"),
                                         bool(data.get("refine_parotid")))
                except ValueError as e:
                    return self._json({"error": str(e)}, 400)
                if job.demo:
                    manager.start(job)
                return self._json(job.public())
            if parts == ["api", "protocol-presets"]:
                data = json.loads(self._body() or b"{}")
                try:
                    manager.save_protocol(str(data.get("protocol")), str(data.get("intent")),
                                          None if data.get("reset") else data.get("names", []))
                except ValueError as e:
                    return self._json({"error": str(e)}, 400)
                return self._json({"protocol_names": manager.protocol_names()})
            if parts == ["api", "cleanup"]:
                return self._json(manager.cleanup())
            if parts == ["api", "export"]:
                try:
                    return self._json(manager.export_dataset())
                except Exception as e:  # noqa: BLE001
                    return self._json({"error": f"Không xuất được: {e}"}, 500)
            if parts == ["api", "open-export"]:
                folder = Path.home() / "QuanContour_XuatAnDanh"
                folder.mkdir(exist_ok=True)
                opener = ["open"] if sys.platform == "darwin" else ["explorer"] if sys.platform.startswith("win") else ["xdg-open"]
                subprocess.Popen(opener + [str(folder)])
                return self._json({"ok": True})
            if parts == ["api", "presets"]:
                data = json.loads(self._body() or b"{}")
                try:
                    manager.save_preset(str(data.get("site")), None if data.get("reset") else data.get("names", []))
                except ValueError as e:
                    return self._json({"error": str(e)}, 400)
                return self._json({"presets": manager.presets()})
            if parts == ["api", "quit"]:
                self._json({"ok": True})
                threading.Thread(target=server_ref["server"].shutdown, daemon=True).start()
                return
            if len(parts) == 4 and parts[:2] == ["api", "jobs"]:
                job = self._job(parts[2])
                if job is None:
                    return
                if parts[3] == "start":
                    if job.status != "uploading":
                        return self._json({"error": "Ca đã chạy"}, 409)
                    manager.start(job)
                    return self._json(job.public())
                if parts[3] in ("edit", "undo", "structure", "approve"):
                    if job.status != "done":
                        return self._json({"error": "Ca chưa xong"}, 409)
                    v = manager.viewer(job)
                    data = json.loads(self._body() or b"{}")
                    try:
                        if parts[3] == "edit":
                            axis = str(data.get("axis", "axial"))
                            if axis not in ("axial", "coronal", "sagittal") or data.get("op") not in ("add", "erase"):
                                raise ValueError("Tham số không hợp lệ")
                            pts = [(float(x), float(y)) for x, y in data.get("points", [])][:5000]
                            i = v.edit(str(data.get("name")), axis, int(data.get("i", 0)), data["op"], pts,
                                       float(np.clip(float(data.get("radius_mm", 3)), 0.5, 30)))
                            return self._json({"i": i, "contours": v.contours(axis, i), "dirty": True})
                        if parts[3] == "undo":
                            return self._json({"undone": v.undo_last(), "dirty": v.dirty})
                        if parts[3] == "structure":
                            name = str(data.get("name", "")).strip()
                            if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,31}", name):
                                raise ValueError("Tên chỉ gồm chữ không dấu, số, dấu _ (ví dụ Brainstem, OpticChiasm)")
                            if name in v.masks:
                                raise ValueError("Đã có cấu trúc này")
                            palette = [(255, 99, 71), (60, 179, 113), (65, 105, 225), (238, 130, 238), (255, 215, 0),
                                       (0, 206, 209), (255, 140, 0), (154, 205, 50)]
                            v.add_structure(name, palette[len(v.masks) % len(palette)])
                            return self._json({"colors": {n: v.colors[n] for n in v.masks}, "dirty": True})
                        if parts[3] == "approve":
                            chk = manager.checklist(job)
                            if chk and chk["missing"] and not data.get("force"):
                                return self._json({"error": "missing", "missing": chk["missing"]}, 409)
                            return self._json(manager.approve(job))
                    except ValueError as e:
                        return self._json({"error": str(e)}, 400)
                if parts[3] == "reveal":
                    if sys.platform == "darwin":
                        subprocess.Popen(["open", str(job.dir)])
                    elif sys.platform.startswith("win"):
                        subprocess.Popen(["explorer", str(job.dir)])
                    else:
                        subprocess.Popen(["xdg-open", str(job.dir)])
                    return self._json({"ok": True})
            self._json({"error": "not found"}, 404)

        def do_PUT(self):
            if not self._local_only():
                return
            url = urlparse(self.path)
            parts = [p for p in url.path.split("/") if p]
            if len(parts) == 4 and parts[:2] == ["api", "jobs"] and parts[3] == "files":
                job = self._job(parts[2])
                if job is None:
                    return
                if job.status != "uploading":
                    return self._json({"error": "Ca đã chạy"}, 409)
                name = SAFE_NAME.sub("_", unquote(parse_qs(url.query).get("name", ["f"])[0]))[-120:]
                target = job.dir / "upload" / f"{uuid.uuid4().hex[:8]}_{name}"
                target.write_bytes(self._body())
                return self._json({"ok": True})
            self._json({"error": "not found"}, 404)

    return Handler


def serve(root: Path, port: int = DEFAULT_PORT, open_browser: bool = True, segmenter_factory=None):
    url = f"http://127.0.0.1:{port}/"
    manager = JobManager(root, segmenter_factory, isolate=segmenter_factory is None)
    ref: dict = {}
    try:
        server = ThreadingHTTPServer(("127.0.0.1", port), make_handler(manager, ref))
    except OSError:
        # app đã mở sẵn ở lần trước -> chỉ mở lại trình duyệt
        print(f"App đã chạy sẵn: {url}")
        if open_browser:
            webbrowser.open(url)
        return
    ref["server"] = server
    print(f"QuanContour đang chạy tại {url}  (đóng bằng nút 'Thoát' trong app hoặc Ctrl+C)")
    print(f"Kết quả lưu tại: {root}")
    if open_browser:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
