# Phác đồ OAR theo vị trí u (bản đề xuất – khoa cần duyệt)

Chỉ gồm cơ quan có trong model **miễn phí**. Trong app, bác sĩ chọn *Mục đích* + *Vị trí xạ trị*, rồi có thể **Mở rộng / chỉnh sửa**: dùng cho riêng ca đó hoặc lưu làm mặc định của khoa.

Thời gian: 1 đơn vị ≈ 1–2 phút trên MacBook chip M, vài giây trên GPU NVIDIA.

## Theo vùng

### U đầu cổ

| | OAR app tự vẽ | Model cần chạy | Thời gian |
|---|---|---|---|
| **Triệt căn** | Brain, SpinalCord, Parotid_L, Parotid_R, Glnd_Submand_L, Glnd_Submand_R, Eye_L, Eye_R, Lens_L, Lens_R, OpticNrv_L, OpticNrv_R, Bone_Mandible, Glnd_Thyroid, Esophagus, Trachea, Lung_L, Lung_R | toàn thân: nội tạng, cơ–xương; Xương hàm, xoang, răng; Tuyến nước bọt, mắt, thần kinh thị | ≈ 6.0 |
| **Triệu chứng** | Brain, SpinalCord, Parotid_L, Parotid_R, Eye_L, Eye_R, Lens_L, Lens_R, OpticNrv_L, OpticNrv_R, Esophagus, Trachea | toàn thân: nội tạng, cơ–xương; Tuyến nước bọt, mắt, thần kinh thị | ≈ 3.5 |

*Ghi chú:* Gồm vòm, khoang miệng, họng miệng, thanh quản, hạ họng, tuyến nước bọt, tuyến giáp, hạch cổ, hốc mũi – xoang, lymphoma hốc mắt / mũi xoang.

### U não

| | OAR app tự vẽ | Model cần chạy | Thời gian |
|---|---|---|---|
| **Triệt căn** | Brain, Eye_L, Eye_R, Lens_L, Lens_R, OpticNrv_L, OpticNrv_R, SpinalCord | toàn thân: cơ–xương; Tuyến nước bọt, mắt, thần kinh thị | ≈ 2.5 |
| **Triệu chứng** | Brain, Eye_L, Eye_R, Lens_L, Lens_R, OpticNrv_L, OpticNrv_R | toàn thân: cơ–xương; Tuyến nước bọt, mắt, thần kinh thị | ≈ 2.5 |

*Ghi chú:* Gồm u não nguyên phát và xạ toàn não.

### U lồng ngực (phổi, trung thất, thực quản)

| | OAR app tự vẽ | Model cần chạy | Thời gian |
|---|---|---|---|
| **Triệt căn** | Lung_L, Lung_R, Lungs, Heart, Esophagus, SpinalCord, Trachea, Liver, Kidney_L, Kidney_R | toàn thân: nội tạng, tim mạch, cơ–xương | ≈ 3 |
| **Triệu chứng** | Lungs, Heart, Esophagus, SpinalCord | toàn thân: nội tạng, tim mạch, cơ–xương | ≈ 3 |

*Ghi chú:* Lungs nên trừ GTV/ITV trong Monaco (Lungs-GTV) khi tính V20.

### U vú

| | OAR app tự vẽ | Model cần chạy | Thời gian |
|---|---|---|---|
| **Triệt căn** | Heart, Lung_L, Lung_R, Lungs, Breast_L, Breast_R, SpinalCord, Esophagus, Glnd_Thyroid, Humerus_L, Humerus_R, Liver | toàn thân: nội tạng, tim mạch, cơ–xương; Tuyến vú | ≈ 4.0 |
| **Triệu chứng** | Heart, Lungs, SpinalCord | toàn thân: nội tạng, tim mạch, cơ–xương | ≈ 3 |

*Ghi chú:* Breast_L/R là tuyến vú hai bên: bên đối diện là OAR.

### U bụng – sau phúc mạc

