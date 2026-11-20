"""Phác đồ: vị trí u + mục đích xạ trị -> danh sách OAR (chỉ từ các model MIỄN PHÍ).

ĐÂY LÀ BẢN ĐỀ XUẤT, khoa xạ trị cần duyệt lại. Bác sĩ chỉnh danh sách ngay trong app
("Mở rộng / chỉnh sửa") và lưu thành mặc định của khoa (lưu ở settings.json, không sửa file này).

Nguyên tắc chọn để chạy ít model nhất:
- Chỉ đưa vào OAR có ràng buộc liều thường dùng cho vị trí đó (triệu chứng: ít hơn, chỉ OAR giới hạn liều).
- Không thêm cấu trúc kéo theo model/phần model mới nếu không cần (mạch máu, xương sườn, đốt sống, cơ).
- OAR quan trọng mà model miễn phí không có -> liệt kê ở `manual` để bác sĩ biết mà tự vẽ.

Tên trong danh sách là tên trong danh mục (catalog.py). "Vertebrae_*" = mọi đốt sống.
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
_PELVIS = ["Bladder", "Bowel_Small", "Colon", "Femur_L", "Femur_R"]
_ILIAC = ["A_Iliac_L", "A_Iliac_R", "V_Iliac_L", "V_Iliac_R"]  # mốc vẽ CTV hạch chậu
_PARAAORTIC = ["A_Aorta", "V_Venacava_I"]  # mốc vẽ CTV hạch cạnh động mạch chủ

PROTOCOLS: list[Protocol] = [
    # ------------------------------------------------------------------ Đầu cổ
    _p("hn_nasopharynx", "U đầu cổ", "Vòm họng",
       ["Brain", "SpinalCord", *_HN_GLANDS, *_EYES, "Bone_Mandible", "Glnd_Thyroid", "Esophagus"],
       ["SpinalCord", "Brain", "Parotid_L", "Parotid_R", "Lens_L", "Lens_R", "OpticNrv_L", "OpticNrv_R"],
       manual=["Brainstem", "OpticChiasm", "Lobe_Temporal_L/R (thùy thái dương)", "Cochlea_L/R", "Pituitary",
               "Joint_TM_L/R (khớp thái dương hàm)", "Larynx", "Cavity_Oral",
               "Musc_Constrict (có bản thử nghiệm trong Mở rộng)", "BrachialPlex_L/R"],
       note="Brain là toàn bộ não; thùy thái dương cần vẽ thêm.", region="headneck"),
    _p("hn_oral", "U đầu cổ", "Khoang miệng",
       ["SpinalCord", *_HN_GLANDS, "Bone_Mandible", "Glnd_Thyroid", "Esophagus"],
       ["SpinalCord", "Parotid_L", "Parotid_R"],
       manual=["Brainstem", "Cavity_Oral (ngoài u)", "Lips", "Larynx", "Musc_Constrict", "Cochlea_L/R",
               "BrachialPlex_L/R"], region="headneck"),
    _p("hn_oropharynx", "U đầu cổ", "Họng miệng (amidan, đáy lưỡi)",
       ["SpinalCord", *_HN_GLANDS, "Bone_Mandible", "Glnd_Thyroid", "Esophagus"],
       ["SpinalCord", "Parotid_L", "Parotid_R"],
       manual=["Brainstem", "Cavity_Oral", "Larynx", "Musc_Constrict", "Cochlea_L/R", "BrachialPlex_L/R"],
       region="headneck"),
    _p("hn_larynx", "U đầu cổ", "Thanh quản",
       ["SpinalCord", *_HN_GLANDS, "Bone_Mandible", "Glnd_Thyroid", "Esophagus", "Trachea"],
       ["SpinalCord", "Esophagus"],
       manual=["Brainstem", "Larynx (nếu không thuộc thể tích bia)", "Musc_Constrict", "Cavity_Oral",
               "BrachialPlex_L/R"], region="headneck"),
    _p("hn_hypopharynx", "U đầu cổ", "Hạ họng",
       ["SpinalCord", *_HN_GLANDS, "Bone_Mandible", "Glnd_Thyroid", "Esophagus", "Trachea"],
       ["SpinalCord", "Esophagus"],
       manual=["Brainstem", "Larynx (nếu không thuộc thể tích bia)", "Musc_Constrict", "Cavity_Oral",
               "BrachialPlex_L/R"], region="headneck"),
    _p("hn_salivary", "U đầu cổ", "Tuyến nước bọt (mang tai, dưới hàm)",
       ["Brain", "SpinalCord", *_HN_GLANDS, "Bone_Mandible"], ["SpinalCord", "Parotid_L", "Parotid_R"],
       manual=["Brainstem", "Cochlea_L/R", "Lobe_Temporal_L/R", "Cavity_Oral", "Joint_TM_L/R"],
       note="Tuyến bên tổn thương thường thuộc thể tích bia: chỉ dùng ràng buộc cho tuyến đối bên.",
       region="headneck"),
    _p("hn_thyroid", "U đầu cổ", "Tuyến giáp",
       ["SpinalCord", "Esophagus", "Trachea", "Lung_L", "Lung_R", "Parotid_L", "Parotid_R"],
       ["SpinalCord", "Esophagus", "Trachea"],
       manual=["Larynx", "Musc_Constrict", "BrachialPlex_L/R"],
       note="Tuyến giáp là cơ quan đích nên không vẽ Glnd_Thyroid.", region="headneck"),
    _p("hn_unknown", "U đầu cổ", "Hạch cổ không rõ u nguyên phát",
       ["SpinalCord", *_HN_GLANDS, "Bone_Mandible", "Glnd_Thyroid", "Esophagus"],
       ["SpinalCord", "Parotid_L", "Parotid_R"],
       manual=["Brainstem", "Larynx", "Cavity_Oral", "Musc_Constrict", "BrachialPlex_L/R"], region="headneck"),
    _p("hn_sinonasal", "U đầu cổ", "Hốc mũi – xoang",
       ["Brain", "SpinalCord", *_EYES, "Parotid_L", "Parotid_R", "Bone_Mandible"],
       ["Brain", "SpinalCord", *_EYES],
       manual=["Brainstem", "OpticChiasm", "Pituitary", "Lobe_Temporal_L/R", "Cochlea_L/R",
               "Glnd_Lacrimal_L/R (tuyến lệ)"], region="headneck"),
    # ------------------------------------------------------------------ Não
    _p("brain_primary", "U não", "U não nguyên phát",
       ["Brain", *_EYES, "SpinalCord"], ["Brain", "Lens_L", "Lens_R", "OpticNrv_L", "OpticNrv_R"],
       manual=["Brainstem", "OpticChiasm", "Cochlea_L/R", "Hippocampus_L/R", "Pituitary", "Glnd_Lacrimal_L/R"],
       note="Brain gồm cả u: trừ thể tích bia trong Monaco nếu khoa dùng Brain-PTV.", region="headneck"),
    _p("brain_wbrt", "U não", "Xạ toàn não (di căn não)",
       [*_EYES], [*_EYES],
       manual=["Hippocampus_L/R (nếu xạ tránh hồi hải mã)", "Cochlea_L/R", "OpticChiasm"],
       note="Toàn bộ não là thể tích bia; app chỉ vẽ mắt, thủy tinh thể, thần kinh thị.", region="headneck"),
    # ------------------------------------------------------------------ Ngực
    _p("lung", "U lồng ngực", "Phổi (3D-CRT / IMRT)",
       [*_LUNGS, "Heart", "Esophagus", "SpinalCord"], ["Lungs", "Heart", "Esophagus", "SpinalCord"],
       manual=["BrachialPlex_L/R (u đỉnh phổi)", "Bronchus_Prox (cây phế quản gốc)"],
       note="Lungs nên trừ GTV/ITV trong Monaco (Lungs-GTV) khi tính V20.", region="thorax"),
    _p("lung_sbrt", "U lồng ngực", "Phổi SBRT",
       [*_LUNGS, "Heart", "Esophagus", "SpinalCord", "Trachea", "A_Aorta", "V_Venacava_S", "Ribs", "Sternum"],
       [*_LUNGS, "Heart", "Esophagus", "SpinalCord"],
       manual=["Bronchus_Prox", "BrachialPlex_L/R", "ChestWall (dùng Ribs tham khảo)", "Skin"],
       note="Ribs/Sternum làm thời gian chạy tăng thêm một chút.", region="thorax"),
    _p("esophagus", "U lồng ngực", "Thực quản",
       [*_LUNGS, "Heart", "SpinalCord", "Liver", "Kidney_L", "Kidney_R"],
       ["Lungs", "Heart", "SpinalCord"],
       manual=["BrachialPlex_L/R (u cổ)"],
       note="Thực quản là cơ quan đích: app không vẽ Esophagus để tránh nhầm với thể tích bia.",
       region="thorax"),
    _p("thymus", "U lồng ngực", "U tuyến ức / trung thất",
       [*_LUNGS, "Heart", "Esophagus", "SpinalCord"], ["Lungs", "Heart", "SpinalCord"],
       manual=["LAD", "BrachialPlex_L/R", "Breast_L/R (bệnh nhân nữ trẻ: thêm trong Mở rộng)"], region="thorax"),
    _p("breast_left", "U lồng ngực", "Vú trái",
       ["Heart", *_LUNGS, "Breast_R", "SpinalCord", "Esophagus", "Glnd_Thyroid", "Humerus_L"],
       ["Heart", "Lungs", "SpinalCord"],
       manual=["LAD (động mạch liên thất trước)", "BrachialPlex_L", "Skin"],
       note="Breast_R là vú đối bên (OAR). CTV vú trái bác sĩ tự vẽ.", region="thorax"),
    _p("breast_right", "U lồng ngực", "Vú phải",
       ["Heart", *_LUNGS, "Breast_L", "SpinalCord", "Esophagus", "Glnd_Thyroid", "Humerus_R", "Liver"],
       ["Lungs", "Heart", "SpinalCord"],
       manual=["BrachialPlex_R", "Skin"],
       note="Breast_L là vú đối bên (OAR). CTV vú phải bác sĩ tự vẽ.", region="thorax"),
    # ------------------------------------------------------------------ Bụng
    _p("stomach", "U vùng bụng – sau phúc mạc", "Dạ dày",
       ["Liver", "Kidney_L", "Kidney_R", "SpinalCord", "Heart", "Bowel_Small", *_LUNGS],
       ["Liver", "Kidney_L", "Kidney_R", "SpinalCord"],
       manual=["Bowel_Bag"], note="Dạ dày là cơ quan đích nên không vẽ Stomach.", region="abdomen"),
    _p("pancreas", "U vùng bụng – sau phúc mạc", "Tuỵ",
       ["Liver", "Kidney_L", "Kidney_R", "SpinalCord", "Duodenum", "Stomach", "Bowel_Small"],
       ["Liver", "Kidney_L", "Kidney_R", "SpinalCord", "Duodenum", "Stomach"],
       manual=["Bowel_Bag"], region="abdomen"),
    _p("liver", "U vùng bụng – sau phúc mạc", "Gan (HCC, di căn gan)",
       ["Liver", "Stomach", "Duodenum", "Kidney_L", "Kidney_R", "SpinalCord", "Heart", "Esophagus",
        "Bowel_Small", "Colon", "Lung_R", "Lung_L"],
       ["Liver", "Stomach", "Duodenum", "Kidney_L", "Kidney_R", "SpinalCord"],
       manual=["Liver-GTV (tự trừ trong Monaco)", "Bowel_Bag", "ChestWall (SBRT)"], region="abdomen"),
    _p("biliary", "U vùng bụng – sau phúc mạc", "Đường mật / túi mật",
       ["Liver", "Kidney_L", "Kidney_R", "SpinalCord", "Duodenum", "Stomach", "Bowel_Small"],
       ["Liver", "Kidney_L", "Kidney_R", "SpinalCord", "Duodenum"],
       manual=["Liver-GTV", "Bowel_Bag"], region="abdomen"),
    _p("retroperitoneum", "U vùng bụng – sau phúc mạc", "Sarcoma sau phúc mạc / u thận",
       ["Kidney_L", "Kidney_R", "Liver", "SpinalCord", "Bowel_Small", "Colon", "Stomach", "Duodenum"],
       ["Kidney_L", "Kidney_R", "SpinalCord", "Bowel_Small"],
       manual=["Bowel_Bag"], note="Thận bên tổn thương có thể nằm trong thể tích bia.", region="abdomen"),
    _p("testis", "U vùng bụng – sau phúc mạc", "Tinh hoàn (xạ hạch cạnh động mạch chủ)",
       ["Kidney_L", "Kidney_R", "Liver", "SpinalCord", "Bowel_Small", "Stomach", "Duodenum", *_PARAAORTIC,
        "A_Iliac_L", "A_Iliac_R", "V_Iliac_L", "V_Iliac_R"],
       ["Kidney_L", "Kidney_R", "SpinalCord", "Bowel_Small"],
       manual=["Testis đối bên", "Bowel_Bag"], region="abdomen"),
    # ------------------------------------------------------------------ Tiểu khung
    _p("rectum", "U vùng tiểu khung", "Trực tràng", [*_PELVIS, *_ILIAC], ["Bladder", "Bowel_Small", "Femur_L", "Femur_R"],
       manual=["Bowel_Bag", "Genitalia", "Anal canal (nếu không thuộc thể tích bia)"], region="pelvis"),
    _p("anal", "U vùng tiểu khung", "Ống hậu môn",
       [*_PELVIS, "Bone_Hips", *_ILIAC], ["Bladder", "Bowel_Small", "Femur_L", "Femur_R"],
       manual=["Genitalia (cơ quan sinh dục ngoài)", "Bowel_Bag", "Mạch đùi (mốc hạch bẹn)"],
       note="Bone_Hips dùng cho xạ tránh tủy xương (cánh chậu); trực tràng/ống hậu môn thuộc thể tích bia.",
       region="pelvis"),
    _p("cervix", "U vùng tiểu khung", "Cổ tử cung",
       [*_PELVIS, "Bone_Hips", *_ILIAC, *_PARAAORTIC, "Kidney_L", "Kidney_R", "SpinalCord"],
       ["Bladder", "Bowel_Small", "Femur_L", "Femur_R"],
       manual=["Rectum", "Sigmoid (đang nằm trong Colon)", "Bowel_Bag"],
       note="Kidney, SpinalCord, A_Aorta, V_Venacava_I dùng khi xạ hạch cạnh động mạch chủ. Muốn tính cả xương cùng: "
            "chọn Bone_Pelvic trong Mở rộng (chạy lâu hơn một chút).", region="pelvis"),
    _p("endometrium", "U vùng tiểu khung", "Nội mạc tử cung",
       [*_PELVIS, "Bone_Hips", *_ILIAC, *_PARAAORTIC, "Kidney_L", "Kidney_R", "SpinalCord"],
       ["Bladder", "Bowel_Small", "Femur_L", "Femur_R"],
       manual=["Rectum", "Sigmoid (đang nằm trong Colon)", "Bowel_Bag"],
       note="Kidney, SpinalCord, A_Aorta, V_Venacava_I dùng khi xạ hạch cạnh động mạch chủ.", region="pelvis"),
    _p("vagina", "U vùng tiểu khung", "Âm đạo",
       [*_PELVIS, "Bone_Hips", *_ILIAC], ["Bladder", "Bowel_Small", "Femur_L", "Femur_R"],
       manual=["Rectum", "Urethra", "Anal canal", "Bowel_Bag"], region="pelvis"),
    _p("vulva", "U vùng tiểu khung", "Âm hộ",
       [*_PELVIS, "Bone_Hips", *_ILIAC], ["Bladder", "Femur_L", "Femur_R"],
       manual=["Rectum", "Anal canal", "Bowel_Bag", "Skin", "Mạch đùi (mốc hạch bẹn)"],
       note="Femur gồm cả xương đùi: chỏm và cổ xương đùi cần chú ý khi xạ hạch bẹn.", region="pelvis"),
    _p("prostate", "U vùng tiểu khung", "Tiền liệt tuyến", [*_PELVIS, "Prostate", *_ILIAC], ["Bladder", "Femur_L", "Femur_R", "Bowel_Small"],
       manual=["Rectum", "PenileBulb", "SeminalVes (túi tinh, thuộc CTV)"],
       note="Prostate tự động chỉ để tham khảo khi vẽ CTV.", region="pelvis"),
    _p("bladder", "U vùng tiểu khung", "Bàng quang", ["Bowel_Small", "Colon", "Femur_L", "Femur_R", *_ILIAC],
       ["Bowel_Small", "Colon", "Femur_L", "Femur_R"],
       manual=["Rectum", "Bowel_Bag"], note="Bàng quang là cơ quan đích nên không vẽ Bladder.", region="pelvis"),
    # ------------------------------------------------------------------ Xương / di căn
    _p("bone_spine", "Di căn xương", "Cột sống",
       ["SpinalCord", "Esophagus", "Heart", *_LUNGS, "Kidney_L", "Kidney_R", "Liver", "Stomach", "Bowel_Small",
        "Vertebrae_*"],
       ["SpinalCord", "Esophagus", "Heart", "Lungs", "Kidney_L", "Kidney_R", "Bowel_Small"],
       manual=["SpinalCanal / Cauda equina (SBRT)"],
       note="Triệt căn (SBRT) có thêm các đốt sống (~1 đơn vị thời gian) để định vị; cơ quan ngoài trường chụp tự bỏ qua.",
       region="thorax"),
    _p("bone_pelvis", "Di căn xương", "Xương chậu / khớp háng",
       ["Bladder", "Bowel_Small", "Colon", "Femur_L", "Femur_R", "SpinalCord"],
       ["Bladder", "Bowel_Small", "Colon"], manual=["Rectum"], region="pelvis"),
]

PROTOCOL_BY_ID = {p.id: p for p in PROTOCOLS}
INTENTS = {"curative": "Triệt căn", "palliative": "Triệu chứng"}


def expand(names) -> list[str]:
    """Đổi "Vertebrae_*" thành danh sách đốt sống trong danh mục; bỏ trùng, giữ thứ tự."""
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
