"""Ẩn danh DICOM (CT, RTSTRUCT...) trước khi đưa ra khỏi bệnh viện.

- Mỗi thư mục con của thư mục nguồn = 1 ca (1 bệnh nhân). Nếu thư mục nguồn chứa file DICOM trực tiếp thì coi là 1 ca.
- Xoá/thay thông tin nhận dạng: tên, mã bệnh nhân, ngày sinh, các ngày giờ, nơi chụp, bác sĩ, kỹ thuật viên,
  mã chỉ định… và mọi thẻ riêng của hãng (private tags).
- Mọi UID định danh (Study/Series/SOP/FrameOfReference và các tham chiếu bên trong RTSTRUCT) được thay NHẤT QUÁN
  -> ảnh và RTSTRUCT đã ẩn danh vẫn khớp nhau.
- Giữ nguyên hình học ảnh (vị trí, hướng, khoảng cách điểm ảnh) và giới tính.
- Bảng đối chiếu mã ca <-> tên thư mục gốc ghi ra file RIÊNG (mặc định ~/QuanContour_maps), KHÔNG nằm trong thư mục ẩn danh.
"""

from __future__ import annotations

import csv
import secrets
import uuid
from datetime import datetime
from pathlib import Path

from pydicom import dcmread
from pydicom.dataset import Dataset
from pydicom.uid import generate_uid

# Thẻ xoá hẳn (keyword DICOM)
REMOVE = [
    "PatientBirthDate", "PatientBirthTime", "PatientAge", "PatientAddress", "PatientTelephoneNumbers",
    "OtherPatientIDs", "OtherPatientIDsSequence", "OtherPatientNames", "PatientMotherBirthName",
    "MilitaryRank", "EthnicGroup", "Occupation", "AdditionalPatientHistory", "PatientComments",
    "MedicalRecordLocator", "PatientInsurancePlanCodeSequence", "IssuerOfPatientID", "PatientWeight", "PatientSize",
    "InstitutionName", "InstitutionAddress", "InstitutionalDepartmentName", "StationName",
    "ReferringPhysicianName", "ReferringPhysicianAddress", "ReferringPhysicianTelephoneNumbers",
    "PerformingPhysicianName", "NameOfPhysiciansReadingStudy", "PhysiciansOfRecord", "OperatorsName",
    "RequestingPhysician", "ScheduledPerformingPhysicianName", "AccessionNumber", "StudyID",
    "RequestAttributesSequence", "RequestedProcedureID", "ScheduledProcedureStepID", "PerformedProcedureStepID",
    "DeviceSerialNumber", "PlateID", "ImageComments", "StudyComments", "ProtocolName", "PerformedStationName",
    "PerformedLocation", "ReviewerName", "StructureSetDescription", "ContentCreatorName", "PersonName",
    "InstanceCreationDate", "InstanceCreationTime",
    "AcquisitionDateTime", "PerformedProcedureStepStartTime", "PerformedProcedureStepStartDate",
    "PerformedProcedureStepEndDate", "PerformedProcedureStepEndTime", "ReviewDate", "ReviewTime",
]
# Ngày giữ thẻ nhưng thay bằng ngày cố định (nhiều phần mềm cần có StudyDate)
FIXED_DATE = "20000101"
DATES = ["StudyDate", "SeriesDate", "AcquisitionDate", "ContentDate", "StructureSetDate"]
FIXED_TIME = "000000"
TIMES = ["StudyTime", "SeriesTime", "AcquisitionTime", "ContentTime", "StructureSetTime"]
# UID không phải định danh (giữ nguyên)
_KEEP_UID_SUFFIX = ("ClassUID", "TransferSyntaxUID")


