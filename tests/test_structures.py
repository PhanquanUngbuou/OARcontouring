import pytest

from oar_contour.structures import NOT_COVERED, REGION_MARKERS, SITES


def test_every_label_exists_in_free_totalsegmentator_task():
    m = pytest.importorskip("totalsegmentator.map_to_binary")
    for site, items in SITES.items():
        for s in items:
            assert s.task not in m.commercial_models, f"{s.name}: task {s.task} cần license"
            names = set(m.class_map[s.task].values())
            missing = set(s.labels) - names
            assert not missing, f"{site}/{s.name}: không có nhãn {missing} trong task {s.task}"
    total = set(m.class_map["total"].values())
    for markers in REGION_MARKERS.values():
        assert set(markers) <= total


def test_sites_consistent():
    assert set(SITES) == set(NOT_COVERED) == set(REGION_MARKERS)
    for items in SITES.values():
        names = [s.name for s in items]
        assert len(names) == len(set(names))
