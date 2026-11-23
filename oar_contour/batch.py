"""Khoanh hàng loạt: mỗi thư mục con = 1 ca (DICOM CT, có thể kèm RTSTRUCT cũ).

Kết quả ghi theo đúng định dạng của app (mỗi ca 1 thư mục có job.json, ct/, RS_AI_OAR.dcm) vào thư mục kết quả,
nên chép thư mục kết quả về máy khác (vd. MacBook, vào ~/OAR_ketqua) là mở được ngay trong QuanContour để sửa.
Chạy lại lệnh thì ca đã xong được bỏ qua (theo tên thư mục nguồn).
"""

from __future__ import annotations

import json
import shutil
import time
from pathlib import Path


def run_batch(cases_root: str | Path, results: str | Path, protocol: str, intent: str = "curative",
              fast: bool = False, segmenter_factory=None, progress=print) -> dict:
    from .app import JobManager
    from .protocols import PROTOCOL_BY_ID

    if protocol != "custom" and protocol not in PROTOCOL_BY_ID:
        raise ValueError(f"Phác đồ không hợp lệ: {protocol}. Có: {', '.join(PROTOCOL_BY_ID)}")
    if segmenter_factory is None:
        from .segment import TotalSegmentatorRunner

        def segmenter_factory(device):
            return TotalSegmentatorRunner(device=device)

    cases_root, results = Path(cases_root), Path(results)
    manager = JobManager(results, segmenter_factory, isolate=False)
    done_sources = {j.source for j in manager.jobs.values() if j.source}
    cases = sorted(p for p in cases_root.iterdir() if p.is_dir())
    summary = {"ok": 0, "skipped": 0, "failed": []}
    t_all = time.time()
    for n, case in enumerate(cases, 1):
        if case.name in done_sources:
            summary["skipped"] += 1
            progress(f"[{n}/{len(cases)}] {case.name}: đã có, bỏ qua")
            continue
        job = manager.create("auto", fast, False, "auto", protocol, intent)
        job.source = case.name
        for f in case.rglob("*"):
            if f.is_file():
                shutil.copy2(f, job.dir / "upload" / f"{f.parent.name}_{f.name}")
        t = time.time()
        manager._run(job)
        if job.status == "done":
            meta = json.loads((job.dir / "job.json").read_text(encoding="utf-8"))
            meta["source"] = case.name
            (job.dir / "job.json").write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
            summary["ok"] += 1
            progress(f"[{n}/{len(cases)}] {case.name}: xong {len(job.result['structures'])} cấu trúc "
                     f"trong {time.time() - t:.0f}s")
        else:
            summary["failed"].append(case.name)
            shutil.rmtree(job.dir, ignore_errors=True)
            progress(f"[{n}/{len(cases)}] {case.name}: LỖI {job.error}")
    summary["seconds"] = round(time.time() - t_all)
    return summary
