#!/bin/bash
# Khoanh hàng loạt trên máy cloud rồi đóng gói kết quả để tải về MacBook.
# Chạy:  bash cloud_batch.sh <thư mục các ca đã ẩn danh> [phác đồ, mặc định headneck]
set -euo pipefail
CASES="$1"; PROTO="${2:-headneck}"
WORK="${WORK:-/workspace}"
cd "$WORK/OARcontouring" && . .venv/bin/activate
quancontour batch "$CASES" --protocol "$PROTO" --intent curative --results "$WORK/ketqua" --device gpu \
  || echo "CÓ CA LỖI: xem log ở trên; các ca chạy được vẫn được đóng gói."
cd "$WORK" && tar czf ketqua.tar.gz ketqua
echo
echo "Xong. Tải file $WORK/ketqua.tar.gz về MacBook (xem HUONG_DAN_CLOUD.md, mục 5)."
