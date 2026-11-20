"""Sinh docs/PHAC_DO_OAR.md (bảng phác đồ để khoa duyệt). Chạy: python scripts/tao_bang_phac_do.py"""
from pathlib import Path

from oar_contour.catalog import TASKS, estimate_cost
from oar_contour.protocols import PROTOCOLS, default_names

PART_VI = {"organs": "nội tạng", "vertebrae": "đốt sống", "cardiac": "tim mạch", "muscles": "cơ–xương",
           "ribs": "xương sườn"}


def short(names):
    vert = [n for n in names if n.startswith("Vertebrae_")]
    rest = [n for n in names if not n.startswith("Vertebrae_")]
    return ", ".join(rest + ([f"Vertebrae (×{len(vert)})"] if vert else []))


def models(names):
    c = estimate_cost(names)
    parts = [PART_VI[p] for p in c["total_parts"]]
    extra = [TASKS[t]["label"] for t in c["tasks"]]
    return "; ".join(filter(None, [("toàn thân: " + ", ".join(parts)) if parts else "", *extra])), c["units"]


lines = ["# Phác đồ OAR theo vị trí u (bản đề xuất – khoa cần duyệt)", "",
         "Chỉ gồm cơ quan có trong model **miễn phí**. Trong app, bác sĩ chọn *Mục đích* + *Vị trí xạ trị*, "
         "rồi có thể **Mở rộng / chỉnh sửa**: dùng cho riêng ca đó hoặc lưu làm mặc định của khoa.", "",
         "Thời gian: 1 đơn vị ≈ 1–2 phút trên MacBook chip M, vài giây trên GPU NVIDIA.", ""]
group = None
for p in PROTOCOLS:
    if p.group != group:
        group = p.group
        lines += [f"## {group}", ""]
    lines += [f"### {p.name}", "", "| | OAR app tự vẽ | Model cần chạy | Thời gian |", "|---|---|---|---|"]
    for intent, vi in (("curative", "Triệt căn"), ("palliative", "Triệu chứng")):
        names = default_names(p.id, intent)
        m, u = models(names)
        lines.append(f"| **{vi}** | {short(names)} | {m} | ≈ {u} |")
    lines.append("")
    if p.note:
        lines.append(f"*Ghi chú:* {p.note}")
    lines.append("")
lines += ["## Trường hợp khác", "", "Vị trí u không có trong danh sách: chọn **Trường hợp khác – tự chọn OAR**, "
          "lấy sẵn danh sách của vùng gần nhất rồi thêm/bớt, hoặc tự tích từ đầu trong danh mục đầy đủ.", ""]
Path(__file__).resolve().parent.parent.joinpath("docs", "PHAC_DO_OAR.md").write_text("\n".join(lines), encoding="utf-8")
print("Đã ghi docs/PHAC_DO_OAR.md")
