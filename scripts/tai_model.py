"""Tải sẵn trọng số các model (để lúc chạy hàng loạt không phải chờ tải). Chạy: python scripts/tai_model.py"""
import totalsegmentator.map_tasks_config as m
from totalsegmentator.config import set_config_key, setup_totalseg
from totalsegmentator.libs import download_pretrained_weights

setup_totalseg()
set_config_key("send_usage_stats", False)
set_config_key("statistics_disclaimer_shown", True)
ids = [291, 292, 293, 294, 295, 297, 298]  # toàn thân: 5 phần, chế độ nhanh, định vị 6 mm
for task in ["head_glands_cavities", "craniofacial_structures", "breasts", "head_muscles", "headneck_bones_vessels"]:
    tid = m.TASK_CONFIGS[task]["task_id"]
    ids += tid if isinstance(tid, list) else [tid]
for i in ids:
    download_pretrained_weights(i)
    print("đã có model", i, flush=True)
