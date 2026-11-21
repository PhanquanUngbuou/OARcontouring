# Danh sách cơ quan QuanContour khoanh được

Tổng cộng **229 cấu trúc** từ các model **miễn phí** của TotalSegmentator (CT). Trong app: **Chọn cơ quan…** để tích/bỏ cho từng vùng; lựa chọn được lưu lại.

## Thời gian chạy

Model **toàn thân** gồm 5 phần. App chỉ chạy phần chứa cơ quan đã chọn, nên chọn thêm cơ quan **cùng phần** gần như không tốn thêm thời gian. Các model riêng chỉ chạy trên đoạn ảnh có vùng đó.

| Model | Chứa | Chi phí (đơn vị) |
|---|---|---|
| Toàn thân – phần nội tạng | 24 nhãn | 1 |
| Toàn thân – phần đốt sống | 26 nhãn | 1 |
| Toàn thân – phần tim mạch | 18 nhãn | 1 |
| Toàn thân – phần cơ – xương | 23 nhãn | 1 |
| Toàn thân – phần xương sườn | 26 nhãn | 1 |
| Tuyến nước bọt, mắt, thần kinh thị (`head_glands_cavities`) | 19 cấu trúc | 1.5 |
| Xương hàm, xoang, răng (`craniofacial_structures`) | 6 cấu trúc | 2.5 |
| Sụn thanh quản, xương móng, mạch cổ (`headneck_bones_vessels`) | 12 cấu trúc | 1.5 |
| Cơ vùng đầu (nhai, lưỡi) (`head_muscles`) | 11 cấu trúc | 1.5 |
| Cơ vùng cổ, cơ khít hầu (thử nghiệm) (`headneck_muscles`) | 23 cấu trúc | 3.0 |
| Tuyến vú (`breasts`) | 2 cấu trúc | 1.0 |
| Cơ thành ngực – bụng (`abdominal_muscles`) | 20 cấu trúc | 4.0 |
| Khoang ngực, khoang bụng, màng tim (`trunk_cavities`) | 4 cấu trúc | 1.0 |
| Phân thùy gan (`liver_segments`) | 8 cấu trúc | 1.5 |

1 đơn vị ≈ 1–2 phút trên MacBook chip M, khoảng 1 phút trên CPU mạnh, vài giây trên GPU NVIDIA. Chế độ nhanh nhanh hơn nhiều nhưng kém chính xác.

## Danh sách theo nhóm

Cột **Mặc định** = vùng mà cơ quan được tích sẵn.

### Hô hấp (10)

| Tên | Model | Mặc định |
|---|---|---|
| Lung_L | toàn thân – nội tạng | Ngực / vú, Bụng |
| Lung_R | toàn thân – nội tạng | Ngực / vú, Bụng |
| Lungs | toàn thân – nội tạng | Ngực / vú |
| Trachea | toàn thân – nội tạng | Ngực / vú, Đầu cổ |
| Lung_LUL | toàn thân – nội tạng |  |
| Lung_LLL | toàn thân – nội tạng |  |
| Lung_RUL | toàn thân – nội tạng |  |
| Lung_RML | toàn thân – nội tạng |  |
| Lung_RLL | toàn thân – nội tạng |  |
| Cavity_Larynx | Sụn thanh quản, xương móng, mạch cổ |  |

### Tim mạch (22)

| Tên | Model | Mặc định |
|---|---|---|
| Heart | toàn thân – tim mạch | Ngực / vú, Bụng |
| A_Aorta | toàn thân – tim mạch | Ngực / vú |
| A_Iliac_L | toàn thân – tim mạch |  |
| A_Iliac_R | toàn thân – tim mạch |  |
| V_Iliac_L | toàn thân – tim mạch |  |
| V_Iliac_R | toàn thân – tim mạch |  |
| V_Venacava_I | toàn thân – tim mạch |  |
| V_Pulmonary | toàn thân – tim mạch |  |
| A_Brachiocephls | toàn thân – tim mạch |  |
| A_Subclavian_R | toàn thân – tim mạch |  |
| A_Subclavian_L | toàn thân – tim mạch |  |
| A_Carotid_R | toàn thân – tim mạch |  |
| A_Carotid_L | toàn thân – tim mạch |  |
| V_Brachioceph_L | toàn thân – tim mạch |  |
| V_Brachioceph_R | toàn thân – tim mạch |  |
| Atrium_Appendage_L | toàn thân – tim mạch |  |
| V_Venacava_S | toàn thân – tim mạch |  |
| V_Portal_Splenic | toàn thân – tim mạch |  |
| A_Carotid_Int_R | Sụn thanh quản, xương móng, mạch cổ |  |
| A_Carotid_Int_L | Sụn thanh quản, xương móng, mạch cổ |  |
| V_Jugular_Int_R | Sụn thanh quản, xương móng, mạch cổ |  |
| V_Jugular_Int_L | Sụn thanh quản, xương móng, mạch cổ |  |

