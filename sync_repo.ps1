# =======================================================
# BankBin GitHub 仓库同步脚本
# =======================================================

param(
    [string]$msg = "Update project"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " 开始同步源码至 GitHub" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 1. 检查并提交本地源码变动
$status = git status --porcelain
if ($status) {
    Write-Host ""
    Write-Host "[1/2] 发现工作区有变动，正在自动提交..." -ForegroundColor Yellow
    git add .
    git commit -m "$msg"
} else {
    Write-Host ""
    Write-Host "[1/2] 工作区整洁，无需重复提交..." -ForegroundColor Green
}

# 2. 推送源码到 GitHub
Write-Host ""
Write-Host "[2/2] 正在将项目同步至 GitHub..." -ForegroundColor Magenta
git push origin main
if ($LASTEXITCODE -eq 0) {
    Write-Host ">> GitHub 同步成功！" -ForegroundColor Green
} else {
    Write-Host ">> GitHub 遇到网络超时或连接失败，可稍后重试。" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " 同步流程处理完成！ " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan