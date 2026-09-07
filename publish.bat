@echo off
chcp 65001 >nul
powershell -ExecutionPolicy Bypass -File "%~dp0publish_release.ps1" "%*"
pause
