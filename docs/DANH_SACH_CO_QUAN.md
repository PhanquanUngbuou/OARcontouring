# Danh sách cơ quan QuanContour khoanh được

Tổng cộng **232 cấu trúc** từ các model **miễn phí** của TotalSegmentator (CT). Trong app: **Chọn cơ quan…** để tích/bỏ cho từng vùng; lựa chọn được lưu lại.

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
| Xương hàm, xoang, răng (`craniofacial_structures`) | 7 cấu trúc | 2.5 |
| Sụn thanh quản, xương móng, mạch cổ (`headneck_bones_vessels`) | 12 cấu trúc | 1.5 |
| Cơ vùng đầu (nhai, lưỡi) (`head_muscles`) | 11 cấu trúc | 1.5 |
| Cơ vùng cổ, cơ khít hầu (thử nghiệm) (`headneck_muscles`) | 23 cấu trúc | 3.0 |
| Tuyến vú (`breasts`) | 2 cấu trúc | 1.0 |
| Cơ thành ngực – bụng (`abdominal_muscles`) | 22 cấu trúc | 4.0 |
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
| Larynx_Air | Sụn thanh quản, xương móng, mạch cổ |  |

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
| Atrial_Appendage_L | toàn thân – tim mạch |  |
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
| Nasal_Cavity_R | Tuyến nước bọt, mắt, thần kinh thị |  |
| Nasal_Cavity_L | Tuyến nước bọt, mắt, thần kinh thị |  |
| Auditory_Canal_R | Tuyến nước bọt, mắt, thần kinh thị |  |
| Auditory_Canal_L | Tuyến nước bọt, mắt, thần kinh thị |  |
| Soft_Palate | Tuyến nước bọt, mắt, thần kinh thị |  |
| Hard_Palate | Tuyến nước bọt, mắt, thần kinh thị |  |
| Teeth_Lower | Xương hàm, xoang, răng |  |
| Head | Xương hàm, xoang, răng |  |
| Sinus_Maxillary | Xương hàm, xoang, răng |  |
| Sinus_Frontal | Xương hàm, xoang, răng |  |
| Teeth_Upper | Xương hàm, xoang, răng |  |
| Cartilage_Thyroid | Sụn thanh quản, xương móng, mạch cổ |  |
| Bone_Hyoid | Sụn thanh quản, xương móng, mạch cổ |  |
| Cartilage_Cricoid | Sụn thanh quản, xương móng, mạch cổ |  |
| Zygomatic_Arch_R | Sụn thanh quản, xương móng, mạch cổ |  |
| Zygomatic_Arch_L | Sụn thanh quản, xương móng, mạch cổ |  |
| Styloid_Process_R | Sụn thanh quản, xương móng, mạch cổ |  |
| Styloid_Process_L | Sụn thanh quản, xương móng, mạch cổ |  |

### Vú (2)

| Tên | Model | Mặc định |
|---|---|---|
| Breast_L | Tuyến vú | Ngực / vú |
| Breast_R | Tuyến vú | Ngực / vú |

### Xương (69)

