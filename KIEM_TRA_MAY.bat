@echo off
title Kiem tra may cho QuanContour
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\kiem_tra_may.ps1"
echo.
pause
