# Kiểm tra máy Windows có chạy được QuanContour không. Chỉ ĐỌC thông tin, không thay đổi gì trên máy.
$ErrorActionPreference = "Continue"
try { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 } catch {}
$ok = 0; $warn = 0; $bad = 0
function Show($status, $label, $value) {
    $color = @{ "OK" = "Green"; "CAN XEM" = "Yellow"; "KHONG DAT" = "Red"; "INFO" = "Gray" }[$status]
    Write-Host ("[{0,-9}] {1,-22} {2}" -f $status, $label, $value) -ForegroundColor $color
    if ($status -eq "OK") { $script:ok++ } elseif ($status -eq "CAN XEM") { $script:warn++ } elseif ($status -eq "KHONG DAT") { $script:bad++ }
}
Write-Host "===== KIEM TRA MAY CHO QUANCONTOUR =====" -ForegroundColor Cyan
# Windows 7 chỉ có PowerShell 2: không có Get-CimInstance / Invoke-WebRequest -> dùng WMI và WebClient
$psMajor = $PSVersionTable.PSVersion.Major
function Get-Info($class, $filter) {
    if (Get-Command Get-CimInstance -ErrorAction SilentlyContinue) {
        if ($filter) { Get-CimInstance $class -Filter $filter } else { Get-CimInstance $class }
    } else {
        if ($filter) { Get-WmiObject $class -Filter $filter } else { Get-WmiObject $class }
    }
}
Show "INFO" "PowerShell" "$($PSVersionTable.PSVersion)"

# Windows
$os = Get-Info Win32_OperatingSystem
$build = [int]$os.BuildNumber
$osText = "$($os.Caption) (build $build, $($os.OSArchitecture))"
if ($build -ge 17763 -and $os.OSArchitecture -match "64") { Show "OK" "Windows" $osText }
elseif ($build -ge 10240) { Show "CAN XEM" "Windows" "$osText - nen cap nhat Windows 10 ban moi hon" }
else { Show "KHONG DAT" "Windows" "$osText - Windows 7/8 KHONG chay duoc PyTorch, can nang cap Windows 10/11 64-bit (hoac cai Linux)" }

# CPU, RAM, ổ đĩa
$cpu = Get-Info Win32_Processor | Select-Object -First 1
Show "INFO" "CPU" "$($cpu.Name.Trim()) - $($cpu.NumberOfCores) nhan"
$ram = [math]::Round($os.TotalVisibleMemorySize / 1MB)
if ($ram -ge 32) { Show "OK" "RAM" "$ram GB" } elseif ($ram -ge 16) { Show "CAN XEM" "RAM" "$ram GB (du dung, 32 GB tot hon)" } else { Show "KHONG DAT" "RAM" "$ram GB (can toi thieu 16 GB)" }
$disk = Get-Info Win32_LogicalDisk "DeviceID='C:'"
$free = [math]::Round($disk.FreeSpace / 1GB)
if ($free -ge 30) { Show "OK" "O C: con trong" "$free GB" } else { Show "KHONG DAT" "O C: con trong" "$free GB (can >= 30 GB)" }

# Card đồ hoạ
$gpus = Get-Info Win32_VideoController | ForEach-Object { $_.Name }
Show "INFO" "Card do hoa" ($gpus -join "; ")
$smi = Get-Command nvidia-smi -ErrorAction SilentlyContinue
if (-not $smi -and (Test-Path "C:\Windows\System32\nvidia-smi.exe")) { $smi = "C:\Windows\System32\nvidia-smi.exe" }
if ($smi) {
    $q = & $smi --query-gpu=name,memory.total,driver_version --format=csv,noheader,nounits 2>$null | Select-Object -First 1
    $cap = & $smi --query-gpu=compute_cap --format=csv,noheader 2>$null | Select-Object -First 1
    if ($q) {
        $parts = $q.Split(",") | ForEach-Object { $_.Trim() }
        $vram = [math]::Round([double]$parts[1] / 1024)
        $text = "$($parts[0]), $vram GB, driver $($parts[2])" + $(if ($cap -and $cap -notmatch "Field") { ", compute $cap" } else { "" })
        if ($cap -and $cap -notmatch "Field" -and [double]$cap -lt 7.0) {
            Show "CAN XEM" "GPU NVIDIA" "$text - card doi cu, PyTorch moi co the khong ho tro (se chay CPU)"
        } elseif ($vram -ge 8) { Show "OK" "GPU NVIDIA" $text }
        else { Show "CAN XEM" "GPU NVIDIA" "$text - VRAM < 8 GB, co the phai chay che do nhanh/CPU" }
    } else { Show "CAN XEM" "GPU NVIDIA" "Co nvidia-smi nhung khong doc duoc - can cap nhat driver NVIDIA" }
} else {
    if ($gpus -match "NVIDIA") { Show "CAN XEM" "GPU NVIDIA" "Co card NVIDIA nhung chua co driver day du (nvidia-smi) - can cai driver moi" }
    else { Show "CAN XEM" "GPU NVIDIA" "Khong co - app se chay bang CPU (cham, 5-20 phut/ca)" }
}

# Mạng: cần lúc cài đặt và lần đầu tải model
if ($psMajor -lt 3) {
    Show "CAN XEM" "Mang" "Windows 7 / PowerShell $psMajor khong kiem tra duoc (thieu TLS 1.2). Mo trinh duyet thu vao https://pypi.org"
} else {
foreach ($site in @("https://astral.sh", "https://pypi.org", "https://download.pytorch.org", "https://github.com", "https://objects.githubusercontent.com")) {
    try {
        Invoke-WebRequest -Uri $site -Method Head -UseBasicParsing -TimeoutSec 10 | Out-Null
        Show "OK" "Mang" $site
    } catch {
        if ($_.Exception.Response) { Show "OK" "Mang" $site }   # trang trả lỗi HTTP vẫn là có kết nối
        else { Show "KHONG DAT" "Mang" "$site - khong vao duoc (nho IT mo tam thoi khi cai dat)" }
    }
}
}

# Quyền chạy script
$pol = Get-ExecutionPolicy -List | Where-Object { $_.Scope -eq "MachinePolicy" -or $_.Scope -eq "UserPolicy" } | Where-Object { $_.ExecutionPolicy -ne "Undefined" }
if ($pol) { Show "CAN XEM" "Chinh sach script" "Bi khoa boi Group Policy ($($pol.ExecutionPolicy -join ', ')) - co the can IT cho phep" }
else { Show "OK" "Chinh sach script" "Chay duoc (CAI_DAT.bat tu bo qua khoa mac dinh)" }

Write-Host ""
if ($bad -eq 0) { Write-Host "KET LUAN: May dung duoc. Bam dup CAI_DAT.bat de cai." -ForegroundColor Green }
else { Write-Host "KET LUAN: Con $bad muc KHONG DAT (mau do). Chup man hinh gui lai de duoc huong dan." -ForegroundColor Red }
Write-Host "Chup man hinh cua so nay gui lai neu can ho tro."
