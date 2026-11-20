import pytest

from oar_contour.catalog import TASKS, catalog, estimate_cost
from oar_contour.structures import DEFAULT_PRESETS, NOT_COVERED, REGION_RULES, TASK_CROP, structures_for
from oar_contour.ts_labels import KNOWN_LABELS, TOTAL_PART_OF


def test_static_labels_match_installed_totalsegmentator():
    m = pytest.importorskip("totalsegmentator.map_to_binary")
    for task, labels in KNOWN_LABELS.items():
        assert task not in m.commercial_models, f"task {task} cần license"
        assert labels == list(m.class_map[task].values()), task
    for part, cmap in m.class_map_5_parts.items():
        if part.startswith("class_map_part_"):
            for label in cmap.values():
                assert TOTAL_PART_OF[label] == part.replace("class_map_part_", "")


def test_catalog_labels_valid_and_unique():
    cat = catalog()
    assert len(cat) > 200
    for name, s in cat.items():
        assert s.name == name
        assert s.task in TASKS
        assert set(s.labels) <= set(KNOWN_LABELS[s.task]), name
    total = set(KNOWN_LABELS["total"])
    for rules in REGION_RULES.values():
        for labels, _ in rules:
            assert set(labels) <= total
    for task, (labels, _) in TASK_CROP.items():
        assert task in TASKS and set(labels) <= total


def test_default_presets_exist_in_catalog():
    cat = catalog()
    assert set(DEFAULT_PRESETS) == set(NOT_COVERED) == set(REGION_RULES)
    for site, names in DEFAULT_PRESETS.items():
        assert len(names) == len(set(names))
        assert all(n in cat for n in names), site
    thorax = {s.name for s in structures_for(["thorax"])}
    assert {"Liver", "Stomach", "Heart", "Breast_L"} <= thorax  # không cắt gan/dạ dày ở vùng ngực nữa


def test_custom_preset_and_cost():
    names = {s.name for s in structures_for(["thorax"], {"thorax": ["Heart", "Lungs", "Không_có"]})}
    assert names == {"Heart", "Lungs"}
    c = estimate_cost(["Lungs", "Liver"])
    assert c["total_parts"] == ["organs"] and c["tasks"] == [] and c["units"] == 1
    c = estimate_cost(["Heart", "Parotid_L"])
    assert c["total_parts"] == ["cardiac"] and c["tasks"] == ["head_glands_cavities"]