| | OAR app tự vẽ | Model cần chạy | Thời gian |
|---|---|---|---|
| **Triệt căn** | Liver, Gallbladder, Stomach, Duodenum, Pancreas, Spleen, Kidney_L, Kidney_R, Bowel_Small, Colon, SpinalCord, Heart, Esophagus, Lung_L, Lung_R, A_Aorta, V_Venacava_I, A_Iliac_L, A_Iliac_R, V_Iliac_L, V_Iliac_R | toàn thân: nội tạng, tim mạch, cơ–xương | ≈ 3 |
| **Triệu chứng** | Liver, Kidney_L, Kidney_R, SpinalCord, Stomach, Duodenum, Bowel_Small | toàn thân: nội tạng, cơ–xương | ≈ 2 |

*Ghi chú:* Gồm dạ dày, tuỵ, gan, đường mật, sarcoma sau phúc mạc, thận, tinh hoàn (hạch cạnh động mạch chủ).

### U tiểu khung

| | OAR app tự vẽ | Model cần chạy | Thời gian |
|---|---|---|---|
| **Triệt căn** | Bladder, Bowel_Small, Colon, Femur_L, Femur_R, Bone_Hips, A_Iliac_L, A_Iliac_R, V_Iliac_L, V_Iliac_R, A_Aorta, V_Venacava_I, Kidney_L, Kidney_R, SpinalCord, Prostate | toàn thân: nội tạng, tim mạch, cơ–xương | ≈ 3 |
| **Triệu chứng** | Bladder, Bowel_Small, Colon, Femur_L, Femur_R | toàn thân: nội tạng, cơ–xương | ≈ 2 |

*Ghi chú:* Gồm trực tràng, ống hậu môn, cổ tử cung, nội mạc, âm đạo, âm hộ, tiền liệt tuyến, bàng quang. Bone_Hips: xương chậu 2 bên (xạ tránh tủy xương).

### Di căn xương

| | OAR app tự vẽ | Model cần chạy | Thời gian |
|---|---|---|---|
| **Triệt căn** | SpinalCord, Esophagus, Heart, Lungs, Kidney_L, Kidney_R, Liver, Stomach, Bowel_Small, Colon, Bladder, Femur_L, Femur_R | toàn thân: nội tạng, tim mạch, cơ–xương | ≈ 3 |
| **Triệu chứng** | SpinalCord, Esophagus, Heart, Lungs, Kidney_L, Kidney_R, Bowel_Small, Bladder, Femur_L, Femur_R | toàn thân: nội tạng, tim mạch, cơ–xương | ≈ 3 |

*Ghi chú:* Cơ quan ngoài trường chụp tự bỏ qua.

## SBRT / SRT

### U não SRT / SRS

| | OAR app tự vẽ | Model cần chạy | Thời gian |
|---|---|---|---|
| **Triệt căn** | Brain, Eye_L, Eye_R, Lens_L, Lens_R, OpticNrv_L, OpticNrv_R | toàn thân: cơ–xương; Tuyến nước bọt, mắt, thần kinh thị | ≈ 2.5 |
| **Triệu chứng** | Brain, Eye_L, Eye_R, Lens_L, Lens_R, OpticNrv_L, OpticNrv_R | toàn thân: cơ–xương; Tuyến nước bọt, mắt, thần kinh thị | ≈ 2.5 |


### Phổi SBRT

| | OAR app tự vẽ | Model cần chạy | Thời gian |
|---|---|---|---|
| **Triệt căn** | Lung_L, Lung_R, Lungs, Heart, Esophagus, SpinalCord, Trachea, A_Aorta, V_Venacava_S, Bone_Ribs, Sternum | toàn thân: nội tạng, tim mạch, cơ–xương, xương sườn | ≈ 4 |
| **Triệu chứng** | Lung_L, Lung_R, Lungs, Heart, Esophagus, SpinalCord, Trachea, A_Aorta, V_Venacava_S, Bone_Ribs, Sternum | toàn thân: nội tạng, tim mạch, cơ–xương, xương sườn | ≈ 4 |

