@echo off
title Cap nhat QuanContour
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\cap_nhat_windows.ps1"
echo.
pause
