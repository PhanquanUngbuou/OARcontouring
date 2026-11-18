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
_MULTI_PART = {"Lungs", "Bowel_Small", "Colon", "Bone_Pelvic", "SpinalCord", "Esophagus", "Duodenum",
               "Breast_L", "Breast_R", "Glnd_Thyroid", "Trachea", "OpticNrv_L", "OpticNrv_R"}


def _s(name, task, labels, color, side=None, note=""):
    if isinstance(labels, str):
        labels = (labels,)
    return Structure(name, task, tuple(labels), tuple(color), side, note, name not in _MULTI_PART)


# Danh sách đã rút gọn: chỉ giữ OAR thường dùng trong ràng buộc liều của khoa.
# Muốn thêm/bớt: sửa các danh sách dưới đây (nhãn TotalSegmentator xem bằng
# `python -c "from totalsegmentator.map_to_binary import class_map; print(class_map['total'])"`).

# ----------------------------------------------------------------- Ngực / vú
THORAX = [
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
    _s("Breast_L", "breasts", "breast", (255, 150, 200), side="left",
       note="Vú tuyến (OAR vú đối bên), KHÔNG phải CTV vú."),
    _s("Breast_R", "breasts", "breast", (255, 110, 180), side="right",
       note="Vú tuyến (OAR vú đối bên), KHÔNG phải CTV vú."),
]

# ----------------------------------------------------------------- Bụng
ABDOMEN = [
    _s("Liver", "total", "liver", (160, 80, 40)),
    _s("Kidney_L", "total", ["kidney_left", "kidney_cyst_left"], (255, 120, 0)),
    _s("Kidney_R", "total", ["kidney_right", "kidney_cyst_right"], (255, 80, 0)),
    _s("Stomach", "total", "stomach", (255, 200, 120)),
    _s("Duodenum", "total", "duodenum", (220, 160, 255)),
    _s("Bowel_Small", "total", "small_bowel", (255, 220, 0)),
    _s("Colon", "total", "colon", (180, 120, 60)),
    _s("SpinalCord", "total", "spinal_cord", (255, 255, 0)),
]

# ----------------------------------------------------------------- Tiểu khung
PELVIS = [
    _s("Bladder", "total", "urinary_bladder", (255, 255, 0),
       note="Thể tích bàng quang thay đổi theo mức độ đầy; kiểm tra thành bàng quang."),
    _s("Femur_L", "total", "femur_left", (0, 200, 0),
       note="Toàn bộ xương đùi trong trường chụp. Khoa dùng Femur_Head thì cắt bớt theo quy ước."),
    _s("Femur_R", "total", "femur_right", (0, 150, 0),
       note="Toàn bộ xương đùi trong trường chụp. Khoa dùng Femur_Head thì cắt bớt theo quy ước."),
    _s("Bowel_Small", "total", "small_bowel", (255, 220, 0)),
    _s("Colon", "total", "colon", (180, 120, 60),
       note="Gồm cả đại tràng sigma; trực tràng KHÔNG có trong model."),
    _s("Bone_Pelvic", "total", ["hip_left", "hip_right", "sacrum"], (200, 200, 160)),
]

# ----------------------------------------------------------------- Đầu cổ
HEAD_NECK = [
    _s("Brain", "total", "brain", (255, 200, 160)),
    _s("SpinalCord", "total", "spinal_cord", (255, 255, 0)),
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
    _s("Esophagus", "total", "esophagus", (255, 170, 0)),
]

SITES: dict[str, list[Structure]] = {
    "thorax": THORAX,
    "abdomen": ABDOMEN,
    "pelvis": PELVIS,
    "headneck": HEAD_NECK,
}

# Cơ quan quan trọng mà model KHÔNG có -> bác sĩ tự vẽ (sau này: model khoa tự huấn luyện).
NOT_COVERED: dict[str, list[str]] = {
    "thorax": ["LAD / buồng tim", "Brachial plexus", "Bronchus_Prox"],
    "abdomen": ["Bowel_Bag", "Liver-GTV (tự trừ trong Monaco)"],
    "pelvis": ["Rectum", "Anal canal", "Bowel_Bag", "Femur_Head (đang là cả xương đùi)", "Penile bulb"],
    "headneck": ["Brainstem", "OpticChiasm", "Cochlea", "Larynx", "Pharyngeal constrictors",
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
    "breasts": (("lung_upper_lobe_left", "lung_lower_lobe_left", "lung_upper_lobe_right",
                 "lung_middle_lobe_right", "lung_lower_lobe_right", "sternum"), 40.0),
}


def structures_for(sites: list[str]) -> list[Structure]:
    """Hợp danh sách cấu trúc của nhiều vùng, bỏ trùng theo tên (giữ thứ tự)."""
    seen: dict[str, Structure] = {}
    for site in sites:
        if site not in SITES:
            raise ValueError(f"Vùng không hợp lệ: {site!r}. Chọn một trong {sorted(SITES)} hoặc 'auto'.")
        for s in SITES[site]:
            seen.setdefault(s.name, s)
    return list(seen.values())


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