### Tiêu hoá (9)

| Tên | Model | Mặc định |
|---|---|---|
| Esophagus | toàn thân – nội tạng | Ngực / vú, Bụng, Đầu cổ |
| Liver | toàn thân – nội tạng | Ngực / vú, Bụng |
| Stomach | toàn thân – nội tạng | Ngực / vú, Bụng |
| Duodenum | toàn thân – nội tạng | Bụng |
| Bowel_Small | toàn thân – nội tạng | Bụng, Tiểu khung |
| Colon | toàn thân – nội tạng | Bụng, Tiểu khung |
| Pancreas | toàn thân – nội tạng | Bụng |
| Spleen | toàn thân – nội tạng | Bụng |
| Gallbladder | toàn thân – nội tạng | Bụng |

### Tiết niệu – sinh dục (7)

| Tên | Model | Mặc định |
|---|---|---|
| Kidney_L | toàn thân – nội tạng | Ngực / vú, Bụng, Tiểu khung |
| Kidney_R | toàn thân – nội tạng | Ngực / vú, Bụng, Tiểu khung |
| Bladder | toàn thân – nội tạng | Tiểu khung |
| Prostate | toàn thân – nội tạng | Tiểu khung |
| Kidneys | toàn thân – nội tạng |  |
| Glnd_Adrenal_R | toàn thân – nội tạng |  |
| Glnd_Adrenal_L | toàn thân – nội tạng |  |

### Thần kinh (4)

| Tên | Model | Mặc định |
|---|---|---|
| SpinalCord | toàn thân – cơ – xương | Ngực / vú, Bụng, Tiểu khung, Đầu cổ |
| Brain | toàn thân – cơ – xương | Đầu cổ |
| OpticNrv_L | Tuyến nước bọt, mắt, thần kinh thị | Đầu cổ |
| OpticNrv_R | Tuyến nước bọt, mắt, thần kinh thị | Đầu cổ |

### Đầu cổ: tuyến, mắt (9)

| Tên | Model | Mặc định |
|---|---|---|
| Parotid_L | Tuyến nước bọt, mắt, thần kinh thị | Đầu cổ |
| Parotid_R | Tuyến nước bọt, mắt, thần kinh thị | Đầu cổ |
| Glnd_Submand_L | Tuyến nước bọt, mắt, thần kinh thị | Đầu cổ |
| Glnd_Submand_R | Tuyến nước bọt, mắt, thần kinh thị | Đầu cổ |
| Eye_L | Tuyến nước bọt, mắt, thần kinh thị | Đầu cổ |
| Eye_R | Tuyến nước bọt, mắt, thần kinh thị | Đầu cổ |
| Lens_L | Tuyến nước bọt, mắt, thần kinh thị | Đầu cổ |
| Lens_R | Tuyến nước bọt, mắt, thần kinh thị | Đầu cổ |
| Glnd_Thyroid | toàn thân – nội tạng | Ngực / vú, Đầu cổ |

### Đầu cổ: khác (22)

| Tên | Model | Mặc định |
|---|---|---|
| Cartilage_Costal | toàn thân – xương sườn |  |
| Nasopharynx | Tuyến nước bọt, mắt, thần kinh thị |  |
| Oropharynx | Tuyến nước bọt, mắt, thần kinh thị |  |
| Hypopharynx | Tuyến nước bọt, mắt, thần kinh thị |  |
| Cavity_Nasal_R | Tuyến nước bọt, mắt, thần kinh thị |  |
| Cavity_Nasal_L | Tuyến nước bọt, mắt, thần kinh thị |  |
| Canal_Auditory_Ext_R | Tuyến nước bọt, mắt, thần kinh thị |  |
| Canal_Auditory_Ext_L | Tuyến nước bọt, mắt, thần kinh thị |  |
| Palate_Soft | Tuyến nước bọt, mắt, thần kinh thị |  |
| Palate_Hard | Tuyến nước bọt, mắt, thần kinh thị |  |
| Teeth_Lower | Xương hàm, xoang, răng |  |
| Head | Xương hàm, xoang, răng |  |
| Sinus_Maxillary | Xương hàm, xoang, răng |  |
| Sinus_Frontal | Xương hàm, xoang, răng |  |
| Teeth_Upper | Xương hàm, xoang, răng |  |
| Cartilage_Thyroid | Sụn thanh quản, xương móng, mạch cổ |  |
| Bone_Hyoid | Sụn thanh quản, xương móng, mạch cổ |  |
| Cartilage_Cricoid | Sụn thanh quản, xương móng, mạch cổ |  |
| Bone_Zygoma_R | Sụn thanh quản, xương móng, mạch cổ |  |
| Bone_Zygoma_L | Sụn thanh quản, xương móng, mạch cổ |  |
| Bone_Styloid_R | Sụn thanh quản, xương móng, mạch cổ |  |
| Bone_Styloid_L | Sụn thanh quản, xương móng, mạch cổ |  |

