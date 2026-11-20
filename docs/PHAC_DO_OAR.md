# Phác đồ OAR theo vị trí u (bản đề xuất – khoa cần duyệt)

Chỉ gồm cơ quan có trong model **miễn phí**. Trong app, bác sĩ chọn *Mục đích* + *Vị trí xạ trị*, rồi có thể **Mở rộng / chỉnh sửa**: dùng cho riêng ca đó hoặc lưu làm mặc định của khoa.

Thời gian: 1 đơn vị ≈ 1–2 phút trên MacBook chip M, vài giây trên GPU NVIDIA.

## U đầu cổ

### Vòm họng

| | OAR app tự vẽ | Model cần chạy | Thời gian |
|---|---|---|---|
| **Triệt căn** | Brain, SpinalCord, Parotid_L, Parotid_R, Glnd_Submand_L, Glnd_Submand_R, Eye_L, Eye_R, Lens_L, Lens_R, OpticNrv_L, OpticNrv_R, Bone_Mandible, Glnd_Thyroid, Esophagus | toàn thân: nội tạng, cơ–xương; Sọ mặt: xương hàm, xoang, răng; Đầu cổ: tuyến, mắt, khoang | ≈ 6.0 |
| **Triệu chứng** | SpinalCord, Brain, Parotid_L, Parotid_R, Lens_L, Lens_R, OpticNrv_L, OpticNrv_R | toàn thân: cơ–xương; Đầu cổ: tuyến, mắt, khoang | ≈ 2.5 |

**Bác sĩ tự vẽ:** Brainstem, OpticChiasm, Lobe_Temporal_L/R (thùy thái dương), Cochlea_L/R, Pituitary, Joint_TM_L/R (khớp thái dương hàm), Larynx, Cavity_Oral, Musc_Constrict (có model thử nghiệm trong Mở rộng), BrachialPlex_L/R  
*Ghi chú:* Brain là toàn bộ não: thùy thái dương chưa có trong model miễn phí, cần tự vẽ.

### Khoang miệng

| | OAR app tự vẽ | Model cần chạy | Thời gian |
|---|---|---|---|
| **Triệt căn** | SpinalCord, Parotid_L, Parotid_R, Glnd_Submand_L, Glnd_Submand_R, Bone_Mandible, Glnd_Thyroid, Esophagus | toàn thân: nội tạng, cơ–xương; Sọ mặt: xương hàm, xoang, răng; Đầu cổ: tuyến, mắt, khoang | ≈ 6.0 |
| **Triệu chứng** | SpinalCord, Parotid_L, Parotid_R | toàn thân: cơ–xương; Đầu cổ: tuyến, mắt, khoang | ≈ 2.5 |

**Bác sĩ tự vẽ:** Brainstem, Cavity_Oral (ngoài u), Lips, Larynx, Musc_Constrict, Cochlea_L/R, BrachialPlex_L/R  

### Họng miệng (amidan, đáy lưỡi)

| | OAR app tự vẽ | Model cần chạy | Thời gian |
|---|---|---|---|
| **Triệt căn** | SpinalCord, Parotid_L, Parotid_R, Glnd_Submand_L, Glnd_Submand_R, Bone_Mandible, Glnd_Thyroid, Esophagus | toàn thân: nội tạng, cơ–xương; Sọ mặt: xương hàm, xoang, răng; Đầu cổ: tuyến, mắt, khoang | ≈ 6.0 |
| **Triệu chứng** | SpinalCord, Parotid_L, Parotid_R | toàn thân: cơ–xương; Đầu cổ: tuyến, mắt, khoang | ≈ 2.5 |

**Bác sĩ tự vẽ:** Brainstem, Cavity_Oral, Larynx, Musc_Constrict, Cochlea_L/R, BrachialPlex_L/R  

### Thanh quản

| | OAR app tự vẽ | Model cần chạy | Thời gian |
|---|---|---|---|
| **Triệt căn** | SpinalCord, Parotid_L, Parotid_R, Glnd_Submand_L, Glnd_Submand_R, Bone_Mandible, Glnd_Thyroid, Esophagus, Trachea | toàn thân: nội tạng, cơ–xương; Sọ mặt: xương hàm, xoang, răng; Đầu cổ: tuyến, mắt, khoang | ≈ 6.0 |
| **Triệu chứng** | SpinalCord, Esophagus | toàn thân: nội tạng, cơ–xương | ≈ 2 |

