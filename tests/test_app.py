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


def test_presets_api_and_job_uses_them(ct_dir, tmp_path):
    manager = JobManager(tmp_path / "results", lambda device: FakeSegmenter(thorax_labels()))
    ref = {}
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(manager, ref))
    base = f"http://127.0.0.1:{server.server_address[1]}"
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        cat = json.loads(_req(base, "/api/catalog")[2])
        assert len(cat["items"]) > 200 and "Liver" in cat["presets"]["thorax"]
        body = json.dumps({"site": "thorax", "names": ["Heart", "Lung_L", "Không_có"]}).encode()
        presets = json.loads(_req(base, "/api/presets", "POST", body)[2])["presets"]
        assert presets["thorax"] == ["Heart", "Lung_L"]
        # mở lại app: vẫn nhớ
        assert JobManager(tmp_path / "results", None).presets()["thorax"] == ["Heart", "Lung_L"]

        jid = json.loads(_req(base, "/api/jobs", "POST", json.dumps({"site": "thorax"}).encode())[2])["id"]
        for f in ct_dir.iterdir():
            _req(base, f"/api/jobs/{jid}/files?name={f.name}", "PUT", f.read_bytes())
        _req(base, f"/api/jobs/{jid}/start", "POST", b"")
        deadline = time.time() + 60
        while time.time() < deadline:
            job = json.loads(_req(base, f"/api/jobs/{jid}")[2])
            if job["status"] in ("done", "error"):
                break
            time.sleep(0.2)
        assert job["status"] == "done", job
        assert {s["name"] for s in job["result"]["structures"]} == {"Heart", "Lung_L"}

        _req(base, "/api/presets", "POST", json.dumps({"site": "thorax", "reset": True}).encode())
        assert "Liver" in manager.presets()["thorax"]
        try:
            _req(base, "/api/presets", "POST", json.dumps({"site": "thorax", "names": []}).encode())
            raise AssertionError("phải báo lỗi")
        except urllib.error.HTTPError as e:
            assert e.code == 400
    finally:
        server.shutdown()


def test_protocol_job_api(ct_dir, tmp_path):
    manager = JobManager(tmp_path / "results", lambda device: FakeSegmenter(thorax_labels()))
    ref = {}
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(manager, ref))
    base = f"http://127.0.0.1:{server.server_address[1]}"
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        cat = json.loads(_req(base, "/api/catalog")[2])
        assert any(p["id"] == "headneck" for p in cat["protocols"])
        assert "Bone_Mandible" in cat["protocol_names"]["headneck"]["curative"]
        # khoa chỉnh danh sách vú trái triệt căn, lưu làm mặc định
        body = json.dumps({"protocol": "breast", "intent": "curative", "names": ["Heart", "Lung_L"]}).encode()
        names = json.loads(_req(base, "/api/protocol-presets", "POST", body)[2])["protocol_names"]
        assert names["breast"]["curative"] == ["Heart", "Lung_L"]
        # ca mới theo phác đồ, thêm Breast_R chỉ cho ca này
        spec = {"protocol": "breast", "intent": "curative", "names": ["Heart", "Lung_L", "Breast_R"]}
        jid = json.loads(_req(base, "/api/jobs", "POST", json.dumps(spec).encode())[2])["id"]
        for f in ct_dir.iterdir():
            _req(base, f"/api/jobs/{jid}/files?name={f.name}", "PUT", f.read_bytes())
        _req(base, f"/api/jobs/{jid}/start", "POST", b"")
        deadline = time.time() + 60
        while time.time() < deadline:
            job = json.loads(_req(base, f"/api/jobs/{jid}")[2])
            if job["status"] in ("done", "error"):
                break
            time.sleep(0.2)
        assert job["status"] == "done", job
        assert {s["name"] for s in job["result"]["structures"]} == {"Heart", "Lung_L", "Breast_R"}
        assert job["label"] == "U vú · triệt căn"
        assert manager.protocol_names()["breast"]["curative"] == ["Heart", "Lung_L"]  # không bị ghi đè
        # trường hợp khác: tự chọn OAR
        jc = json.loads(_req(base, "/api/jobs", "POST", json.dumps(
            {"protocol": "custom", "intent": "palliative", "names": ["Heart", "Bone_Vertebra_*"]}).encode())[2])
        assert jc["label"] == "Tự chọn OAR · triệu chứng"
        assert "Bone_Vertebra_T5" in manager.jobs[jc["id"]].names and "Heart" in manager.jobs[jc["id"]].names
        try:
            _req(base, "/api/jobs", "POST", json.dumps({"protocol": "custom", "intent": "curative", "names": []}).encode())
            raise AssertionError("phải báo lỗi")
        except urllib.error.HTTPError as e:
            assert e.code == 400
        try:
            _req(base, "/api/jobs", "POST", json.dumps({"protocol": "khong_co", "intent": "curative"}).encode())
            raise AssertionError("phải báo lỗi")
        except urllib.error.HTTPError as e:
            assert e.code == 400
    finally:
        server.shutdown()


