# Bộ cấu trúc chuẩn – kho dữ liệu huấn luyện u đầu cổ (khoa đã chốt, 29 cấu trúc)

Căn cứ: đồng thuận quốc tế OAR đầu cổ trên CT (Brouwer et al., *Radiother Oncol* 2015); ung thư vòm tham khảo thêm
Sun et al., *Radiother Oncol* 2014. Lựa chọn của khoa: **cả tủy sống và ống sống**, **thanh quản gộp một cấu trúc**,
**không vẽ cơ khít hầu**, **không vẽ giao thoa thị giác**, nhóm tuỳ chọn chỉ lấy **khớp thái dương hàm**, mạch cảnh do app vẽ nháp.

> **Quy tắc:** vẽ ĐỦ 29 cấu trúc ở MỌI ca (nếu nằm trong trường chụp), cùng một cách vẽ. Ca thiếu cấu trúc làm model
> học sai. App hiện "Bộ dữ liệu đầu cổ: x/29" và nhắc khi lưu bản duyệt còn thiếu.

| # | Cấu trúc | App vẽ nháp | Ghi chú vẽ |
|---|---|---|---|
| 1 | Brainstem | – (vẽ mới) | |
| 2 | SpinalCord | ✓ | Tủy thật |
| 3 | SpinalCanal | ✓ (dựng từ tủy) | Kiểm tra lỗ liên hợp, đĩa đệm |
| 5–6 | OpticNrv_L / _R | ✓ | |
| 7–8 | Eye_L / _R | ✓ | Cả nhãn cầu |
| 9–10 | Lens_L / _R | ✓ | |
| 11–12 | Cochlea_L / _R | – | Cửa sổ xương |
| 13–14 | Lobe_Temporal_L / _R | – | |
| 15 | Pituitary | – | |
| 16–17 | Parotid_L / _R | ✓ | **Vẽ đủ thùy sâu** |
| 18–19 | Glnd_Submand_L / _R | ✓ | |
| 20 | Bone_Mandible | ✓ | |
| 21 | Cavity_Oral | – | Khoang miệng mở rộng (Brouwer) |
| 22 | Larynx | – | Gộp thượng thanh môn + thanh môn |
| 23 | Esophagus | ✓ | Đoạn cổ |
| 24 | Glnd_Thyroid | ✓ | |
| 25–26 | Joint_TM_L / _R | – | Khớp thái dương hàm |
| 27–28 | A_Carotid_L / _R | ✓ | Động mạch cảnh chung |
| 29–30 | A_Carotid_Int_L / _R | ✓ | Động mạch cảnh trong |

App vẽ nháp 19 cấu trúc; **bác sĩ vẽ mới 10 cấu trúc** (bấm tên trong khung "Còn thiếu" hoặc **+ Thêm cấu trúc** để
chọn đúng tên chuẩn, không gõ tay). Muốn đổi bộ này: sửa `TRAINING_SETS` trong `oar_contour/protocols.py` *trước khi*
bắt đầu vẽ, không đổi giữa chừng.
