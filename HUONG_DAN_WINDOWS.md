# Hướng dẫn chạy trên máy Windows (khuyên dùng máy có card NVIDIA)

Máy có card NVIDIA: mỗi ca khoảng **1–3 phút** (so với 5–20 phút trên CPU / MacBook).

## 1. Tải về (1 lần)

1. Trên máy Windows, mở trình duyệt vào https://github.com/PhanquanUngbuou/OARcontouring
2. Bấm nút xanh **Code** → **Download ZIP**.
3. Chuột phải file ZIP vừa tải → **Extract All…** → giải nén ra ổ `C:\`.
4. Đổi tên thư mục vừa giải nén (`OARcontouring-main`) thành **`QuanContour`**,
   được `C:\QuanContour`.

## 2. Bấm đúp 3 file trong `C:\QuanContour` theo thứ tự

| Bước | Bấm đúp | Làm gì | Thời gian |
|---|---|---|---|
| 1 | **KIEM_TRA_MAY.bat** | Kiểm tra Windows, RAM, ổ đĩa, card NVIDIA, mạng. **Chỉ đọc, không thay đổi gì.** | 30 giây |
| 2 | **CAI_DAT.bat** | Cài Python, PyTorch, app, tạo biểu tượng **QuanContour** trên Desktop. Không cần quyền admin. | 10–20 phút |
| 3 | **QuanContour** (trên Desktop) | Mở app | – |

- Bước 1: dòng **xanh** là đạt, **vàng** là cần xem, **đỏ** là chưa đạt. Có dòng đỏ hoặc vàng thì
  chụp màn hình gửi lại để được hướng dẫn trước khi làm bước 2.
- Nếu Windows hiện **"Windows protected your PC"**: bấm **More info** → **Run anyway**
  (do file tải từ Internet, không phải virus).
- Cuối bước 2 phải thấy dòng xanh **GPU NVIDIA sẵn sàng**. Nếu thấy dòng vàng "CHƯA dùng được GPU",
  app vẫn chạy được nhưng bằng CPU; chụp màn hình gửi lại.

**Cập nhật bản mới:** bấm Thoát trong app → bấm đúp **CAP_NHAT.bat** → mở lại app.
Kết quả các ca cũ và model đã tải vẫn giữ nguyên.

## 3. Dùng app

1. Bấm đúp **QuanContour** trên Desktop. Một cửa sổ đen hiện lên (**giữ nguyên, đừng tắt**) và trình
   duyệt tự mở giao diện.
2. Thao tác giống trên Mac: **Chọn thư mục CT** → chọn vùng → **Khoanh OAR** → xem → **Tải RTSTRUCT**.
3. Ở mục **Bộ xử lý** để **Tự động**: máy sẽ dùng GPU NVIDIA. Dòng trạng thái ghi **(GPU NVIDIA)**.
4. Xong việc bấm **Thoát** trong app (cửa sổ đen tự dừng, bấm phím bất kỳ để đóng).

Kết quả lưu trong `C:\Users\<tên>\OAR_ketqua`. Model AI lưu trong `C:\Users\<tên>\.totalsegmentator`
(không xoá thư mục này).

### Máy lập kế hoạch cũ (ví dụ máy Eclipse không dùng nữa)

- Không cần gỡ phần mềm cũ: app cài riêng trong `C:\QuanContour\.venv`, không đụng tới phần mềm khác.
- Máy này thường **không nối Internet**: nhờ IT mở mạng **tạm thời** trong lúc cài đặt và lần chạy
  đầu tiên (tải model). Sau đó có thể ngắt Internet, app vẫn chạy.
- Card đồ hoạ Quadro đời cũ có thể không được PyTorch mới hỗ trợ; KIEM_TRA_MAY.bat sẽ báo.
  Khi đó app vẫn chạy bằng CPU.
- Máy cũ có thể còn dữ liệu bệnh nhân trong Eclipse: giữ nguyên mật khẩu đăng nhập, không để người
  ngoài dùng chung.

## 4. (Giai đoạn sau) Chạy tự động CT-sim → máy này → Monaco

Máy chuyên chạy model là nơi phù hợp nhất để chạy **DICOM node**: CT-sim đẩy thêm 1 bản CT sang máy
này, máy tự khoanh và gửi RTSTRUCT sang Monaco, bác sĩ không phải thao tác gì. Cần kỹ sư vật lý / IT
cấu hình CT-sim và Monaco (xem mục "Chạy tự động" trong README). Khi làm bước này, mở cổng 11112 trên
Windows Firewall **chỉ cho IP của CT-sim**.

## Lỗi thường gặp

| Lỗi | Cách xử lý |
|---|---|
| `Chua cai dat` khi mở app | Chưa chạy CAI_DAT.bat, hoặc bị lỗi giữa chừng → bấm đúp CAI_DAT.bat lại (chạy lại nhiều lần không sao) |
| Cửa sổ báo lỗi đỏ khi cài | Chụp màn hình gửi lại |
| Trình duyệt không tự mở | Mở Chrome/Edge, vào `http://127.0.0.1:8765` |
| Không tải được model / thư viện | Mạng bệnh viện chặn GitHub hoặc PyPI → nhờ IT mở, hoặc cài bằng mạng khác rồi mang máy về |
| Antivirus chặn | Cho phép thư mục `C:\QuanContour` |

## An toàn dữ liệu

- App chỉ nhận kết nối **từ chính máy này** (127.0.0.1): máy khác trong mạng không mở được giao diện.
  Người khác muốn dùng thì ngồi tại máy hoặc qua Remote Desktop.
- Ảnh CT không gửi ra Internet. Máy cần mật khẩu đăng nhập, bật BitLocker nếu có thể.
