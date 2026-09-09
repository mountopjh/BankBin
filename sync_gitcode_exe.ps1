# =======================================================
# BankBin GitCode EXE 专属上传脚本 (仅上传 EXE，不传任何源码)
# =======================================================

param(
    [string]$remoteUrl = "git@gitcode.com:mountop2026/BankBin.git"
)

$scriptDir = $PSScriptRoot
if (-not $scriptDir) { $scriptDir = (Get-Location).Path }

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host " 正在同步 EXE 到 GitCode (国内极速分发通道)" -ForegroundColor Cyan
Write-Host " 规则: 仅上传已编译 EXE，坚决不上传任何源码 " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 1. 扫描待发布的 EXE 文件
$releaseDir = Join-Path $scriptDir "BankBin_Releases"
$exeFiles = @()
if (Test-Path $releaseDir) {
    $exeFiles += Get-ChildItem -Path $releaseDir -Filter "BankBin_*.exe" -File
}

# 根目录下若有独立的 BankBin_*.exe 也加入
$rootExes = Get-ChildItem -Path $scriptDir -Filter "BankBin_*.exe" -File
foreach ($re in $rootExes) {
    if (-not ($exeFiles | Where-Object { $_.Name -eq $re.Name })) {
        $exeFiles += $re
    }
}

if ($exeFiles.Count -eq 0) {
    Write-Host "[WARN] 未在 BankBin_Releases 或根目录找到任何 BankBin_*.exe 文件！" -ForegroundColor Yellow
    Write-Host ">> GitCode 仅用于托管与分发 EXE 程序。如需更新，请先运行 build_root_exe.bat 打包后再同步。" -ForegroundColor Yellow
    return
}

# 排序并展示待上传的 EXE 文件
$exeFiles = $exeFiles | Sort-Object Name
Write-Host ">> 检索到待上传的 EXE 文件 ($($exeFiles.Count) 个):" -ForegroundColor Green
$exeFiles | ForEach-Object {
    $sizeMB = [math]::Round($_.Length / 1MB, 2)
    Write-Host "   - $($_.Name) ($sizeMB MB)" -ForegroundColor Gray
}

# 2. 建立纯净的临时暂存仓库进行发布
$stageDir = Join-Path $env:TEMP "BankBin_GitCode_Deploy"
if (Test-Path $stageDir) { Remove-Item -Recurse -Force $stageDir }
New-Item -ItemType Directory -Path $stageDir | Out-Null

Push-Location $stageDir
try {
    git init -b main | Out-Null
    git config user.name "mountopjh"
    git config user.email "mountopjh@users.noreply.github.com"
    git remote add gitcode $remoteUrl

    # 仅复制 EXE 文件，绝对不包含任何代码文件、配置文件或文档
    foreach ($f in $exeFiles) {
        Copy-Item $f.FullName -Destination .
        git add $f.Name
    }

    $fileNames = ($exeFiles | Select-Object -ExpandProperty Name) -join ", "
    git commit -m "Release binaries: $fileNames" | Out-Null

    Write-Host ">> 正在推送至 GitCode main 分支 (EXE-Only)..." -ForegroundColor Magenta
    git push gitcode main --force
    if ($LASTEXITCODE -eq 0) {
        Write-Host ">> GitCode 同步成功！线上仓库仅含 EXE 程序，无任何源码。" -ForegroundColor Green
    } else {
        Write-Host ">> GitCode 推送失败，请检查网络连接或 SSH 密钥权限。" -ForegroundColor Red
    }
}
finally {
    Pop-Location
    if (Test-Path $stageDir) { Remove-Item -Recurse -Force $stageDir }
}