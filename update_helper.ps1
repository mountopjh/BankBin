param(
    [Parameter(Mandatory = $true)][string]$Source,
    [Parameter(Mandatory = $true)][string]$Target,
    [Parameter(Mandatory = $true)][int]$OldPid,
    [Parameter(Mandatory = $true)][string]$LogPath,
    [Parameter(Mandatory = $true)][string]$Token
)

$ErrorActionPreference = "Stop"
$backup = "$Target.update-backup"
$ack = Join-Path (Split-Path -Parent $Source) "startup.ack"
$newProcess = $null
$replaced = $false

function Write-UpdateLog([string]$Message) {
    $line = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') $Message"
    Add-Content -LiteralPath $LogPath -Value $line -Encoding UTF8
}

function Start-Target([bool]$WithAcknowledgement) {
    if ($WithAcknowledgement) {
        $env:BANKBIN_UPDATE_ACK = $ack
        $env:BANKBIN_UPDATE_TOKEN = $Token
    } else {
        Remove-Item Env:BANKBIN_UPDATE_ACK -ErrorAction SilentlyContinue
        Remove-Item Env:BANKBIN_UPDATE_TOKEN -ErrorAction SilentlyContinue
    }
    return Start-Process -FilePath $Target -WorkingDirectory (Split-Path -Parent $Target) -PassThru
}

try {
    Write-UpdateLog "Updater started for PID $OldPid."
    $deadline = (Get-Date).AddSeconds(60)
    while (Get-Process -Id $OldPid -ErrorAction SilentlyContinue) {
        if ((Get-Date) -ge $deadline) {
            throw "旧程序未在 60 秒内退出。"
        }
        Start-Sleep -Milliseconds 250
    }

    if (-not (Test-Path -LiteralPath $Source -PathType Leaf)) {
        throw "下载文件不存在。"
    }
    if (-not (Test-Path -LiteralPath $Target -PathType Leaf)) {
        throw "旧程序文件不存在。"
    }

    Remove-Item -LiteralPath $backup -Force -ErrorAction SilentlyContinue
    Move-Item -LiteralPath $Target -Destination $backup -Force
    Move-Item -LiteralPath $Source -Destination $Target -Force
    $replaced = $true

    Remove-Item -LiteralPath $ack -Force -ErrorAction SilentlyContinue
    $newProcess = Start-Target $true
    $deadline = (Get-Date).AddSeconds(45)
    $acknowledged = $false
    while ((Get-Date) -lt $deadline) {
        if (Test-Path -LiteralPath $ack -PathType Leaf) {
            $acknowledged = ((Get-Content -LiteralPath $ack -Raw).Trim() -eq $Token)
            if ($acknowledged) { break }
        }
        if ($newProcess.HasExited) { break }
        Start-Sleep -Milliseconds 250
        $newProcess.Refresh()
    }
    if (-not $acknowledged) {
        throw "新程序未能确认启动。"
    }

    Remove-Item -LiteralPath $backup -Force
    Remove-Item -LiteralPath $ack -Force -ErrorAction SilentlyContinue
    Write-UpdateLog "Update completed; old executable removed and new executable started."
    exit 0
} catch {
    Write-UpdateLog "Update failed: $($_.Exception.Message)"
    if ($newProcess -and -not $newProcess.HasExited) {
        Stop-Process -Id $newProcess.Id -Force -ErrorAction SilentlyContinue
        Start-Sleep -Milliseconds 500
    }
    if ($replaced -and (Test-Path -LiteralPath $backup -PathType Leaf)) {
        Remove-Item -LiteralPath $Target -Force -ErrorAction SilentlyContinue
        Move-Item -LiteralPath $backup -Destination $Target -Force
        Start-Target $false | Out-Null
        Write-UpdateLog "Rollback completed; old executable restarted."
    } elseif (Test-Path -LiteralPath $Target -PathType Leaf) {
        Start-Target $false | Out-Null
        Write-UpdateLog "Existing executable restarted."
    }
    exit 1
} finally {
    Remove-Item -LiteralPath $Source -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $ack -Force -ErrorAction SilentlyContinue
    $helperDirectory = Split-Path -Parent $PSCommandPath
    Remove-Item -LiteralPath $PSCommandPath -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $helperDirectory -Force -ErrorAction SilentlyContinue
}
