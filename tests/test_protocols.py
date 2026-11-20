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
    for p in PROTOCOLS:
        if p.group not in ("U đầu cổ", "U não"):
            continue
        for intent in ("curative", "palliative"):
            c = estimate_cost(default_names(p.id, intent))
            # đầu cổ / não: không chạy tim mạch, xương sườn, đốt sống, model mạch máu/cơ cổ
            assert not {"cardiac", "ribs", "vertebrae"} & set(c["total_parts"]), (p.id, intent)
            assert not {"headneck_bones_vessels", "headneck_muscles", "head_muscles"} & set(c["tasks"])
    # xương hàm dưới có trong ung thư đầu cổ triệt căn
    for pid in ("hn_nasopharynx", "hn_oral", "hn_oropharynx", "hn_larynx", "hn_hypopharynx", "hn_unknown"):
        assert "Bone_Mandible" in default_names(pid, "curative")
    # xương sườn chỉ ở SBRT phổi, đốt sống chỉ ở SBRT cột sống
    for p in PROTOCOLS:
        for intent in ("curative", "palliative"):
            parts = estimate_cost(default_names(p.id, intent))["total_parts"]
            if "ribs" in parts:
                assert (p.id, intent) == ("lung_sbrt", "curative")
            if "vertebrae" in parts:
                assert (p.id, intent) == ("bone_spine", "curative")
    assert len([n for n in default_names("bone_spine", "curative") if n.startswith("Vertebrae_")]) >= 20


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
    names = default_names("brain_wbrt", "curative")
    try:
        run_pipeline(ct_dir, tmp_path / "b.dcm", seg, names=names, manual=list(PROTOCOL_BY_ID["brain_wbrt"].manual))
    except RuntimeError:
        pass  # phantom không có mắt -> "Không tạo được cấu trúc nào" là đúng
    assert seg.calls == ["total", "head_glands_cavities"]
    assert seg.kwargs[0]["fastest"] is True


def test_all_head_neck_curative_include_optic_and_lens():
    for p in PROTOCOLS:
        if p.group == "U đầu cổ":
            names = default_names(p.id, "curative")
            assert {"Lens_L", "Lens_R", "OpticNrv_L", "OpticNrv_R"} <= set(names), p.id
    assert {"hn_orbit_lymphoma", "hn_nasal_lymphoma"} <= set(PROTOCOL_BY_ID)
