# FUYU 服務一鍵關閉腳本
# 使用方法：在 PowerShell 中執行 .\stop_services.ps1

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "  FUYU 服務關閉腳本" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# 查找並顯示當前運行的服務
Write-Host "[1/3] 查找運行中的服務..." -ForegroundColor Yellow

$nodeProcesses = Get-Process -Name node -ErrorAction SilentlyContinue
$pythonProcesses = Get-Process -Name python -ErrorAction SilentlyContinue

if ($nodeProcesses) {
    Write-Host "  找到 Node.js 進程：" -ForegroundColor White
    foreach ($proc in $nodeProcesses) {
        $runtime = (Get-Date) - $proc.StartTime
        Write-Host "    - PID: $($proc.Id) | 運行時長: $([int]$runtime.TotalHours)h $($runtime.Minutes)m" -ForegroundColor Gray
    }
} else {
    Write-Host "  未找到 Node.js 進程" -ForegroundColor Gray
}

if ($pythonProcesses) {
    Write-Host "  找到 Python 進程：" -ForegroundColor White
    foreach ($proc in $pythonProcesses) {
        $runtime = (Get-Date) - $proc.StartTime
        Write-Host "    - PID: $($proc.Id) | 運行時長: $([int]$runtime.TotalHours)h $($runtime.Minutes)m" -ForegroundColor Gray
    }
} else {
    Write-Host "  未找到 Python 進程" -ForegroundColor Gray
}

Write-Host ""

# 關閉服務
Write-Host "[2/3] 關閉服務..." -ForegroundColor Yellow

$stoppedCount = 0

if ($nodeProcesses) {
    Stop-Process -Name node -Force -ErrorAction SilentlyContinue
    $stoppedCount += $nodeProcesses.Count
    Write-Host "  ✓ 已關閉 $($nodeProcesses.Count) 個 Node.js 進程" -ForegroundColor Green
}

if ($pythonProcesses) {
    Stop-Process -Name python -Force -ErrorAction SilentlyContinue
    $stoppedCount += $pythonProcesses.Count
    Write-Host "  ✓ 已關閉 $($pythonProcesses.Count) 個 Python 進程" -ForegroundColor Green
}

if ($stoppedCount -eq 0) {
    Write-Host "  沒有需要關閉的服務" -ForegroundColor Gray
}

Start-Sleep -Seconds 2

# 驗證關閉
Write-Host ""
Write-Host "[3/3] 驗證服務已關閉..." -ForegroundColor Yellow

$remainingNode = Get-Process -Name node -ErrorAction SilentlyContinue
$remainingPython = Get-Process -Name python -ErrorAction SilentlyContinue

if (-not $remainingNode -and -not $remainingPython) {
    Write-Host "  ✓ 所有服務已成功關閉" -ForegroundColor Green
} else {
    Write-Host "  ⚠ 部分進程可能仍在運行" -ForegroundColor Yellow
    if ($remainingNode) {
        Write-Host "    - 剩餘 Node.js 進程: $($remainingNode.Count)" -ForegroundColor Red
    }
    if ($remainingPython) {
        Write-Host "    - 剩餘 Python 進程: $($remainingPython.Count)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "  服務關閉完成！" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "按任意鍵退出..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