**Bác sĩ tự vẽ:** Brainstem, Larynx (nếu không thuộc thể tích bia), Musc_Constrict, Cavity_Oral, BrachialPlex_L/R  

### Hạ họng

| | OAR app tự vẽ | Model cần chạy | Thời gian |
|---|---|---|---|
| **Triệt căn** | SpinalCord, Parotid_L, Parotid_R, Glnd_Submand_L, Glnd_Submand_R, Bone_Mandible, Glnd_Thyroid, Esophagus, Trachea | toàn thân: nội tạng, cơ–xương; Sọ mặt: xương hàm, xoang, răng; Đầu cổ: tuyến, mắt, khoang | ≈ 6.0 |
| **Triệu chứng** | SpinalCord, Esophagus | toàn thân: nội tạng, cơ–xương | ≈ 2 |

**Bác sĩ tự vẽ:** Brainstem, Larynx (nếu không thuộc thể tích bia), Musc_Constrict, Cavity_Oral, BrachialPlex_L/R  

### Tuyến nước bọt (mang tai, dưới hàm)

| | OAR app tự vẽ | Model cần chạy | Thời gian |
|---|---|---|---|
| **Triệt căn** | Brain, SpinalCord, Parotid_L, Parotid_R, Glnd_Submand_L, Glnd_Submand_R, Bone_Mandible | toàn thân: cơ–xương; Sọ mặt: xương hàm, xoang, răng; Đầu cổ: tuyến, mắt, khoang | ≈ 5.0 |
| **Triệu chứng** | SpinalCord, Parotid_L, Parotid_R | toàn thân: cơ–xương; Đầu cổ: tuyến, mắt, khoang | ≈ 2.5 |

**Bác sĩ tự vẽ:** Brainstem, Cochlea_L/R, Lobe_Temporal_L/R, Cavity_Oral, Joint_TM_L/R  
*Ghi chú:* Tuyến bên tổn thương thường thuộc thể tích bia: chỉ dùng ràng buộc cho tuyến đối bên.

### Tuyến giáp

| | OAR app tự vẽ | Model cần chạy | Thời gian |
|---|---|---|---|
| **Triệt căn** | SpinalCord, Esophagus, Trachea, Lung_L, Lung_R, Parotid_L, Parotid_R | toàn thân: nội tạng, cơ–xương; Đầu cổ: tuyến, mắt, khoang | ≈ 3.5 |
| **Triệu chứng** | SpinalCord, Esophagus, Trachea | toàn thân: nội tạng, cơ–xương | ≈ 2 |

**Bác sĩ tự vẽ:** Larynx, Musc_Constrict, BrachialPlex_L/R  
*Ghi chú:* Tuyến giáp là cơ quan đích nên không vẽ Glnd_Thyroid.

### Hạch cổ không rõ u nguyên phát

| | OAR app tự vẽ | Model cần chạy | Thời gian |
|---|---|---|---|
| **Triệt căn** | SpinalCord, Parotid_L, Parotid_R, Glnd_Submand_L, Glnd_Submand_R, Bone_Mandible, Glnd_Thyroid, Esophagus | toàn thân: nội tạng, cơ–xương; Sọ mặt: xương hàm, xoang, răng; Đầu cổ: tuyến, mắt, khoang | ≈ 6.0 |
| **Triệu chứng** | SpinalCord, Parotid_L, Parotid_R | toàn thân: cơ–xương; Đầu cổ: tuyến, mắt, khoang | ≈ 2.5 |

**Bác sĩ tự vẽ:** Brainstem, Larynx, Cavity_Oral, Musc_Constrict, BrachialPlex_L/R  

### Hốc mũi – xoang

| | OAR app tự vẽ | Model cần chạy | Thời gian |
|---|---|---|---|
| **Triệt căn** | Brain, SpinalCord, Eye_L, Eye_R, Lens_L, Lens_R, OpticNrv_L, OpticNrv_R, Parotid_L, Parotid_R, Bone_Mandible | toàn thân: cơ–xương; Sọ mặt: xương hàm, xoang, răng; Đầu cổ: tuyến, mắt, khoang | ≈ 5.0 |
| **Triệu chứng** | Brain, SpinalCord, Eye_L, Eye_R, Lens_L, Lens_R, OpticNrv_L, OpticNrv_R | toàn thân: cơ–xương; Đầu cổ: tuyến, mắt, khoang | ≈ 2.5 |

