import csv
import shutil

import numpy as np
from pydicom import dcmread
from rt_utils import RTStructBuilder

from oar_contour.anonymize import anonymize_tree
from oar_contour.app import JobManager
from oar_contour.batch import run_batch
from oar_contour.pipeline import run_pipeline

from conftest import FakeSegmenter, make_ct_series, thorax_labels


def test_anonymize_keeps_rtstruct_linked_and_removes_phi(tmp_path):
    src = tmp_path / "src"
    for k, name in enumerate(["Nguyen Van A", "Tran Thi B"]):
        ct = make_ct_series(src / name / "ct", seed=k)
        for f in ct.iterdir():  # thêm thông tin nhận dạng
            ds = dcmread(f)
            ds.PatientName, ds.PatientID, ds.PatientBirthDate = name, f"BN{k}9999", "19600101"
            ds.InstitutionName, ds.ReferringPhysicianName, ds.AccessionNumber = "BV K", "BS X", "ACC123"
            ds.StudyDate, ds.StudyTime = "20250315", "101530"
            ds.save_as(f)
        run_pipeline(ct, src / name / "RS.dcm", FakeSegmenter(thorax_labels()), site="thorax")

    dst, map_path = tmp_path / "anon", tmp_path / "maps" / "map.csv"
    anonymize_tree(src, dst, map_path, progress=lambda *_: None)
    cases = sorted(p for p in dst.iterdir() if p.is_dir())
    assert len(cases) == 2
    for case in cases:
        files = list(case.rglob("*.dcm"))
        blob = b"".join(f.read_bytes() for f in files)
        for bad in (b"Nguyen", b"Tran", b"9999", b"19600101", b"BV K", b"BS X", b"ACC123", b"20250315", b"101530",
                    b"PHANTOM"):
            assert bad not in blob, bad
        ds = dcmread(next((case / "CT").iterdir()))
        assert ds.PatientName == case.name and ds.PatientIdentityRemoved == "YES"
        # RTSTRUCT vẫn khớp ảnh CT sau ẩn danh
        rt = RTStructBuilder.create_from(str(case / "CT"), str(next((case / "RTSTRUCT").iterdir())))
        assert rt.get_roi_mask_by_name("Heart").any()
        # tạo được RTSTRUCT mới trên ảnh đã ẩn danh (cần ngày/giờ chụp)
        RTStructBuilder.create_new(str(case / "CT"))
    rows = list(csv.DictReader(open(map_path, encoding="utf-8")))
    assert {r["thu_muc_goc"] for r in rows} == {"Nguyen Van A", "Tran Thi B"}
    assert not list(dst.rglob("*.csv"))  # bảng đối chiếu không nằm trong thư mục ẩn danh


def test_batch_results_open_in_app_and_resume(tmp_path):
    cases = tmp_path / "cases"
    for k in range(2):
        make_ct_series(cases / f"QC_{k}" / "CT", seed=k)
    res = tmp_path / "results"
    s = run_batch(cases, res, "breast", "curative", segmenter_factory=lambda d: FakeSegmenter(thorax_labels()),
                  progress=lambda *_: None)
    assert s["ok"] == 2 and not s["failed"]
    m = JobManager(res, None)  # như khi mở app trên MacBook
    assert len(m.jobs) == 2 and {j.source for j in m.jobs.values()} == {"QC_0", "QC_1"}
    j = next(iter(m.jobs.values()))
    assert j.status == "done" and j.label() == "U vú · triệt căn"
    v = m.viewer(j)
    assert "Heart" in v.masks
    # chép kết quả sang "máy khác" vẫn mở được
    shutil.copytree(res, tmp_path / "mac_OAR_ketqua")
    assert len(JobManager(tmp_path / "mac_OAR_ketqua", None).jobs) == 2
    # chạy lại: bỏ qua ca đã xong
    s2 = run_batch(cases, res, "breast", "curative", segmenter_factory=lambda d: FakeSegmenter(thorax_labels()),
                   progress=lambda *_: None)
    assert s2["skipped"] == 2 and s2["ok"] == 0
