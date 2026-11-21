"""Phác đồ: vị trí u + mục đích xạ trị -> danh sách OAR (chỉ từ các model MIỄN PHÍ).

ĐÂY LÀ BẢN ĐỀ XUẤT, khoa xạ trị cần duyệt lại. Bác sĩ chỉnh danh sách ngay trong app
("Mở rộng / chỉnh sửa") và lưu thành mặc định của khoa (lưu ở settings.json, không sửa file này).

Nguyên tắc chọn để chạy ít model nhất:
- Chỉ đưa vào OAR có ràng buộc liều thường dùng cho vị trí đó (triệu chứng: ít hơn, chỉ OAR giới hạn liều).
- Không thêm cấu trúc kéo theo model/phần model mới nếu không cần (mạch máu, xương sườn, đốt sống, cơ).

Tên trong danh sách là tên trong danh mục (catalog.py). "Bone_Vertebra_*" = mọi đốt sống.
"""

from __future__ import annotations

from dataclasses import dataclass, field

@dataclass(frozen=True)
class Protocol:
    id: str
    group: str  # nhóm hiển thị
    name: str  # tên tiếng Việt
    curative: tuple[str, ...]
    palliative: tuple[str, ...]
    manual: tuple[str, ...] = ()  # OAR model chưa vẽ được -> bác sĩ tự vẽ
    note: str = ""
    region: str = ""  # vùng giải phẫu chính (để gợi ý khi mở rộng)


def _p(id, group, name, curative, palliative=None, manual=(), note="", region=""):
    return Protocol(id, group, name, tuple(curative), tuple(palliative or curative), tuple(manual), note, region)


_HN_GLANDS = ["Parotid_L", "Parotid_R", "Glnd_Submand_L", "Glnd_Submand_R"]
_EYES = ["Eye_L", "Eye_R", "Lens_L", "Lens_R", "OpticNrv_L", "OpticNrv_R"]
_LUNGS = ["Lung_L", "Lung_R", "Lungs"]
_KIDNEYS = ["Kidney_L", "Kidney_R"]
_FEMURS = ["Femur_L", "Femur_R"]
_ILIAC = ["A_Iliac_L", "A_Iliac_R", "V_Iliac_L", "V_Iliac_R"]  # mốc vẽ CTV hạch chậu
_PARAAORTIC = ["A_Aorta", "V_Venacava_I"]  # mốc vẽ CTV hạch cạnh động mạch chủ