**Bác sĩ tự vẽ:** Brainstem, OpticChiasm, Pituitary, Lobe_Temporal_L/R, Cochlea_L/R, Glnd_Lacrimal_L/R (tuyến lệ)  

## U não

### U não nguyên phát

| | OAR app tự vẽ | Model cần chạy | Thời gian |
|---|---|---|---|
| **Triệt căn** | Brain, Eye_L, Eye_R, Lens_L, Lens_R, OpticNrv_L, OpticNrv_R, SpinalCord | toàn thân: cơ–xương; Đầu cổ: tuyến, mắt, khoang | ≈ 2.5 |
| **Triệu chứng** | Brain, Lens_L, Lens_R, OpticNrv_L, OpticNrv_R | toàn thân: cơ–xương; Đầu cổ: tuyến, mắt, khoang | ≈ 2.5 |

**Bác sĩ tự vẽ:** Brainstem, OpticChiasm, Cochlea_L/R, Hippocampus_L/R, Pituitary, Glnd_Lacrimal_L/R  
*Ghi chú:* Brain gồm cả u: trừ thể tích bia trong Monaco nếu khoa dùng Brain-PTV.

### Xạ toàn não (di căn não)

| | OAR app tự vẽ | Model cần chạy | Thời gian |
|---|---|---|---|
| **Triệt căn** | Eye_L, Eye_R, Lens_L, Lens_R, OpticNrv_L, OpticNrv_R | Đầu cổ: tuyến, mắt, khoang | ≈ 1.5 |
| **Triệu chứng** | Eye_L, Eye_R, Lens_L, Lens_R, OpticNrv_L, OpticNrv_R | Đầu cổ: tuyến, mắt, khoang | ≈ 1.5 |

**Bác sĩ tự vẽ:** Hippocampus_L/R (nếu xạ tránh hồi hải mã), Cochlea_L/R, OpticChiasm  
*Ghi chú:* Toàn bộ não là thể tích bia; app chỉ vẽ mắt, thủy tinh thể, thần kinh thị.

## U lồng ngực

### Phổi (3D-CRT / IMRT)

| | OAR app tự vẽ | Model cần chạy | Thời gian |
|---|---|---|---|
| **Triệt căn** | Lung_L, Lung_R, Lungs, Heart, Esophagus, SpinalCord | toàn thân: nội tạng, tim mạch, cơ–xương | ≈ 3 |
| **Triệu chứng** | Lungs, Heart, Esophagus, SpinalCord | toàn thân: nội tạng, tim mạch, cơ–xương | ≈ 3 |

**Bác sĩ tự vẽ:** BrachialPlex_L/R (u đỉnh phổi), Bronchus_Prox (cây phế quản gốc)  
*Ghi chú:* Lungs nên trừ GTV/ITV trong Monaco (Lungs-GTV) khi tính V20.

### Phổi SBRT

| | OAR app tự vẽ | Model cần chạy | Thời gian |
|---|---|---|---|
| **Triệt căn** | Lung_L, Lung_R, Lungs, Heart, Esophagus, SpinalCord, Trachea, A_Aorta, V_Venacava_S, Ribs, Sternum | toàn thân: nội tạng, tim mạch, cơ–xương, xương sườn | ≈ 4 |
| **Triệu chứng** | Lung_L, Lung_R, Lungs, Heart, Esophagus, SpinalCord | toàn thân: nội tạng, tim mạch, cơ–xương | ≈ 3 |

**Bác sĩ tự vẽ:** Bronchus_Prox, BrachialPlex_L/R, ChestWall (dùng Ribs tham khảo), Skin  
*Ghi chú:* Ribs/Sternum cần thêm phần model xương sườn (~1 đơn vị thời gian).

### Thực quản

| | OAR app tự vẽ | Model cần chạy | Thời gian |
|---|---|---|---|
| **Triệt căn** | Lung_L, Lung_R, Lungs, Heart, SpinalCord, Liver, Kidney_L, Kidney_R | toàn thân: nội tạng, tim mạch, cơ–xương | ≈ 3 |
| **Triệu chứng** | Lungs, Heart, SpinalCord | toàn thân: nội tạng, tim mạch, cơ–xương | ≈ 3 |

**Bác sĩ tự vẽ:** BrachialPlex_L/R (u cổ)  
*Ghi chú:* Thực quản là cơ quan đích: app không vẽ Esophagus để tránh nhầm với thể tích bia.