### Vú (2)

| Tên | Model | Mặc định |
|---|---|---|
| Breast_L | Tuyến vú | Ngực / vú |
| Breast_R | Tuyến vú | Ngực / vú |

### Xương (68)

| Tên | Model | Mặc định |
|---|---|---|
| Femur_L | toàn thân – cơ – xương | Tiểu khung |
| Femur_R | toàn thân – cơ – xương | Tiểu khung |
| Bone_Pelvic | toàn thân – cơ – xương, đốt sống | Tiểu khung |
| Bone_Hips | toàn thân – cơ – xương |  |
| Bone_Mandible | Xương hàm, xoang, răng | Đầu cổ |
| Bone_Ribs_L | toàn thân – xương sườn |  |
| Bone_Ribs_R | toàn thân – xương sườn |  |
| Bone_Ribs | toàn thân – xương sườn | Ngực / vú |
| Sacrum | toàn thân – đốt sống | Tiểu khung |
| Bone_Vertebra_S1 | toàn thân – đốt sống |  |
| Bone_Vertebra_L5 | toàn thân – đốt sống |  |
| Bone_Vertebra_L4 | toàn thân – đốt sống |  |
| Bone_Vertebra_L3 | toàn thân – đốt sống |  |
| Bone_Vertebra_L2 | toàn thân – đốt sống |  |
| Bone_Vertebra_L1 | toàn thân – đốt sống |  |
| Bone_Vertebra_T12 | toàn thân – đốt sống |  |
| Bone_Vertebra_T11 | toàn thân – đốt sống |  |
| Bone_Vertebra_T10 | toàn thân – đốt sống |  |
| Bone_Vertebra_T9 | toàn thân – đốt sống |  |
| Bone_Vertebra_T8 | toàn thân – đốt sống |  |
| Bone_Vertebra_T7 | toàn thân – đốt sống |  |
| Bone_Vertebra_T6 | toàn thân – đốt sống |  |
| Bone_Vertebra_T5 | toàn thân – đốt sống |  |
| Bone_Vertebra_T4 | toàn thân – đốt sống |  |
| Bone_Vertebra_T3 | toàn thân – đốt sống |  |
| Bone_Vertebra_T2 | toàn thân – đốt sống |  |
| Bone_Vertebra_T1 | toàn thân – đốt sống |  |
| Bone_Vertebra_C7 | toàn thân – đốt sống |  |
| Bone_Vertebra_C6 | toàn thân – đốt sống |  |
| Bone_Vertebra_C5 | toàn thân – đốt sống |  |
| Bone_Vertebra_C4 | toàn thân – đốt sống |  |
| Bone_Vertebra_C3 | toàn thân – đốt sống |  |
| Bone_Vertebra_C2 | toàn thân – đốt sống |  |
| Bone_Vertebra_C1 | toàn thân – đốt sống |  |
| Humerus_L | toàn thân – cơ – xương | Ngực / vú |
| Humerus_R | toàn thân – cơ – xương | Ngực / vú |
| Scapula_L | toàn thân – cơ – xương |  |
| Scapula_R | toàn thân – cơ – xương |  |
| Clavicle_L | toàn thân – cơ – xương |  |
| Clavicle_R | toàn thân – cơ – xương |  |
| Bone_Hip_L | toàn thân – cơ – xương |  |
| Bone_Hip_R | toàn thân – cơ – xương |  |
| Bone_Skull | toàn thân – cơ – xương |  |
| Bone_Rib_L1 | toàn thân – xương sườn |  |
| Bone_Rib_L2 | toàn thân – xương sườn |  |
| Bone_Rib_L3 | toàn thân – xương sườn |  |
| Bone_Rib_L4 | toàn thân – xương sườn |  |
| Bone_Rib_L5 | toàn thân – xương sườn |  |
| Bone_Rib_L6 | toàn thân – xương sườn |  |
| Bone_Rib_L7 | toàn thân – xương sườn |  |
| Bone_Rib_L8 | toàn thân – xương sườn |  |
| Bone_Rib_L9 | toàn thân – xương sườn |  |
| Bone_Rib_L10 | toàn thân – xương sườn |  |
| Bone_Rib_L11 | toàn thân – xương sườn |  |
| Bone_Rib_L12 | toàn thân – xương sườn |  |
| Bone_Rib_R1 | toàn thân – xương sườn |  |
| Bone_Rib_R2 | toàn thân – xương sườn |  |
| Bone_Rib_R3 | toàn thân – xương sườn |  |
| Bone_Rib_R4 | toàn thân – xương sườn |  |
| Bone_Rib_R5 | toàn thân – xương sườn |  |
| Bone_Rib_R6 | toàn thân – xương sườn |  |
| Bone_Rib_R7 | toàn thân – xương sườn |  |
| Bone_Rib_R8 | toàn thân – xương sườn |  |
| Bone_Rib_R9 | toàn thân – xương sườn |  |
| Bone_Rib_R10 | toàn thân – xương sườn |  |
| Bone_Rib_R11 | toàn thân – xương sườn |  |
| Bone_Rib_R12 | toàn thân – xương sườn |  |
| Sternum | toàn thân – xương sườn |  |

