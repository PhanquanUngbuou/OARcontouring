"""CT DICOM -> phân vùng -> RTSTRUCT (bản nháp OAR để bác sĩ duyệt trong Monaco)."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import SimpleITK as sitk

from .segment import Segmenter, load_ct_series
from .structures import (
    NOT_COVERED,
    REGION_MARKERS,
    Structure,
    structures_for,
    tasks_for,
)

log = logging.getLogger(__name__)

STRUCTURE_SET_LABEL = "AI_OAR_DRAFT"
ROI_DESCRIPTION = "AI draft - bac si phai duyet truoc khi lap ke hoach"
MIN_VOXELS_DEFAULT = 50  # bỏ các mảnh quá nhỏ (cơ quan chỉ lọt mép trường chụp)
REGION_MIN_VOXELS = 2000  # ngưỡng để coi là "vùng này có trong ảnh"


@dataclass
class Report:
    sites: list[str]
    written: dict[str, float] = field(default_factory=dict)  # tên -> thể tích cc
    skipped_empty: list[str] = field(default_factory=list)
    not_covered: list[str] = field(default_factory=list)
    notes: dict[str, str] = field(default_factory=dict)

    def summary(self) -> str:
        lines = [f"Vùng: {', '.join(self.sites)}", f"Đã tạo {len(self.written)} cấu trúc:"]
        lines += [f"  - {n}: {v:.1f} cc" for n, v in self.written.items()]
        if self.skipped_empty:
            lines.append("Không thấy trong ảnh (bỏ qua): " + ", ".join(self.skipped_empty))
        if self.not_covered:
            lines.append("Model KHÔNG hỗ trợ, bác sĩ cần tự vẽ: " + ", ".join(self.not_covered))
        if self.notes:
            lines.append("Lưu ý khi duyệt:")
            lines += [f"  - {n}: {t}" for n, t in self.notes.items()]
        return "\n".join(lines)


def detect_regions(total_labels: np.ndarray, class_map: dict[int, str]) -> list[str]:
    """Nhận diện vùng chụp từ kết quả task 'total'."""
    name_to_idx = {v: k for k, v in class_map.items()}
    counts = np.bincount(total_labels.ravel(), minlength=max(class_map) + 1)
    regions = []
    for region, markers in REGION_MARKERS.items():
        n = sum(int(counts[name_to_idx[m]]) for m in markers if m in name_to_idx)
        if n >= REGION_MIN_VOXELS:
            regions.append(region)
    return regions


def _patient_x(image: sitk.Image) -> np.ndarray:
    """Toạ độ x (LPS, mm) của từng cột ảnh; x dương = bên TRÁI bệnh nhân."""
    nx, ny, nz = image.GetSize()
    return np.array([
        image.TransformContinuousIndexToPhysicalPoint((i, ny / 2, nz / 2))[0] for i in range(nx)
    ])


def _midline_x(image: sitk.Image, labelmaps, class_maps) -> float:
    """Đường giữa: trọng tâm xương ức/tủy sống nếu có, không thì trọng tâm cơ thể."""
    total = labelmaps.get("total")
    xs = _patient_x(image)
    if total is not None:
        name_to_idx = {v: k for k, v in class_maps["total"].items()}
        for marker in ("sternum", "spinal_cord"):
            idx = name_to_idx.get(marker)
            if idx is not None:
                cols = np.nonzero(total == idx)[2]
                if cols.size > 100:
                    return float(xs[cols].mean())
    body = sitk.GetArrayViewFromImage(image) > -300
    cols = np.nonzero(body)[2]
    return float(xs[cols].mean()) if cols.size else float(xs.mean())


def build_masks(
    structures: list[Structure],
    labelmaps: dict[str, np.ndarray],
    class_maps: dict[str, dict[int, str]],
    image: sitk.Image,
    min_voxels: int = MIN_VOXELS_DEFAULT,
) -> tuple[dict[str, np.ndarray], list[str]]:
    masks: dict[str, np.ndarray] = {}
    empty: list[str] = []
    midline = None
    for s in structures:
        lab = labelmaps[s.task]
        name_to_idx = {v: k for k, v in class_maps[s.task].items()}
        missing = [l for l in s.labels if l not in name_to_idx]
        if missing:
            raise KeyError(f"{s.name}: task {s.task} không có nhãn {missing}")
        mask = np.isin(lab, [name_to_idx[l] for l in s.labels])
        if s.side:
            if midline is None:
                midline = _midline_x(image, labelmaps, class_maps)
            xs = _patient_x(image)
            keep_cols = xs > midline if s.side == "left" else xs <= midline
            mask &= keep_cols[np.newaxis, np.newaxis, :]
        if int(mask.sum()) < min_voxels:
            empty.append(s.name)
            continue
        masks[s.name] = mask
    return masks, empty


def write_rtstruct(
    dicom_dir: str | Path,
    image: sitk.Image,
    masks: dict[str, np.ndarray],
    colors: dict[str, tuple[int, int, int]],
    out_path: str | Path,
) -> None:
    """Ghi RTSTRUCT tham chiếu đúng series CT gốc (cùng FrameOfReference)."""
    from rt_utils import RTStructBuilder

    rt = RTStructBuilder.create_new(dicom_series_path=str(dicom_dir))
    # Ghép từng lát của rt_utils với lát tương ứng của SimpleITK theo toạ độ,
    # không giả định thứ tự sắp xếp của hai thư viện giống nhau.
    nz = image.GetSize()[2]
    slice_index = []
    for ds in rt.series_data:
        k = image.TransformPhysicalPointToContinuousIndex([float(v) for v in ds.ImagePositionPatient])[2]
        k_round = int(round(k))
        if abs(k - k_round) > 0.1 or not 0 <= k_round < nz:
            raise ValueError("Lát cắt DICOM không khớp lưới ảnh CT (series lỗi hoặc lẫn series).")
        slice_index.append(k_round)

    for name, mask in masks.items():
        rt_mask = np.stack([mask[k] for k in slice_index], axis=-1)  # (rows, cols, n)
        rt.add_roi(
            mask=rt_mask,
            color=list(colors[name]),
            name=name,
            description=ROI_DESCRIPTION,
            roi_generation_algorithm=0,  # AUTOMATIC
            roi_interpreted_type="ORGAN",
        )
    rt.set_series_description("AI OAR draft")
    rt.ds.StructureSetLabel = STRUCTURE_SET_LABEL
    rt.ds.StructureSetName = STRUCTURE_SET_LABEL
    rt.save(str(out_path))


def run_pipeline(
    dicom_dir: str | Path,
    out_path: str | Path,
    segmenter: Segmenter,
    site: str = "auto",
    min_voxels: int = MIN_VOXELS_DEFAULT,
) -> Report:
    image = load_ct_series(dicom_dir)
    labelmaps: dict[str, np.ndarray] = {}
    class_maps: dict[str, dict[int, str]] = {}

    labelmaps["total"], class_maps["total"] = segmenter.run(image, "total")
    if site == "auto":
        sites = detect_regions(labelmaps["total"], class_maps["total"])
        if not sites:
            raise RuntimeError("Không nhận diện được vùng chụp; hãy chỉ định --site.")
    else:
        sites = [s.strip() for s in site.split(",")]

    structures = structures_for(sites)
    for task in tasks_for(structures):
        if task not in labelmaps:
            labelmaps[task], class_maps[task] = segmenter.run(image, task)

    masks, empty = build_masks(structures, labelmaps, class_maps, image, min_voxels)
    if not masks:
        raise RuntimeError("Không tạo được cấu trúc nào.")
    colors = {s.name: s.color for s in structures}
    write_rtstruct(dicom_dir, image, masks, colors, out_path)

    voxel_cc = float(np.prod(image.GetSpacing())) / 1000.0
    report = Report(sites=sites, skipped_empty=empty)
    report.written = {n: float(m.sum()) * voxel_cc for n, m in masks.items()}
    report.not_covered = list(dict.fromkeys(x for s in sites for x in NOT_COVERED.get(s, [])))
    report.notes = {s.name: s.note for s in structures if s.note and s.name in masks}
    return report