### U tuyến ức / trung thất

| | OAR app tự vẽ | Model cần chạy | Thời gian |
|---|---|---|---|
| **Triệt căn** | Lung_L, Lung_R, Lungs, Heart, Esophagus, SpinalCord | toàn thân: nội tạng, tim mạch, cơ–xương | ≈ 3 |
| **Triệu chứng** | Lungs, Heart, SpinalCord | toàn thân: nội tạng, tim mạch, cơ–xương | ≈ 3 |

**Bác sĩ tự vẽ:** LAD, BrachialPlex_L/R, Breast_L/R (bệnh nhân nữ trẻ: thêm trong Mở rộng)  

### Vú trái

| | OAR app tự vẽ | Model cần chạy | Thời gian |
|---|---|---|---|
| **Triệt căn** | Heart, Lung_L, Lung_R, Lungs, Breast_R, SpinalCord, Esophagus, Glnd_Thyroid, Humerus_L | toàn thân: nội tạng, tim mạch, cơ–xương; Tuyến vú | ≈ 4.0 |
| **Triệu chứng** | Heart, Lungs, SpinalCord | toàn thân: nội tạng, tim mạch, cơ–xương | ≈ 3 |

**Bác sĩ tự vẽ:** LAD (động mạch liên thất trước), BrachialPlex_L, Skin  
*Ghi chú:* Breast_R là vú đối bên (OAR). CTV vú trái bác sĩ tự vẽ.

### Vú phải

| | OAR app tự vẽ | Model cần chạy | Thời gian |
|---|---|---|---|
| **Triệt căn** | Heart, Lung_L, Lung_R, Lungs, Breast_L, SpinalCord, Esophagus, Glnd_Thyroid, Humerus_R, Liver | toàn thân: nội tạng, tim mạch, cơ–xương; Tuyến vú | ≈ 4.0 |
| **Triệu chứng** | Lungs, Heart, SpinalCord | toàn thân: nội tạng, tim mạch, cơ–xương | ≈ 3 |

**Bác sĩ tự vẽ:** BrachialPlex_R, Skin  
*Ghi chú:* Breast_L là vú đối bên (OAR). CTV vú phải bác sĩ tự vẽ.

## U vùng bụng – sau phúc mạc

### Dạ dày

| | OAR app tự vẽ | Model cần chạy | Thời gian |
|---|---|---|---|
| **Triệt căn** | Liver, Kidney_L, Kidney_R, SpinalCord, Heart, Bowel_Small, Lung_L, Lung_R, Lungs | toàn thân: nội tạng, tim mạch, cơ–xương | ≈ 3 |
| **Triệu chứng** | Liver, Kidney_L, Kidney_R, SpinalCord | toàn thân: nội tạng, cơ–xương | ≈ 2 |

**Bác sĩ tự vẽ:** Bowel_Bag  
*Ghi chú:* Dạ dày là cơ quan đích nên không vẽ Stomach.

### Tuỵ

| | OAR app tự vẽ | Model cần chạy | Thời gian |
|---|---|---|---|
| **Triệt căn** | Liver, Kidney_L, Kidney_R, SpinalCord, Duodenum, Stomach, Bowel_Small | toàn thân: nội tạng, cơ–xương | ≈ 2 |
| **Triệu chứng** | Liver, Kidney_L, Kidney_R, SpinalCord, Duodenum, Stomach | toàn thân: nội tạng, cơ–xương | ≈ 2 |

**Bác sĩ tự vẽ:** Bowel_Bag  

### Gan (HCC, di căn gan)

| | OAR app tự vẽ | Model cần chạy | Thời gian |
|---|---|---|---|
| **Triệt căn** | Liver, Stomach, Duodenum, Kidney_L, Kidney_R, SpinalCord, Heart, Esophagus, Bowel_Small, Colon, Lung_R, Lung_L | toàn thân: nội tạng, tim mạch, cơ–xương | ≈ 3 |
| **Triệu chứng** | Liver, Stomach, Duodenum, Kidney_L, Kidney_R, SpinalCord | toàn thân: nội tạng, cơ–xương | ≈ 2 |

**Bác sĩ tự vẽ:** Liver-GTV (tự trừ trong Monaco), Bowel_Bag, ChestWall (SBRT)  

### Đường mật / túi mật

