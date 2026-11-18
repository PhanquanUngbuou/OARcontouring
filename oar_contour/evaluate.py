"""So sánh contour AI với contour bác sĩ (Dice, HD95, tỉ lệ thể tích).

Dùng cho bước kiểm định: chạy trên các ca cũ của khoa (đã ẩn danh), so với
RTSTRUCT bác sĩ đã duyệt, để biết cơ quan nào đủ tốt, cơ quan nào chưa.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy import ndimage


@dataclass
class Metric:
    name: str
    dice: float
    hd95_mm: float
    volume_ai_cc: float
    volume_ref_cc: float

    @property
    def volume_ratio(self) -> float:
        return self.volume_ai_cc / self.volume_ref_cc if self.volume_ref_cc else float("nan")


def dice(a: np.ndarray, b: np.ndarray) -> float:
    s = int(a.sum()) + int(b.sum())
    return 2.0 * int(np.logical_and(a, b).sum()) / s if s else 1.0


def _surface(mask: np.ndarray) -> np.ndarray:
    return mask & ~ndimage.binary_erosion(mask, border_value=0)


def hd95(a: np.ndarray, b: np.ndarray, spacing: tuple[float, float, float]) -> float:
    """Khoảng cách Hausdorff 95% (mm), đối xứng. spacing theo đúng thứ tự trục của mask."""
    if not a.any() or not b.any():
        return float("inf")
    sa, sb = _surface(a), _surface(b)
    dt_b = ndimage.distance_transform_edt(~sb, sampling=spacing)
    dt_a = ndimage.distance_transform_edt(~sa, sampling=spacing)
    d = np.concatenate([dt_b[sa], dt_a[sb]])
    return float(np.percentile(d, 95))


def _norm(name: str) -> str:
    return name.strip().lower().replace(" ", "_")


def compare_rtstructs(
    dicom_dir: str | Path,
    ai_rtstruct: str | Path,
    ref_rtstruct: str | Path,
    aliases: dict[str, str] | None = None,
) -> list[Metric]:
    """aliases: tên trong RTSTRUCT bác sĩ -> tên TG-263 (ví dụ {"Tuy song": "SpinalCord"})."""
    from rt_utils import RTStructBuilder

    ai = RTStructBuilder.create_from(str(dicom_dir), str(ai_rtstruct), warn_only=True)
    ref = RTStructBuilder.create_from(str(dicom_dir), str(ref_rtstruct), warn_only=True)

    ds0 = ai.series_data[0]
    row_mm, col_mm = (float(v) for v in ds0.PixelSpacing)
    if len(ai.series_data) > 1:
        p0 = np.array(ai.series_data[0].ImagePositionPatient, float)
        p1 = np.array(ai.series_data[1].ImagePositionPatient, float)
        slice_mm = float(np.linalg.norm(p1 - p0))
    else:
        slice_mm = float(getattr(ds0, "SliceThickness", 1.0))
    spacing = (row_mm, col_mm, slice_mm)  # mask rt_utils: (rows, cols, slices)
    voxel_cc = row_mm * col_mm * slice_mm / 1000.0

    alias_map = {_norm(k): v for k, v in (aliases or {}).items()}
    ref_names = {}
    for n in ref.get_roi_names():
        ref_names[_norm(alias_map.get(_norm(n), n))] = n

    results = []
    for name in ai.get_roi_names():
        ref_name = ref_names.get(_norm(name))
        if ref_name is None:
            continue
        a = ai.get_roi_mask_by_name(name)
        b = ref.get_roi_mask_by_name(ref_name)
        results.append(Metric(
            name=name,
            dice=dice(a, b),
            hd95_mm=hd95(a, b, spacing),
            volume_ai_cc=float(a.sum()) * voxel_cc,
            volume_ref_cc=float(b.sum()) * voxel_cc,
        ))
    return results


def write_csv(rows: list[tuple[str, Metric]], path: str | Path) -> None:
    """rows: (mã ca đã ẩn danh, Metric)."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["case", "structure", "dice", "hd95_mm", "vol_ai_cc", "vol_ref_cc", "vol_ratio"])
        for case, m in rows:
            w.writerow([case, m.name, f"{m.dice:.3f}", f"{m.hd95_mm:.1f}",
                        f"{m.volume_ai_cc:.1f}", f"{m.volume_ref_cc:.1f}", f"{m.volume_ratio:.2f}"])


def summarize(rows: list[tuple[str, Metric]]) -> str:
    by_name: dict[str, list[Metric]] = {}
    for _, m in rows:
        by_name.setdefault(m.name, []).append(m)
    lines = [f"{'Cấu trúc':<16}{'n':>4}{'Dice TB':>9}{'Dice min':>10}{'HD95 TB':>9}"]
    for name, ms in sorted(by_name.items()):
        d = [m.dice for m in ms]
        h = [m.hd95_mm for m in ms if np.isfinite(m.hd95_mm)]
        lines.append(f"{name:<16}{len(ms):>4}{np.mean(d):>9.3f}{np.min(d):>10.3f}"
                     f"{(np.mean(h) if h else float('nan')):>9.1f}")
    return "\n".join(lines)
