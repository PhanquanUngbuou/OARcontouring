"""Đọc CT DICOM và chạy model phân vùng.

Segmenter là một interface nhỏ: nhận ảnh CT (SimpleITK) + tên task, trả về
label map (numpy, thứ tự z,y,x, cùng lưới với ảnh CT) và bảng {số nhãn: tên}.
Nhờ đó có thể thay TotalSegmentator bằng model khác (ví dụ model khoa tự
huấn luyện bằng nnU-Net) mà không phải sửa phần còn lại.
"""

from __future__ import annotations

import logging
import os
import tempfile
from pathlib import Path
from typing import Protocol

import numpy as np
import SimpleITK as sitk

log = logging.getLogger(__name__)


class Segmenter(Protocol):
    def run(self, image: sitk.Image, task: str) -> tuple[np.ndarray, dict[int, str]]: ...


def load_ct_series(dicom_dir: str | Path) -> sitk.Image:
    """Đọc đúng MỘT series CT trong thư mục. Thư mục có nhiều series -> lỗi rõ ràng."""
    dicom_dir = str(dicom_dir)
    series_ids = sitk.ImageSeriesReader.GetGDCMSeriesIDs(dicom_dir) or []
    if len(series_ids) != 1:
        raise ValueError(
            f"Thư mục cần chứa đúng 1 series CT, đang có {len(series_ids)}. "
            "Hãy tách mỗi series ra một thư mục riêng."
        )
    files = sitk.ImageSeriesReader.GetGDCMSeriesFileNames(dicom_dir, series_ids[0])
    reader = sitk.ImageSeriesReader()
    reader.SetFileNames(files)
    image = reader.Execute()
    return sitk.Cast(image, sitk.sitkInt16)


def resample_labels_to(label_img: sitk.Image, reference: sitk.Image) -> np.ndarray:
    """Đưa label map về đúng lưới ảnh CT (nearest neighbour), trả về mảng z,y,x."""
    same_grid = (
        label_img.GetSize() == reference.GetSize()
        and np.allclose(label_img.GetSpacing(), reference.GetSpacing(), atol=1e-4)
        and np.allclose(label_img.GetOrigin(), reference.GetOrigin(), atol=1e-3)
        and np.allclose(label_img.GetDirection(), reference.GetDirection(), atol=1e-4)
    )
    if not same_grid:
        label_img = sitk.Resample(label_img, reference, sitk.Transform(), sitk.sitkNearestNeighbor, 0)
    return sitk.GetArrayFromImage(label_img).astype(np.int16)


def pick_device() -> str:
    """GPU NVIDIA -> "gpu"; Mac chip Apple có chip đồ hoạ -> "mps"; còn lại "cpu"."""
    try:
        import torch

        if torch.cuda.is_available():
            return "gpu"
        if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
            return "mps"
    except Exception:
        pass
    return "cpu"


DEVICE_LABEL = {"gpu": "GPU NVIDIA", "mps": "chip đồ hoạ Apple", "cpu": "CPU"}


class TotalSegmentatorRunner:
    """Chạy TotalSegmentator (chỉ các task miễn phí) trên máy nội bộ.

    - Tắt gửi thống kê sử dụng về server TotalSegmentator.
    - Ảnh CT chỉ được ghi ra thư mục tạm cục bộ, xoá ngay sau khi chạy.
    """

    def __init__(self, device: str = "gpu", fast: bool = False):
        if device == "mps":
            # phép tính nào chip Apple chưa hỗ trợ thì PyTorch tự làm bằng CPU
            os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
        self.device = device
        self.fast = fast
        self.fell_back = False  # True nếu chip đồ hoạ lỗi và đã chuyển sang CPU
        self._ready = False

    def _setup(self):
        if self._ready:
            return
        from totalsegmentator.config import set_config_key, setup_totalseg
        from totalsegmentator.map_to_binary import commercial_models

        setup_totalseg()
        set_config_key("send_usage_stats", False)
        # Đã tắt thống kê nên ẩn luôn thông báo "sends anonymous usage statistics"
        set_config_key("statistics_disclaimer_shown", True)
        self._commercial = set(commercial_models)
        self._ready = True

    def run(self, image: sitk.Image, task: str) -> tuple[np.ndarray, dict[int, str]]:
        self._setup()
        if task in self._commercial:
            raise ValueError(f"Task {task!r} cần license thương mại, không dùng trong công cụ này.")
        from totalsegmentator.map_to_binary import class_map
        from totalsegmentator.python_api import totalsegmentator

        # --fast chỉ có ở task total
        fast = self.fast and task == "total"
        with tempfile.TemporaryDirectory(prefix="oar_") as tmp:
            ct_path = Path(tmp) / "ct.nii.gz"
            seg_path = Path(tmp) / f"{task}.nii.gz"
            sitk.WriteImage(image, str(ct_path))
            log.info("Chạy TotalSegmentator task=%s fast=%s device=%s", task, fast, self.device)
            try:
                totalsegmentator(
                    input=ct_path, output=seg_path, task=task, ml=True,
                    fast=fast, device=self.device, quiet=True,
                )
            except Exception:
                if self.device != "mps":
                    raise
                # chip đồ hoạ Apple lỗi -> chạy lại bằng CPU, các lần sau dùng luôn CPU
                log.warning("Chip đồ hoạ (mps) lỗi ở task %s, chạy lại bằng CPU", task, exc_info=True)
                self.device, self.fell_back = "cpu", True
                totalsegmentator(
                    input=ct_path, output=seg_path, task=task, ml=True,
                    fast=fast, device="cpu", quiet=True,
                )
            labels = sitk.ReadImage(str(seg_path))
            arr = resample_labels_to(labels, image)
        return arr, dict(class_map[task])
