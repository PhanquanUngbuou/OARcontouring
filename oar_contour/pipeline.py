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
               image: sitk.Image) -> tuple[int, int] | None:
    """Đoạn lát [z0, z1) chứa các nhãn (theo kết quả model nhanh) + lề; không thấy vùng đó thì None."""
    nz = image.GetSize()[2]
    name_to_idx = {v: k for k, v in class_map.items()}
    ids = [name_to_idx[l] for l in labels if l in name_to_idx]
    zs = np.nonzero(np.isin(rough, ids).any(axis=(1, 2)))[0] if ids else np.array([])
    if zs.size == 0:
        return None
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
    presets: dict[str, list[str]] | None = None,
    names: list[str] | None = None,
    manual: list[str] | None = None,
    label: str | None = None,
    on_plan: Callable[[list[tuple[str, float]]], None] | None = None,
    on_step: Callable[[int], None] | None = None,
    refine_parotid: bool = False,
) -> Report:
    """names: danh sách cấu trúc cố định (theo phác đồ) -> bỏ qua nhận diện vùng.
    manual: OAR bác sĩ phải tự vẽ (hiện trong báo cáo); label: tên phác đồ."""
    say = progress or (lambda msg: None)
    say("Đọc ảnh CT")
    image = load_ct_series(dicom_dir)
    labelmaps: dict[str, np.ndarray] = {}
    class_maps: dict[str, dict[int, str]] = {}

    voxel_cc = float(np.prod(image.GetSpacing())) / 1000.0
    # Model nhanh 6 mm (vài giây): nhận diện vùng + biết cắt ảnh ở đâu cho model phụ
    say("Định vị vùng chụp")
    rough, rough_map = segmenter.run(image, "total", fastest=True)
    if names:
        sites = [label or "Danh sách tuỳ chọn"]
    elif site == "auto":
        sites = detect_regions(rough, rough_map, voxel_cc)
        if not sites:
            raise RuntimeError("Không nhận diện được vùng chụp; hãy chọn vùng giải phẫu.")
    else:
        sites = [s.strip() for s in site.split(",")]

    if names and refine_parotid and ({"Parotid_L", "Parotid_R"} & set(names)):
        from .parotid_refine import LANDMARK_NAMES

        names = list(names) + [n for n in LANDMARK_NAMES if n not in names]  # mốc chặn: vẽ và xuất luôn
    if names:
        from .catalog import catalog

        cat = catalog()
        structures = [cat[n] for n in dict.fromkeys(names) if n in cat]
        if not structures:
            raise ValueError("Danh sách cơ quan trống.")
    else:
        structures = structures_for(sites, presets)
    # Chỉ chạy phần model "total" chứa các cơ quan cần, cắt ảnh quanh vùng đó -> nhanh hơn nhiều
    total_labels = total_labels_for(structures)
    # Kế hoạch các bước (trọng số ~ thời gian) để app hiện % và thời gian còn lại
    from .catalog import TASKS
    from .ts_labels import TOTAL_PART_OF

    extra_tasks = [t for t in tasks_for(structures) if t != "total"]
    n_parts = len({TOTAL_PART_OF[l] for l in total_labels if l in TOTAL_PART_OF})
    plan = [("Đọc ảnh CT", 0.05), ("Định vị vùng chụp", 0.2)]
    if total_labels:
        plan.append((TASKS["total"]["label"], 1.0 if getattr(segmenter, "fast", False) else float(n_parts)))
    plan += [(TASKS[t]["label"], float(TASKS[t]["cost"])) for t in extra_tasks]
    plan.append(("Ghi kết quả", 0.1))
    if on_plan:
        on_plan(plan)
    step_i = 2
    def next_step():
        nonlocal step_i
        if on_step:
            on_step(step_i)
        step_i += 1

    if total_labels:  # danh sách rỗng mà gửi đi thì sẽ chạy TOÀN BỘ -> bỏ qua hẳn
        next_step()
        say("Khoanh nhóm cơ quan chính")
        labelmaps["total"], class_maps["total"] = segmenter.run(image, "total", roi_subset=total_labels)
    for task in extra_tasks:
        if task in labelmaps:
            continue
        next_step()
        z0, z1 = 0, image.GetSize()[2]
        if task in TASK_CROP:
            labels, margin = TASK_CROP[task]
            rng = crop_range(rough, rough_map, labels, margin, image)
            if rng is None:  # vùng của model này không có trong ảnh -> bỏ qua, tiết kiệm thời gian
                say(f"Bỏ qua {TASKS[task]['label'].lower()}: không có trong vùng chụp")
                from .ts_labels import KNOWN_LABELS

                class_maps[task] = {i + 1: l for i, l in enumerate(KNOWN_LABELS.get(task, []))}
                labelmaps[task] = np.zeros(image.GetSize()[::-1], np.uint8)  # -> các cấu trúc này "không thấy"
                continue
            z0, z1 = rng
        say(f"Khoanh {TASKS[task]['label'].lower()}")
        sub = image if (z0, z1) == (0, image.GetSize()[2]) else image[:, :, z0:z1]
        arr, class_maps[task] = segmenter.run(sub, task)
        full = np.zeros(image.GetSize()[::-1], arr.dtype)
        full[z0:z1] = arr
        labelmaps[task] = full

    masks, empty = build_masks(structures, labelmaps, class_maps, image, min_voxels)
    extra_colors: dict[str, tuple[int, int, int]] = {}
    if refine_parotid and any(n in masks for n in ("Parotid_L", "Parotid_R")):
        from .parotid_refine import BARRIER_LABELS, DEFAULTS, REFINED, refine_parotid as _refine

        say("Hiệu chỉnh tuyến mang tai")

        def label_mask(label: str):
            for task, cmap in class_maps.items():
                for idx, name in cmap.items():
                    if name == label and task in labelmaps:
                        return labelmaps[task] == idx
            return None

        hu = sitk.GetArrayViewFromImage(image)
        sx, sy, sz = image.GetSpacing()
        for name, (side, label, out_name, color) in REFINED.items():
            if name not in masks:
                continue
            bar = np.zeros(hu.shape, bool)
            for b in BARRIER_LABELS[side]:
                m = label_mask(b)
                if m is not None:
                    bar |= m
            refined = _refine(hu, masks[name], bar, (sz, sy, sx), **DEFAULTS)
            if refined.sum() > masks[name].sum():
                masks[out_name] = refined
                extra_colors[out_name] = color
    if not masks:
        raise RuntimeError("Không tạo được cấu trúc nào.")
    colors = {s.name: s.color for s in structures} | extra_colors
    next_step()
    say("Ghi kết quả")
    write_rtstruct(dicom_dir, image, masks, colors, out_path)

    report = Report(sites=sites, skipped_empty=empty)
    report.written = {n: float(m.sum()) * voxel_cc for n, m in masks.items()}
    if names:
        report.not_covered = list(manual or [])
    else:
        report.not_covered = list(dict.fromkeys(x for s in sites for x in NOT_COVERED.get(s, [])))
    report.notes = {s.name: s.note for s in structures if s.note and s.name in masks}
    for n in extra_colors:
        report.notes[n] = "Tuyến mang tai đã hiệu chỉnh (thử nghiệm): so sánh với bản gốc trước khi dùng."
    return report
