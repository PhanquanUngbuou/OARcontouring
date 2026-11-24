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
            # đầu cổ / não: không chạy xương sườn, đốt sống, cơ vùng đầu cổ
            assert not {"ribs", "vertebrae"} & set(c["total_parts"]), (pid, intent)
            assert not {"headneck_muscles", "head_muscles"} & set(c["tasks"])
            if pid != "headneck" or intent == "palliative":  # mạch cảnh chỉ ở đầu cổ triệt căn (khoa chọn)
                assert "cardiac" not in c["total_parts"] and "headneck_bones_vessels" not in c["tasks"], (pid, intent)
    assert "Bone_Mandible" in default_names("headneck", "curative")
    for p in PROTOCOLS:
        for intent in ("curative", "palliative"):
            parts = estimate_cost(default_names(p.id, intent))["total_parts"]
            if "ribs" in parts:
                assert p.id in ("lung_sbrt", "liver_sbrt"), p.id
            if "vertebrae" in parts:
                assert p.id == "spine_sbrt", p.id
    assert len([n for n in default_names("spine_sbrt", "curative") if n.startswith("Bone_Vertebra_")]) >= 20
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


def test_parotid_refine_adds_landmarks_and_refined_structure(ct_dir, tmp_path):
    import numpy as np
    from conftest import NX, NY, NZ
    from oar_contour.parotid_refine import LANDMARK_NAMES

    # phantom: "tuyến mang tai" model vẽ thiếu (lõi nhỏ) trong vùng mô mềm lớn hơn, xương hàm chặn một phía
    t = np.zeros((NZ, NY, NX), np.int16)
    t[:, 40:43, 31:33] = 79
    t[0:4, 5:15, 10:30] = 90  # não: để app biết đây là vùng đầu (chạy các model đầu cổ)
    hg = np.zeros_like(t)
    hg[8:12, 20:26, 44:50] = 7  # parotid_gland_left (lõi)
    cf = np.zeros_like(t)
    cf[4:16, 20:30, 40:42] = 1  # mandible
    seg = FakeSegmenter({"total": t, "head_glands_cavities": hg, "craniofacial_structures": cf})
    from oar_contour.ts_labels import KNOWN_LABELS
    report = run_pipeline(ct_dir, tmp_path / "p.dcm", seg, names=["Parotid_L", "SpinalCord"], refine_parotid=True)
    assert "Parotid_L_Ref" in report.written
    assert report.written["Parotid_L_Ref"] > report.written["Parotid_L"]
    assert "Bone_Mandible" in report.written  # mốc được xuất ra
    assert {"head_muscles", "headneck_bones_vessels", "craniofacial_structures"} <= set(seg.calls)
    assert all(n in __import__("oar_contour.catalog", fromlist=["x"]).catalog() for n in LANDMARK_NAMES)


def test_spinal_canal_draft_grows_from_cord_and_stops_at_bone():
    import numpy as np
    from oar_contour.pipeline import spinal_canal_from_cord

    hu = np.full((4, 40, 40), 300.0)  # xương
    yy, xx = np.mgrid[0:40, 0:40]
    canal = (yy - 20) ** 2 + (xx - 20) ** 2 <= 36  # ống sống bán kính 6 voxel, dịch não tuỷ HU 10
    hu[:, canal] = 10.0
    cord = np.zeros(hu.shape, bool)
    cord[:, (yy - 20) ** 2 + (xx - 20) ** 2 <= 9] = True
    out = spinal_canal_from_cord(cord, hu, (1.0, 1.0, 3.0), max_mm=8)
    assert out[:, canal].all() and not out[:, ~canal].any()


def test_headneck_training_set_has_department_choices():
    from oar_contour.protocols import TRAINING_SETS

    t = TRAINING_SETS["headneck"]
    assert {"SpinalCanal", "SpinalCord", "Larynx"} <= set(t) and len(t) == 30
    assert not [n for n in t if n.startswith("Musc_Constrict")]
    assert {"Joint_TM_L", "Joint_TM_R", "A_Carotid_L", "A_Carotid_Int_R"} <= set(t)
