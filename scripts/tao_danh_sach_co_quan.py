"""Sinh docs/DANH_SACH_CO_QUAN.md từ danh mục trong app. Chạy: python scripts/tao_danh_sach_co_quan.py"""
from pathlib import Path

from oar_contour.catalog import GROUP_OF, GROUPS, TASKS, catalog
from oar_contour.structures import DEFAULT_PRESETS, NOT_COVERED, SITE_NAMES
from oar_contour.ts_labels import TOTAL_PART_OF

PART_VI = {"organs": "nội tạng", "vertebrae": "đốt sống", "cardiac": "tim mạch", "muscles": "cơ – xương",
           "ribs": "xương sườn"}
cat = catalog()
default_sites = {n: [SITE_NAMES[s] for s, names in DEFAULT_PRESETS.items() if n in names] for n in cat}

lines = ["# Danh sách cơ quan QuanContour khoanh được", "",
         f"Tổng cộng **{len(cat)} cấu trúc** từ các model **miễn phí** của TotalSegmentator (CT). "
         "Trong app: **Chọn cơ quan…** để tích/bỏ cho từng vùng; lựa chọn được lưu lại.", "",
         "## Thời gian chạy", "",
         "Model **toàn thân** gồm 5 phần. App chỉ chạy phần chứa cơ quan đã chọn, nên chọn thêm cơ quan "
         "**cùng phần** gần như không tốn thêm thời gian. Các model riêng chỉ chạy trên đoạn ảnh có vùng đó.", "",
         "| Model | Chứa | Chi phí (đơn vị) |", "|---|---|---|"]
for part, vi in PART_VI.items():
    n = sum(1 for v in TOTAL_PART_OF.values() if v == part)
    lines.append(f"| Toàn thân – phần {vi} | {n} nhãn | 1 |")
for t, info in TASKS.items():
    if t != "total":
        lines.append(f"| {info['label']} (`{t}`) | {sum(1 for s in cat.values() if s.task == t)} cấu trúc | {info['cost']} |")
lines += ["", "1 đơn vị ≈ 1–2 phút trên MacBook chip M, khoảng 1 phút trên CPU mạnh, vài giây trên GPU NVIDIA. "
          "Chế độ nhanh nhanh hơn nhiều nhưng kém chính xác.", "",
          "## Danh sách theo nhóm", "",
          "Cột **Mặc định** = vùng mà cơ quan được tích sẵn.", ""]
for g in GROUPS:
    items = [s for n, s in cat.items() if GROUP_OF.get(n) == g]
    if not items:
        continue
    lines += [f"### {g} ({len(items)})", "", "| Tên | Model | Mặc định |", "|---|---|---|"]
    for s in items:
        if s.task == "total":
            parts = sorted({PART_VI[TOTAL_PART_OF[l]] for l in s.labels if l in TOTAL_PART_OF})
            model = "toàn thân – " + ", ".join(parts)
        else:
            model = TASKS[s.task]["label"]
        lines.append(f"| {s.name} | {model} | {', '.join(default_sites[s.name]) or ''} |")
    lines.append("")
lines += ["## Cơ quan KHÔNG có trong model miễn phí (bác sĩ tự vẽ / khoa tự huấn luyện)", ""]
for site, names in NOT_COVERED.items():
    lines.append(f"- **{SITE_NAMES[site]}:** {', '.join(names)}")
lines.append("")
Path(__file__).resolve().parent.parent.joinpath("docs", "DANH_SACH_CO_QUAN.md").write_text("\n".join(lines), encoding="utf-8")
print("Đã ghi docs/DANH_SACH_CO_QUAN.md")