### Cơ (64)

| Tên | Model | Mặc định |
|---|---|---|
| Musc_Gluteus_Max_L | toàn thân – cơ – xương | Tiểu khung |
| Musc_Gluteus_Max_R | toàn thân – cơ – xương | Tiểu khung |
| Musc_Gluteus_Med_L | toàn thân – cơ – xương |  |
| Musc_Gluteus_Med_R | toàn thân – cơ – xương |  |
| Musc_Gluteus_Min_L | toàn thân – cơ – xương |  |
| Musc_Gluteus_Min_R | toàn thân – cơ – xương |  |
| Musc_Paraspinal_L | toàn thân – cơ – xương | Bụng |
| Musc_Paraspinal_R | toàn thân – cơ – xương | Bụng |
| Musc_Iliopsoas_L | toàn thân – cơ – xương | Bụng, Tiểu khung |
| Musc_Iliopsoas_R | toàn thân – cơ – xương | Bụng, Tiểu khung |
| Musc_Masseter_R | Cơ vùng đầu (nhai, lưỡi) |  |
| Musc_Masseter_L | Cơ vùng đầu (nhai, lưỡi) |  |
| Musc_Temporal_R | Cơ vùng đầu (nhai, lưỡi) |  |
| Musc_Temporal_L | Cơ vùng đầu (nhai, lưỡi) |  |
| Musc_Pterygoid_Lat_R | Cơ vùng đầu (nhai, lưỡi) |  |
| Musc_Pterygoid_Lat_L | Cơ vùng đầu (nhai, lưỡi) |  |
| Musc_Pterygoid_Med_R | Cơ vùng đầu (nhai, lưỡi) |  |
| Musc_Pterygoid_Med_L | Cơ vùng đầu (nhai, lưỡi) |  |
| Tongue | Cơ vùng đầu (nhai, lưỡi) |  |
| Musc_Digastric_R | Cơ vùng đầu (nhai, lưỡi) |  |
| Musc_Digastric_L | Cơ vùng đầu (nhai, lưỡi) |  |
| Musc_Sclmast_R | Cơ vùng cổ, cơ khít hầu (thử nghiệm) |  |
| Musc_Sclmast_L | Cơ vùng cổ, cơ khít hầu (thử nghiệm) |  |
| Musc_Constrict_S | Cơ vùng cổ, cơ khít hầu (thử nghiệm) |  |
| Musc_Constrict_M | Cơ vùng cổ, cơ khít hầu (thử nghiệm) |  |
| Musc_Constrict_I | Cơ vùng cổ, cơ khít hầu (thử nghiệm) |  |
| Musc_Trapezius_R | Cơ vùng cổ, cơ khít hầu (thử nghiệm) |  |
| Musc_Trapezius_L | Cơ vùng cổ, cơ khít hầu (thử nghiệm) |  |
| Musc_Platysma_R | Cơ vùng cổ, cơ khít hầu (thử nghiệm) |  |
| Musc_Platysma_L | Cơ vùng cổ, cơ khít hầu (thử nghiệm) |  |
| Musc_LevatorScap_R | Cơ vùng cổ, cơ khít hầu (thử nghiệm) |  |
| Musc_LevatorScap_L | Cơ vùng cổ, cơ khít hầu (thử nghiệm) |  |
| Musc_Scalene_Ant_R | Cơ vùng cổ, cơ khít hầu (thử nghiệm) |  |
| Musc_Scalene_Ant_L | Cơ vùng cổ, cơ khít hầu (thử nghiệm) |  |
| Musc_Scalene_Mid_R | Cơ vùng cổ, cơ khít hầu (thử nghiệm) |  |
| Musc_Scalene_Mid_L | Cơ vùng cổ, cơ khít hầu (thử nghiệm) |  |
| Musc_Scalene_Post_R | Cơ vùng cổ, cơ khít hầu (thử nghiệm) |  |
| Musc_Scalene_Post_L | Cơ vùng cổ, cơ khít hầu (thử nghiệm) |  |
| Musc_Sternothyroid_R | Cơ vùng cổ, cơ khít hầu (thử nghiệm) |  |
| Musc_Sternothyroid_L | Cơ vùng cổ, cơ khít hầu (thử nghiệm) |  |
| Musc_Thyrohyoid_R | Cơ vùng cổ, cơ khít hầu (thử nghiệm) |  |
| Musc_Thyrohyoid_L | Cơ vùng cổ, cơ khít hầu (thử nghiệm) |  |
| Musc_Prevertebral_R | Cơ vùng cổ, cơ khít hầu (thử nghiệm) |  |
| Musc_Prevertebral_L | Cơ vùng cổ, cơ khít hầu (thử nghiệm) |  |
| Musc_Pectoralis_Maj_R | Cơ thành ngực – bụng |  |
| Musc_Pectoralis_Maj_L | Cơ thành ngực – bụng |  |
| Musc_RectusAbd_R | Cơ thành ngực – bụng |  |
| Musc_RectusAbd_L | Cơ thành ngực – bụng |  |
| Musc_Serratus_Ant_R | Cơ thành ngực – bụng |  |
| Musc_Serratus_Ant_L | Cơ thành ngực – bụng |  |
| Musc_Latissimus_R | Cơ thành ngực – bụng |  |
| Musc_Latissimus_L | Cơ thành ngực – bụng |  |
| Musc_Oblique_Ext_R | Cơ thành ngực – bụng |  |
| Musc_Oblique_Ext_L | Cơ thành ngực – bụng |  |
| Musc_Oblique_Int_R | Cơ thành ngực – bụng |  |
| Musc_Oblique_Int_L | Cơ thành ngực – bụng |  |
| Musc_ErectorSpinae_R | Cơ thành ngực – bụng |  |
| Musc_ErectorSpinae_L | Cơ thành ngực – bụng |  |
| Musc_Transversospinal_R | Cơ thành ngực – bụng |  |
| Musc_Transversospinal_L | Cơ thành ngực – bụng |  |
| Musc_Psoas_R | Cơ thành ngực – bụng |  |
| Musc_Psoas_L | Cơ thành ngực – bụng |  |
| Musc_QuadLumb_R | Cơ thành ngực – bụng |  |
| Musc_QuadLumb_L | Cơ thành ngực – bụng |  |