| Tên | Model | Mặc định |
|---|---|---|
| Femur_L | toàn thân – cơ – xương | Tiểu khung |
| Femur_R | toàn thân – cơ – xương | Tiểu khung |
| Bone_Pelvic | toàn thân – cơ – xương, đốt sống | Tiểu khung |
| Bone_Hips | toàn thân – cơ – xương |  |
| Bone_Mandible | Xương hàm, xoang, răng | Đầu cổ |
| Ribs_L | toàn thân – xương sườn |  |
| Ribs_R | toàn thân – xương sườn |  |
| Ribs | toàn thân – xương sườn | Ngực / vú |
| Sacrum | toàn thân – đốt sống | Tiểu khung |
| Vertebrae_S1 | toàn thân – đốt sống |  |
| Vertebrae_L5 | toàn thân – đốt sống |  |
| Vertebrae_L4 | toàn thân – đốt sống |  |
| Vertebrae_L3 | toàn thân – đốt sống |  |
| Vertebrae_L2 | toàn thân – đốt sống |  |
| Vertebrae_L1 | toàn thân – đốt sống |  |
| Vertebrae_T12 | toàn thân – đốt sống |  |
| Vertebrae_T11 | toàn thân – đốt sống |  |
| Vertebrae_T10 | toàn thân – đốt sống |  |
| Vertebrae_T9 | toàn thân – đốt sống |  |
| Vertebrae_T8 | toàn thân – đốt sống |  |
| Vertebrae_T7 | toàn thân – đốt sống |  |
| Vertebrae_T6 | toàn thân – đốt sống |  |
| Vertebrae_T5 | toàn thân – đốt sống |  |
| Vertebrae_T4 | toàn thân – đốt sống |  |
| Vertebrae_T3 | toàn thân – đốt sống |  |
| Vertebrae_T2 | toàn thân – đốt sống |  |
| Vertebrae_T1 | toàn thân – đốt sống |  |
| Vertebrae_C7 | toàn thân – đốt sống |  |
| Vertebrae_C6 | toàn thân – đốt sống |  |
| Vertebrae_C5 | toàn thân – đốt sống |  |
| Vertebrae_C4 | toàn thân – đốt sống |  |
| Vertebrae_C3 | toàn thân – đốt sống |  |
| Vertebrae_C2 | toàn thân – đốt sống |  |
| Vertebrae_C1 | toàn thân – đốt sống |  |
| Humerus_L | toàn thân – cơ – xương | Ngực / vú |
| Humerus_R | toàn thân – cơ – xương | Ngực / vú |
| Scapula_L | toàn thân – cơ – xương |  |
| Scapula_R | toàn thân – cơ – xương |  |
| Clavicle_L | toàn thân – cơ – xương |  |
| Clavicle_R | toàn thân – cơ – xương |  |
| Bone_Hip_L | toàn thân – cơ – xương |  |
| Bone_Hip_R | toàn thân – cơ – xương |  |
| Skull | toàn thân – cơ – xương |  |
| Rib_Left_1 | toàn thân – xương sườn |  |
| Rib_Left_2 | toàn thân – xương sườn |  |
| Rib_Left_3 | toàn thân – xương sườn |  |
| Rib_Left_4 | toàn thân – xương sườn |  |
| Rib_Left_5 | toàn thân – xương sườn |  |
| Rib_Left_6 | toàn thân – xương sườn |  |
| Rib_Left_7 | toàn thân – xương sườn |  |
| Rib_Left_8 | toàn thân – xương sườn |  |
| Rib_Left_9 | toàn thân – xương sườn |  |
| Rib_Left_10 | toàn thân – xương sườn |  |
| Rib_Left_11 | toàn thân – xương sườn |  |
| Rib_Left_12 | toàn thân – xương sườn |  |
| Rib_Right_1 | toàn thân – xương sườn |  |
| Rib_Right_2 | toàn thân – xương sườn |  |
| Rib_Right_3 | toàn thân – xương sườn |  |
| Rib_Right_4 | toàn thân – xương sườn |  |
| Rib_Right_5 | toàn thân – xương sườn |  |
| Rib_Right_6 | toàn thân – xương sườn |  |
| Rib_Right_7 | toàn thân – xương sườn |  |
| Rib_Right_8 | toàn thân – xương sườn |  |
| Rib_Right_9 | toàn thân – xương sườn |  |
| Rib_Right_10 | toàn thân – xương sườn |  |
| Rib_Right_11 | toàn thân – xương sườn |  |
| Rib_Right_12 | toàn thân – xương sườn |  |
| Sternum | toàn thân – xương sườn |  |
| Skull_craniofacial | Xương hàm, xoang, răng |  |

### Cơ (66)

