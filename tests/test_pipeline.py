import numpy as np
import pytest
from rt_utils import RTStructBuilder

from oar_contour.evaluate import dice
from oar_contour.pipeline import STRUCTURE_SET_LABEL, _patient_x, detect_regions, run_pipeline
from oar_contour.segment import load_ct_series

from conftest import PRONE, TOTAL_MAP, FakeSegmenter, make_ct_series, thorax_labels


def _rt_mask_to_sitk_order(rt, image, mask):
    """Đổi mask của rt_utils (rows, cols, n theo thứ tự rt_utils) về (z, y, x) của SimpleITK."""
    out = np.zeros(image.GetSize()[::-1], bool)
    for n, ds in enumerate(rt.series_data):
        k = int(round(image.TransformPhysicalPointToContinuousIndex(
            [float(v) for v in ds.ImagePositionPatient])[2]))
        out[k] = mask[:, :, n]
    return out


SMALL_RULES = {  # ngưỡng thể tích thu nhỏ cho phantom bé
    "headneck": [(("brain",), 5.0)],
    "thorax": [(("lung_upper_lobe_left", "lung_upper_lobe_right"), 20.0)],
    "abdomen": [(("liver",), 50.0)],
    "pelvis": [(("urinary_bladder",), 5.0)],
}


def test_thorax_auto_roundtrip(ct_dir, tmp_path, monkeypatch):
    import oar_contour.pipeline as pl

    monkeypatch.setattr(pl, "REGION_RULES", SMALL_RULES)
    labels = thorax_labels()
    seg = FakeSegmenter(labels)
    out = tmp_path / "rs.dcm"
    report = run_pipeline(ct_dir, out, seg, site="auto")

    assert report.sites == ["thorax"]
    assert seg.calls == ["total", "total", "breasts"]
    assert seg.sizes[2] == 24  # phổi chiếm lát 4..19, lề 40 mm -> cả ảnh
    assert seg.kwargs[0]["fastest"] is True  # nhận diện vùng
    assert "heart" in seg.kwargs[1]["roi_subset"] and "liver" not in seg.kwargs[1]["roi_subset"]
    for name in ["Lung_L", "Lung_R", "Lungs", "Heart", "SpinalCord", "Breast_L", "Breast_R"]:
        assert name in report.written
    assert "Esophagus" in report.skipped_empty
    assert "A_Aorta" not in report.written and "Liver" not in report.skipped_empty
    assert "Brachial plexus" in report.not_covered

    rt = RTStructBuilder.create_from(str(ct_dir), str(out))
    assert rt.ds.StructureSetLabel == STRUCTURE_SET_LABEL
    image = load_ct_series(ct_dir)
    t = labels["total"]
    expected = {
        "Lung_L": np.isin(t, [10, 11]),
        "Lung_R": np.isin(t, [12, 13, 14]),
        "Heart": t == 51,
        "SpinalCord": t == 79,
    }
    for name, exp in expected.items():
        got = _rt_mask_to_sitk_order(rt, image, rt.get_roi_mask_by_name(name))
        assert dice(got, exp) > 0.98, name


def test_breast_split_follows_patient_side(tmp_path):
    for orient in (None, PRONE):
        ct = make_ct_series(tmp_path / f"ct_{orient}", **({"orientation": orient} if orient else {}))
        out = tmp_path / f"rs_{orient}.dcm"
        run_pipeline(ct, out, FakeSegmenter(thorax_labels()), site="thorax")
        image = load_ct_series(ct)
        xs = _patient_x(image)
        rt = RTStructBuilder.create_from(str(ct), str(out))
        left = _rt_mask_to_sitk_order(rt, image, rt.get_roi_mask_by_name("Breast_L"))
        right = _rt_mask_to_sitk_order(rt, image, rt.get_roi_mask_by_name("Breast_R"))
        cols_l = np.nonzero(left)[2]
        cols_r = np.nonzero(right)[2]
        # Bên trái bệnh nhân = x (LPS) lớn hơn
        assert xs[cols_l].min() > xs[cols_r].max()
        assert not (left & right).any()


