# QuanContour — ghi chú bàn giao cho phiên Claude Code mới

Người dùng: bác sĩ xạ trị (anh Quân), giao tiếp tiếng Việt, xưng "anh – em". Trả lời ngắn gọn, tiết kiệm token.

## Sản phẩm
App khoanh OAR tự động cho khoa xạ trị (TPS Monaco), chạy cục bộ (web UI 127.0.0.1:8765, `quancontour app`).
Mac: `scripts/tao_app_mac.sh` tạo QuanContour.app; Windows 10/11: `KIEM_TRA_MAY.bat`, `CAI_DAT.bat`, `CAP_NHAT.bat`.
Model nền: TotalSegmentator (chỉ task miễn phí, Apache-2.0). **Không ghi chữ "miễn phí"/tên model trên giao diện**
(người dùng yêu cầu), nhưng giữ ghi công giấy phép ở README và hộp "Thông tin & giấy phép".

## Mã nguồn chính (`oar_contour/`)
- `protocols.py`: phác đồ theo vùng (U đầu cổ, U não, U lồng ngực, U vú, U bụng–sau phúc mạc, U tiểu khung, Di căn
  xương) + SBRT/SRT (não SRS, phổi, gan, cột sống) + "Trường hợp khác – tự chọn OAR"; `TRAINING_SETS["headneck"]`.
- `catalog.py` (231 cấu trúc, quy ước tên `docs/QUY_UOC_TEN.md`), `structures.py`, `pipeline.py` (chạy ít model nhất,
  roi_subset, cắt vùng, SpinalCanal dựng từ tủy), `segment.py`, `app.py` (server, sửa contour, duyệt, kho dữ liệu,
  xuất ẩn danh, xoá ca chưa duyệt), `web/index.html` (UI), `anonymize.py`, `batch.py`, `parotid_refine.py` (ĐÃ ẨN:
  thử trên ca thật cho kết quả xấu, chạy 2 giờ trên MacBook).
- Test: `pytest` (33 test, phantom giả). Chạy: `pip install -e ".[test]" && pytest`.

## Quyết định đã chốt
- Gộp OAR theo vùng (cơ quan đích vẫn vẽ cũng được); bỏ khung "bác sĩ vẽ thêm".
- U tiểu khung triệt căn có mạch chậu (gộp, không tách nhánh) + Bone_Hips; cổ tử cung/nội mạc thêm A_Aorta, V_Venacava_I.
- Mọi u đầu cổ triệt căn có Lens + OpticNrv; đầu cổ vẽ cả SpinalCord và SpinalCanal, mạch cảnh chung + cảnh trong.
- Bộ dữ liệu huấn luyện đầu cổ **29 cấu trúc** (`docs/BO_DU_LIEU_DAU_CO.md`): không cơ khít hầu, không giao thoa
  thị giác, Larynx gộp, có Joint_TM. Không đổi bộ này giữa chừng.
- Tuyến mang tai giữ như model gốc; cải thiện bằng huấn luyện model của khoa sau.

## Kế hoạch đang làm (HUONG_DAN_CLOUD.md)
① xuất ~60 ca u đầu cổ → ② `quancontour anonymize` trên Mac → ③ thuê GPU cloud (RunPod Secure Cloud, RTX 4090),
`scripts/cloud_setup.sh` + `scripts/cloud_batch.sh` → ④ tải `ketqua.tar.gz` về `~/OAR_ketqua`, bác sĩ sửa trong app,
"Lưu bản đã duyệt" → ⑤ "Xuất kho dữ liệu ẩn danh" (`~/QuanContour_XuatAnDanh`: ct.nii.gz + labels/*.nii.gz).
Đã thử đầu-cuối trên Linux CPU; CHƯA thử trên GPU thật.

## Việc còn lại
1. Script huấn luyện nnU-Net v2 trên cloud từ thư mục xuất ẩn danh (chọn 29 nhãn đầu cổ, nhãn không chồng lấn
   → multi-label; lưu ý SpinalCord nằm trong SpinalCanal, Lens trong Eye: cần huấn luyện tách nhóm hoặc theo vùng chồng).
2. Gắn model của khoa vào app (ưu tiên hơn model gốc cho các cơ quan có trong model khoa) + kiểm chứng trên ~10 ca giữ riêng.
3. Nhắc người dùng: xin phép viện trước khi đưa dữ liệu (dù đã ẩn danh) lên cloud/Google Drive.

## Lưu ý
- Máy người dùng: MacBook Air 8 GB (chậm, ~60 GB trống); máy Eclipse cũ chạy Windows 7 (không dùng được).
- Không commit dữ liệu bệnh nhân. Không ghi PHI vào log.
