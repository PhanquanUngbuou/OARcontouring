# Quy ước đặt tên cấu trúc của QuanContour

1. **Có tên chuẩn TG-263** (AAPM) → dùng đúng tên TG-263. Ví dụ: `Parotid_L`, `SpinalCord`, `Glnd_Submand_R`,
   `Bone_Mandible`, `A_Aorta`, `Lung_L`, `Femur_R`.
2. **Chưa có tên TG-263** → đặt theo giải phẫu, cùng kiểu TG-263:

   ```
   <Loại mô>_<Tên giải phẫu>[_Phân loại]_<L|R>
   ```

   | Loại mô | Tiền tố | Ví dụ |
   |---|---|---|
   | Xương | `Bone_` | `Bone_Styloid_L`, `Bone_Zygoma_R`, `Bone_Rib_L3`, `Bone_Vertebra_T5`, `Bone_Hips` |
   | Cơ | `Musc_` | `Musc_Masseter_L`, `Musc_Pterygoid_Med_R`, `Musc_Gluteus_Max_L`, `Musc_Paraspinal_R` |
   | Động mạch / tĩnh mạch | `A_` / `V_` | `A_Carotid_Int_L`, `A_Iliac_R`, `V_Jugular_Int_L`, `V_Venacava_I` |
   | Tuyến | `Glnd_` | `Glnd_Thyroid`, `Glnd_Adrenal_L` |
   | Sụn | `Cartilage_` | `Cartilage_Thyroid`, `Cartilage_Cricoid` |
   | Khoang | `Cavity_` | `Cavity_Nasal_L`, `Cavity_Larynx`, `Cavity_Thoracic` |
   | Ống | `Canal_` | `Canal_Auditory_Ext_L` (ống tai ngoài) |

   - Bên: `_L` (trái bệnh nhân), `_R` (phải); số thứ tự viết liền sau bên: `Bone_Rib_L3`.
   - Phân loại viết tắt: `Ant/Mid/Post` (trước/giữa/sau), `Int/Ext` (trong/ngoài), `Max/Med/Min`, `Maj`.
   - Phân thùy gan theo Couinaud: `Liver_Seg1` … `Liver_Seg8`.
3. **Cấu trúc ghép** (nhiều nhãn hợp lại): tên số nhiều hoặc tên vùng: `Lungs`, `Kidneys`, `Bone_Ribs`, `Bone_Ribs_L`,
   `Bone_Pelvic` (xương chậu + xương cùng), `Bone_Hips` (xương chậu 2 bên, không gồm xương cùng).
4. **Phiên bản xử lý thêm** của cùng cơ quan: thêm hậu tố, giữ nguyên tên gốc phía trước:
   `Parotid_L_Ref` = tuyến mang tai trái đã hiệu chỉnh (Ref = refined), bên cạnh bản gốc `Parotid_L`.

Danh sách đầy đủ: [DANH_SACH_CO_QUAN.md](DANH_SACH_CO_QUAN.md). Khoa muốn đổi tên nào, sửa trong
`oar_contour/catalog.py` (bảng `_TG263` và `_QC`).