def test_edit_contours_approve_and_dataset(ct_dir, tmp_path):
    from rt_utils import RTStructBuilder

    manager = JobManager(tmp_path / "results", lambda device: FakeSegmenter(thorax_labels()))
    ref = {}
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(manager, ref))
    base = f"http://127.0.0.1:{server.server_address[1]}"
    threading.Thread(target=server.serve_forever, daemon=True).start()
    post = lambda path, obj: json.loads(_req(base, path, "POST", json.dumps(obj).encode())[2])
    try:
        jid = post("/api/jobs", {"protocol": "custom", "intent": "curative", "names": ["Heart", "Lung_L"]})["id"]
        for f in ct_dir.iterdir():
            _req(base, f"/api/jobs/{jid}/files?name={f.name}", "PUT", f.read_bytes())
        _req(base, f"/api/jobs/{jid}/start", "POST", b"")
        deadline = time.time() + 60
        while time.time() < deadline and json.loads(_req(base, f"/api/jobs/{jid}")[2])["status"] != "done":
            time.sleep(0.2)
        vol = json.loads(_req(base, f"/api/jobs/{jid}/volume")[2])
        i = vol["centers"]["Heart"]["axial"]
        v = manager.jobs[jid].viewer
        area0 = int(v._plane(v.full_mask("Heart"), "axial", i).sum())

        # vẽ thêm một vòng kín bên cạnh tim -> phần trong được tô kín
        ring = [[10, 30], [20, 30], [20, 40], [10, 40], [10, 30]]
        r = post(f"/api/jobs/{jid}/edit", {"name": "Heart", "axis": "axial", "i": i, "op": "add", "points": ring, "radius_mm": 1})
        area1 = int(v._plane(v.full_mask("Heart"), "axial", i).sum())
        assert area1 > area0 + 80 and "Heart" in r["contours"]
        assert json.loads(_req(base, f"/api/jobs/{jid}")[2])["dirty"] is True
        # tẩy, rồi hoàn tác 2 lần -> về như cũ
        post(f"/api/jobs/{jid}/edit", {"name": "Heart", "axis": "axial", "i": i, "op": "erase", "points": [[15, 35]], "radius_mm": 6})
        assert int(v._plane(v.full_mask("Heart"), "axial", i).sum()) < area1
        post(f"/api/jobs/{jid}/undo", {}); post(f"/api/jobs/{jid}/undo", {})
        assert int(v._plane(v.full_mask("Heart"), "axial", i).sum()) == area0
        # sửa trên mặt cắt coronal cũng được
        post(f"/api/jobs/{jid}/edit", {"name": "Lung_L", "axis": "coronal", "i": 20, "op": "erase", "points": [[46, 12]], "radius_mm": 4})

        # cấu trúc mới (app chưa vẽ được) do bác sĩ vẽ
        post(f"/api/jobs/{jid}/structure", {"name": "Brainstem"})
        try:
            post(f"/api/jobs/{jid}/structure", {"name": "thân não"})
            raise AssertionError("tên có dấu phải bị từ chối")
        except urllib.error.HTTPError as e:
            assert e.code == 400
        post(f"/api/jobs/{jid}/edit", {"name": "Brainstem", "axis": "axial", "i": i, "op": "add", "points": [[40, 10]], "radius_mm": 4})
        post(f"/api/jobs/{jid}/edit", {"name": "Heart", "axis": "axial", "i": i, "op": "add", "points": ring, "radius_mm": 1})

        res = post(f"/api/jobs/{jid}/approve", {})
        stats = {s["name"]: s for s in res["stats"]}
        assert stats["Heart"]["edited"] and stats["Heart"]["dice"] < 1
        assert stats["Brainstem"].get("new")
        assert (manager.jobs[jid].dir / "RS_DUYET.dcm").exists() and manager.jobs[jid].approved
        rs = RTStructBuilder.create_from(str(manager.jobs[jid].ct_dir), str(manager.jobs[jid].dir / "RS_DUYET.dcm"))
        assert {"Heart", "Lung_L", "Brainstem"} <= set(rs.get_roi_names())
        # tải về: mặc định bản duyệt, có thể lấy bản gốc
        _, _, b1 = _req(base, f"/api/jobs/{jid}/rtstruct")
        _, _, b2 = _req(base, f"/api/jobs/{jid}/rtstruct?version=goc")
        assert b1 != b2
        ds = json.loads(_req(base, "/api/dataset")[2])
        assert ds["cases"] == 1 and any(r["name"] == "Brainstem" and r["new"] == 1 for r in ds["structures"])
        # mở lại app: ca vẫn được đánh dấu đã duyệt
        assert JobManager(tmp_path / "results", None).jobs[jid].approved
    finally:
        server.shutdown()


