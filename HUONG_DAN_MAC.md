# Hướng dẫn chạy trên MacBook

Áp dụng cho MacBook chip Apple (M1–M4) hoặc chip Intel, macOS 12 trở lên.
Model chạy bằng CPU của Mac. Ảnh CT mẫu mất khoảng 1–3 phút, ca thật 5–20 phút tuỳ vùng.

## 1. Cài công cụ (làm 1 lần, khoảng 15 phút)

Mở **Terminal** (Cmd + Space, gõ "Terminal"), dán **nguyên khối** dưới đây rồi Enter.
Không cần cài Python trước: công cụ `uv` tự cài Python 3.12, không cần mật khẩu máy.

```bash
cd ~
git clone https://github.com/PhanquanUngbuou/OARcontouring.git
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
cd ~/OARcontouring
uv venv --python 3.12
source .venv/bin/activate
uv pip install -e ".[model]"
```

- Nếu `git clone` báo đã có thư mục `OARcontouring` thì bỏ qua, chạy tiếp các dòng sau.
- Nếu Mac hỏi cài "command line developer tools" khi chạy `git`, bấm **Install** rồi chạy lại khối lệnh.
- Bước `uv pip install` tải khoảng 1–2 GB (PyTorch), cần mạng ổn định.

**Mỗi lần mở Terminal mới** để dùng công cụ, chạy trước:

```bash
cd ~/OARcontouring && source .venv/bin/activate
```

## 2. Chạy thử với ảnh CT mẫu (không cần dữ liệu bệnh nhân)

```bash
cd ~/OARcontouring
source .venv/bin/activate
oar-contour demo
open demo/preview.png
```

Lệnh `demo` tải ảnh CT mẫu công khai (bụng–chậu), khoanh 15 cơ quan và mở ảnh kết quả.
Lần đầu sẽ tải thêm model khoảng 135 MB. Thêm `--fast` nếu muốn nhanh hơn (kém chính xác hơn).

## 3. Chạy với một ca của khoa

1. Từ Monaco hoặc PACS, export **1 series CT mô phỏng** (DICOM) vào một thư mục, ví dụ
   `~/OAR_test/ca01/ct`. Nên dùng ca cũ đã ẩn danh. Thư mục chỉ chứa đúng 1 series.
2. Chạy (đổi `--site`: `thorax`, `abdomen`, `pelvis`, `headneck`, hoặc bỏ đi để tự nhận diện):

```bash
cd ~/OARcontouring && source .venv/bin/activate
oar-contour run ~/OAR_test/ca01/ct --site thorax \
  -o ~/OAR_test/ca01/RS_AI.dcm --preview ~/OAR_test/ca01/preview.png
open ~/OAR_test/ca01/preview.png
```

## 4. Xem contour chi tiết bằng 3D Slicer (miễn phí)

Ảnh `preview.png` chỉ để xem nhanh 5 lát cắt. Muốn cuộn từng lát và xem 3D:

1. Tải **3D Slicer** bản Stable tại https://download.slicer.org (chọn macOS), kéo vào Applications.
   Lần đầu mở nếu macOS chặn: chuột phải vào Slicer → Open.
2. Trong Slicer: **View → Extensions Manager** → tìm **SlicerRT** → Install → khởi động lại Slicer.
3. Kéo **cả thư mục ca** (gồm `ct/` và `RS_AI.dcm`) vào cửa sổ Slicer → chọn
   "Load directory into DICOM database" → OK.
4. Mở **DICOM** (biểu tượng trên thanh công cụ) → chọn bệnh nhân → tích cả CT và RTSTRUCT → **Load**.
5. Contour hiện màu trên 3 mặt cắt. Cuộn chuột để chuyển lát. Mở module **Data** để bật/tắt từng
   cơ quan. Bấm biểu tượng mắt ở dòng segmentation, chọn "Show 3D" để xem 3D.

## 5. Cập nhật bản mới

```bash
cd ~/OARcontouring && git pull && source .venv/bin/activate && uv pip install -e ".[model]"
```

## Lỗi thường gặp

| Lỗi | Cách xử lý |
|---|---|
| `command not found: oar-contour` | Chưa kích hoạt môi trường: `cd ~/OARcontouring && source .venv/bin/activate` |
| `command not found: uv` | Chạy `source $HOME/.local/bin/env` hoặc mở lại Terminal |
| `Thư mục cần chứa đúng 1 series CT` | Thư mục export có nhiều series (CT + scout + ...). Giữ lại series CT mô phỏng |
| Chạy rất lâu, máy nóng | Bình thường khi chạy CPU. Thử `--fast`, hoặc chỉ định `--site` thay vì để tự nhận diện |
| Không tải được model | Kiểm tra mạng (một số mạng bệnh viện chặn GitHub). Thử lại bằng mạng khác |

## An toàn dữ liệu

- Ảnh CT chỉ được xử lý **trên chính máy Mac này**; công cụ không gửi ảnh đi đâu và đã tắt
  chức năng gửi thống kê của TotalSegmentator.
- Laptop có dữ liệu bệnh nhân cần đặt mật khẩu, bật **FileVault** (System Settings → Privacy & Security)
  và xoá ca sau khi thử xong.
- Contour là **bản nháp nghiên cứu**, không dùng trực tiếp cho lập kế hoạch khi chưa có bác sĩ duyệt.
