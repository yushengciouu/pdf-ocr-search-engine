@echo off
set "PROJECT_ROOT=C:\Users\705\Desktop\BigOne\paddle\FUYU"
set "PYTHON_EXE=C:\Users\705\anaconda3\envs\paddle_env\python.exe"

cd /d "%PROJECT_ROOT%\backend"
if not exist "%PYTHON_EXE%" (
  echo 找不到 paddle_env 的 Python: %PYTHON_EXE%
  pause
  exit /b 1
)

"%PYTHON_EXE%" -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
if errorlevel 1 (
  echo 後端啟動失敗
  pause
)
