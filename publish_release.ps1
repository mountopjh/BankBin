# =======================================================
# BankBin Dual-Platform Release Script (GitHub + GitCode)
# =======================================================

param(
    [string]$tag = ""
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  BankBin 双平台版本发布自动化工具        " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 1. 自动读取当前版本号
$manifestPath = "update_manifest.json"
if (Test-Path $manifestPath) {
    $manifest = Get-Content $manifestPath | ConvertFrom-Json
    if (-not $tag) {
        $tag = $manifest.version
    }
}
if (-not $tag) {
    $tag = "v1.7.7"
}
if (-not $manifest) {
    $manifest = [PSCustomObject]@{
        version = $tag
        download_url = ""
        sha256 = ""
    }
}

Write-Host "[1/5] 当前待发布版本: $tag" -ForegroundColor Green

# 2. 查找最新的打包 EXE
$releaseDir = "BankBin_Releases"
$latestExe = Get-ChildItem -Path $releaseDir -Filter "BankBin_*.exe" | Sort-Object Name -Descending | Select-Object -First 1

if ($latestExe) {
    Write-Host "[2/5] 找到待发布打包文件: $($latestExe.FullName) ($([math]::Round($latestExe.Length/1MB, 2)) MB)" -ForegroundColor Green
} else {
    Write-Host "[ERROR] 未在 $releaseDir 中找到已编译的 EXE 文件，请先运行 build_root_exe.bat 进行打包！" -ForegroundColor Red
    exit 1
}

# Make the update manifest describe the exact executable uploaded below.
$manifest.version = $tag
$manifest.download_url = "https://github.com/mountopjh/BankBin/releases/download/$tag/$($latestExe.Name)"
$manifest.sha256 = (Get-FileHash -LiteralPath $latestExe.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
$manifestJson = $manifest | ConvertTo-Json
$utf8WithoutBom = New-Object System.Text.UTF8Encoding($false)
$manifestFullPath = [System.IO.Path]::GetFullPath($manifestPath)
[System.IO.File]::WriteAllText($manifestFullPath, $manifestJson, $utf8WithoutBom)
Write-Host ">> 更新清单已同步: $($latestExe.Name)" -ForegroundColor Green

# 3. 提交未保存的修改并推送代码及 Tags 到 GitHub
Write-Host "
[3/5] 正在同步源码与版本标签到 GitHub..." -ForegroundColor Magenta
$status = git status --porcelain
if ($status) {
    git add .
    git commit -m "Release $tag"
}

# 检查 tag 是否存在，不存在则创建
$existingTag = git tag -l $tag
if (-not $existingTag) {
    git tag -a $tag -m "Release $tag"
    Write-Host ">> 本地创建标签: $tag" -ForegroundColor Green
}

# 仅推送到 GitHub
git push github main --tags
Write-Host ">> 源码与 Tags 已同步推送至 GitHub！" -ForegroundColor Green

# 4. 发布到 GitHub Releases
Write-Host "
[4/5] 正在发布到 GitHub Releases..." -ForegroundColor Magenta
$ghCheck = where.exe gh 2>$null
if ($ghCheck) {
    # 检查 release 是否已存在
    gh release view $tag --repo mountopjh/BankBin 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host ">> GitHub Release $tag 已存在，上传/更新附件..." -ForegroundColor Yellow
        gh release upload $tag $latestExe.FullName --clobber --repo mountopjh/BankBin
    } else {
        gh release create $tag $latestExe.FullName --title "BankBin $tag" --notes "Release $tag - BankBin 银行BIN码查询单文件绿色版 ($($latestExe.Name))" --repo mountopjh/BankBin
    }
    if ($LASTEXITCODE -eq 0) {
        Write-Host ">> GitHub Release 发布成功！" -ForegroundColor Green
    }
} else {
    Write-Host ">> 未找到 GitHub CLI (gh)，跳过 GitHub Release 自动上传。" -ForegroundColor Yellow
}

# 5. 同步 EXE 至 GitCode (仅上传 EXE)
Write-Host "
[5/5] 正在将最新编译的 EXE 同步至 GitCode (纯 EXE 分发，无源码)..." -ForegroundColor Magenta
$gitcodeScript = Join-Path $PSScriptRoot "sync_gitcode_exe.ps1"
if (Test-Path $gitcodeScript) {
    & $gitcodeScript
} else {
    Write-Host "[WARN] 未找到 $gitcodeScript" -ForegroundColor Yellow
}

Write-Host "
==========================================" -ForegroundColor Cyan
Write-Host "  发布完成！" -ForegroundColor Cyan
Write-Host "  - GitHub:  https://github.com/mountopjh/BankBin/releases/tag/$tag" -ForegroundColor Cyan
Write-Host "  - GitCode: https://gitcode.com/mountop2026/BankBin" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

