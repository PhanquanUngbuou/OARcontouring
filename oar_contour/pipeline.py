"""CT DICOM -> phân vùng -> RTSTRUCT (bản nháp OAR để bác sĩ duyệt trong Monaco)."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import numpy as np
import SimpleITK as sitk

from .segment import Segmenter, load_ct_series
from .structures import (
    NOT_COVERED,
    REGION_RULES,
    TASK_CROP,
    Structure,
    structures_for,
    tasks_for,
    total_labels_for,
)

log = logging.getLogger(__name__)

STRUCTURE_SET_LABEL = "AI_OAR_DRAFT"
ROI_DESCRIPTION = "AI draft - bac si phai duyet truoc khi lap ke hoach"
MIN_VOXELS_DEFAULT = 50  # bỏ các mảnh quá nhỏ (cơ quan chỉ lọt mép trường chụp)


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


def detect_regions(total_labels: np.ndarray, class_map: dict[int, str], voxel_cc: float) -> list[str]:
    """Nhận diện vùng chụp từ kết quả task 'total' theo thể tích (xem REGION_RULES)."""
    name_to_idx = {v: k for k, v in class_map.items()}
    counts = np.bincount(total_labels.ravel(), minlength=max(class_map) + 1)
    regions = []
    for region, rules in REGION_RULES.items():
        for labels, min_cc in rules:
            n = sum(int(counts[name_to_idx[m]]) for m in labels if m in name_to_idx)
            if n * voxel_cc >= min_cc:
                regions.append(region)
                break
    return regions


def crop_range(rough: np.ndarray, class_map: dict[int, str], labels, margin_mm: float,
               image: sitk.Image) -> tuple[int, int]:
    """Đoạn lát [z0, z1) chứa các nhãn (theo kết quả model nhanh) + lề; không thấy thì cả ảnh."""
    nz = image.GetSize()[2]
    name_to_idx = {v: k for k, v in class_map.items()}
    ids = [name_to_idx[l] for l in labels if l in name_to_idx]
    zs = np.nonzero(np.isin(rough, ids).any(axis=(1, 2)))[0] if ids else np.array([])
    if zs.size == 0:
        return 0, nz
    pad = int(np.ceil(margin_mm / image.GetSpacing()[2]))
    return max(0, int(zs.min()) - pad), min(nz, int(zs.max()) + 1 + pad)


def largest_component(mask: np.ndarray) -> np.ndarray:
    from scipy import ndimage

    lab, n = ndimage.label(mask)
    if n <= 1:
        return mask
    sizes = np.bincount(lab.ravel())
    sizes[0] = 0
    return lab == int(sizes.argmax())


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
        if s.single and mask.any():
            mask = largest_component(mask)
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
    progress: Callable[[str], None] | None = None,
) -> Report:
    say = progress or (lambda msg: None)
    say("Đọc ảnh CT")
    image = load_ct_series(dicom_dir)
    labelmaps: dict[str, np.ndarray] = {}
    class_maps: dict[str, dict[int, str]] = {}

    voxel_cc = float(np.prod(image.GetSpacing())) / 1000.0
    # Model nhanh 6 mm (vài giây): nhận diện vùng + biết cắt ảnh ở đâu cho model phụ
    say("Nhận diện vùng chụp (model nhanh 6 mm)")
    rough, rough_map = segmenter.run(image, "total", fastest=True)
    if site == "auto":
        sites = detect_regions(rough, rough_map, voxel_cc)
        if not sites:
            raise RuntimeError("Không nhận diện được vùng chụp; hãy chọn vùng giải phẫu.")
    else:
        sites = [s.strip() for s in site.split(",")]

    structures = structures_for(sites)
    # Chỉ chạy phần model "total" chứa các cơ quan cần, cắt ảnh quanh vùng đó -> nhanh hơn nhiều
    say("Chạy model: cơ quan chính (task total)")
    labelmaps["total"], class_maps["total"] = segmenter.run(
        image, "total", roi_subset=total_labels_for(structures))
    for task in tasks_for(structures):
        if task in labelmaps:
            continue
        z0, z1 = 0, image.GetSize()[2]
        if task in TASK_CROP:
            labels, margin = TASK_CROP[task]
            z0, z1 = crop_range(rough, rough_map, labels, margin, image)
        say(f"Chạy model bổ sung: {task} ({z1 - z0}/{image.GetSize()[2]} lát)")
        sub = image if (z0, z1) == (0, image.GetSize()[2]) else image[:, :, z0:z1]
        arr, class_maps[task] = segmenter.run(sub, task)
        full = np.zeros(image.GetSize()[::-1], arr.dtype)
        full[z0:z1] = arr
        labelmaps[task] = full

    masks, empty = build_masks(structures, labelmaps, class_maps, image, min_voxels)
    if not masks:
        raise RuntimeError("Không tạo được cấu trúc nào.")
    colors = {s.name: s.color for s in structures}
    say("Ghi file RTSTRUCT")
    write_rtstruct(dicom_dir, image, masks, colors, out_path)

    report = Report(sites=sites, skipped_empty=empty)
    report.written = {n: float(m.sum()) * voxel_cc for n, m in masks.items()}
    report.not_covered = list(dict.fromkeys(x for s in sites for x in NOT_COVERED.get(s, [])))
    report.notes = {s.name: s.note for s in structures if s.note and s.name in masks}
    return report