| Tên | Model | Mặc định |
|---|---|---|
| Gluteus_Maximus_L | toàn thân – cơ – xương | Tiểu khung |
| Gluteus_Maximus_R | toàn thân – cơ – xương | Tiểu khung |
| Gluteus_Medius_L | toàn thân – cơ – xương |  |
| Gluteus_Medius_R | toàn thân – cơ – xương |  |
| Gluteus_Minimus_L | toàn thân – cơ – xương |  |
| Gluteus_Minimus_R | toàn thân – cơ – xương |  |
| Musc_Autochthon_L | toàn thân – cơ – xương | Bụng |
| Musc_Autochthon_R | toàn thân – cơ – xương | Bụng |
| Iliopsoas_L | toàn thân – cơ – xương | Bụng, Tiểu khung |
| Iliopsoas_R | toàn thân – cơ – xương | Bụng, Tiểu khung |
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
| Musc_Levator_Scapulae_R | Cơ vùng cổ, cơ khít hầu (thử nghiệm) |  |
| Musc_Levator_Scapulae_L | Cơ vùng cổ, cơ khít hầu (thử nghiệm) |  |
| Musc_Anterior_Scalene_R | Cơ vùng cổ, cơ khít hầu (thử nghiệm) |  |
| Musc_Anterior_Scalene_L | Cơ vùng cổ, cơ khít hầu (thử nghiệm) |  |
| Musc_Middle_Scalene_R | Cơ vùng cổ, cơ khít hầu (thử nghiệm) |  |
| Musc_Middle_Scalene_L | Cơ vùng cổ, cơ khít hầu (thử nghiệm) |  |
| Musc_Posterior_Scalene_R | Cơ vùng cổ, cơ khít hầu (thử nghiệm) |  |
| Musc_Posterior_Scalene_L | Cơ vùng cổ, cơ khít hầu (thử nghiệm) |  |
| Musc_Sterno_Thyroid_R | Cơ vùng cổ, cơ khít hầu (thử nghiệm) |  |
| Musc_Sterno_Thyroid_L | Cơ vùng cổ, cơ khít hầu (thử nghiệm) |  |
| Musc_Thyrohyoid_R | Cơ vùng cổ, cơ khít hầu (thử nghiệm) |  |
| Musc_Thyrohyoid_L | Cơ vùng cổ, cơ khít hầu (thử nghiệm) |  |
| Musc_Prevertebral_R | Cơ vùng cổ, cơ khít hầu (thử nghiệm) |  |
| Musc_Prevertebral_L | Cơ vùng cổ, cơ khít hầu (thử nghiệm) |  |
| Musc_Pectoralis_Major_R | Cơ thành ngực – bụng |  |
| Musc_Pectoralis_Major_L | Cơ thành ngực – bụng |  |
| Musc_Rectus_Abdominis_R | Cơ thành ngực – bụng |  |
| Musc_Rectus_Abdominis_L | Cơ thành ngực – bụng |  |
| Musc_Serratus_Anterior_R | Cơ thành ngực – bụng |  |
| Musc_Serratus_Anterior_L | Cơ thành ngực – bụng |  |
| Musc_Latissimus_Dorsi_R | Cơ thành ngực – bụng |  |
| Musc_Latissimus_Dorsi_L | Cơ thành ngực – bụng |  |
| Musc_Trapezius_R_abdominal | Cơ thành ngực – bụng |  |
| Musc_Trapezius_L_abdominal | Cơ thành ngực – bụng |  |
| Musc_External_Oblique_R | Cơ thành ngực – bụng |  |
| Musc_External_Oblique_L | Cơ thành ngực – bụng |  |
| Musc_Internal_Oblique_R | Cơ thành ngực – bụng |  |
| Musc_Internal_Oblique_L | Cơ thành ngực – bụng |  |
| Musc_Erector_Spinae_R | Cơ thành ngực – bụng |  |
| Musc_Erector_Spinae_L | Cơ thành ngực – bụng |  |
| Musc_Transversospinalis_R | Cơ thành ngực – bụng |  |
| Musc_Transversospinalis_L | Cơ thành ngực – bụng |  |
| Musc_Psoas_Major_R | Cơ thành ngực – bụng |  |
| Musc_Psoas_Major_L | Cơ thành ngực – bụng |  |
| Musc_Quadratus_Lumborum_R | Cơ thành ngực – bụng |  |
| Musc_Quadratus_Lumborum_L | Cơ thành ngực – bụng |  |

### Khoang cơ thể (4)

| Tên | Model | Mặc định |
|---|---|---|
| Abdominal_Cavity | Khoang ngực, khoang bụng, màng tim |  |
| Thoracic_Cavity | Khoang ngực, khoang bụng, màng tim |  |
| Pericardium | Khoang ngực, khoang bụng, màng tim |  |
| Mediastinum | Khoang ngực, khoang bụng, màng tim |  |

### Phân thùy gan (8)

| Tên | Model | Mặc định |
|---|---|---|
| Liver_Segment_1 | Phân thùy gan |  |
| Liver_Segment_2 | Phân thùy gan |  |
| Liver_Segment_3 | Phân thùy gan |  |
| Liver_Segment_4 | Phân thùy gan |  |
| Liver_Segment_5 | Phân thùy gan |  |
| Liver_Segment_6 | Phân thùy gan |  |
| Liver_Segment_7 | Phân thùy gan |  |
| Liver_Segment_8 | Phân thùy gan |  |

## Cơ quan KHÔNG có trong model miễn phí (bác sĩ tự vẽ / khoa tự huấn luyện)

- **Ngực / vú:** LAD / buồng tim, Brachial plexus, Bronchus_Prox
- **Bụng:** Bowel_Bag, Liver-GTV (tự trừ trong Monaco)
- **Tiểu khung:** Rectum, Anal canal, Bowel_Bag, Femur_Head (đang là cả xương đùi), Penile bulb
- **Đầu cổ:** Brainstem, OpticChiasm, Cochlea, Larynx (có sụn giáp/nhẫn trong danh mục), Oral cavity, Lips, Brachial plexus, Pituitary
