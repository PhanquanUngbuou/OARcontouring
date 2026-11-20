from oar_contour.catalog import catalog, estimate_cost
from oar_contour.pipeline import run_pipeline
from oar_contour.protocols import PROTOCOL_BY_ID, PROTOCOLS, default_names

from conftest import FakeSegmenter, thorax_labels


def test_every_protocol_name_exists_in_free_catalog():
    cat = catalog()
    for p in PROTOCOLS:
        for names in (p.curative, p.palliative):
            for n in names:
                assert n.endswith("*") or n in cat, f"{p.id}: {n}"
        assert default_names(p.id, "curative") and default_names(p.id, "palliative")


def test_minimal_models_rules():
    for pid in ("headneck", "brain", "brain_srs"):
        for intent in ("curative", "palliative"):
            c = estimate_cost(default_names(pid, intent))
            # đầu cổ / não: không chạy tim mạch, xương sườn, đốt sống, mạch máu/cơ cổ
            assert not {"cardiac", "ribs", "vertebrae"} & set(c["total_parts"]), (pid, intent)
            assert not {"headneck_bones_vessels", "headneck_muscles", "head_muscles"} & set(c["tasks"])
    assert "Bone_Mandible" in default_names("headneck", "curative")
    for p in PROTOCOLS:
        for intent in ("curative", "palliative"):
            parts = estimate_cost(default_names(p.id, intent))["total_parts"]
            if "ribs" in parts:
                assert p.id in ("lung_sbrt", "liver_sbrt"), p.id
            if "vertebrae" in parts:
                assert p.id == "spine_sbrt", p.id
    assert len([n for n in default_names("spine_sbrt", "curative") if n.startswith("Vertebrae_")]) >= 20
    assert {"Breast_L", "Breast_R"} <= set(default_names("breast", "curative"))
    assert not {"Breast_L", "Breast_R"} & set(default_names("thorax", "curative"))  # vú tách riêng


def test_protocol_run_uses_fixed_list_and_skips_total_when_not_needed(ct_dir, tmp_path):
    seg = FakeSegmenter(thorax_labels())
    report = run_pipeline(ct_dir, tmp_path / "a.dcm", seg, names=["Heart", "Lung_L", "Breast_R"],
                          manual=["LAD"], label="Vú trái · triệt căn")
    assert report.sites == ["Vú trái · triệt căn"] and report.not_covered == ["LAD"]
    assert set(report.written) == {"Heart", "Lung_L", "Breast_R"}
    assert seg.calls == ["total", "total", "breasts"]
    # xạ toàn não: chỉ cần model tuyến/mắt -> không chạy model total (ngoài model nhanh 6 mm)
    labels = thorax_labels()
    labels["total"][0:4, 10:30, 10:50] = 90
    seg = FakeSegmenter(labels)
    names = ["Eye_L", "Eye_R", "Lens_L", "Lens_R"]  # chỉ cần model mắt
    try:
        run_pipeline(ct_dir, tmp_path / "b.dcm", seg, names=names)
    except RuntimeError:
        pass  # phantom không có mắt -> "Không tạo được cấu trúc nào" là đúng
    assert seg.calls == ["total", "head_glands_cavities"]
    assert seg.kwargs[0]["fastest"] is True


def test_head_neck_curative_include_optic_and_lens():
    assert {"Lens_L", "Lens_R", "OpticNrv_L", "OpticNrv_R"} <= set(default_names("headneck", "curative"))
    assert {"brain_srs", "lung_sbrt", "liver_sbrt", "spine_sbrt"} <= set(PROTOCOL_BY_ID)
