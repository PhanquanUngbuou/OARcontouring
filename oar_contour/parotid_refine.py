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
    side: str | None = None,
    lateral_max: float | None = None,
    posterior_max: float | None = None,
    post_sign: int = 1,
    left_sign: int = 1,
) -> np.ndarray:
    """ct (HU), parotid, barriers: mảng (z, y, x) cùng lưới. Trả về mask tuyến đã hiệu chỉnh.

    side + lateral_max/posterior_max (mm): giới hạn nở ra phía ngoài (về phía da) và phía sau (về phía cơ ức đòn
    chũm), vì tuyến thường bị vẽ thiếu ở phía trong (thùy sâu), phía trước và cực trên.
    post_sign / left_sign: +1 nếu chỉ số y tăng = phía sau / chỉ số x tăng = bên trái bệnh nhân (ảnh nằm ngửa
    chuẩn); -1 nếu ngược lại (pipeline tính từ hướng ảnh DICOM)."""
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

    if side and (lateral_max is not None or posterior_max is not None):
        # vị trí so với điểm gần nhất của contour ban đầu
        _, (iz, iy, ix) = ndimage.distance_transform_edt(~p, sampling=(sz, sy, sx), return_indices=True)
        zz_, yy_, xx_ = np.indices(p.shape)
        dy = (yy_ - iy) * sy * post_sign  # >0: ra sau
        dx = (xx_ - ix) * sx * left_sign  # >0: về bên trái bệnh nhân
        lat = dx if side == "left" else -dx  # >0: ra ngoài
        keep = np.ones(p.shape, bool)
        if posterior_max is not None:
            keep &= dy <= posterior_max
        if lateral_max is not None:
            keep &= lat <= lateral_max
        grown &= keep | p

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
# chỉnh trên HaN-Seg ca 1–4, kiểm chứng ca 5–8 (docs/KIEM_CHUNG_PAROTID.md)
DEFAULTS = dict(d_xy=10.0, d_z=8.0, hu_pad=10.0, lateral_max=3.0, posterior_max=1.0)


def deep_lobe(
    ct: np.ndarray,
    parotid: np.ndarray,
    barriers: np.ndarray,
    corridor_marks: np.ndarray,
    medial_marks: np.ndarray,
    side: str,
    spacing_zyx: tuple[float, float, float],
    d_max: float = 20.0,
    hu_pad: float = 10.0,
    lo_min: float = -150.0,
    hi_max: float = 90.0,
) -> np.ndarray:
    """Bước 2: nở có định hướng vào thùy sâu, từng lát cắt.

    Hành lang = bao lồi (tuyến + cơ chân bướm trong + mỏm trâm + động mạch cảnh trong) trên lát đó, không vượt
    vào phía trong bờ ngoài của mỏm trâm / động mạch cảnh trong (medial_marks), trừ các cấu trúc chặn.
    Chỉ nở trong mặt phẳng, tối đa d_max mm, qua mô có HU giống tuyến.
    side: "left" (bên trái bệnh nhân = x lớn) hoặc "right".
    """
    import cv2

    if not parotid.any():
        return parotid
    sz, sy, sx = spacing_zyx
    pxy = min(sy, sx)
    lo, hi = _hu_range(ct, parotid, hu_pad, lo_min, hi_max)
    gap = max(1, int(round(1.0 / pxy)))
    out = parotid.copy()
    n_iter = int(round(d_max / pxy))
    st = ndimage.generate_binary_structure(2, 1)
    for k in np.nonzero(parotid.any(axis=(1, 2)))[0]:
        p = parotid[k]
        marks = corridor_marks[k] | p
        if not medial_marks[k].any() or not corridor_marks[k].any():
            continue
        pts = np.column_stack(np.nonzero(marks)[::-1]).astype(np.int32)  # (x, y)
        hull = np.zeros(p.shape, np.uint8)
        cv2.fillConvexPoly(hull, cv2.convexHull(pts), 1)
        corridor = hull.astype(bool)
        # không vượt vào phía trong bờ ngoài của mỏm trâm / động mạch cảnh trong
        mx = np.nonzero(medial_marks[k].any(axis=0))[0]
        xs = np.arange(p.shape[1])
        corridor &= (xs >= mx.max())[None, :] if side == "left" else (xs <= mx.min())[None, :]
        bar = ndimage.binary_dilation(barriers[k], structure=np.ones((3, 3), bool), iterations=gap)
        allowed = corridor & ~bar & (ct[k] >= lo) & (ct[k] <= hi) | p
        g = p.copy()
        for _ in range(n_iter):
            nxt = ndimage.binary_dilation(g, structure=st) & allowed
            if (nxt == g).all():
                break
            g = nxt
        g = ndimage.binary_closing(g, structure=np.ones((3, 3), bool)) & (allowed | p)
        out[k] = ndimage.binary_fill_holes(g)
    return out


CORRIDOR_LABELS = {
    "left": ["medial_pterygoid_left", "styloid_process_left", "internal_carotid_artery_left"],
    "right": ["medial_pterygoid_right", "styloid_process_right", "internal_carotid_artery_right"],
}
MEDIAL_LABELS = {
    "left": ["styloid_process_left", "internal_carotid_artery_left"],
    "right": ["styloid_process_right", "internal_carotid_artery_right"],
}