class Anonymizer:
    def __init__(self, salt: str | None = None):
        self.salt = salt or secrets.token_hex(16)
        self.uid_map: dict[str, str] = {}

    def _uid(self, old: str) -> str:
        if old not in self.uid_map:
            self.uid_map[old] = generate_uid(entropy_srcs=[self.salt, old])
        return self.uid_map[old]

    def _walk(self, ds: Dataset):
        for elem in list(ds):
            if elem.VR == "SQ":
                for item in elem.value:
                    self._walk(item)
            elif elem.VR == "UI" and elem.value and not (elem.keyword or "").endswith(_KEEP_UID_SUFFIX):
                if elem.VM > 1:
                    elem.value = [self._uid(str(v)) for v in elem.value]
                else:
                    elem.value = self._uid(str(elem.value))
            elif elem.VR == "PN" and elem.keyword != "PatientName":
                elem.value = ""
        for kw in REMOVE:
            if kw in ds:
                delattr(ds, kw)
        for kw in DATES:
            if kw in ds:
                setattr(ds, kw, FIXED_DATE)
        for kw in TIMES:
            if kw in ds:
                setattr(ds, kw, FIXED_TIME)

    def anonymize(self, ds: Dataset, code: str) -> Dataset:
        ds.remove_private_tags()
        self._walk(ds)
        ds.PatientName = code
        ds.PatientID = code
        if "StudyInstanceUID" in ds:  # nhiều phần mềm (Monaco, rt-utils) cần có ngày/giờ chụp
            ds.StudyDate = getattr(ds, "StudyDate", FIXED_DATE) or FIXED_DATE
            ds.StudyTime = getattr(ds, "StudyTime", FIXED_TIME) or FIXED_TIME
        ds.PatientIdentityRemoved = "YES"
        ds.DeidentificationMethod = "QuanContour: basic profile, UIDs remapped, dates fixed"
        if hasattr(ds, "file_meta"):
            if "MediaStorageSOPInstanceUID" in ds.file_meta and "SOPInstanceUID" in ds:
                ds.file_meta.MediaStorageSOPInstanceUID = ds.SOPInstanceUID
        return ds


def _cases(src: Path) -> list[Path]:
    subs = sorted(p for p in src.iterdir() if p.is_dir())
    direct = [p for p in src.iterdir() if p.is_file()]
    if direct and not subs:
        return [src]
    return subs


def anonymize_tree(src: str | Path, dst: str | Path, map_path: str | Path | None = None,
                   prefix: str = "QC", progress=print) -> Path:
    """Ẩn danh mọi ca trong src -> dst/<mã ca>/... Trả về đường dẫn bảng đối chiếu."""
    src, dst = Path(src), Path(dst)
    dst.mkdir(parents=True, exist_ok=True)
    map_path = Path(map_path) if map_path else (
        Path.home() / "QuanContour_maps" / f"anon_map_{datetime.now():%Y%m%d_%H%M%S}.csv")
    map_path.parent.mkdir(parents=True, exist_ok=True)
    if dst in map_path.parents or map_path.parent == dst:
        raise ValueError("Bảng đối chiếu không được nằm trong thư mục ẩn danh")
    rows = []
    for case in _cases(src):
        code = f"{prefix}_{uuid.uuid4().hex[:8].upper()}"
        anon = Anonymizer()
        n = 0
        for f in sorted(case.rglob("*")):
            if not f.is_file():
                continue
            try:
                ds = dcmread(f, force=True)
                if "SOPInstanceUID" not in ds:
                    continue
            except Exception:
                continue
            anon.anonymize(ds, code)
            modality = str(getattr(ds, "Modality", "XX"))
            out = dst / code / modality / f"{modality}_{n:05d}.dcm"
            out.parent.mkdir(parents=True, exist_ok=True)
            ds.save_as(out, enforce_file_format=True)
            n += 1
        if n:
            rows.append({"ma_ca": code, "thu_muc_goc": case.name, "so_file": n})
            progress(f"{case.name} -> {code} ({n} file)")
        else:
            progress(f"{case.name}: không có file DICOM, bỏ qua")
    with open(map_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["ma_ca", "thu_muc_goc", "so_file"])
        w.writeheader()
        w.writerows(rows)
    return map_path
