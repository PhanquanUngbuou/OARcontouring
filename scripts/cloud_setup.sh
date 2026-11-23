#!/bin/bash
# Cài QuanContour trên máy cloud có GPU NVIDIA (Linux, ví dụ mẫu "PyTorch" của RunPod).
# Chạy:  bash cloud_setup.sh
set -euo pipefail
WORK="${WORK:-/workspace}"
mkdir -p "$WORK" && cd "$WORK"
if [ ! -d OARcontouring ]; then
  git clone https://github.com/PhanquanUngbuou/OARcontouring.git
fi
cd OARcontouring && git pull --ff-only
# dùng lại PyTorch bản GPU có sẵn của máy thuê, không tải lại
python3 -m venv --system-site-packages .venv
. .venv/bin/activate
pip install -q --upgrade pip
pip install -q -e ".[model]"
python - <<'PY'
import torch
if torch.cuda.is_available():
    print("GPU sẵn sàng:", torch.cuda.get_device_name(0))
else:
    print("CẢNH BÁO: không thấy GPU. Kiểm tra lại loại máy đã thuê.")
PY
python scripts/tai_model.py
echo
echo "Cài xong. Bước tiếp theo xem HUONG_DAN_CLOUD.md (mục 4)."
