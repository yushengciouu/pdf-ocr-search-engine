@echo off
echo ====================================
echo   FUYU 服務啟動中...
echo ====================================
echo.

echo [0/2] 清理既有 8000/5173 服務...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173 ^| findstr LISTENING') do taskkill /PID %%a /F >nul 2>&1
timeout /t 2 /nobreak >nul

echo [1/1] 啟動 FUYU 核心服務 (Port 8000)...
start "FUYU 服務" cmd /k "cd /d C:\Users\705\Desktop\BigOne\paddle\FUYU\backend && C:\Users\705\anaconda3\envs\paddle_env\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 || pause"

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
