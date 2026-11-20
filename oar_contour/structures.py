"""Bảng ánh xạ nhãn TotalSegmentator -> tên cơ quan chuẩn TG-263.

Chỉ dùng các task MIỄN PHÍ (Apache-2.0) của TotalSegmentator. Các task cần
license thương mại (brain_structures, appendicular_bones, heartchambers_highres,
...) KHÔNG được dùng ở đây.

Mỗi Structure là hợp (union) của một hoặc nhiều nhãn trong một task.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Structure:
    name: str  # tên TG-263, đúng tên sẽ hiện trong Monaco
    task: str  # task TotalSegmentator sinh ra nhãn
    labels: tuple[str, ...]  # tên nhãn TotalSegmentator, hợp lại thành 1 cấu trúc
    color: tuple[int, int, int]
    # "left"/"right": sau khi hợp nhãn, chỉ giữ nửa trái/phải bệnh nhân
    # (dùng cho nhãn không tách bên, ví dụ "breast").
    side: str | None = None
    note: str = ""
    # True: cơ quan liền một khối -> chỉ giữ khối lớn nhất, bỏ mảnh vụn khoanh nhầm chỗ khác
    single: bool = True


# Cơ quan có thể gồm nhiều khối rời trên ảnh -> KHÔNG lọc khối lớn nhất
_MULTI_PART = {"Lungs", "Bowel_Small", "Colon", "Bone_Pelvic", "Bone_Hips", "SpinalCord", "Esophagus", "Duodenum",
               "Breast_L", "Breast_R", "Glnd_Thyroid", "Trachea", "OpticNrv_L", "OpticNrv_R"}


def _s(name, task, labels, color, side=None, note=""):
    if isinstance(labels, str):
        labels = (labels,)
    return Structure(name, task, tuple(labels), tuple(color), side, note, name not in _MULTI_PART)


from .ts_labels import KNOWN_LABELS, TOTAL_PART_OF  # noqa: E402  (nhãn TotalSegmentator, không cần import TS)

# Cấu trúc hay dùng: màu cố định + ghi chú khi duyệt. Toàn bộ danh mục (hơn 200 cấu trúc) nằm ở catalog.py.
CURATED = [
    _s("Lung_L", "total", ["lung_upper_lobe_left", "lung_lower_lobe_left"], (0, 170, 255)),
    _s("Lung_R", "total", ["lung_upper_lobe_right", "lung_middle_lobe_right", "lung_lower_lobe_right"], (0, 120, 255)),
    _s("Lungs", "total", ["lung_upper_lobe_left", "lung_lower_lobe_left", "lung_upper_lobe_right",
                          "lung_middle_lobe_right", "lung_lower_lobe_right"], (80, 200, 255)),
    _s("Heart", "total", "heart", (255, 0, 0),
       note="Tim toàn bộ; ranh giới trên (mạch máu lớn) cần bác sĩ kiểm tra theo atlas của khoa."),
    _s("Esophagus", "total", "esophagus", (255, 170, 0)),
    _s("Trachea", "total", "trachea", (120, 255, 255)),
    _s("SpinalCord", "total", "spinal_cord", (255, 255, 0),
       note="Tủy sống thật, không phải ống sống. Khoa vẽ SpinalCanal thì cần đối chiếu."),
    _s("A_Aorta", "total", "aorta", (200, 0, 60)),
    _s("Breast_L", "breasts", "breast", (255, 150, 200), side="left",
       note="Vú tuyến (OAR vú đối bên), KHÔNG phải CTV vú."),
    _s("Breast_R", "breasts", "breast", (255, 110, 180), side="right",
       note="Vú tuyến (OAR vú đối bên), KHÔNG phải CTV vú."),
    _s("Liver", "total", "liver", (160, 80, 40)),
    _s("Kidney_L", "total", ["kidney_left", "kidney_cyst_left"], (255, 120, 0)),
    _s("Kidney_R", "total", ["kidney_right", "kidney_cyst_right"], (255, 80, 0)),
    _s("Stomach", "total", "stomach", (255, 200, 120)),
    _s("Duodenum", "total", "duodenum", (220, 160, 255)),
    _s("Bowel_Small", "total", "small_bowel", (255, 220, 0)),
    _s("Colon", "total", "colon", (180, 120, 60),
       note="Gồm cả đại tràng sigma; trực tràng cần vẽ thêm."),
    _s("Pancreas", "total", "pancreas", (255, 180, 200)),
    _s("Spleen", "total", "spleen", (140, 0, 140)),
    _s("Gallbladder", "total", "gallbladder", (120, 200, 60)),
    _s("Bladder", "total", "urinary_bladder", (255, 255, 0),
       note="Thể tích bàng quang thay đổi theo mức độ đầy; kiểm tra thành bàng quang."),
    _s("Femur_L", "total", "femur_left", (0, 200, 0),
       note="Toàn bộ xương đùi trong trường chụp. Khoa dùng Femur_Head thì cắt bớt theo quy ước."),
    _s("Femur_R", "total", "femur_right", (0, 150, 0),
       note="Toàn bộ xương đùi trong trường chụp. Khoa dùng Femur_Head thì cắt bớt theo quy ước."),
    _s("Bone_Pelvic", "total", ["hip_left", "hip_right", "sacrum"], (200, 200, 160),
       note="Gồm xương cùng (chạy lâu hơn Bone_Hips)."),
    _s("Bone_Hips", "total", ["hip_left", "hip_right"], (215, 205, 150),
       note="Xương chậu 2 bên (cánh chậu, ngồi, mu), không gồm xương cùng: dùng cho xạ tránh tủy xương."),
    _s("Prostate", "total", "prostate", (0, 255, 200)),
    _s("A_Iliac_L", "total", "iliac_artery_left", (230, 40, 40),
       note="Mốc vẽ CTV hạch chậu (~7 mm quanh mạch)."),
    _s("A_Iliac_R", "total", "iliac_artery_right", (200, 20, 20),
       note="Mốc vẽ CTV hạch chậu (~7 mm quanh mạch)."),
    _s("V_Iliac_L", "total", "iliac_vena_left", (40, 90, 230)),
    _s("V_Iliac_R", "total", "iliac_vena_right", (20, 60, 200)),
    _s("V_Venacava_I", "total", "inferior_vena_cava", (60, 110, 255),
       note="Cùng động mạch chủ làm mốc vẽ CTV hạch cạnh động mạch chủ."),
    _s("Brain", "total", "brain", (255, 200, 160)),
    _s("Parotid_L", "head_glands_cavities", "parotid_gland_left", (0, 200, 255)),
    _s("Parotid_R", "head_glands_cavities", "parotid_gland_right", (0, 140, 255)),
    _s("Glnd_Submand_L", "head_glands_cavities", "submandibular_gland_left", (120, 255, 120)),
    _s("Glnd_Submand_R", "head_glands_cavities", "submandibular_gland_right", (60, 200, 60)),
    _s("Eye_L", "head_glands_cavities", "eye_left", (255, 255, 120)),
    _s("Eye_R", "head_glands_cavities", "eye_right", (255, 220, 80)),
    _s("Lens_L", "head_glands_cavities", "eye_lens_left", (255, 0, 255)),
    _s("Lens_R", "head_glands_cavities", "eye_lens_right", (200, 0, 200)),
    _s("OpticNrv_L", "head_glands_cavities", "optic_nerve_left", (255, 120, 0)),
    _s("OpticNrv_R", "head_glands_cavities", "optic_nerve_right", (220, 90, 0)),
    _s("Bone_Mandible", "craniofacial_structures", "mandible", (230, 230, 200)),
    _s("Glnd_Thyroid", "total", "thyroid_gland", (150, 80, 255)),
]

# Danh sách MẶC ĐỊNH cho từng vùng (tên trong danh mục). Bác sĩ chỉnh trong app: "Chọn cơ quan".
DEFAULT_PRESETS: dict[str, list[str]] = {
    "thorax": ["Lung_L", "Lung_R", "Lungs", "Heart", "Esophagus", "Trachea", "SpinalCord", "A_Aorta",
               "Breast_L", "Breast_R", "Liver", "Stomach", "Glnd_Thyroid", "Kidney_L", "Kidney_R",
               "Humerus_L", "Humerus_R", "Ribs"],
    "abdomen": ["Liver", "Kidney_L", "Kidney_R", "Stomach", "Duodenum", "Bowel_Small", "Colon",
                "SpinalCord", "Pancreas", "Spleen", "Gallbladder", "Esophagus", "Heart", "Lung_L", "Lung_R",
                "Musc_Autochthon_L", "Musc_Autochthon_R", "Iliopsoas_L", "Iliopsoas_R"],
    "pelvis": ["Bladder", "Femur_L", "Femur_R", "Bowel_Small", "Colon", "Bone_Pelvic", "Prostate",
               "Kidney_L", "Kidney_R", "SpinalCord", "Sacrum", "Iliopsoas_L", "Iliopsoas_R",
               "Gluteus_Maximus_L", "Gluteus_Maximus_R"],
    "headneck": ["Brain", "SpinalCord", "Parotid_L", "Parotid_R", "Glnd_Submand_L", "Glnd_Submand_R",
                 "Eye_L", "Eye_R", "Lens_L", "Lens_R", "OpticNrv_L", "OpticNrv_R", "Bone_Mandible",
                 "Glnd_Thyroid", "Esophagus", "Trachea"],
}
SITE_NAMES = {"thorax": "Ngực / vú", "abdomen": "Bụng", "pelvis": "Tiểu khung", "headneck": "Đầu cổ"}

# Cơ quan quan trọng mà model KHÔNG có -> bác sĩ tự vẽ (sau này: model khoa tự huấn luyện).
NOT_COVERED: dict[str, list[str]] = {
    "thorax": ["LAD / buồng tim", "Brachial plexus", "Bronchus_Prox"],
    "abdomen": ["Bowel_Bag", "Liver-GTV (tự trừ trong Monaco)"],
    "pelvis": ["Rectum", "Anal canal", "Bowel_Bag", "Femur_Head (đang là cả xương đùi)", "Penile bulb"],
    "headneck": ["Brainstem", "OpticChiasm", "Cochlea", "Larynx (có sụn giáp/nhẫn trong danh mục)",
                 "Oral cavity", "Lips", "Brachial plexus", "Pituitary"],
}

# Tự nhận diện vùng chụp (site="auto") từ model nhanh 6 mm.
# Một vùng được chọn khi tổng thể tích các nhãn >= ngưỡng (cc), tức là phần LỚN cơ quan
# chuẩn nằm trong ảnh, không phải chỉ một mảnh lọt vào mép trường chụp.
REGION_RULES: dict[str, list[tuple[tuple[str, ...], float]]] = {
    "headneck": [(("brain",), 300.0), (("skull",), 150.0)],
    "thorax": [(("lung_upper_lobe_left", "lung_lower_lobe_left", "lung_upper_lobe_right",
                 "lung_middle_lobe_right", "lung_lower_lobe_right"), 1500.0)],
    "abdomen": [(("liver",), 900.0), (("kidney_left", "kidney_right"), 180.0)],
    "pelvis": [(("urinary_bladder",), 40.0), (("hip_left", "hip_right"), 250.0)],
}

# Model phụ chỉ chạy trên đoạn ảnh (theo trục đầu–chân) chứa các nhãn này (+ lề), không chạy cả người.
TASK_CROP: dict[str, tuple[tuple[str, ...], float]] = {
    "head_glands_cavities": (("brain", "skull", "vertebrae_C1", "vertebrae_C2", "vertebrae_C3"), 40.0),
    "craniofacial_structures": (("brain", "skull", "vertebrae_C1", "vertebrae_C2", "vertebrae_C3",
                                 "vertebrae_C4"), 40.0),
    "headneck_bones_vessels": (("brain", "skull", "vertebrae_C1", "vertebrae_C2", "vertebrae_C3", "vertebrae_C4",
                                "vertebrae_C5", "vertebrae_C6", "vertebrae_C7", "thyroid_gland"), 30.0),
    "head_muscles": (("brain", "skull", "vertebrae_C1", "vertebrae_C2", "vertebrae_C3"), 40.0),
    "headneck_muscles": (("skull", "vertebrae_C1", "vertebrae_C2", "vertebrae_C3", "vertebrae_C4",
                          "vertebrae_C5", "vertebrae_C6", "vertebrae_C7", "vertebrae_T1"), 30.0),
    "liver_segments": (("liver",), 20.0),
    "breasts": (("lung_upper_lobe_left", "lung_lower_lobe_left", "lung_upper_lobe_right",
                 "lung_middle_lobe_right", "lung_lower_lobe_right", "sternum"), 40.0),
}


def structures_for(sites: list[str], presets: dict[str, list[str]] | None = None) -> list[Structure]:
    """Hợp danh sách cấu trúc của nhiều vùng (theo preset của khoa, mặc định DEFAULT_PRESETS), bỏ trùng."""
    from .catalog import catalog

    presets = presets or DEFAULT_PRESETS
    cat = catalog()
    seen: dict[str, Structure] = {}
    for site in sites:
        if site not in DEFAULT_PRESETS:
            raise ValueError(f"Vùng không hợp lệ: {site!r}. Chọn một trong {sorted(DEFAULT_PRESETS)} hoặc 'auto'.")
        for name in presets.get(site, DEFAULT_PRESETS[site]):
            if name in cat:
                seen.setdefault(name, cat[name])
    return list(seen.values())


def site_structures(site: str) -> list[Structure]:
    return structures_for([site])


def total_labels_for(structures: list[Structure]) -> list[str]:
    """Các nhãn của task "total" thực sự cần -> chỉ chạy phần model chứa chúng (roi_subset)."""
    return sorted({l for s in structures if s.task == "total" for l in s.labels})


def tasks_for(structures: list[Structure]) -> list[str]:
    tasks = []
    for s in structures:
        if s.task not in tasks:
            tasks.append(s.task)
    # "total" luôn chạy đầu tiên (dùng để nhận diện vùng)
    return sorted(tasks, key=lambda t: t != "total")