| | OAR app tự vẽ | Model cần chạy | Thời gian |
|---|---|---|---|
| **Triệt căn** | Liver, Kidney_L, Kidney_R, SpinalCord, Duodenum, Stomach, Bowel_Small | toàn thân: nội tạng, cơ–xương | ≈ 2 |
| **Triệu chứng** | Liver, Kidney_L, Kidney_R, SpinalCord, Duodenum | toàn thân: nội tạng, cơ–xương | ≈ 2 |

**Bác sĩ tự vẽ:** Liver-GTV, Bowel_Bag  

### Sarcoma sau phúc mạc / u thận

| | OAR app tự vẽ | Model cần chạy | Thời gian |
|---|---|---|---|
| **Triệt căn** | Kidney_L, Kidney_R, Liver, SpinalCord, Bowel_Small, Colon, Stomach, Duodenum | toàn thân: nội tạng, cơ–xương | ≈ 2 |
| **Triệu chứng** | Kidney_L, Kidney_R, SpinalCord, Bowel_Small | toàn thân: nội tạng, cơ–xương | ≈ 2 |

**Bác sĩ tự vẽ:** Bowel_Bag  
*Ghi chú:* Thận bên tổn thương có thể nằm trong thể tích bia.

### Tinh hoàn (xạ hạch cạnh động mạch chủ)

| | OAR app tự vẽ | Model cần chạy | Thời gian |
|---|---|---|---|
| **Triệt căn** | Kidney_L, Kidney_R, Liver, SpinalCord, Bowel_Small, Stomach, Duodenum | toàn thân: nội tạng, cơ–xương | ≈ 2 |
| **Triệu chứng** | Kidney_L, Kidney_R, SpinalCord, Bowel_Small | toàn thân: nội tạng, cơ–xương | ≈ 2 |

**Bác sĩ tự vẽ:** Testis đối bên, Bowel_Bag  

## U vùng tiểu khung

### Trực tràng

| | OAR app tự vẽ | Model cần chạy | Thời gian |
|---|---|---|---|
| **Triệt căn** | Bladder, Bowel_Small, Colon, Femur_L, Femur_R | toàn thân: nội tạng, cơ–xương | ≈ 2 |
| **Triệu chứng** | Bladder, Bowel_Small, Femur_L, Femur_R | toàn thân: nội tạng, cơ–xương | ≈ 2 |

**Bác sĩ tự vẽ:** Bowel_Bag, Genitalia, Anal canal (nếu không thuộc thể tích bia)  

### Ống hậu môn

| | OAR app tự vẽ | Model cần chạy | Thời gian |
|---|---|---|---|
| **Triệt căn** | Bladder, Bowel_Small, Colon, Femur_L, Femur_R, Bone_Hips | toàn thân: nội tạng, cơ–xương | ≈ 2 |
| **Triệu chứng** | Bladder, Bowel_Small, Femur_L, Femur_R | toàn thân: nội tạng, cơ–xương | ≈ 2 |

**Bác sĩ tự vẽ:** Genitalia (cơ quan sinh dục ngoài), Bowel_Bag  
*Ghi chú:* Bone_Hips dùng cho xạ tránh tủy xương (cánh chậu); trực tràng/ống hậu môn thuộc thể tích bia.

### Cổ tử cung

| | OAR app tự vẽ | Model cần chạy | Thời gian |
|---|---|---|---|
| **Triệt căn** | Bladder, Bowel_Small, Colon, Femur_L, Femur_R, Bone_Hips, Kidney_L, Kidney_R, SpinalCord | toàn thân: nội tạng, cơ–xương | ≈ 2 |
| **Triệu chứng** | Bladder, Bowel_Small, Femur_L, Femur_R | toàn thân: nội tạng, cơ–xương | ≈ 2 |

**Bác sĩ tự vẽ:** Rectum, Sigmoid (đang nằm trong Colon), Bowel_Bag  
*Ghi chú:* Kidney, SpinalCord dùng khi xạ hạch cạnh động mạch chủ. Muốn tính cả xương cùng: chọn Bone_Pelvic trong Mở rộng (thêm 1 phần model).

### Nội mạc tử cung

| | OAR app tự vẽ | Model cần chạy | Thời gian |
|---|---|---|---|
| **Triệt căn** | Bladder, Bowel_Small, Colon, Femur_L, Femur_R, Bone_Hips, Kidney_L, Kidney_R, SpinalCord | toàn thân: nội tạng, cơ–xương | ≈ 2 |
| **Triệu chứng** | Bladder, Bowel_Small, Femur_L, Femur_R | toàn thân: nội tạng, cơ–xương | ≈ 2 |

