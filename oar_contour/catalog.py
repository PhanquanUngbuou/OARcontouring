"""Danh mục ĐẦY ĐỦ các cấu trúc có thể khoanh bằng các model MIỄN PHÍ của TotalSegmentator (CT).

- Tên hiển thị theo TG-263 khi có quy ước rõ ràng; các cấu trúc khác đặt tên tự động từ nhãn
  model; cấu trúc chưa có tên TG-263 đặt theo quy ước QuanContour (docs/QUY_UOC_TEN.md).
- Mỗi model có "chi phí" tương đối để app ước lượng thời gian khi bác sĩ chọn thêm cơ quan.
"""

from __future__ import annotations

from .structures import Structure

# Các model (task) dùng được: miễn phí, CT, có ích cho xạ trị. Chi phí: số "đơn vị" thời gian,
# 1 đơn vị ~ 1 phần của model total (đo trên CPU 4 nhân ~60 s ở chế độ đầy đủ).
TASKS: dict[str, dict] = {
    "total": {"label": "Nhóm cơ quan chính", "cost": None},
    "head_glands_cavities": {"label": "Tuyến nước bọt, mắt, thần kinh thị", "cost": 1.5},
    "craniofacial_structures": {"label": "Xương hàm, xoang, răng", "cost": 2.5},
    "headneck_bones_vessels": {"label": "Sụn thanh quản, xương móng, mạch cổ", "cost": 1.5},
    "head_muscles": {"label": "Cơ vùng đầu (nhai, lưỡi)", "cost": 1.5},
    "headneck_muscles": {"label": "Cơ vùng cổ, cơ khít hầu (thử nghiệm)", "cost": 3.0},
    "breasts": {"label": "Tuyến vú", "cost": 1.0},
    "abdominal_muscles": {"label": "Cơ thành ngực – bụng", "cost": 4.0},
    "trunk_cavities": {"label": "Khoang ngực, khoang bụng, màng tim", "cost": 1.0},
    "liver_segments": {"label": "Phân thùy gan", "cost": 1.5},
}

# Thứ tự giải phẫu để hiển thị danh sách OAR (từ đầu xuống chân); cấu trúc khác xếp sau theo ABC
ANATOMY_ORDER: list[tuple[str, list[str]]] = [
    ("Thần kinh – mắt", ["Brain", "SpinalCord", "SpinalCanal", "Eye_L", "Eye_R", "Lens_L", "Lens_R", "OpticNrv_L", "OpticNrv_R"]),
    ("Đầu cổ", ["Parotid_L", "Parotid_R", "Parotid_L_Ref", "Parotid_R_Ref", "Glnd_Submand_L", "Glnd_Submand_R", "Bone_Mandible", "Tongue",
                "Musc_Constrict_S", "Musc_Constrict_M", "Musc_Constrict_I", "Larynx_Air", "Cartilage_Thyroid",
                "Cartilage_Cricoid", "Glnd_Thyroid"]),
    ("Cơ – mạch vùng cổ", ["Musc_Masseter_L", "Musc_Masseter_R", "Musc_Pterygoid_Med_L", "Musc_Pterygoid_Med_R",
                           "Musc_Pterygoid_Lat_L", "Musc_Pterygoid_Lat_R", "Musc_Digastric_L", "Musc_Digastric_R",
                           "Bone_Styloid_L", "Bone_Styloid_R", "A_Carotid_Int_L", "A_Carotid_Int_R",
                           "V_Jugular_Int_L", "V_Jugular_Int_R", "Canal_Auditory_Ext_L", "Canal_Auditory_Ext_R"]),
    ("Lồng ngực", ["Trachea", "Esophagus", "Lung_L", "Lung_R", "Lungs", "Heart", "V_Venacava_S",
                   "Breast_L", "Breast_R", "Humerus_L", "Humerus_R", "Sternum", "Bone_Ribs", "Bone_Ribs_L", "Bone_Ribs_R"]),
    ("Bụng", ["Liver", "Gallbladder", "Stomach", "Duodenum", "Pancreas", "Spleen", "Kidney_L", "Kidney_R",
              "Kidneys", "Bowel_Small", "Colon"]),
    ("Mạch máu (mốc vẽ hạch)", ["A_Aorta", "V_Venacava_I", "A_Iliac_L", "A_Iliac_R", "V_Iliac_L", "V_Iliac_R"]),
    ("Tiểu khung", ["Bladder", "Prostate", "Bone_Hips", "Bone_Pelvic", "Sacrum", "Femur_L", "Femur_R"]),
]

