@echo off
echo ====================================
echo   FUYU 服務啟動中...
echo ====================================
echo.

echo [0/2] 清理既有 8000/5173 服務...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173 ^| findstr LISTENING') do taskkill /PID %%a /F >nul 2>&1
timeout /t 2 /nobreak >nul

echo [1/2] 啟動後端服務 (Port 8000)...
start "FUYU 後端" cmd /k "cd c:\Users\705\Desktop\BigOne\paddle\FUYU\backend && conda run -n paddle_env uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak >nul

echo [2/2] 啟動前端服務 (Port 5173)...
start "FUYU 前端" cmd /k "cd c:\Users\705\Desktop\BigOne\paddle\FUYU\frontend && npm run dev"

echo.
echo ====================================
echo   服務啟動完成！
echo ====================================
echo.
echo 前端: http://localhost:5173
echo 後端: http://localhost:8000/docs
echo.
echo 兩個視窗已開啟，請勿關閉！
echo.
pause
