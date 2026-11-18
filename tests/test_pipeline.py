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


def test_thorax_auto_roundtrip(ct_dir, tmp_path):
    labels = thorax_labels()
    seg = FakeSegmenter(labels)
    out = tmp_path / "rs.dcm"
    report = run_pipeline(ct_dir, out, seg, site="auto")

    assert report.sites == ["thorax"]
    assert seg.calls == ["total", "breasts"]
    for name in ["Lung_L", "Lung_R", "Lungs", "Heart", "SpinalCord", "Breast_L", "Breast_R"]:
        assert name in report.written
    assert "Esophagus" in report.skipped_empty
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


def test_detect_regions():
    t = np.zeros((10, 50, 50), np.int16)
    t[:, :30, :30] = 5  # liver 9000 voxels
    assert detect_regions(t, TOTAL_MAP) == ["abdomen"]
    t[:, 30:, 30:] = 90  # brain
    assert detect_regions(t, TOTAL_MAP) == ["headneck", "abdomen"]


def test_not_covered_deduplicated(ct_dir, tmp_path):
    report = run_pipeline(ct_dir, tmp_path / "x.dcm", FakeSegmenter(thorax_labels()), site="abdomen,pelvis")
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
