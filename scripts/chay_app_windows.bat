@echo off
title QuanContour (giu cua so nay mo khi dang dung app)
cd /d "%~dp0\.."
if not exist ".venv\Scripts\oar-contour.exe" (
  echo Chua cai dat. Chuot phai scripts\cai_dat_windows.ps1 -^> Run with PowerShell.
  pause
  exit /b 1
)
".venv\Scripts\oar-contour.exe" app
pause
