# Khoanh hàng loạt ~50 ca trên máy cloud có GPU, sửa trên MacBook

```
① Xuất DICOM từ Monaco/PACS  →  ② Ẩn danh trên MacBook  →  ③ Thuê máy GPU, khoanh hàng loạt
→  ④ Tải kết quả về MacBook, sửa từng ca trong QuanContour  →  ⑤ Xuất kho ẩn danh (dùng để huấn luyện)
```

> **Trước khi bắt đầu:** xin phép viện (hội đồng đạo đức / phòng CNTT) cho việc xử lý ảnh **đã ẩn danh** trên cloud.
> Chốt danh sách cấu trúc + atlas sẽ vẽ thống nhất cho tất cả các ca.

## ① Xuất dữ liệu

Xuất CT mô phỏng (DICOM) của ~60 ca từ Monaco/PACS vào một thư mục, **mỗi bệnh nhân một thư mục con**, ví dụ:

```
~/DuLieu_Goc/
   BN_001/   (các file DICOM CT, có thể kèm RTSTRUCT cũ)
   BN_002/
   ...
```

## ② Ẩn danh (trên MacBook, KHÔNG đưa dữ liệu gốc lên cloud)

```bash
cd ~/OARcontouring && source .venv/bin/activate && git pull
quancontour anonymize ~/DuLieu_Goc ~/DuLieu_AnDanh
cd ~ && zip -qr DuLieu_AnDanh.zip DuLieu_AnDanh
```

- Mỗi ca thành một thư mục mã ngẫu nhiên `QC_XXXXXXXX`: xoá tên, mã bệnh nhân, ngày sinh, ngày giờ chụp, nơi chụp,
  bác sĩ, kỹ thuật viên…; UID được thay nhất quán (RTSTRUCT cũ vẫn khớp ảnh).
- **Bảng đối chiếu** mã ca ↔ thư mục gốc ở `~/QuanContour_maps/` — **giữ trên máy này, không đưa lên cloud**.
- Nếu ca có kèm RTSTRUCT cũ (contour bác sĩ đã vẽ trước đây), file đó cũng được ẩn danh và vẫn khớp ảnh;
  bước khoanh hàng loạt hiện chỉ dùng ảnh CT (RTSTRUCT cũ chưa được dùng).
- ~50 ca khoảng 5–8 GB. Nếu mạng chậm, chia thành vài file zip nhỏ (ví dụ mỗi file 10 ca).

## ③ Thuê máy GPU và khoanh hàng loạt

Ví dụ với RunPod (tên nút trên web có thể khác một chút; nhà cung cấp trong nước làm tương tự):

1. Tạo tài khoản, nạp khoảng 20 USD.
2. **Deploy GPU Pod** → chọn **Secure Cloud** (máy trong trung tâm dữ liệu, *không* chọn Community) → GPU
   **RTX 4090** (hoặc L40S/A100) → mẫu **PyTorch** → ổ **Volume ~60 GB** (`/workspace`) → Deploy.
3. Khi máy chạy: **Connect** → **Jupyter Lab** → mở **Terminal**, dán:

   ```bash
   cd /workspace
   curl -sO https://raw.githubusercontent.com/PhanquanUngbuou/OARcontouring/main/scripts/cloud_setup.sh
   bash cloud_setup.sh
   ```
   (~10–15 phút; cuối cùng phải thấy dòng `GPU sẵn sàng: NVIDIA ...`).
4. Kéo thả file `DuLieu_AnDanh.zip` vào khung file bên trái của Jupyter (thư mục `/workspace`), rồi:

   ```bash
   cd /workspace && unzip -q DuLieu_AnDanh.zip
   nohup bash OARcontouring/scripts/cloud_batch.sh /workspace/DuLieu_AnDanh headneck > log.txt 2>&1 &
   tail -f log.txt
   ```
   - Mỗi ca ~3–5 phút; 50 ca ~3–4 giờ. Có thể đóng trình duyệt, máy vẫn chạy; mở lại Terminal và
     `tail -f /workspace/log.txt` để xem tiếp. Nếu bị dừng giữa chừng, chạy lại đúng lệnh trên: ca đã xong tự bỏ qua.
   - Phác đồ khác: thay `headneck` bằng `brain`, `thorax`, `breast`, `abdomen`, `pelvis`…

## ④ Tải kết quả về MacBook

1. Khi log báo `Xong`, trong Jupyter chuột phải `ketqua.tar.gz` → **Download**.
2. **Xoá dữ liệu trên máy thuê và tắt máy** (tránh tốn tiền, tránh để dữ liệu trên cloud):

   ```bash
   rm -rf /workspace/DuLieu_AnDanh* /workspace/ketqua*
   ```
   rồi trên web RunPod: **Stop** → **Terminate** pod (xoá cả Volume).
3. Trên MacBook (Terminal):

   ```bash
   mkdir -p ~/OAR_ketqua /tmp/qc && tar xzf ~/Downloads/ketqua.tar.gz -C /tmp/qc && cp -R /tmp/qc/ketqua/ ~/OAR_ketqua/
   ```
4. Mở lại QuanContour → 50 ca nằm trong **Ca gần đây** (đã khoanh sẵn, mở không phải chạy lại model).
5. Sửa từng ca → **Lưu bản đã duyệt** (xem phần "Sửa contour" trong HUONG_DAN_MAC.md). Vẽ thống nhất cùng một atlas;
   vẽ thêm các cơ quan cần dạy model (Brainstem, OpticChiasm, Cochlea…) bằng **+ Thêm cấu trúc**.

## ⑤ Sau khi sửa xong

Thẻ **Kho dữ liệu huấn luyện** → **Xuất kho dữ liệu ẩn danh** → thư mục `~/QuanContour_XuatAnDanh` dùng cho bước
huấn luyện (hướng dẫn huấn luyện sẽ bổ sung).

## Chi phí ước tính

| Việc | Máy | Thời gian | Chi phí |
|---|---|---|---|
| Khoanh 50 ca | RTX 4090 (~0,4–0,7 USD/giờ) | ~4–5 giờ (kể cả cài đặt, tải lên) | ~2–4 USD |
| Lưu trữ Volume khi máy dừng | | | tính theo ngày → nhớ Terminate |
