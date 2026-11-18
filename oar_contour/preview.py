"""Xuất ảnh PNG chồng contour lên CT để xem nhanh (không thay thế việc duyệt trong TPS)."""

from __future__ import annotations

from pathlib import Path

import numpy as np


def render_preview(ct_dir: str | Path, rtstruct: str | Path, out_png: str | Path) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from pydicom import dcmread
    from rt_utils import RTStructBuilder

    rt = RTStructBuilder.create_from(str(ct_dir), str(rtstruct))
    s0 = rt.series_data[0]
    slope = float(getattr(s0, "RescaleSlope", 1))
    intercept = float(getattr(s0, "RescaleIntercept", 0))
    vol = np.stack([s.pixel_array.astype(np.float32) for s in rt.series_data], -1) * slope + intercept

    rs = dcmread(str(rtstruct))
    numbers = {r.ROINumber: r.ROIName for r in rs.StructureSetROISequence}
    colors = {numbers[c.ReferencedROINumber]: np.array(c.ROIDisplayColor, float) / 255
              for c in rs.ROIContourSequence}
    masks = {n: rt.get_roi_mask_by_name(n) for n in colors}
    masks = {n: m for n, m in masks.items() if m.any()}
    if not masks:
        raise RuntimeError("RTSTRUCT không có contour nào.")

    union = np.zeros(vol.shape, bool)
    for m in masks.values():
        union |= m
    rows, cols, zs = np.nonzero(union)
    r0, c0 = int(np.median(rows)), int(np.median(cols))
    # 3 lát axial: 25%, 50%, 75% chiều trên-dưới của vùng có contour
    z_lo, z_hi = int(zs.min()), int(zs.max())
    axial = [int(z_lo + f * (z_hi - z_lo)) for f in (0.25, 0.5, 0.75)]

    row_mm, col_mm = (float(v) for v in s0.PixelSpacing)
    if len(rt.series_data) > 1:
        p0 = np.array(rt.series_data[0].ImagePositionPatient, float)
        p1 = np.array(rt.series_data[1].ImagePositionPatient, float)
        z_mm = float(np.linalg.norm(p1 - p0))
    else:
        z_mm = float(getattr(s0, "SliceThickness", 1.0))

    views = [(f"Axial {i + 1}", vol[:, :, z], {n: m[:, :, z] for n, m in masks.items()}, row_mm / col_mm)
             for i, z in enumerate(axial)]
    # lát dọc: trục z dựng đứng, đầu ở trên (rt_utils xếp lát theo z tăng dần = về phía đầu)
    views.append(("Coronal", vol[r0, :, :].T[::-1], {n: m[r0, :, :].T[::-1] for n, m in masks.items()}, z_mm / col_mm))
    views.append(("Sagittal", vol[:, c0, :].T[::-1], {n: m[:, c0, :].T[::-1] for n, m in masks.items()}, z_mm / row_mm))

    fig, axes = plt.subplots(1, len(views), figsize=(4.2 * len(views), 5.2), facecolor="black")
    for ax, (title, img, ms, aspect) in zip(axes, views):
        ax.imshow(np.clip(img, -200, 300), cmap="gray", aspect=aspect)
        for n, m in ms.items():
            if m.any():
                ax.contour(m, levels=[0.5], colors=[colors[n]], linewidths=1.1)
        ax.set_title(title, color="white")
        ax.axis("off")
    handles = [plt.Line2D([], [], color=colors[n], lw=3, label=n) for n in masks]
    fig.legend(handles=handles, loc="lower center", ncol=min(9, len(handles)),
               facecolor="black", labelcolor="white", fontsize=9, frameon=False)
    fig.text(0.01, 0.97, "AI DRAFT - bac si phai duyet", color="orange", fontsize=10, va="top")
    plt.tight_layout(rect=(0, 0.1, 1, 0.95))
    out_png = Path(out_png)
    fig.savefig(out_png, dpi=110, facecolor="black")
    plt.close(fig)
    return out_png
