# Cập nhật QuanContour lên bản mới nhất trên GitHub (không cần git). Giữ nguyên .venv và kết quả các ca.
$ErrorActionPreference = "Stop"
try { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 } catch {}
$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo
if (Test-Path ".git") {
    Write-Host "Thu muc dung git: chay 'git pull'..." -ForegroundColor Cyan
    git pull
} else {
    $tmp = Join-Path $env:TEMP ("quancontour_" + [guid]::NewGuid().ToString("N"))
    New-Item -ItemType Directory $tmp | Out-Null
    Write-Host "Tai ban moi nhat tu GitHub..." -ForegroundColor Cyan
    Invoke-WebRequest -UseBasicParsing -Uri "https://github.com/PhanquanUngbuou/OARcontouring/archive/refs/heads/main.zip" -OutFile "$tmp\main.zip"
    Expand-Archive "$tmp\main.zip" -DestinationPath $tmp
    $src = Get-ChildItem $tmp -Directory | Select-Object -First 1
    # Chép đè mã nguồn, KHÔNG đụng tới .venv
    robocopy $src.FullName $Repo /E /XD .venv /NFL /NDL /NJH /NJS /NP | Out-Null
    Remove-Item $tmp -Recurse -Force
}
$env:Path = "$env:USERPROFILE\.local\bin;$env:Path"
Write-Host "Cap nhat thu vien (neu co thay doi)..." -ForegroundColor Cyan
uv pip install --torch-backend=auto -e ".[model]"
Write-Host "Xong. Mo lai QuanContour tren Desktop." -ForegroundColor Green
