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


def _s(name, task, labels, color, side=None, note=""):
    if isinstance(labels, str):
        labels = (labels,)
    return Structure(name, task, tuple(labels), tuple(color), side, note)


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
    _s("A_Aorta", "total", "aorta", (200, 0, 60)),
    _s("Breast_L", "breasts", "breast", (255, 150, 200), side="left",
       note="Vú tuyến (OAR vú đối bên), KHÔNG phải CTV vú."),
    _s("Breast_R", "breasts", "breast", (255, 110, 180), side="right",
       note="Vú tuyến (OAR vú đối bên), KHÔNG phải CTV vú."),
    _s("Glnd_Thyroid", "total", "thyroid_gland", (150, 80, 255)),
    _s("Liver", "total", "liver", (160, 80, 40)),
    _s("Stomach", "total", "stomach", (255, 200, 120)),
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
    _s("Pancreas", "total", "pancreas", (255, 180, 200)),
    _s("Spleen", "total", "spleen", (140, 0, 140)),
    _s("SpinalCord", "total", "spinal_cord", (255, 255, 0)),
    _s("Esophagus", "total", "esophagus", (255, 170, 0)),
    _s("Heart", "total", "heart", (255, 0, 0)),
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
    _s("Prostate", "total", "prostate", (0, 255, 200)),
    _s("Bone_Pelvic", "total", ["hip_left", "hip_right", "sacrum"], (200, 200, 160)),
    _s("Kidney_L", "total", ["kidney_left", "kidney_cyst_left"], (255, 120, 0)),
    _s("Kidney_R", "total", ["kidney_right", "kidney_cyst_right"], (255, 80, 0)),
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
    _s("Trachea", "total", "trachea", (120, 255, 255)),
]

SITES: dict[str, list[Structure]] = {
    "thorax": THORAX,
    "abdomen": ABDOMEN,
    "pelvis": PELVIS,
    "headneck": HEAD_NECK,
}

# Cơ quan quan trọng mà model miễn phí KHÔNG có -> bác sĩ phải tự vẽ.
NOT_COVERED: dict[str, list[str]] = {
    "thorax": ["Heart substructures (LAD, buồng tim)", "Brachial plexus", "Bronchus_Prox"],
    "abdomen": ["Bowel_Bag", "Liver-GTV (tự trừ trong Monaco)"],
    "pelvis": ["Rectum", "Anal canal", "Bowel_Bag", "Femur_Head (đang là cả xương đùi)", "Penile bulb"],
    "headneck": ["Brainstem", "OpticChiasm", "Cochlea", "Larynx", "Pharyngeal constrictors",
                 "Oral cavity", "Lips", "Brachial plexus", "Pituitary"],
}

# Nhóm nhãn trong task "total" dùng để tự nhận diện vùng chụp (site="auto").
REGION_MARKERS: dict[str, tuple[str, ...]] = {
    "headneck": ("brain", "skull"),
    "thorax": ("lung_upper_lobe_left", "lung_upper_lobe_right", "heart"),
    "abdomen": ("liver", "kidney_left", "kidney_right"),
    "pelvis": ("urinary_bladder", "hip_left", "hip_right"),
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


def tasks_for(structures: list[Structure]) -> list[str]:
    tasks = []
    for s in structures:
        if s.task not in tasks:
            tasks.append(s.task)
    # "total" luôn chạy đầu tiên (dùng để nhận diện vùng)
    return sorted(tasks, key=lambda t: t != "total")
