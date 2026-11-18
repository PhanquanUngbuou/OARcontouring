"""Chạy thử bằng ảnh CT MẪU CÔNG KHAI của TotalSegmentator (không phải dữ liệu bệnh nhân).

Tải file NIfTI mẫu, chuyển thành series DICOM CT với header giả, rồi chạy pipeline
như với ca thật. Dùng để kiểm tra cài đặt trên máy mới.
"""

from __future__ import annotations

import urllib.request
from pathlib import Path

import numpy as np

SAMPLE_URL = ("https://raw.githubusercontent.com/wasserth/TotalSegmentator/master/"
              "tests/reference_files/example_ct.nii.gz")


def download_sample(dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists():
        print(f"Tải ảnh CT mẫu công khai -> {dest}")
        urllib.request.urlretrieve(SAMPLE_URL, dest)
    return dest


def nifti_to_dicom_series(nifti: Path, out_dir: Path) -> Path:
    import SimpleITK as sitk
    from pydicom.dataset import Dataset, FileMetaDataset
    from pydicom.uid import CTImageStorage, ExplicitVRLittleEndian, generate_uid

    img = sitk.DICOMOrient(sitk.ReadImage(str(nifti)), "LPS")
    arr = sitk.GetArrayFromImage(img).astype(np.int16)
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("*.dcm"):
        old.unlink()
    study, series, frame = generate_uid(), generate_uid(), generate_uid()
    sx, sy, sz = img.GetSpacing()
    d = img.GetDirection()
    iop = [float(d[0]), float(d[3]), float(d[6]), float(d[1]), float(d[4]), float(d[7])]
    for k in range(arr.shape[0]):
        meta = FileMetaDataset()
        sop = generate_uid()
        meta.MediaStorageSOPClassUID = CTImageStorage
        meta.MediaStorageSOPInstanceUID = sop
        meta.TransferSyntaxUID = ExplicitVRLittleEndian
        ds = Dataset()
        ds.file_meta = meta
        ds.SOPClassUID, ds.SOPInstanceUID = CTImageStorage, sop
        ds.StudyInstanceUID, ds.SeriesInstanceUID, ds.FrameOfReferenceUID = study, series, frame
        ds.PatientName, ds.PatientID, ds.Modality = "DEMO^PUBLIC_SAMPLE", "DEMO0001", "CT"
        ds.StudyDate = ds.SeriesDate = "20260101"
        ds.StudyTime = ds.SeriesTime = "120000"
        ds.SeriesDescription = "TotalSegmentator public sample"
        ds.InstanceNumber = k + 1
        ds.ImagePositionPatient = [float(v) for v in img.TransformIndexToPhysicalPoint((0, 0, k))]
        ds.ImageOrientationPatient = iop
        ds.PixelSpacing = [sy, sx]
        ds.SliceThickness = sz
        ds.Rows, ds.Columns = arr.shape[1], arr.shape[2]
        ds.SamplesPerPixel = 1
        ds.PhotometricInterpretation = "MONOCHROME2"
        ds.BitsAllocated = ds.BitsStored = 16
        ds.HighBit = 15
        ds.PixelRepresentation = 1
        ds.RescaleIntercept, ds.RescaleSlope = 0, 1
        ds.PixelData = arr[k].tobytes()
        ds.save_as(out_dir / f"ct_{k:04d}.dcm", enforce_file_format=True)
    return out_dir
