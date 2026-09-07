@echo off
chcp 65001 >nul
powershell -ExecutionPolicy Bypass -File "%~dp0sync_repo.ps1" "%*"
pause
