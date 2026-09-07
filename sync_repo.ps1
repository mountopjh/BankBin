# =======================================================
# BankBin Sync Script (GitCode + GitHub)
# =======================================================

param(
    [string]$msg = "Update project"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Starting sync to GitCode and GitHub... " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 1. Check workspace
$status = git status --porcelain
if ($status) {
    Write-Host "[1/3] Detected changes, committing..." -ForegroundColor Yellow
    git add .
    git commit -m "$msg"
} else {
    Write-Host "[1/3] Working tree clean, ready to push..." -ForegroundColor Green
}

# 2. Push to GitCode
Write-Host "
[2/3] Pushing to GitCode (Primary)..." -ForegroundColor Magenta
git push gitcode main
if ($LASTEXITCODE -eq 0) {
    Write-Host ">> GitCode push succeeded!" -ForegroundColor Green
} else {
    Write-Host ">> GitCode push failed. Please check network." -ForegroundColor Red
}

# 3. Push to GitHub
Write-Host "
[3/3] Syncing to GitHub..." -ForegroundColor Magenta
git push github main
if ($LASTEXITCODE -eq 0) {
    Write-Host ">> GitHub sync succeeded!" -ForegroundColor Green
} else {
    Write-Host ">> GitHub sync timed out or failed. Code is safely stored in GitCode." -ForegroundColor Yellow
}

Write-Host "
========================================" -ForegroundColor Cyan
Write-Host " Sync completed! " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
