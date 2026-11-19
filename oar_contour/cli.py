"""Dòng lệnh: oar-contour {run,evaluate,serve,structures}."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from . import structures as st


def _segmenter(args):
    from .segment import TotalSegmentatorRunner

    return TotalSegmentatorRunner(device=args.device or _default_device(), fast=args.fast)


def cmd_structures(args) -> int:
    for site, items in st.SITES.items():
        print(f"\n[{site}]")
        for s in items:
            print(f"  {s.name:<16} <- {s.task}: {' + '.join(s.labels)}" + (f" ({s.side})" if s.side else ""))
        print("  Bác sĩ tự vẽ: " + ", ".join(st.NOT_COVERED[site]))
    return 0


def cmd_run(args) -> int:
    from .pipeline import run_pipeline

    report = run_pipeline(args.dicom, args.out, _segmenter(args), site=args.site)
    print(report.summary())
    print(f"\nĐã ghi RTSTRUCT: {args.out}")
    if args.preview:
        from .preview import render_preview

        print(f"Ảnh xem nhanh: {render_preview(args.dicom, args.out, args.preview)}")
    if args.send:
        from .dicom_node import Destination, send_rtstruct

        host, port, aet = _parse_dest(args.send)
        send_rtstruct(Path(args.out), Destination(host, port, aet), args.ae_title)
        print(f"Đã gửi tới {aet}@{host}:{port}")
    return 0


def cmd_preview(args) -> int:
    from .preview import render_preview

    print(f"Ảnh xem nhanh: {render_preview(args.dicom, args.rtstruct, args.out)}")
    return 0


def cmd_demo(args) -> int:
    from .demo import download_sample, nifti_to_dicom_series
    from .pipeline import run_pipeline
    from .preview import render_preview

    work = Path(args.dir)
    nifti = download_sample(work / "example_ct.nii.gz")
    ct = nifti_to_dicom_series(nifti, work / "ct")
    out = work / "RS_AI_OAR.dcm"
    print("Đang khoanh cơ quan (lần đầu sẽ tải model ~135 MB)...")
    report = run_pipeline(ct, out, _segmenter(args), site=args.site)
    print(report.summary())
    png = render_preview(ct, out, work / "preview.png")
    print(f"\nXong. CT DICOM: {ct}\nRTSTRUCT: {out}\nẢnh xem nhanh: {png}")
    return 0


def cmd_app(args) -> int:
    from .app import serve

    serve(Path(args.results).expanduser(), port=args.port, open_browser=not args.no_browser)
    return 0


def cmd_evaluate(args) -> int:
    from .evaluate import compare_rtstructs, summarize, write_csv

    aliases = json.loads(Path(args.aliases).read_text(encoding="utf-8")) if args.aliases else None
    rows = []
    # Mỗi ca là 1 thư mục con gồm: ct/ (series CT), ai.dcm, ref.dcm
    cases = sorted(p for p in Path(args.cases).iterdir() if p.is_dir())
    for case in cases:
        try:
            metrics = compare_rtstructs(case / "ct", case / "ai.dcm", case / "ref.dcm", aliases)
        except Exception as e:  # một ca lỗi không làm hỏng cả đợt
            print(f"[bỏ qua] {case.name}: {e}", file=sys.stderr)
            continue
        rows += [(case.name, m) for m in metrics]
    write_csv(rows, args.csv)
    print(summarize(rows))
    print(f"\nChi tiết từng ca: {args.csv}")
    return 0


def cmd_serve(args) -> int:
    from .dicom_node import Destination, NodeConfig, OarNode

    ae_site = dict(x.split("=", 1) for x in args.ae_site)
    for site in ae_site.values():
        if site != "auto":
            st.structures_for(site.split(","))
    cfg = NodeConfig(
        ae_title=args.ae_title, port=args.port, work_dir=Path(args.work_dir),
        settle_seconds=args.settle, ae_site=ae_site, default_site=args.site,
        forward=Destination(*_parse_dest(args.send)) if args.send else None,
        keep_images=args.keep_images,
    )
    OarNode(cfg, _segmenter(args)).start(block=True)
    return 0


def _default_device() -> str:
    from .segment import pick_device

    return pick_device()


def _parse_dest(text: str) -> tuple[str, int, str]:
    """AE@host:port -> (host, port, AE)."""
    aet, _, hostport = text.partition("@")
    host, _, port = hostport.rpartition(":")
    if not (aet and host and port.isdigit()):
        raise SystemExit(f"Đích không hợp lệ: {text!r}, cần dạng AE_TITLE@host:port")
    return host, int(port), aet


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="quancontour", description="QuanContour: tự động khoanh OAR")
    p.add_argument("-v", "--verbose", action="store_true")
    sub = p.add_subparsers(dest="cmd", required=True)

    def model_opts(sp):
        sp.add_argument("--device", default=None, help="gpu | mps (chip đồ hoạ Mac) | cpu; bỏ trống = tự chọn")
        sp.add_argument("--fast", action="store_true", help="model 3mm cho task total (nhanh, kém chính xác hơn)")
        sp.add_argument("--site", default="auto",
                        help="auto | thorax | abdomen | pelvis | headneck (nhiều vùng: thorax,abdomen)")

    sp = sub.add_parser("structures", help="liệt kê cấu trúc theo vùng")
    sp.set_defaults(func=cmd_structures)

    sp = sub.add_parser("run", help="khoanh 1 series CT, ghi RTSTRUCT")
    sp.add_argument("dicom", help="thư mục chứa đúng 1 series CT")
    sp.add_argument("-o", "--out", default="RS_AI_OAR.dcm")
    sp.add_argument("--send", help="gửi RTSTRUCT tới AE@host:port (ví dụ Monaco)")
    sp.add_argument("--ae-title", default="OAR_AI")
    sp.add_argument("--preview", metavar="PNG", help="xuất thêm ảnh PNG chồng contour để xem nhanh")
    model_opts(sp)
    sp.set_defaults(func=cmd_run)

    sp = sub.add_parser("preview", help="xuất ảnh PNG chồng contour từ CT + RTSTRUCT")
    sp.add_argument("dicom", help="thư mục series CT")
    sp.add_argument("rtstruct", help="file RTSTRUCT")
    sp.add_argument("-o", "--out", default="preview.png")
    sp.set_defaults(func=cmd_preview)

    sp = sub.add_parser("demo", help="chạy thử với ảnh CT mẫu công khai (không cần dữ liệu bệnh nhân)")
    sp.add_argument("--dir", default="demo", help="thư mục chứa kết quả demo")
    model_opts(sp)
    sp.set_defaults(func=cmd_demo)

    sp = sub.add_parser("app", help="mở giao diện app trên trình duyệt (chạy cục bộ)")
    sp.add_argument("--port", type=int, default=8765)
    sp.add_argument("--results", default="~/OAR_ketqua", help="thư mục lưu kết quả các ca")
    sp.add_argument("--no-browser", action="store_true", help="không tự mở trình duyệt")
    sp.set_defaults(func=cmd_app)

    sp = sub.add_parser("evaluate", help="so sánh contour AI với contour bác sĩ trên nhiều ca")
    sp.add_argument("cases", help="thư mục, mỗi ca 1 thư mục con: ct/, ai.dcm, ref.dcm")
    sp.add_argument("--aliases", help="JSON đổi tên cấu trúc của khoa -> TG-263")
    sp.add_argument("--csv", default="evaluation.csv")
    sp.set_defaults(func=cmd_evaluate)

    sp = sub.add_parser("serve", help="chạy DICOM node nhận CT từ CT-sim")
    sp.add_argument("--port", type=int, default=11112)
    sp.add_argument("--ae-title", default="OAR_AI")
    sp.add_argument("--ae-site", action="append", default=[],
                    help="AE title được gọi = vùng, ví dụ OAR_HN=headneck (lặp lại được)")
    sp.add_argument("--work-dir", default="./oar_work")
    sp.add_argument("--settle", type=float, default=60, help="giây chờ không có lát mới thì coi là đủ series")
    sp.add_argument("--send", help="gửi RTSTRUCT tới AE@host:port (Monaco)")
    sp.add_argument("--keep-images", action="store_true", help="giữ lại CT sau khi xử lý (mặc định xoá)")
    model_opts(sp)
    sp.set_defaults(func=cmd_serve)
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")
    logging.getLogger("pydicom").setLevel(logging.ERROR)  # cảnh báo deprecation từ rt_utils
    logging.getLogger("matplotlib").setLevel(logging.WARNING)  # thông báo font lần đầu
    return args.func(args)
