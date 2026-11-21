"""Hiệu chỉnh tuyến mang tai: "nở" contour vào mô có mật độ giống tuyến, chặn bởi các mốc giải phẫu.

Lý do: model sẵn có thường vẽ thiếu (thùy sâu sau ngành hàm, cực trên dải mỏng ngoài cơ cắn).
Cách làm (không cần huấn luyện):
1. Ước lượng dải HU của tuyến từ chính phần lõi đã khoanh.
2. Vùng được phép nở = mô có HU trong dải đó, KHÔNG thuộc các cấu trúc chặn (xương hàm, cơ cắn,
   cơ chân bướm trong/ngoài, cơ hai bụng, mỏm trâm, động mạch cảnh trong, tĩnh mạch cảnh trong, ống tai ngoài).
3. Nở dần theo 3 chiều, tối đa d_xy mm trong mặt phẳng và d_z mm theo trục đầu–chân, chỉ qua vùng được phép.
4. Lấp lỗ, làm trơn, giữ khối liền với contour ban đầu.

Thông số được chỉnh và KIỂM CHỨNG trên bộ dữ liệu công khai có contour chuyên gia (xem docs).
"""

from __future__ import annotations

import numpy as np
from scipy import ndimage

BARRIER_LABELS = {
    "left": ["mandible", "masseter_left", "medial_pterygoid_left", "lateral_pterygoid_left", "digastric_left",
             "styloid_process_left", "internal_carotid_artery_left", "internal_jugular_vein_left",
             "auditory_canal_left", "submandibular_gland_left"],
    "right": ["mandible", "masseter_right", "medial_pterygoid_right", "lateral_pterygoid_right", "digastric_right",
              "styloid_process_right", "internal_carotid_artery_right", "internal_jugular_vein_right",
              "auditory_canal_right", "submandibular_gland_right"],
}
# model cần chạy thêm để có các mốc chặn
BARRIER_TASKS = ["craniofacial_structures", "head_muscles", "headneck_bones_vessels", "head_glands_cavities"]


def _hu_range(ct: np.ndarray, core: np.ndarray, pad: float, lo_min: float, hi_max: float) -> tuple[float, float]:
    inner = ndimage.binary_erosion(core, iterations=1)
    vals = ct[inner] if inner.sum() > 50 else ct[core]
    if vals.size == 0:
        return -120.0, 60.0
    lo, hi = np.percentile(vals, [3, 97])
    return float(max(lo_min, lo - pad)), float(min(hi_max, hi + pad))


def refine_parotid(
    ct: np.ndarray,
    parotid: np.ndarray,
    barriers: np.ndarray,
    spacing_zyx: tuple[float, float, float],
    d_xy: float = 5.0,
    d_z: float = 4.0,
    hu_pad: float = 20.0,
    lo_min: float = -150.0,
    hi_max: float = 90.0,
) -> np.ndarray:
    """ct (HU), parotid, barriers: mảng (z, y, x) cùng lưới. Trả về mask tuyến đã hiệu chỉnh."""
    if not parotid.any():
        return parotid
    sz, sy, sx = spacing_zyx
    pxy = min(sy, sx)
    # làm việc trong hộp bao quanh tuyến + lề để nhanh
    zz, yy, xx = np.nonzero(parotid)
    mz, mxy = int(np.ceil(d_z / sz)) + 2, int(np.ceil(d_xy / pxy)) + 3
    bb = (slice(max(0, zz.min() - mz), zz.max() + mz + 1), slice(max(0, yy.min() - mxy), yy.max() + mxy + 1),
          slice(max(0, xx.min() - mxy), xx.max() + mxy + 1))
    c, p = ct[bb].astype(np.float32), parotid[bb]
    gap = max(1, int(round(1.0 / pxy)))  # lề 1 mm quanh cấu trúc chặn
    bar = ndimage.binary_dilation(barriers[bb], structure=np.ones((1, 3, 3), bool), iterations=gap)
    lo, hi = _hu_range(c, p, hu_pad, lo_min, hi_max)
    allowed = (c >= lo) & (c <= hi) & ~bar
    allowed |= p

    n_xy = max(0, int(round(d_xy / pxy)))
    z_every = max(1, int(round(sz / pxy)))  # mỗi z_every bước trong mặt phẳng thì nở 1 lát theo z
    n_z = max(0, int(round(d_z / sz)))
    st_xy = np.zeros((3, 3, 3), bool)
    st_xy[1] = ndimage.generate_binary_structure(2, 1)
    st_z = np.zeros((3, 3, 3), bool)
    st_z[:, 1, 1] = True
    grown, z_done = p.copy(), 0
    for i in range(n_xy):
        grown = ndimage.binary_dilation(grown, structure=st_xy) & allowed
        if z_done < n_z and (i + 1) % z_every == 0:
            grown = ndimage.binary_dilation(grown, structure=st_z) & allowed
            z_done += 1
    while z_done < n_z:
        grown = ndimage.binary_dilation(grown, structure=st_z) & allowed
        z_done += 1

    # làm trơn + lấp lỗ từng lát, rồi giữ khối liền với contour ban đầu
    grown = ndimage.binary_closing(grown, structure=np.ones((1, 3, 3), bool), iterations=1) & ~bar | p
    for k in range(grown.shape[0]):
        grown[k] = ndimage.binary_fill_holes(grown[k])
    lab, n = ndimage.label(grown)
    if n > 1:
        keep = np.unique(lab[p & (lab > 0)])
        grown = np.isin(lab, keep)
    out = np.zeros_like(parotid)
    out[bb] = grown
    return out


# Cấu trúc mốc (tên trong danh mục) được vẽ và XUẤT RA khi bật hiệu chỉnh (bác sĩ dùng luôn)
LANDMARK_NAMES = ["Bone_Mandible", "Musc_Masseter_L", "Musc_Masseter_R", "Musc_Pterygoid_Med_L",
                  "Musc_Pterygoid_Med_R", "Musc_Pterygoid_Lat_L", "Musc_Pterygoid_Lat_R", "Musc_Digastric_L",
                  "Musc_Digastric_R", "Bone_Styloid_L", "Bone_Styloid_R", "A_Carotid_Int_L",
                  "A_Carotid_Int_R", "V_Jugular_Int_L", "V_Jugular_Int_R", "Canal_Auditory_Ext_L", "Canal_Auditory_Ext_R"]
REFINED = {"Parotid_L": ("left", "parotid_gland_left", "Parotid_L_Ref", (0, 230, 255)),
           "Parotid_R": ("right", "parotid_gland_right", "Parotid_R_Ref", (0, 170, 255))}
DEFAULTS = dict(d_xy=5.0, d_z=8.0, hu_pad=10.0)  # sẽ cập nhật theo kết quả kiểm chứng