# Phần nào của model "total" chứa nhãn nào (khớp với TotalSegmentator; dùng để ước lượng thời gian)
TOTAL_PARTS = ["organs", "vertebrae", "cardiac", "muscles", "ribs"]

GROUPS = ["Hô hấp", "Tim mạch", "Tiêu hoá", "Tiết niệu – sinh dục", "Thần kinh", "Đầu cổ: tuyến, mắt",
          "Đầu cổ: khác", "Vú", "Xương", "Cơ", "Khoang cơ thể", "Phân thùy gan"]

# Tên TG-263 cho các nhãn hay dùng (nhãn TotalSegmentator -> tên)
_TG263 = {
    "spleen": "Spleen", "gallbladder": "Gallbladder", "liver": "Liver", "stomach": "Stomach",
    "pancreas": "Pancreas", "adrenal_gland_right": "Glnd_Adrenal_R", "adrenal_gland_left": "Glnd_Adrenal_L",
    "lung_upper_lobe_left": "Lung_LUL", "lung_lower_lobe_left": "Lung_LLL",
    "lung_upper_lobe_right": "Lung_RUL", "lung_middle_lobe_right": "Lung_RML",
    "lung_lower_lobe_right": "Lung_RLL", "esophagus": "Esophagus", "trachea": "Trachea",
    "thyroid_gland": "Glnd_Thyroid", "small_bowel": "Bowel_Small", "duodenum": "Duodenum", "colon": "Colon",
    "urinary_bladder": "Bladder", "prostate": "Prostate", "sacrum": "Sacrum", "heart": "Heart",
    "aorta": "A_Aorta", "pulmonary_vein": "V_Pulmonary", "brachiocephalic_trunk": "A_Brachiocephls",
    "subclavian_artery_right": "A_Subclavian_R", "subclavian_artery_left": "A_Subclavian_L",
    "common_carotid_artery_right": "A_Carotid_R", "common_carotid_artery_left": "A_Carotid_L",
    "brachiocephalic_vein_left": "V_Brachioceph_L", "brachiocephalic_vein_right": "V_Brachioceph_R",
    "superior_vena_cava": "V_Venacava_S", "inferior_vena_cava": "V_Venacava_I",
    "portal_vein_and_splenic_vein": "V_Portal_Splenic", "iliac_artery_left": "A_Iliac_L",
    "iliac_artery_right": "A_Iliac_R", "iliac_vena_left": "V_Iliac_L", "iliac_vena_right": "V_Iliac_R",
    "humerus_left": "Humerus_L", "humerus_right": "Humerus_R", "scapula_left": "Scapula_L",
    "scapula_right": "Scapula_R", "clavicula_left": "Clavicle_L", "clavicula_right": "Clavicle_R",
    "femur_left": "Femur_L", "femur_right": "Femur_R", "hip_left": "Bone_Hip_L", "hip_right": "Bone_Hip_R",
    "spinal_cord": "SpinalCord", "brain": "Brain", "skull": "Bone_Skull", "sternum": "Sternum",
    "costal_cartilages": "Cartilage_Costal",
    "parotid_gland_left": "Parotid_L", "parotid_gland_right": "Parotid_R",
    "submandibular_gland_left": "Glnd_Submand_L", "submandibular_gland_right": "Glnd_Submand_R",
    "eye_left": "Eye_L", "eye_right": "Eye_R", "eye_lens_left": "Lens_L", "eye_lens_right": "Lens_R",
    "optic_nerve_left": "OpticNrv_L", "optic_nerve_right": "OpticNrv_R",
    "mandible": "Bone_Mandible", "hyoid": "Bone_Hyoid", "thyroid_cartilage": "Cartilage_Thyroid",
    "cricoid_cartilage": "Cartilage_Cricoid",
    "internal_carotid_artery_left": "A_Carotid_Int_L", "internal_carotid_artery_right": "A_Carotid_Int_R",
    "internal_jugular_vein_left": "V_Jugular_Int_L", "internal_jugular_vein_right": "V_Jugular_Int_R",
    "superior_pharyngeal_constrictor": "Musc_Constrict_S",
    "middle_pharyngeal_constrictor": "Musc_Constrict_M",
    "inferior_pharyngeal_constrictor": "Musc_Constrict_I",
    "sternocleidomastoid_left": "Musc_Sclmast_L", "sternocleidomastoid_right": "Musc_Sclmast_R",
    "masseter_left": "Musc_Masseter_L", "masseter_right": "Musc_Masseter_R",
    "temporalis_left": "Musc_Temporal_L", "temporalis_right": "Musc_Temporal_R",
    "medial_pterygoid_left": "Musc_Pterygoid_Med_L", "medial_pterygoid_right": "Musc_Pterygoid_Med_R",
    "lateral_pterygoid_left": "Musc_Pterygoid_Lat_L", "lateral_pterygoid_right": "Musc_Pterygoid_Lat_R",
    "tongue": "Tongue", "nasopharynx": "Nasopharynx", "oropharynx": "Oropharynx",
    "hypopharynx": "Hypopharynx", "pericardium": "Pericardium",
}

