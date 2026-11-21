# Kiểm chứng: hiệu chỉnh tuyến mang tai (thử nghiệm)

**Dữ liệu:** HaN-Seg (Podobnik et al., *Medical Physics* 2023, doi:10.1002/mp.16197), CT lập kế hoạch xạ trị đầu cổ
có contour tuyến mang tai do chuyên gia vẽ. Dùng 8 ca đầu: **ca 1–4 để chỉnh thông số**, **ca 5–8 để kiểm tra**
(không dùng khi chỉnh). Chạy trên CPU, chế độ đầy đủ.

**Thông số chọn:** nở tối đa 7 mm trong mặt phẳng, 6 mm theo trục đầu–chân, dải HU của tuyến ±10.

## Kết quả trên 4 ca kiểm tra (8 tuyến)

| Ca | Bên | Thể tích chuyên gia | Thể tích tự động (gốc) | Dice gốc → hiệu chỉnh | HD95 (mm) gốc → hiệu chỉnh |
|---|---|---|---|---|---|
| 05 | L | 28,9 cc | 8,7 cc | 0,46 → **0,69** | 16,8 → **8,8** |
| 05 | R | 26,5 cc | 11,3 cc | 0,54 → **0,69** | 15,1 → **7,8** |
| 06 | L | 34,5 cc | 17,6 cc | 0,54 → **0,63** | 15,7 → **10,5** |
| 06 | R | 33,6 cc | 18,1 cc | 0,62 → **0,68** | 15,7 → **9,4** |
| 07 | L | 21,4 cc | 9,9 cc | 0,51 → 0,51 | 14,2 → **10,5** |
| 07 | R | 22,3 cc | 10,9 cc | 0,56 → 0,56 | 15,0 → **11,9** |
| 08 | L | 28,4 cc | 13,1 cc | 0,62 → **0,77** | 17,1 → **10,2** |
| 08 | R | 35,9 cc | 16,0 cc | 0,61 → **0,76** | 19,5 → **11,8** |
| **TB** | | | | **0,56 → 0,66** | **16,1 → 10,1** |

(Ca chỉnh thông số 1–4: Dice 0,56 → 0,69; HD95 15,7 → 8,5 mm.)

## Nhận xét

- Model gốc chỉ vẽ khoảng **một nửa thể tích** tuyến so với chuyên gia.
- Hiệu chỉnh cải thiện ở mọi tuyến về HD95, Dice tăng ở 6/8 tuyến, không tuyến nào xấu đi.
- Cải thiện chủ yếu ở **cực trên** (các lát bị bỏ sót) và **phần nông**. **Thùy sâu (phần chui vào khoang cạnh hầu)
  vẫn thiếu nhiều**; biên ngoài đôi chỗ răng cưa.
- Dice 0,66 vẫn thấp hơn mức đồng thuận giữa các chuyên gia (thường ~0,8): **bác sĩ vẫn phải chỉnh**, đặc biệt thùy sâu.
- Hướng tiếp: (1) bước nở có định hướng vào khe sau ngành hàm – trước mỏm trâm cho thùy sâu; (2) model khoa tự huấn luyện.
