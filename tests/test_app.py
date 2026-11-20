import json
import threading
import time
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

from oar_contour.app import JobManager, make_handler

from conftest import FakeSegmenter, thorax_labels


def _req(base, path, method="GET", data=None, headers=None):
    req = urllib.request.Request(base + path, data=data, method=method, headers=headers or {})
    with urllib.request.urlopen(req, timeout=30) as r:
        body = r.read()
        return r.status, r.headers.get("Content-Type"), body


def test_app_upload_run_view(ct_dir, tmp_path):
    manager = JobManager(tmp_path / "results", lambda device: FakeSegmenter(thorax_labels()))
    ref = {}
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(manager, ref))
    ref["server"] = server
    base = f"http://127.0.0.1:{server.server_address[1]}"
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        _, ctype, html = _req(base, "/")
        assert "text/html" in ctype and b"QuanContour" in html

        _, _, body = _req(base, "/api/jobs", "POST", json.dumps({"site": "thorax"}).encode())
        jid = json.loads(body)["id"]
        for f in ct_dir.iterdir():
            _req(base, f"/api/jobs/{jid}/files?name=../../{f.name}", "PUT", f.read_bytes())
        (tmp_path / "junk.txt").write_text("not dicom")
        _req(base, f"/api/jobs/{jid}/files?name=junk.txt", "PUT", b"not dicom")
        _req(base, f"/api/jobs/{jid}/start", "POST", b"")

        deadline = time.time() + 60
        while time.time() < deadline:
            job = json.loads(_req(base, f"/api/jobs/{jid}")[2])
            if job["status"] in ("done", "error"):
                break
            time.sleep(0.2)
        assert job["status"] == "done", job
        assert job["n_files"] == 24
        names = {s["name"] for s in job["result"]["structures"]}
        assert {"Lung_L", "Heart", "Breast_R"} <= names
        # tên file "../../x" không thoát ra ngoài thư mục ca
        assert not list((tmp_path).glob("*.dcm"))

        vol = json.loads(_req(base, f"/api/jobs/{jid}/volume")[2])
        assert vol["sizes"] == {"axial": 24, "coronal": 48, "sagittal": 64}
        assert vol["geom"]["axial"] == {"w": 64, "h": 48, "px_w": 2.0, "px_h": 2.0}
        assert vol["geom"]["coronal"] == {"w": 64, "h": 24, "px_w": 2.0, "px_h": 3.0}
        assert json.loads(_req(base, "/api/info")[2])["accelerator"] in ("cpu", "gpu", "mps")
        for axis in ("axial", "coronal", "sagittal"):
            i = vol["centers"]["Heart"][axis]
            _, ctype, png = _req(base, f"/api/jobs/{jid}/slice?axis={axis}&i={i}&w=lung")
            assert ctype == "image/png" and png[:4] == b"\x89PNG"
            g = vol["geom"][axis]
            from PIL import Image
            import io
            assert Image.open(io.BytesIO(png)).size == (g["w"], g["h"])  # độ phân giải gốc
            cont = json.loads(_req(base, f"/api/jobs/{jid}/contours?axis={axis}&i={i}")[2])
            assert "Heart" in cont
            xs = [x for poly in cont["Heart"] for x, _ in poly]
            ys = [y for poly in cont["Heart"] for _, y in poly]
            assert 0 <= min(xs) and max(xs) <= g["w"] and 0 <= min(ys) and max(ys) <= g["h"]
        _, ctype, rs = _req(base, f"/api/jobs/{jid}/rtstruct")
        assert ctype == "application/dicom" and rs[128:132] == b"DICM"

        # trang web lạ không được gọi API của app
        try:
            _req(base, "/api/jobs", "POST", b"{}", {"Origin": "https://evil.example"})
            raise AssertionError("phải bị chặn")
        except urllib.error.HTTPError as e:
            assert e.code == 403

        # mở lại app: ca cũ vẫn còn trong lịch sử
        again = JobManager(tmp_path / "results", lambda device: None)
        assert jid in again.jobs and again.jobs[jid].status == "done"
    finally:
        server.shutdown()


def test_mps_failure_falls_back_to_cpu(monkeypatch, ct_dir):
    pytest = __import__("pytest")
    api = pytest.importorskip("totalsegmentator.python_api")
    import SimpleITK as sitk
    from oar_contour import segment

    calls = []

    def fake_ts(input, output, task, device, **kw):
        calls.append(device)
        if device == "mps":
            raise RuntimeError("MPS: operator not implemented")
        img = sitk.ReadImage(str(input))
        sitk.WriteImage(sitk.Image(img.GetSize(), sitk.sitkUInt8) * 0 + 0, str(output))

    monkeypatch.setattr(api, "totalsegmentator", fake_ts)
    monkeypatch.setattr(segment.TotalSegmentatorRunner, "_setup",
                        lambda self: setattr(self, "_commercial", set()))
    runner = segment.TotalSegmentatorRunner(device="mps")
    image = segment.load_ct_series(ct_dir)
    runner.run(image, "total")
    runner.run(image, "total")
    assert calls == ["mps", "cpu", "cpu"]
    assert runner.fell_back and runner.device == "cpu"