*Ghi chú:* Bone_Ribs/Sternum dùng tham khảo cho thành ngực.

### Gan SBRT

| | OAR app tự vẽ | Model cần chạy | Thời gian |
|---|---|---|---|
| **Triệt căn** | Liver, Gallbladder, Stomach, Duodenum, Bowel_Small, Colon, Kidney_L, Kidney_R, SpinalCord, Heart, Esophagus, Lung_L, Lung_R, Bone_Ribs | toàn thân: nội tạng, tim mạch, cơ–xương, xương sườn | ≈ 4 |
| **Triệu chứng** | Liver, Gallbladder, Stomach, Duodenum, Bowel_Small, Colon, Kidney_L, Kidney_R, SpinalCord, Heart, Esophagus, Lung_L, Lung_R, Bone_Ribs | toàn thân: nội tạng, tim mạch, cơ–xương, xương sườn | ≈ 4 |

*Ghi chú:* Liver nên trừ GTV trong Monaco (Liver-GTV). Bone_Ribs dùng tham khảo cho thành ngực.

### Cột sống SBRT

| | OAR app tự vẽ | Model cần chạy | Thời gian |
|---|---|---|---|
| **Triệt căn** | SpinalCord, Esophagus, Trachea, Heart, Lung_L, Lung_R, Lungs, Kidney_L, Kidney_R, Liver, Stomach, Bowel_Small, Colon, Bone_Vertebra_S1, Bone_Vertebra_L5, Bone_Vertebra_L4, Bone_Vertebra_L3, Bone_Vertebra_L2, Bone_Vertebra_L1, Bone_Vertebra_T12, Bone_Vertebra_T11, Bone_Vertebra_T10, Bone_Vertebra_T9, Bone_Vertebra_T8, Bone_Vertebra_T7, Bone_Vertebra_T6, Bone_Vertebra_T5, Bone_Vertebra_T4, Bone_Vertebra_T3, Bone_Vertebra_T2, Bone_Vertebra_T1, Bone_Vertebra_C7, Bone_Vertebra_C6, Bone_Vertebra_C5, Bone_Vertebra_C4, Bone_Vertebra_C3, Bone_Vertebra_C2, Bone_Vertebra_C1 | toàn thân: nội tạng, đốt sống, tim mạch, cơ–xương | ≈ 4 |
| **Triệu chứng** | SpinalCord, Esophagus, Trachea, Heart, Lung_L, Lung_R, Lungs, Kidney_L, Kidney_R, Liver, Stomach, Bowel_Small, Colon, Bone_Vertebra_S1, Bone_Vertebra_L5, Bone_Vertebra_L4, Bone_Vertebra_L3, Bone_Vertebra_L2, Bone_Vertebra_L1, Bone_Vertebra_T12, Bone_Vertebra_T11, Bone_Vertebra_T10, Bone_Vertebra_T9, Bone_Vertebra_T8, Bone_Vertebra_T7, Bone_Vertebra_T6, Bone_Vertebra_T5, Bone_Vertebra_T4, Bone_Vertebra_T3, Bone_Vertebra_T2, Bone_Vertebra_T1, Bone_Vertebra_C7, Bone_Vertebra_C6, Bone_Vertebra_C5, Bone_Vertebra_C4, Bone_Vertebra_C3, Bone_Vertebra_C2, Bone_Vertebra_C1 | toàn thân: nội tạng, đốt sống, tim mạch, cơ–xương | ≈ 4 |

*Ghi chú:* Các đốt sống giúp định vị; cơ quan ngoài trường chụp tự bỏ qua.

## Trường hợp khác

Vị trí u không có trong danh sách: chọn **Trường hợp khác – tự chọn OAR**, lấy sẵn danh sách của vùng gần nhất rồi thêm/bớt, hoặc tự tích từ đầu trong danh mục đầy đủ.
