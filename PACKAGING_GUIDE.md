# FUYU 專案移植與打包指南 (Windows 綠色免安裝版)

本指南說明如何將 **FUYU 智慧文件搜尋系統** 打包成綠色免安裝版本，方便直接移植到其他 Windows 電腦上解壓即用。

---

## 📦 打包原理
1. **前端免 Node.js 依賴**：在開發機預先將 Vue 3 前端編譯為靜態檔案（`frontend/dist`），由 FastAPI 後端直接進行靜態託管。
2. **免安裝 Python 環境**：使用 `conda-pack` 將現有的 Conda 虛擬環境（包含 PaddleOCR、PyTorch、PyMuPDF 等所有依賴）完整封裝。
3. **原生 GUI 支援**：本專案後端直接執行於 Windows 本地環境，能正常彈出原生的 Windows 資料夾選擇視窗。

---

## 🛠️ 打包步驟 (開發機操作)

### 1. 編譯前端靜態檔案
在開發機開啟命令提示字元 (CMD) 或 PowerShell，進入前端目錄編譯：
```cmd
cd frontend
npm run build
```
*確認 `frontend/` 下多出 `dist/` 資料夾。*

### 2. 打包 Conda 虛擬環境
開啟 **Anaconda Prompt**，切換到專案根目錄並安裝 `conda-pack` 進行打包：
```cmd
cd c:\Users\705\Desktop\BigOne\paddle\FUYU
pip install conda-pack
conda pack -n paddle_env -o fuyu_env.zip
```
*執行完成後，根目錄下會生成一個 `fuyu_env.zip` 檔案。*

### 3. 解壓縮虛擬環境
在專案根目錄開啟 **PowerShell** 執行解壓指令，解壓到專案目錄的 `fuyu_env`：
```powershell
# 建立目錄
New-Item -ItemType Directory -Path ".\fuyu_env"
# 解壓縮 zip 檔案
Expand-Archive -Path ".\fuyu_env.zip" -DestinationPath ".\fuyu_env"
```

### 4. 整理移植包 (桌面生成)
在 **PowerShell** 中執行以下腳本，這會自動在您的「桌面」建立 `FUYU_Portable` 移植資料夾，並只複製運行所需的檔案（排除不必要的開發原始碼以進行瘦身）：

```powershell
# 1. 在桌面建立移植資料夾與子目錄
New-Item -ItemType Directory -Path "$HOME\Desktop\FUYU_Portable"
New-Item -ItemType Directory -Path "$HOME\Desktop\FUYU_Portable\frontend"

# 2. 複製後端程式碼與前端編譯後的靜態檔案 (排除了 frontend 其他原始碼與 node_modules)
Copy-Item -Path ".\backend" -Destination "$HOME\Desktop\FUYU_Portable\backend" -Recurse
Copy-Item -Path ".\frontend\dist" -Destination "$HOME\Desktop\FUYU_Portable\frontend\dist" -Recurse

# 3. 複製封裝好的 Python 虛擬環境
Copy-Item -Path ".\fuyu_env" -Destination "$HOME\Desktop\FUYU_Portable\fuyu_env" -Recurse

# 4. 建立一鍵啟動腳本
@'
@echo off
title FUYU Document Search System
cd /d "%~dp0"

echo ==================================================
echo   FUYU System Starting (Portable Version)...
echo ==================================================
echo.

:: 1. Check Python Environment
if not exist "%~dp0fuyu_env\python.exe" (
    echo [ERROR] Cannot find python environment at: %~dp0fuyu_env\python.exe
    echo Please make sure fuyu_env is unzipped correctly.
    echo.
    pause
    exit
)

:: 2. Start Backend Service
echo [1/1] Starting backend service (Port 8000)...
cd /d "%~dp0backend"
"..\fuyu_env\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8000

if errorlevel 1 (
    echo.
    echo ==================================================
    echo   [ERROR] Service failed to start or terminated!
    echo ==================================================
    echo.
    pause
)
'@ | Out-File -FilePath "$HOME\Desktop\FUYU_Portable\啟動服務.bat" -Encoding utf8
```

---

## 🚀 移植與執行 (目標電腦操作)

1. 將桌面生成的 **`FUYU_Portable`** 資料夾壓縮成 `.zip`。
2. 將壓縮檔複製並解壓縮至目標電腦。
3. 雙擊 **`啟動服務.bat`** 即可直接運行。
4. 使用瀏覽器訪問 `http://localhost:8000` 開始使用系統。

> 📌 **注意**：系統啟動時，若找不到資料庫 `fuyu.sqlite`，系統會自動在根目錄下初始化建立一個全新的空白資料庫；使用者亦可自行於網頁設定欲監控掃描的 PDF 資料夾路徑。
