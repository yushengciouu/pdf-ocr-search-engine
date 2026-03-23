@echo off
echo ====================================
echo   FUYU 資料庫重置工具
echo ====================================
echo.

echo [警告] 此操作將刪除所有已處理的文件資料！
echo.
set /p confirm="確定要重置資料庫嗎？(yes/no): "

if /i not "%confirm%"=="yes" (
    if /i not "%confirm%"=="y" (
        echo.
        echo 取消重置
        pause
        exit /b
    )
)

echo.
echo [1/3] 刪除舊資料庫...
if exist fuyu.sqlite (
    del /f fuyu.sqlite
    echo ✓ 舊資料庫已刪除
) else (
    echo ℹ 未發現舊資料庫
)

echo.
echo [2/3] 建立新資料庫...
python database_creation_multipage.py

echo.
echo [3/3] 完成！
echo.
echo ====================================
echo   資料庫重置完成
echo ====================================
echo.
echo 下一步：
echo   1. 確保後端服務正在運行
echo   2. 在前端點擊「掃描資料夾」重新處理 PDF
echo.
pause
