#!/bin/bash
# Tạo "QuanContour.app" trong thư mục Applications của người dùng.
# Bấm đúp app -> mở giao diện QuanContour trên trình duyệt.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
APP="$HOME/Applications/QuanContour.app"

if [ ! -x "$REPO/.venv/bin/oar-contour" ]; then
  echo "Chưa cài công cụ trong $REPO/.venv. Làm bước cài đặt trong HUONG_DAN_MAC.md trước." >&2
  exit 1
fi

rm -rf "$HOME/Applications/OAR Contour.app"  # bản tên cũ
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources" "$HOME/OAR_ketqua"

cat > "$APP/Contents/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleName</key><string>QuanContour</string>
  <key>CFBundleDisplayName</key><string>QuanContour</string>
  <key>CFBundleIdentifier</key><string>local.quancontour.app</string>
  <key>CFBundleVersion</key><string>1</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>CFBundleExecutable</key><string>QuanContour</string>
  <key>CFBundleIconFile</key><string>AppIcon</string>
  <key>LSMinimumSystemVersion</key><string>11.0</string>
</dict>
</plist>
PLIST

cat > "$APP/Contents/MacOS/QuanContour" <<SCRIPT
#!/bin/bash
cd "$REPO"
exec "$REPO/.venv/bin/oar-contour" app >> "\$HOME/OAR_ketqua/app.log" 2>&1
SCRIPT
chmod +x "$APP/Contents/MacOS/QuanContour"

# Biểu tượng: lấy icon hệ thống (nếu có) cho dễ nhận
for icon in \
  "/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/ToolbarCustomizeIcon.icns" \
  "/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/GenericApplicationIcon.icns"; do
  if [ -f "$icon" ]; then cp "$icon" "$APP/Contents/Resources/AppIcon.icns"; break; fi
done
touch "$APP"

echo "Đã tạo: $APP"
echo "Mở Finder > Applications (của bạn) hoặc Launchpad, bấm đúp 'QuanContour'. Có thể kéo vào Dock."
open -R "$APP" 2>/dev/null || true
