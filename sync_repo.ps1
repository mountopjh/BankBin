# =======================================================
# BankBin 双平台协同同步脚本 (GitHub 源码 + GitCode 纯EXE)
# =======================================================

param(
    [string]$msg = "Update project"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " 开始双平台同步 (GitHub源码 + GitCode纯EXE)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 1. 检查并提交本地源码变动
$status = git status --porcelain
if ($status) {
    Write-Host ""
    Write-Host "[1/3] 发现工作区有代码变动，正在自动提交..." -ForegroundColor Yellow
    git add .
    git commit -m "$msg"
} else {
    Write-Host ""
    Write-Host "[1/3] 源码工作区整洁，无需重复提交..." -ForegroundColor Green
}

# 2. 推送源码到 GitHub (官方开源代码主干)
Write-Host ""
Write-Host "[2/3] 正在将项目源码同步至 GitHub..." -ForegroundColor Magenta
git push github main
if ($LASTEXITCODE -eq 0) {
    Write-Host ">> GitHub 源码同步成功！" -ForegroundColor Green
} else {
    Write-Host ">> GitHub 遇到网络超时或连接失败，可稍后重试。" -ForegroundColor Yellow
}

# 3. 推送纯 EXE 到 GitCode (国内极速下载通道，不上传源码)
Write-Host ""
Write-Host "[3/3] 正在将已编译 EXE 发布到 GitCode (仅含 EXE，无源码)..." -ForegroundColor Magenta
$gitcodeScript = Join-Path $PSScriptRoot "sync_gitcode_exe.ps1"
if (Test-Path $gitcodeScript) {
    & $gitcodeScript
} else {
    Write-Host "[ERROR] 未找到 $gitcodeScript 脚本！" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " 所有同步流程处理完成！ " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan