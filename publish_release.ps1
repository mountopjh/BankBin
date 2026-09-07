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
    $tag = "v1.7.4"
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

# 3. 提交未保存的修改并推送代码及 Tags 到 GitCode 和 GitHub
Write-Host "
[3/5] 正在同步代码与版本标签到 GitCode 和 GitHub..." -ForegroundColor Magenta
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

# 双端推送
git push origin main --tags
Write-Host ">> 代码与 Tags 已同步推送至 GitCode 与 GitHub！" -ForegroundColor Green

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

# 5. GitCode 发布指引
Write-Host "
[5/5] GitCode 发行版设置:" -ForegroundColor Magenta
Write-Host "GitCode Releases 页面: https://gitcode.com/mountop2026/BankBin/releases/create" -ForegroundColor Cyan
Write-Host "已为您将最新 EXE 文件路径复制到剪贴板，并在资源管理器中选中该文件。" -ForegroundColor Green

# 将路径复制到剪贴板，并在资源管理器中高亮选中 EXE
Set-Clipboard -Value $latestExe.FullName
& explorer.exe /select, "$($latestExe.FullName)"

Write-Host "
==========================================" -ForegroundColor Cyan
Write-Host "  发布完成！" -ForegroundColor Cyan
Write-Host "  - GitHub:  https://github.com/mountopjh/BankBin/releases/tag/$tag" -ForegroundColor Cyan
Write-Host "  - GitCode: https://gitcode.com/mountop2026/BankBin/releases" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