# Quy ước QuanContour cho cấu trúc CHƯA có tên TG-263 (xem docs/QUY_UOC_TEN.md):
#   <Loại mô>_<Tên giải phẫu>[_Phân loại]_<L|R>   Loại mô: Bone, Musc, A, V, Glnd, Cartilage, Cavity, Canal...
_QC = {
    "atrial_appendage_left": "Atrium_Appendage_L",
    "gluteus_maximus_left": "Musc_Gluteus_Max_L", "gluteus_maximus_right": "Musc_Gluteus_Max_R",
    "gluteus_medius_left": "Musc_Gluteus_Med_L", "gluteus_medius_right": "Musc_Gluteus_Med_R",
    "gluteus_minimus_left": "Musc_Gluteus_Min_L", "gluteus_minimus_right": "Musc_Gluteus_Min_R",
    "autochthon_left": "Musc_Paraspinal_L", "autochthon_right": "Musc_Paraspinal_R",
    "iliopsoas_left": "Musc_Iliopsoas_L", "iliopsoas_right": "Musc_Iliopsoas_R",
    "nasal_cavity_left": "Cavity_Nasal_L", "nasal_cavity_right": "Cavity_Nasal_R",
    "auditory_canal_left": "Canal_Auditory_Ext_L", "auditory_canal_right": "Canal_Auditory_Ext_R",
    "soft_palate": "Palate_Soft", "hard_palate": "Palate_Hard", "teeth_lower": "Teeth_Lower",
    "teeth_upper": "Teeth_Upper", "head": "Head", "sinus_maxillary": "Sinus_Maxillary",
    "sinus_frontal": "Sinus_Frontal", "larynx_air": "Cavity_Larynx",
    "zygomatic_arch_left": "Bone_Zygoma_L", "zygomatic_arch_right": "Bone_Zygoma_R",
    "styloid_process_left": "Bone_Styloid_L", "styloid_process_right": "Bone_Styloid_R",
    "digastric_left": "Musc_Digastric_L", "digastric_right": "Musc_Digastric_R",
    "trapezius_left": "Musc_Trapezius_L", "trapezius_right": "Musc_Trapezius_R",
    "platysma_left": "Musc_Platysma_L", "platysma_right": "Musc_Platysma_R",
    "levator_scapulae_left": "Musc_LevatorScap_L", "levator_scapulae_right": "Musc_LevatorScap_R",
    "anterior_scalene_left": "Musc_Scalene_Ant_L", "anterior_scalene_right": "Musc_Scalene_Ant_R",
    "middle_scalene_left": "Musc_Scalene_Mid_L", "middle_scalene_right": "Musc_Scalene_Mid_R",
    "posterior_scalene_left": "Musc_Scalene_Post_L", "posterior_scalene_right": "Musc_Scalene_Post_R",
    "sterno_thyroid_left": "Musc_Sternothyroid_L", "sterno_thyroid_right": "Musc_Sternothyroid_R",
    "thyrohyoid_left": "Musc_Thyrohyoid_L", "thyrohyoid_right": "Musc_Thyrohyoid_R",
    "prevertebral_left": "Musc_Prevertebral_L", "prevertebral_right": "Musc_Prevertebral_R",
    "pectoralis_major_left": "Musc_Pectoralis_Maj_L", "pectoralis_major_right": "Musc_Pectoralis_Maj_R",
    "rectus_abdominis_left": "Musc_RectusAbd_L", "rectus_abdominis_right": "Musc_RectusAbd_R",
    "serratus_anterior_left": "Musc_Serratus_Ant_L", "serratus_anterior_right": "Musc_Serratus_Ant_R",
    "latissimus_dorsi_left": "Musc_Latissimus_L", "latissimus_dorsi_right": "Musc_Latissimus_R",
    "external_oblique_left": "Musc_Oblique_Ext_L", "external_oblique_right": "Musc_Oblique_Ext_R",
    "internal_oblique_left": "Musc_Oblique_Int_L", "internal_oblique_right": "Musc_Oblique_Int_R",
    "erector_spinae_left": "Musc_ErectorSpinae_L", "erector_spinae_right": "Musc_ErectorSpinae_R",
    "transversospinalis_left": "Musc_Transversospinal_L", "transversospinalis_right": "Musc_Transversospinal_R",
    "psoas_major_left": "Musc_Psoas_L", "psoas_major_right": "Musc_Psoas_R",
    "quadratus_lumborum_left": "Musc_QuadLumb_L", "quadratus_lumborum_right": "Musc_QuadLumb_R",
    "abdominal_cavity": "Cavity_Abdominal", "thoracic_cavity": "Cavity_Thoracic", "mediastinum": "Mediastinum",
    "tongue": "Tongue",
}
for _i in range(1, 13):
    _QC[f"rib_left_{_i}"] = f"Bone_Rib_L{_i}"
    _QC[f"rib_right_{_i}"] = f"Bone_Rib_R{_i}"
