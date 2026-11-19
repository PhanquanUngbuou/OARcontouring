# Hướng dẫn chạy trên máy Windows (khuyên dùng máy có card NVIDIA)

Máy có card NVIDIA: mỗi ca khoảng **1–3 phút** (so với 5–20 phút trên CPU / MacBook).

## 1. Lấy mã nguồn (1 lần)

Cách đơn giản nhất, không cần cài gì:

1. Mở https://github.com/PhanquanUngbuou/OARcontouring
2. Bấm nút xanh **Code** → **Download ZIP**.
3. Giải nén ra `C:\OARcontouring` (đường dẫn **không dấu, không dấu cách**).

(Nếu máy có Git: `git clone https://github.com/PhanquanUngbuou/OARcontouring.git C:\OARcontouring`,
sau này cập nhật chỉ cần `git pull`.)

## 2. Cài đặt (1 lần, 10–20 phút)

1. Mở thư mục `C:\OARcontouring\scripts`.
2. **Chuột phải** file `cai_dat_windows.ps1` → **Run with PowerShell**.
   Nếu Windows hỏi về quyền chạy script, chọn **Yes / Run once**.
3. Chờ cửa sổ chạy xong. Cuối cùng phải thấy dòng màu xanh:
   - `GPU NVIDIA sẵn sàng: NVIDIA ...` → tốt.
   - Dòng màu vàng `CHƯA dùng được GPU NVIDIA` → app vẫn chạy nhưng bằng CPU. Cập nhật driver NVIDIA
     (GeForce Experience / NVIDIA App hoặc trang nvidia.com) rồi chạy lại script.
4. Trên Desktop xuất hiện biểu tượng **QuanContour**.

Script tự cài Python 3.12 (qua công cụ `uv`), PyTorch bản hợp với card NVIDIA và thư viện của app,
**không cần quyền admin**, không ảnh hưởng phần mềm khác trên máy.

## 3. Dùng app

1. Bấm đúp **QuanContour** trên Desktop. Một cửa sổ đen hiện lên (**giữ nguyên, đừng tắt**) và trình
   duyệt tự mở giao diện.
2. Thao tác giống trên Mac: **Chọn thư mục CT** → chọn vùng → **Khoanh OAR** → xem → **Tải RTSTRUCT**.
3. Ở mục **Bộ xử lý** để **Tự động**: máy sẽ dùng GPU NVIDIA. Dòng trạng thái ghi **(GPU NVIDIA)**.
4. Xong việc bấm **Thoát** trong app (cửa sổ đen tự dừng, bấm phím bất kỳ để đóng).

Kết quả lưu trong `C:\Users\<tên>\OAR_ketqua`. Model AI lưu trong `C:\Users\<tên>\.totalsegmentator`
(không xoá thư mục này).

## 4. (Giai đoạn sau) Chạy tự động CT-sim → máy này → Monaco

Máy chuyên chạy model là nơi phù hợp nhất để chạy **DICOM node**: CT-sim đẩy thêm 1 bản CT sang máy
này, máy tự khoanh và gửi RTSTRUCT sang Monaco, bác sĩ không phải thao tác gì. Cần kỹ sư vật lý / IT
cấu hình CT-sim và Monaco (xem mục "Chạy tự động" trong README). Khi làm bước này, mở cổng 11112 trên
Windows Firewall **chỉ cho IP của CT-sim**.

## Lỗi thường gặp

| Lỗi | Cách xử lý |
|---|---|
| Bấm "Run with PowerShell" cửa sổ tắt ngay | Mở PowerShell, gõ `powershell -ExecutionPolicy Bypass -File C:\OARcontouring\scripts\cai_dat_windows.ps1` |
| `Chua cai dat` khi mở app | Chưa chạy bước 2, hoặc bước 2 lỗi giữa chừng → chạy lại |
| Trình duyệt không tự mở | Mở Chrome/Edge, vào `http://127.0.0.1:8765` |
| Không tải được model / thư viện | Mạng bệnh viện chặn GitHub hoặc PyPI → nhờ IT mở, hoặc cài bằng mạng khác rồi mang máy về |
| Antivirus chặn | Cho phép thư mục `C:\OARcontouring` |

## An toàn dữ liệu

- App chỉ nhận kết nối **từ chính máy này** (127.0.0.1): máy khác trong mạng không mở được giao diện.
  Người khác muốn dùng thì ngồi tại máy hoặc qua Remote Desktop.
- Ảnh CT không gửi ra Internet. Máy cần mật khẩu đăng nhập, bật BitLocker nếu có thể.
