# FUYU 服務一鍵啟動腳本
# 使用方法：在 PowerShell 中執行 .\start_services.ps1

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "  FUYU 服務啟動腳本" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# 獲取專案根目錄
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

# 檢查並關閉已存在的服務
Write-Host "[1/5] 檢查現有服務..." -ForegroundColor Yellow

$nodeProcess = Get-Process -Name node -ErrorAction SilentlyContinue
$pythonProcess = Get-Process -Name python -ErrorAction SilentlyContinue

if ($nodeProcess) {
    Write-Host "  發現運行中的 Node.js 進程，正在關閉..." -ForegroundColor Red
    Stop-Process -Name node -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}

if ($pythonProcess) {
    Write-Host "  發現運行中的 Python 進程，正在關閉..." -ForegroundColor Red
    Stop-Process -Name python -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}

Write-Host "  ✓ 清理完成" -ForegroundColor Green
Write-Host ""

# 啟動後端服務
Write-Host "[2/5] 啟動後端服務 (Port 8000)..." -ForegroundColor Yellow

$backendPath = Join-Path $projectRoot "backend"
$backendCommand = "cd '$backendPath'; conda activate paddle_env; uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCommand -WindowStyle Normal

Write-Host "  ✓ 後端服務啟動中..." -ForegroundColor Green
Start-Sleep -Seconds 3

# 啟動前端服務
Write-Host "[3/5] 啟動前端服務 (Port 5173)..." -ForegroundColor Yellow

$frontendPath = Join-Path $projectRoot "frontend"
$frontendCommand = "cd '$frontendPath'; npm run dev"

Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCommand -WindowStyle Normal

Write-Host "  ✓ 前端服務啟動中..." -ForegroundColor Green
Start-Sleep -Seconds 5

# 驗證服務
Write-Host "[4/5] 驗證服務狀態..." -ForegroundColor Yellow

$maxRetries = 10
$retryCount = 0
$backendReady = $false
$frontendReady = $false

while ($retryCount -lt $maxRetries) {
    # 檢查後端
    try {
        $backendResponse = Invoke-WebRequest -Uri "http://localhost:8000/docs" -Method GET -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($backendResponse.StatusCode -eq 200) {
            $backendReady = $true
        }
    } catch {
        # 繼續等待
    }

    # 檢查前端
    try {
        $frontendResponse = Invoke-WebRequest -Uri "http://localhost:5173" -Method GET -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($frontendResponse.StatusCode -eq 200) {
            $frontendReady = $true
        }
    } catch {
        # 繼續等待
    }

    if ($backendReady -and $frontendReady) {
        break
    }

    $retryCount++
    Start-Sleep -Seconds 2
}

# 顯示結果
Write-Host ""
Write-Host "[5/5] 服務狀態報告" -ForegroundColor Yellow
Write-Host "  後端 (Port 8000): " -NoNewline
if ($backendReady) {
    Write-Host "✓ 運行中" -ForegroundColor Green
} else {
    Write-Host "✗ 啟動中或失敗" -ForegroundColor Red
}

Write-Host "  前端 (Port 5173): " -NoNewline
if ($frontendReady) {
    Write-Host "✓ 運行中" -ForegroundColor Green
} else {
    Write-Host "✗ 啟動中或失敗" -ForegroundColor Red
}

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "  服務啟動完成！" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "訪問位址：" -ForegroundColor White
Write-Host "  前端應用：http://localhost:5173" -ForegroundColor Cyan
Write-Host "  後端 API：http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "按任意鍵退出..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
