# Kiểm chứng: hiệu chỉnh tuyến mang tai (thử nghiệm)

**Dữ liệu:** HaN-Seg (Podobnik et al., *Medical Physics* 2023, doi:10.1002/mp.16197), CT lập kế hoạch xạ trị đầu cổ
có contour tuyến mang tai do chuyên gia vẽ. 8 ca đầu: **ca 1–4 để chỉnh thông số**, **ca 5–8 để kiểm tra** (không dùng
khi chỉnh, thông số chọn theo ca 1–4). Chạy trên CPU, chế độ đầy đủ.

**Thuật toán:** nở contour tự động vào mô có mật độ giống tuyến, chặn bởi xương hàm, cơ cắn, cơ chân bướm trong/ngoài,
cơ hai bụng, mỏm trâm, động mạch/tĩnh mạch cảnh trong, ống tai ngoài, tuyến dưới hàm; **có hướng**: tối đa 10 mm vào
phía trong / phía trước, 8 mm lên trên–xuống dưới, nhưng chỉ ≤3 mm ra ngoài (về phía da) và ≤1 mm ra sau.

## Kết quả trên 4 ca kiểm tra (8 tuyến)

| Ca | Bên | Chuyên gia | Tự động gốc | Dice gốc → hiệu chỉnh | HD95 (mm) gốc → hiệu chỉnh |
|---|---|---|---|---|---|
| 05 | L | 28,9 cc | 8,7 cc | 0,46 → **0,70** | 16,8 → **8** |
| 05 | R | 26,5 cc | 11,3 cc | 0,54 → **0,68** | 15,1 → **7** |
| 06 | L | 34,5 cc | 17,6 cc | 0,54 → **0,69** | 15,7 → **8** |
| 06 | R | 33,6 cc | 18,1 cc | 0,62 → **0,73** | 15,7 → **8** |
| 07 | L | 21,4 cc | 9,9 cc | 0,51 → **0,55** | 14,2 → **10** |
| 07 | R | 22,3 cc | 10,9 cc | 0,56 → **0,58** | 15,0 → **12** |
| 08 | L | 28,4 cc | 13,1 cc | 0,62 → **0,80** | 17,1 → **7** |
| 08 | R | 35,9 cc | 16,0 cc | 0,61 → **0,81** | 19,5 → **9** |
| **TB** | | | | **0,56 → 0,69** | **16,1 → 8,5** |

Ca chỉnh thông số 1–4: Dice 0,56 → 0,72; HD95 15,7 → 7,2 mm.
Phiên bản trước (nở đều mọi hướng): kiểm tra Dice 0,66, HD95 10,1 mm → giới hạn hướng giúp giảm lấn ra sau/ra da.

## Nhận xét

- Model gốc chỉ vẽ khoảng **một nửa thể tích** tuyến so với chuyên gia.
- **Cả 8 tuyến kiểm tra đều tốt lên**; tốt nhất ca 08 (Dice 0,80–0,81, gần mức đồng thuận giữa chuyên gia ~0,8).
- Cải thiện ở cực trên, phần nông và một phần thùy sâu. **Phần thùy sâu chui sâu vào khoang cạnh hầu ở các lát thấp
  vẫn còn thiếu**; ca 07 cải thiện ít.
- Vẫn là **thử nghiệm**: bác sĩ so sánh `Parotid_L_Ref` với bản gốc và chỉnh trước khi dùng.
- Đã thử thêm bước "hành lang" vào thùy sâu (bao lồi cơ chân bướm – mỏm trâm – cảnh trong): làm Dice **giảm**
  (lấn vào mỡ khoang cạnh hầu) nên **không dùng**.