### Khoang cơ thể (4)

| Tên | Model | Mặc định |
|---|---|---|
| Cavity_Abdominal | Khoang ngực, khoang bụng, màng tim |  |
| Cavity_Thoracic | Khoang ngực, khoang bụng, màng tim |  |
| Pericardium | Khoang ngực, khoang bụng, màng tim |  |
| Mediastinum | Khoang ngực, khoang bụng, màng tim |  |

### Phân thùy gan (8)

| Tên | Model | Mặc định |
|---|---|---|
| Liver_Seg1 | Phân thùy gan |  |
| Liver_Seg2 | Phân thùy gan |  |
| Liver_Seg3 | Phân thùy gan |  |
| Liver_Seg4 | Phân thùy gan |  |
| Liver_Seg5 | Phân thùy gan |  |
| Liver_Seg6 | Phân thùy gan |  |
| Liver_Seg7 | Phân thùy gan |  |
| Liver_Seg8 | Phân thùy gan |  |

## Cơ quan KHÔNG có trong model miễn phí (bác sĩ tự vẽ / khoa tự huấn luyện)

- **Ngực / vú:** LAD / buồng tim, Brachial plexus, Bronchus_Prox
- **Bụng:** Bowel_Bag, Liver-GTV (tự trừ trong Monaco)
- **Tiểu khung:** Rectum, Anal canal, Bowel_Bag, Femur_Head (đang là cả xương đùi), Penile bulb
- **Đầu cổ:** Brainstem, OpticChiasm, Cochlea, Larynx (có sụn giáp/nhẫn trong danh mục), Oral cavity, Lips, Brachial plexus, Pituitary
