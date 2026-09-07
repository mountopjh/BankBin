# =======================================================
# BankBin 双平台同步推送脚本 (GitCode 主推 + GitHub 同步)
# =======================================================

param(
    [string]$msg = "Update project"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " 开始双平台同步推送 (GitCode + GitHub) " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 1. 检查是否有未暂存或未提交的代码
$status = git status --porcelain
if ($status) {
    Write-Host "[1/3] 发现有未提交的代码变动，自动暂存并提交..." -ForegroundColor Yellow
    git add .
    git commit -m $msg
} else {
    Write-Host "[1/3] 工作区干净，准备推送当前最新 Commit..." -ForegroundColor Green
}

# 2. 推送国内 GitCode (主干)
Write-Host "`n[2/3] 正在推送到国内 GitCode..." -ForegroundColor Magenta
git push gitcode main
if ($LASTEXITCODE -eq 0) {
    Write-Host ">> GitCode 推送成功！" -ForegroundColor Green
} else {
    Write-Host ">> GitCode 推送遇到异常，请检查网络或远程源地址！" -ForegroundColor Red
}

# 3. 推送 GitHub (海外主干)
Write-Host "`n[3/3] 正在同步推送到 GitHub..." -ForegroundColor Magenta
git push github main
if ($LASTEXITCODE -eq 0) {
    Write-Host ">> GitHub 同步成功！" -ForegroundColor Green
} else {
    Write-Host ">> GitHub 遇到网络超时或连接失败，由于国内 GitCode 已成功保存，可稍后重试 GitHub 同步。" -ForegroundColor Yellow
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " 同步流程结束！ " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
