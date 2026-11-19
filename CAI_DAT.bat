@echo off
title Cai dat QuanContour
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\cai_dat_windows.ps1"
echo.
pause
