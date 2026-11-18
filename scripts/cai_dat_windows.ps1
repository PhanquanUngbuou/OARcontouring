# Cài OAR Contour trên Windows (chạy 1 lần). Cách chạy: chuột phải file này -> "Run with PowerShell".
$ErrorActionPreference = "Stop"
$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo
Write-Host "== Cài OAR Contour vào $Repo ==" -ForegroundColor Cyan

# 1. uv: tự cài Python 3.12 và thư viện, không cần quyền admin
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "Cài uv..."
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    $env:Path = "$env:USERPROFILE\.local\bin;$env:Path"
}

# 2. Môi trường Python riêng cho app
if (-not (Test-Path ".venv")) { uv venv --python 3.12 }

# 3. Thư viện. --torch-backend=auto: có card NVIDIA thì tự chọn PyTorch bản CUDA phù hợp driver
Write-Host "Cài thư viện (PyTorch khoảng 2-3 GB, cần mạng ổn định)..."
uv pip install --torch-backend=auto -e ".[model]"

# 4. Kiểm tra GPU
$gpu = & .\.venv\Scripts\python.exe -c "import torch; print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else '')"
if ($gpu) {
    Write-Host "GPU NVIDIA sẵn sàng: $gpu" -ForegroundColor Green
} else {
    Write-Host "CHƯA dùng được GPU NVIDIA: app sẽ chạy bằng CPU (chậm)." -ForegroundColor Yellow
    Write-Host "Kiểm tra: máy có card NVIDIA không, driver NVIDIA đã cập nhật chưa (lệnh nvidia-smi)." -ForegroundColor Yellow
}

# 5. Biểu tượng trên Desktop
$desktop = [Environment]::GetFolderPath("Desktop")
$ws = New-Object -ComObject WScript.Shell
$lnk = $ws.CreateShortcut("$desktop\OAR Contour.lnk")
$lnk.TargetPath = "$Repo\scripts\chay_app_windows.bat"
$lnk.WorkingDirectory = $Repo
$lnk.IconLocation = "$env:SystemRoot\System32\imageres.dll,190"
$lnk.Save()
Write-Host "Xong. Bấm đúp 'OAR Contour' trên Desktop để mở app." -ForegroundColor Green
Read-Host "Nhấn Enter để đóng"
