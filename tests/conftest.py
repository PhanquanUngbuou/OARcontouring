"""Dữ liệu GIẢ hoàn toàn: phantom CT tổng hợp, không có dữ liệu bệnh nhân."""

from __future__ import annotations

import random
from pathlib import Path

import numpy as np
import pytest
from pydicom.dataset import Dataset, FileMetaDataset
from pydicom.uid import CTImageStorage, ExplicitVRLittleEndian, generate_uid

NX, NY, NZ = 64, 48, 24
SPACING = (2.0, 2.0, 3.0)

SUPINE = (1, 0, 0, 0, 1, 0)  # HFS
PRONE = (-1, 0, 0, 0, -1, 0)  # HFP


def make_ct_series(
    out_dir: Path,
    orientation=SUPINE,
    z_step: float = SPACING[2],
    seed: int = 0,
) -> Path:
    """Ghi series CT giả (thân hình elip). Tên file xáo trộn để không phụ thuộc thứ tự."""
    out_dir.mkdir(parents=True, exist_ok=True)
    study, series, frame = generate_uid(), generate_uid(), generate_uid()
    yy, xx = np.mgrid[0:NY, 0:NX]
    body = ((xx - NX / 2) / (NX * 0.45)) ** 2 + ((yy - NY / 2) / (NY * 0.45)) ** 2 <= 1
    pixels = np.where(body, 1024, 0).astype(np.uint16)  # HU = pixel - 1024

    row_dir = np.array(orientation[:3], float)
    col_dir = np.array(orientation[3:], float)
    normal = np.cross(row_dir, col_dir)
    first = np.array([-NX, -NY, -30.0])
    order = list(range(NZ))
    random.Random(seed).shuffle(order)
    for n, k in enumerate(order):
        pos = first + normal * z_step * k
        meta = FileMetaDataset()
        meta.MediaStorageSOPClassUID = CTImageStorage
        sop = generate_uid()
        meta.MediaStorageSOPInstanceUID = sop
        meta.TransferSyntaxUID = ExplicitVRLittleEndian
        ds = Dataset()
        ds.file_meta = meta
        ds.SOPClassUID = CTImageStorage
        ds.SOPInstanceUID = sop
        ds.StudyInstanceUID, ds.SeriesInstanceUID, ds.FrameOfReferenceUID = study, series, frame
        ds.PatientName, ds.PatientID = "PHANTOM^TEST", "PHANTOM001"
        ds.Modality = "CT"
        ds.StudyDate = ds.SeriesDate = "20260101"
        ds.StudyTime = ds.SeriesTime = "120000"
        ds.InstanceNumber = k + 1
        ds.ImagePositionPatient = [float(v) for v in pos]
        ds.ImageOrientationPatient = [float(v) for v in orientation]
        ds.PixelSpacing = [SPACING[1], SPACING[0]]
        ds.SliceThickness = abs(z_step)
        ds.Rows, ds.Columns = NY, NX
        ds.SamplesPerPixel = 1
        ds.PhotometricInterpretation = "MONOCHROME2"
        ds.BitsAllocated = ds.BitsStored = 16
        ds.HighBit = 15
        ds.PixelRepresentation = 0
        ds.RescaleIntercept, ds.RescaleSlope = -1024, 1
        ds.PixelData = pixels.tobytes()
        ds.save_as(out_dir / f"img_{n:03d}.dcm", enforce_file_format=True)
    return out_dir


TOTAL_MAP = {
    10: "lung_upper_lobe_left", 11: "lung_lower_lobe_left", 12: "lung_upper_lobe_right",
    13: "lung_middle_lobe_right", 14: "lung_lower_lobe_right", 15: "esophagus", 51: "heart",
    79: "spinal_cord", 116: "sternum", 5: "liver", 90: "brain", 21: "urinary_bladder",
}
BREAST_MAP = {1: "breast"}


def _complete(cmap: dict[int, str], task: str) -> dict[int, str]:
    """Bổ sung mọi nhãn khác của model (không có voxel nào trong phantom)."""
    from oar_contour.ts_labels import KNOWN_LABELS

    cmap = dict(cmap)
    names = set(cmap.values())
    nxt = 200
    for label in KNOWN_LABELS.get(task, []):
        if label not in names:
            cmap[nxt] = label
            names.add(label)
            nxt += 1
    return cmap


def thorax_labels() -> dict[str, np.ndarray]:
    """Label map giả (z, y, x) mô phỏng ảnh ngực, theo chỉ số ảnh."""
    t = np.zeros((NZ, NY, NX), np.int16)
    t[4:12, 10:30, 38:54] = 10
    t[12:20, 10:30, 38:54] = 11
    t[4:9, 10:30, 10:26] = 12
    t[9:14, 10:30, 10:26] = 13
    t[14:20, 10:30, 10:26] = 14
    t[8:16, 25:38, 28:37] = 51
    t[:, 40:43, 31:33] = 79
    t[6:16, 5:8, 30:34] = 116
    b = np.zeros_like(t)
    b[6:16, 0:6, 8:56] = 1
    return {"total": t, "breasts": b}


class FakeSegmenter:
    def __init__(self, labelmaps: dict[str, np.ndarray]):
        self.labelmaps = labelmaps
        self.calls: list[str] = []
        self.kwargs: list[dict] = []
        self.sizes: list[int] = []  # số lát ảnh đưa vào mỗi lần chạy
        self._full = None

    def run(self, image, task, roi_subset=None, fastest=False):
        self.calls.append(task)
        self.kwargs.append({"roi_subset": roi_subset, "fastest": fastest})
        self.sizes.append(image.GetSize()[2])
        if self._full is None:
            self._full = image  # lần gọi đầu luôn là ảnh đầy đủ
        z0 = int(round(self._full.TransformPhysicalPointToContinuousIndex(image.GetOrigin())[2]))
        arr = self.labelmaps.get(task)
        if arr is None:
            arr = np.zeros(self._full.GetSize()[::-1], np.int16)
        arr = arr[z0:z0 + image.GetSize()[2]]
        base = TOTAL_MAP if task == "total" else BREAST_MAP if task == "breasts" else {}
        return arr.copy(), _complete(base, task)


@pytest.fixture
def ct_dir(tmp_path):
    return make_ct_series(tmp_path / "ct")