def test_reversed_slice_direction(tmp_path):
    ct = make_ct_series(tmp_path / "ct", z_step=-3.0)
    out = tmp_path / "rs.dcm"
    labels = thorax_labels()
    run_pipeline(ct, out, FakeSegmenter(labels), site="thorax")
    image = load_ct_series(ct)
    rt = RTStructBuilder.create_from(str(ct), str(out))
    got = _rt_mask_to_sitk_order(rt, image, rt.get_roi_mask_by_name("Heart"))
    assert dice(got, labels["total"] == 51) > 0.98


def test_detect_regions_by_volume():
    t = np.zeros((10, 50, 50), np.int16)
    t[:, :30, :30] = 5  # gan 9000 voxel
    assert detect_regions(t, TOTAL_MAP, voxel_cc=0.2) == ["abdomen"]  # 1800 cc
    t[:2, 40:, 40:] = 90  # mảnh não nhỏ lọt mép ảnh: 200 voxel = 40 cc -> KHÔNG tính đầu cổ
    assert detect_regions(t, TOTAL_MAP, voxel_cc=0.2) == ["abdomen"]
    t[:, 30:, 30:] = 90  # não đủ lớn: 4000 voxel = 800 cc
    assert detect_regions(t, TOTAL_MAP, voxel_cc=0.2) == ["headneck", "abdomen"]
    assert detect_regions(t, TOTAL_MAP, voxel_cc=0.01) == []  # cùng số voxel nhưng thể tích nhỏ


def test_stray_fragment_removed(ct_dir, tmp_path):
    labels = thorax_labels()
    labels["total"][22:24, 2:4, 2:4] = 51  # mảnh "tim" lạc ở góc ảnh
    report = run_pipeline(ct_dir, tmp_path / "x.dcm", FakeSegmenter(labels), site="thorax")
    exact = (labels["total"] == 51).sum() - 8
    assert report.written["Heart"] == pytest.approx(exact * 2 * 2 * 3 / 1000)


def test_extra_model_runs_on_cropped_slices(ct_dir, tmp_path):
    labels = thorax_labels()
    seg = FakeSegmenter(labels)
    run_pipeline(ct_dir, tmp_path / "x.dcm", seg, site="thorax")
    # vú chỉ chạy trên đoạn có phổi (lát 4..19) + lề 40 mm (14 lát -> chạm 2 đầu ảnh 24 lát)
    i = seg.calls.index("breasts")
    assert seg.sizes[i] <= 24
    # ca đầu cổ: model tuyến chỉ chạy quanh vùng não
    labels["total"][:] = 0
    labels["total"][0:4, 10:30, 10:50] = 90  # não ở 4 lát đầu
    labels["total"][:, 40:43, 31:33] = 79
    seg = FakeSegmenter(labels)
    run_pipeline(ct_dir, tmp_path / "y.dcm", seg, site="headneck")
    i = seg.calls.index("head_glands_cavities")
    assert seg.sizes[i] == 4 + 14  # 4 lát não + lề 40 mm (14 lát x 3 mm) phía dưới


def test_not_covered_deduplicated(ct_dir, tmp_path):
    labels = thorax_labels()
    labels["total"][2:20, 30:40, 30:40] = 5  # thêm "gan" để vùng bụng có cấu trúc
    report = run_pipeline(ct_dir, tmp_path / "x.dcm", FakeSegmenter(labels), site="abdomen,pelvis")
    assert report.not_covered.count("Bowel_Bag") == 1


def test_multi_series_dir_rejected(tmp_path):
    make_ct_series(tmp_path / "mix", seed=1)
    make_ct_series(tmp_path / "other", seed=2)
    for f in (tmp_path / "other").iterdir():
        f.rename(tmp_path / "mix" / f"b_{f.name}")
    with pytest.raises(ValueError, match="đúng 1 series"):
        load_ct_series(tmp_path / "mix")


def test_unknown_site_rejected(ct_dir, tmp_path):
    with pytest.raises(ValueError, match="Vùng không hợp lệ"):
        run_pipeline(ct_dir, tmp_path / "x.dcm", FakeSegmenter(thorax_labels()), site="brain")