**Bác sĩ tự vẽ:** Rectum, Sigmoid (đang nằm trong Colon), Bowel_Bag  
*Ghi chú:* Kidney, SpinalCord dùng khi xạ hạch cạnh động mạch chủ.

### Âm đạo

| | OAR app tự vẽ | Model cần chạy | Thời gian |
|---|---|---|---|
| **Triệt căn** | Bladder, Bowel_Small, Colon, Femur_L, Femur_R, Bone_Hips | toàn thân: nội tạng, cơ–xương | ≈ 2 |
| **Triệu chứng** | Bladder, Bowel_Small, Femur_L, Femur_R | toàn thân: nội tạng, cơ–xương | ≈ 2 |

**Bác sĩ tự vẽ:** Rectum, Urethra, Anal canal, Bowel_Bag  

### Âm hộ

| | OAR app tự vẽ | Model cần chạy | Thời gian |
|---|---|---|---|
| **Triệt căn** | Bladder, Bowel_Small, Colon, Femur_L, Femur_R, Bone_Hips | toàn thân: nội tạng, cơ–xương | ≈ 2 |
| **Triệu chứng** | Bladder, Femur_L, Femur_R | toàn thân: nội tạng, cơ–xương | ≈ 2 |

**Bác sĩ tự vẽ:** Rectum, Anal canal, Bowel_Bag, Skin  
*Ghi chú:* Femur gồm cả xương đùi: chỏm và cổ xương đùi cần chú ý khi xạ hạch bẹn.

### Tiền liệt tuyến

| | OAR app tự vẽ | Model cần chạy | Thời gian |
|---|---|---|---|
| **Triệt căn** | Bladder, Bowel_Small, Colon, Femur_L, Femur_R, Prostate | toàn thân: nội tạng, cơ–xương | ≈ 2 |
| **Triệu chứng** | Bladder, Femur_L, Femur_R, Bowel_Small | toàn thân: nội tạng, cơ–xương | ≈ 2 |

**Bác sĩ tự vẽ:** Rectum, PenileBulb, SeminalVes (túi tinh, thuộc CTV)  
*Ghi chú:* Prostate do model vẽ chỉ để tham khảo khi vẽ CTV.

### Bàng quang

| | OAR app tự vẽ | Model cần chạy | Thời gian |
|---|---|---|---|
| **Triệt căn** | Bowel_Small, Colon, Femur_L, Femur_R | toàn thân: nội tạng, cơ–xương | ≈ 2 |
| **Triệu chứng** | Bowel_Small, Colon, Femur_L, Femur_R | toàn thân: nội tạng, cơ–xương | ≈ 2 |

**Bác sĩ tự vẽ:** Rectum, Bowel_Bag  
*Ghi chú:* Bàng quang là cơ quan đích nên không vẽ Bladder.

## Di căn xương

### Cột sống

| | OAR app tự vẽ | Model cần chạy | Thời gian |
|---|---|---|---|
| **Triệt căn** | SpinalCord, Esophagus, Heart, Lung_L, Lung_R, Lungs, Kidney_L, Kidney_R, Liver, Stomach, Bowel_Small, Vertebrae (×25) | toàn thân: nội tạng, đốt sống, tim mạch, cơ–xương | ≈ 4 |
| **Triệu chứng** | SpinalCord, Esophagus, Heart, Lungs, Kidney_L, Kidney_R, Bowel_Small | toàn thân: nội tạng, tim mạch, cơ–xương | ≈ 3 |

**Bác sĩ tự vẽ:** SpinalCanal / Cauda equina (SBRT)  
*Ghi chú:* Triệt căn (SBRT) có thêm các đốt sống (~1 đơn vị thời gian) để định vị; cơ quan ngoài trường chụp tự bỏ qua.

### Xương chậu / khớp háng

| | OAR app tự vẽ | Model cần chạy | Thời gian |
|---|---|---|---|
| **Triệt căn** | Bladder, Bowel_Small, Colon, Femur_L, Femur_R, SpinalCord | toàn thân: nội tạng, cơ–xương | ≈ 2 |
| **Triệu chứng** | Bladder, Bowel_Small, Colon | toàn thân: nội tạng | ≈ 1 |

**Bác sĩ tự vẽ:** Rectum  
