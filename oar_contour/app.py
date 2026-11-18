"""App giao diện web chạy CỤC BỘ (chỉ 127.0.0.1): chọn CT, khoanh OAR, xem contour, tải RTSTRUCT.

Mở bằng `oar-contour app` hoặc bấm đúp "OAR Contour.app" trên Mac.
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

WEB_DIR = Path(__file__).parent / "web"
DEFAULT_PORT = 8765
WINDOWS = {"soft": (40, 400), "lung": (-600, 1500), "bone": (400, 1800)}
SAFE_NAME = re.compile(r"[^A-Za-z0-9._-]")


# ------------------------------------------------------------------ dữ liệu xem ảnh
@dataclass
class ViewerData:
    """CT (HU) và mask theo thứ tự rt_utils: (rows, cols, slices), lát tăng dần về phía đầu."""
    vol: np.ndarray
    spacing: tuple[float, float, float]  # row_mm, col_mm, slice_mm
    masks: dict[str, tuple[tuple[slice, slice, slice], np.ndarray]]  # tên -> (bbox, mask con)
    colors: dict[str, tuple[int, int, int]]

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
        return full

    def _plane_shape(self, axis):
        r, c, n = self.vol.shape
        return {"axial": (r, c), "coronal": (c, n), "sagittal": (r, n)}[axis]

    def render(self, axis: str, i: int, window: str, hidden: set[str]) -> bytes:
        from PIL import Image
        from scipy import ndimage

        i = int(np.clip(i, 0, self.shape(axis) - 1))
        if axis == "axial":
            img = self.vol[:, :, i]
        elif axis == "coronal":
            img = self.vol[i, :, :]
        else:
            img = self.vol[:, i, :]
        level, width = WINDOWS.get(window, WINDOWS["soft"])
        gray = np.clip((img.astype(np.float32) - (level - width / 2)) / width * 255, 0, 255).astype(np.uint8)
        rgb = np.repeat(gray[..., None], 3, axis=2)
        for name in self.masks:
            if name in hidden:
                continue
            m = self._mask_slice(name, axis, i)
            if m is None or not m.any():
                continue
            edge = m & ~ndimage.binary_erosion(m)
            col = np.array(self.colors[name], np.uint8)
            rgb[m] = (rgb[m] * 0.82 + col * 0.18).astype(np.uint8)  # tô mờ bên trong
            rgb[edge] = col
        row_mm, col_mm, z_mm = self.spacing
        if axis != "axial":
            rgb = rgb.transpose(1, 0, 2)[::-1]  # trục z dựng đứng, đầu ở trên
        h, w = rgb.shape[:2]
        px_h = {"axial": row_mm, "coronal": z_mm, "sagittal": z_mm}[axis]
        px_w = {"axial": col_mm, "coronal": col_mm, "sagittal": row_mm}[axis]
        # đưa về tỉ lệ mm thật; ảnh nhỏ thì phóng to để cạnh dài >= 600 px
        phys_w, phys_h = w * px_w, h * px_h
        mm_per_px = min(min(px_w, px_h), max(phys_w, phys_h) / 600)
        size = (max(1, round(phys_w / mm_per_px)), max(1, round(phys_h / mm_per_px)))
        im = Image.fromarray(np.ascontiguousarray(rgb)).resize(size, Image.NEAREST)
        buf = io.BytesIO()
        im.save(buf, "PNG", compress_level=1)
        return buf.getvalue()

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

    def public(self) -> dict:
        elapsed = (self.finished or time.time()) - self.started if self.started else 0
        return {"id": self.id, "status": self.status, "message": self.message, "site": self.site,
                "fast": self.fast, "demo": self.demo, "elapsed": round(elapsed), "n_files": self.n_files,
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
    def __init__(self, root: Path, segmenter_factory):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        self.jobs: dict[str, Job] = {}
        self._segmenter_factory = segmenter_factory
        self._segmenter = None
        self._run_lock = threading.Lock()  # mỗi lúc chạy 1 ca (nặng CPU/GPU)
        self._load_history()

    def _load_history(self):
        for meta in sorted(self.root.glob("*/job.json")):
            try:
                data = json.loads(meta.read_text(encoding="utf-8"))
                job = Job(id=data["id"], dir=meta.parent, site=data.get("site", "auto"),
                          fast=data.get("fast", False), demo=data.get("demo", False), status="done",
                          message="Hoàn tất", result=data.get("result", {}), n_files=data.get("n_files", 0))
                if job.rtstruct.exists() and job.ct_dir.exists():
                    self.jobs[job.id] = job
            except Exception:
                continue

    def create(self, site: str, fast: bool, demo: bool) -> Job:
        jid = datetime.now().strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:4]
        job = Job(id=jid, dir=self.root / jid, site=site, fast=fast, demo=demo)
        (job.dir / "upload").mkdir(parents=True)
        self.jobs[jid] = job
        return job

    def start(self, job: Job):
        job.status, job.message = "queued", "Đang chờ ca trước chạy xong"
        threading.Thread(target=self._run, args=(job,), daemon=True).start()

    def _run(self, job: Job):
        with self._run_lock:
            job.status, job.started = "running", time.time()

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
                if self._segmenter is None:
                    self._segmenter = self._segmenter_factory()
                self._segmenter.fast = job.fast
                from .pipeline import run_pipeline

                report = run_pipeline(job.ct_dir, job.rtstruct, self._segmenter, site=job.site, progress=say)
                job.result = {
                    "sites": report.sites,
                    "structures": [{"name": n, "cc": round(v, 1)} for n, v in report.written.items()],
                    "skipped": report.skipped_empty,
                    "not_covered": report.not_covered,
                    "notes": report.notes,
                }
                say("Chuẩn bị ảnh để xem")
                job.viewer = ViewerData.load(job.ct_dir, job.rtstruct)
                job.status, job.message = "done", "Hoàn tất"
                (job.dir / "job.json").write_text(json.dumps(
                    {"id": job.id, "site": job.site, "fast": job.fast, "demo": job.demo,
                     "n_files": job.n_files, "result": job.result}, ensure_ascii=False), encoding="utf-8")
            except Exception as e:
                log.error("Ca %s lỗi:\n%s", job.id, traceback.format_exc())
                job.status, job.error = "error", str(e) or e.__class__.__name__
                job.message = "Lỗi"
            finally:
                job.finished = time.time()

    def viewer(self, job: Job) -> ViewerData:
        if job.viewer is None:
            job.viewer = ViewerData.load(job.ct_dir, job.rtstruct)
        return job.viewer


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
                    })
                if what == "slice":
                    v = manager.viewer(job)
                    axis = q.get("axis", ["axial"])[0]
                    if axis not in ("axial", "coronal", "sagittal"):
                        return self._json({"error": "axis"}, 400)
                    hidden = set(filter(None, q.get("hide", [""])[0].split(",")))
                    png = v.render(axis, int(q.get("i", ["0"])[0]), q.get("w", ["soft"])[0], hidden)
                    return self._send(200, png, "image/png")
                if what == "rtstruct":
                    return self._send(200, job.rtstruct.read_bytes(), "application/dicom",
                                      {"Content-Disposition": f'attachment; filename="RS_AI_OAR_{job.id}.dcm"'})
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
                job = manager.create(site, bool(data.get("fast")), bool(data.get("demo")))
                if job.demo:
                    manager.start(job)
                return self._json(job.public())
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
    if segmenter_factory is None:
        from .segment import TotalSegmentatorRunner

        def segmenter_factory():
            try:
                import torch

                device = "gpu" if torch.cuda.is_available() else "cpu"
            except Exception:
                device = "cpu"
            return TotalSegmentatorRunner(device=device)

    url = f"http://127.0.0.1:{port}/"
    manager = JobManager(root, segmenter_factory)
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
    print(f"OAR Contour đang chạy tại {url}  (đóng bằng nút 'Thoát' trong app hoặc Ctrl+C)")
    print(f"Kết quả lưu tại: {root}")
    if open_browser:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