for _i in range(1, 9):
    _QC[f"liver_segment_{_i}"] = f"Liver_Seg{_i}"
for _v in ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9", "T10",
           "T11", "T12", "L1", "L2", "L3", "L4", "L5", "S1"]:
    _QC[f"vertebrae_{_v}"] = f"Bone_Vertebra_{_v}"
# nhãn trùng với model khác -> bỏ, dùng bản của model chính
_SKIP = {("craniofacial_structures", "skull"), ("abdominal_muscles", "trapezius_left"),
         ("abdominal_muscles", "trapezius_right")}

_GROUP_RULES = [
    ("Hô hấp", ("lung", "trachea", "larynx_air")),
    ("Tim mạch", ("heart", "aorta", "artery", "vein", "vena", "atrial", "trunk", "pulmonary")),
    ("Tiêu hoá", ("liver", "stomach", "pancreas", "spleen", "gallbladder", "bowel", "duodenum", "colon",
                  "esophagus")),
    ("Tiết niệu – sinh dục", ("kidney", "bladder", "prostate", "adrenal")),
    ("Thần kinh", ("brain", "spinal_cord", "optic_nerve")),
    ("Đầu cổ: tuyến, mắt", ("parotid", "submandibular", "eye", "thyroid_gland")),
    ("Đầu cổ: khác", ("pharynx", "nasal", "auditory", "palate", "hyoid", "cartilage", "zygomatic", "styloid",
                      "sinus", "teeth", "head")),
    ("Vú", ("breast",)),
    ("Xương", ("vertebrae", "sacrum", "rib", "sternum", "skull", "mandible", "femur", "hip", "humerus",
               "scapula", "clavicula", "costal")),
    ("Khoang cơ thể", ("cavity", "pericardium", "mediastinum")),
]


