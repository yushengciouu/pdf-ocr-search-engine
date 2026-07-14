@echo off
echo ====================================
echo   FUYU 服務啟動中...
echo ====================================
echo.

echo [0/2] 清理既有 8000/5173 服務...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173 ^| findstr LISTENING') do taskkill /PID %%a /F >nul 2>&1
timeout /t 2 /nobreak >nul

set "PROJECT_ROOT=%~dp0"

:: 1. 優先使用 uv/venv 建立的專案內置虛擬環境 (.venv)
if exist "%PROJECT_ROOT%backend\.venv\Scripts\python.exe" (
    set "PYTHON_EXE=%PROJECT_ROOT%backend\.venv\Scripts\python.exe"
) else if exist "%PROJECT_ROOT%fuyu_env\python.exe" (
    :: 2. 其次使用打包版的 python env
    set "PYTHON_EXE=%PROJECT_ROOT%fuyu_env\python.exe"
) else if exist "C:\Users\705\anaconda3\envs\paddle_env\python.exe" (
    :: 3. 再者使用開發機預設環境路徑
    set "PYTHON_EXE=C:\Users\705\anaconda3\envs\paddle_env\python.exe"
) else (
    :: 4. 最後使用系統的 python
    where python >nul 2>&1
    if %errorlevel% equ 0 (
        set "PYTHON_EXE=python"
    ) else (
        echo [錯誤] 找不到可用的 Python 環境！
        pause
        exit /b 1
    )
)

echo [1/1] 啟動 FUYU 核心服務 (Port 8000)...
start "FUYU 服務" cmd /k "cd /d "%PROJECT_ROOT%backend" && "%PYTHON_EXE%" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 || pause"

echo.
echo ====================================
echo   服務啟動完成！
echo ====================================
echo.
echo [正式版] 系統入口 (含前後端): http://localhost:8000
echo [開發用] API 說明文件: http://localhost:8000/docs
echo.
echo 請勿關閉彈出的黑色終端機視窗！
echo.
pause