def test_export_anonymized_and_cleanup(ct_dir, tmp_path):
    import SimpleITK as sitk

    manager = JobManager(tmp_path / "results", lambda device: FakeSegmenter(thorax_labels()))
    jobs = []
    for k in range(2):
        job = manager.create("thorax", False, False, protocol="custom", intent="curative", names=["Heart", "Lung_L"])
        for f in ct_dir.iterdir():
            (job.dir / "upload" / f.name).write_bytes(f.read_bytes())
        manager._run(job)
        assert job.status == "done", job.error
        jobs.append(job)
    v = manager.viewer(jobs[0])
    v.add_structure("Brainstem", (255, 0, 0))
    i = v.centers()["Heart"]["axial"]
    v.edit("Brainstem", "axial", i, "add", [(20, 20)], 4)
    manager.approve(jobs[0])

    out = tmp_path / "export"
    r = manager.export_dataset(out)
    assert r["cases"] == 1
    cases = [d for d in out.iterdir() if d.is_dir()]
    assert len(cases) == 1 and cases[0].name.startswith("case_")
    labels = {f.name for f in (cases[0] / "labels").iterdir()}
    assert {"Heart.nii.gz", "Lung_L.nii.gz", "Brainstem.nii.gz"} <= labels
    ct = sitk.ReadImage(str(cases[0] / "ct.nii.gz"))
    lab = sitk.ReadImage(str(cases[0] / "labels" / "Heart.nii.gz"))
    assert ct.GetSize() == lab.GetSize()
    assert int(sitk.GetArrayFromImage(lab).sum()) == int(v.full_mask("Heart").sum())
    # không còn thông tin nhận dạng trong thư mục xuất
    blob = b"".join(f.read_bytes() for f in out.rglob("*") if f.is_file() and f.suffix == ".json")
    assert b"PHANTOM" not in blob and jobs[0].id.encode() not in blob
    import gzip
    assert b"PHANTOM" not in gzip.decompress((cases[0] / "ct.nii.gz").read_bytes())
    # bảng đối chiếu nằm ngoài thư mục xuất; xuất lại không tạo mã mới
    assert (tmp_path / "results" / "_export_map.json").exists()
    manager.export_dataset(out)
    assert len([d for d in out.iterdir() if d.is_dir()]) == 1

    # xoá ca chưa duyệt: giữ ca đã duyệt
    pv = manager.cleanup_preview()
    assert pv["count"] == 1
    res = manager.cleanup()
    assert res["deleted"] == 1 and jobs[0].id in manager.jobs and jobs[1].id not in manager.jobs
    assert not jobs[1].dir.exists() and jobs[0].dir.exists()


def test_checklist_and_approve_warning(ct_dir, tmp_path):
    manager = JobManager(tmp_path / "results", lambda device: FakeSegmenter(thorax_labels()))
    ref = {}
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(manager, ref))
    base = f"http://127.0.0.1:{server.server_address[1]}"
    threading.Thread(target=server.serve_forever, daemon=True).start()
    post = lambda path, obj: json.loads(_req(base, path, "POST", json.dumps(obj).encode())[2])
    try:
        job = manager.create("auto", False, False, protocol="headneck", intent="curative",
                             names=["SpinalCanal", "Lung_L"])
        for f in ct_dir.iterdir():
            (job.dir / "upload" / f.name).write_bytes(f.read_bytes())
        manager._run(job)
        assert job.status == "done", job.error
        chk = json.loads(_req(base, f"/api/jobs/{job.id}/checklist")[2])
        assert "Brainstem" in chk["missing"] and len(chk["required"]) == 29
        try:
            post(f"/api/jobs/{job.id}/approve", {})
            raise AssertionError("phải nhắc thiếu cấu trúc")
        except urllib.error.HTTPError as e:
            assert e.code == 409 and "Brainstem" in json.loads(e.read())["missing"]
        post(f"/api/jobs/{job.id}/structure", {"name": "Brainstem"})
        post(f"/api/jobs/{job.id}/edit", {"name": "Brainstem", "axis": "axial", "i": 10, "op": "add",
                                          "points": [[30, 20]], "radius_mm": 4})
        chk2 = json.loads(_req(base, f"/api/jobs/{job.id}/checklist")[2])
        assert "Brainstem" in chk2["present"]
        r = post(f"/api/jobs/{job.id}/approve", {"force": True})
        assert "Brainstem" not in r["missing"] and "Cochlea_L" in r["missing"]
    finally:
        server.shutdown()