def _auto_name(label: str) -> str:
    words = label.split("_")
    side = ""
    if words[-1] in ("left", "right"):
        side = "_" + words.pop()[0].upper()
    return "_".join(w[:1].upper() + w[1:] for w in words) + side


def _group(task: str, label: str) -> str:
    if task == "liver_segments":
        return "Phân thùy gan"
    if task in ("head_muscles", "headneck_muscles", "abdominal_muscles") or any(
            k in label for k in ("gluteus", "autochthon", "iliopsoas", "muscle")):
        return "Cơ"
    for group, keys in _GROUP_RULES:
        if any(k in label for k in keys):
            return group
    return "Đầu cổ: khác"


def _labels_of(task: str) -> list[str]:
    from .ts_labels import KNOWN_LABELS

    return KNOWN_LABELS.get(task, [])


def _build() -> dict[str, Structure]:
    from .structures import _s

    cat: dict[str, Structure] = {}

    def add(s: Structure, group: str):
        if s.name not in cat:
            cat[s.name] = s
            GROUP_OF[s.name] = group

    from .structures import CURATED

    group_of_curated = {s.name: _group(s.task, s.labels[0]) for s in CURATED}
    for s in CURATED:
        add(s, group_of_curated[s.name])
    add(_s("Kidneys", "total", ["kidney_left", "kidney_cyst_left", "kidney_right", "kidney_cyst_right"],
           (255, 150, 60)), "Tiết niệu – sinh dục")
    ribs_l = [f"rib_left_{i}" for i in range(1, 13)]
    ribs_r = [f"rib_right_{i}" for i in range(1, 13)]
    add(_s("Bone_Ribs_L", "total", ribs_l, (220, 220, 190)), "Xương")
    add(_s("Bone_Ribs_R", "total", ribs_r, (200, 200, 170)), "Xương")
    add(_s("Bone_Ribs", "total", ribs_l + ribs_r, (210, 210, 180)), "Xương")

    palette = [(255, 99, 71), (60, 179, 113), (65, 105, 225), (238, 130, 238), (255, 215, 0),
               (0, 206, 209), (255, 140, 0), (154, 205, 50), (186, 85, 211), (100, 149, 237)]
    k = 0
    for task in TASKS:
        for label in _labels_of(task):
            if (task == "total" and label.startswith("kidney_cyst")) or (task == "breasts"):
                continue  # đã gộp vào Kidney_L/R, Breast_L/R
            if (task, label) in _SKIP:
                continue
            name = _TG263.get(label) or _QC.get(label) or _auto_name(label)
            if task in ("head_muscles", "headneck_muscles", "abdominal_muscles") and not name.startswith("Musc_") \
                    and label not in _TG263 and label not in _QC:
                name = "Musc_" + name
            if name in cat and cat[name].task == task and cat[name].labels == (label,):
                continue  # đã có trong CURATED
            if name in cat and cat[name].task != task:
                name = f"{name}_{task.split('_')[0]}"  # trùng tên giữa 2 model (ví dụ Skull)
            add(_s(name, task, label, palette[k % len(palette)]), _group(task, label))
            k += 1
    return cat


GROUP_OF: dict[str, str] = {}
CATALOG: dict[str, Structure] = {}


def catalog() -> dict[str, Structure]:
    if not CATALOG:
        CATALOG.update(_build())
    return CATALOG


def total_part_of(label: str) -> str | None:
    from .structures import TOTAL_PART_OF

    return TOTAL_PART_OF.get(label)


def estimate_cost(names: list[str]) -> dict:
    """Ước lượng chi phí (đơn vị ~ 1 phần model total) và danh sách model cần chạy."""
    cat = catalog()
    parts, tasks = set(), set()
    for n in names:
        s = cat.get(n)
        if s is None:
            continue
        if s.task == "total":
            for l in s.labels:
                p = total_part_of(l)
                if p:
                    parts.add(p)
        else:
            tasks.add(s.task)
    units = len(parts) + sum(TASKS[t]["cost"] for t in tasks)
    return {"total_parts": sorted(parts, key=TOTAL_PARTS.index), "tasks": sorted(tasks), "units": units}