# Mỗi vùng là HỢP các OAR của mọi vị trí u trong vùng (kể cả cơ quan đích: kỹ sư không áp ràng buộc liều
# cho cơ quan đích thì không ảnh hưởng). Kỹ thuật SBRT/SRT tách riêng vì cần thêm cấu trúc đặc thù.
PROTOCOLS: list[Protocol] = [
    # ------------------------------------------------------------------ theo vùng
    _p("headneck", "Theo vùng", "U đầu cổ",
       ["Brain", "SpinalCord", *_HN_GLANDS, *_EYES, "Bone_Mandible", "Glnd_Thyroid", "Esophagus", "Trachea",
        "Lung_L", "Lung_R"],
       ["Brain", "SpinalCord", "Parotid_L", "Parotid_R", *_EYES, "Esophagus", "Trachea"],
       note="Gồm vòm, khoang miệng, họng miệng, thanh quản, hạ họng, tuyến nước bọt, tuyến giáp, "
            "hạch cổ, hốc mũi – xoang, lymphoma hốc mắt / mũi xoang.", region="headneck"),
    _p("brain", "Theo vùng", "U não",
       ["Brain", *_EYES, "SpinalCord"], ["Brain", *_EYES],
       note="Gồm u não nguyên phát và xạ toàn não.", region="headneck"),
    _p("thorax", "Theo vùng", "U lồng ngực (phổi, trung thất, thực quản)",
       [*_LUNGS, "Heart", "Esophagus", "SpinalCord", "Trachea", "Liver", *_KIDNEYS],
       ["Lungs", "Heart", "Esophagus", "SpinalCord"],
       note="Lungs nên trừ GTV/ITV trong Monaco (Lungs-GTV) khi tính V20.", region="thorax"),
    _p("breast", "Theo vùng", "U vú",
       ["Heart", *_LUNGS, "Breast_L", "Breast_R", "SpinalCord", "Esophagus", "Glnd_Thyroid",
        "Humerus_L", "Humerus_R", "Liver"],
       ["Heart", "Lungs", "SpinalCord"],
       note="Breast_L/R là tuyến vú hai bên: bên đối diện là OAR.", region="thorax"),
    _p("abdomen", "Theo vùng", "U bụng – sau phúc mạc",
       ["Liver", "Gallbladder", "Stomach", "Duodenum", "Pancreas", "Spleen", *_KIDNEYS, "Bowel_Small", "Colon",
        "SpinalCord", "Heart", "Esophagus", "Lung_L", "Lung_R", *_PARAAORTIC, *_ILIAC],
       ["Liver", *_KIDNEYS, "SpinalCord", "Stomach", "Duodenum", "Bowel_Small"],
       note="Gồm dạ dày, tuỵ, gan, đường mật, sarcoma sau phúc mạc, thận, tinh hoàn (hạch cạnh động mạch chủ).",
       region="abdomen"),
    _p("pelvis", "Theo vùng", "U tiểu khung",
       ["Bladder", "Bowel_Small", "Colon", *_FEMURS, "Bone_Hips", *_ILIAC, *_PARAAORTIC, *_KIDNEYS,
        "SpinalCord", "Prostate"],
       ["Bladder", "Bowel_Small", "Colon", *_FEMURS],
       note="Gồm trực tràng, ống hậu môn, cổ tử cung, nội mạc, âm đạo, âm hộ, tiền liệt tuyến, bàng quang. "
            "Bone_Hips: xương chậu 2 bên (xạ tránh tủy xương).", region="pelvis"),
    _p("bone", "Theo vùng", "Di căn xương",
       ["SpinalCord", "Esophagus", "Heart", "Lungs", *_KIDNEYS, "Liver", "Stomach", "Bowel_Small", "Colon",
        "Bladder", *_FEMURS],
       ["SpinalCord", "Esophagus", "Heart", "Lungs", *_KIDNEYS, "Bowel_Small", "Bladder", *_FEMURS],
       note="Cơ quan ngoài trường chụp tự bỏ qua.", region="thorax"),
    # ------------------------------------------------------------------ SBRT / SRT
    _p("brain_srs", "SBRT / SRT", "U não SRT / SRS",
       ["Brain", *_EYES], ["Brain", *_EYES], region="headneck"),
    _p("lung_sbrt", "SBRT / SRT", "Phổi SBRT",
       [*_LUNGS, "Heart", "Esophagus", "SpinalCord", "Trachea", "A_Aorta", "V_Venacava_S", "Bone_Ribs", "Sternum"],
       [*_LUNGS, "Heart", "Esophagus", "SpinalCord", "Trachea", "A_Aorta", "V_Venacava_S", "Bone_Ribs", "Sternum"],
       note="Bone_Ribs/Sternum dùng tham khảo cho thành ngực.", region="thorax"),
    _p("liver_sbrt", "SBRT / SRT", "Gan SBRT",
       ["Liver", "Gallbladder", "Stomach", "Duodenum", "Bowel_Small", "Colon", *_KIDNEYS, "SpinalCord", "Heart",
        "Esophagus", "Lung_L", "Lung_R", "Bone_Ribs"],
       ["Liver", "Gallbladder", "Stomach", "Duodenum", "Bowel_Small", "Colon", *_KIDNEYS, "SpinalCord", "Heart",
        "Esophagus", "Lung_L", "Lung_R", "Bone_Ribs"],
       note="Liver nên trừ GTV trong Monaco (Liver-GTV). Bone_Ribs dùng tham khảo cho thành ngực.", region="abdomen"),
    _p("spine_sbrt", "SBRT / SRT", "Cột sống SBRT",
       ["SpinalCord", "Esophagus", "Trachea", "Heart", *_LUNGS, *_KIDNEYS, "Liver", "Stomach", "Bowel_Small",
        "Colon", "Bone_Vertebra_*"],
       ["SpinalCord", "Esophagus", "Trachea", "Heart", *_LUNGS, *_KIDNEYS, "Liver", "Stomach", "Bowel_Small",
        "Colon", "Bone_Vertebra_*"],
       note="Các đốt sống giúp định vị; cơ quan ngoài trường chụp tự bỏ qua.", region="thorax"),
]

PROTOCOL_BY_ID = {p.id: p for p in PROTOCOLS}
INTENTS = {"curative": "Triệt căn", "palliative": "Triệu chứng"}


def expand(names) -> list[str]:
    """Đổi "Bone_Vertebra_*" thành danh sách đốt sống trong danh mục; bỏ trùng, giữ thứ tự."""
    from .catalog import catalog

    cat = catalog()
    out: list[str] = []
    for n in names:
        if n.endswith("*"):
            out += [c for c in cat if c.startswith(n[:-1])]
        else:
            out.append(n)
    return [n for n in dict.fromkeys(out) if n in cat]


def default_names(protocol_id: str, intent: str) -> list[str]:
    p = PROTOCOL_BY_ID[protocol_id]
    return expand(p.curative if intent == "curative" else p.palliative)
