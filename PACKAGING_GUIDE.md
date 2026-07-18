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

### 2. 建立包含 CUDA/cuDNN 的 Conda 虛擬環境並打包
為了讓綠色包移植到目標電腦（如 RTX 3060 或更高規格）時不需要手動安裝 CUDA 和 cuDNN 驅動程式，必須在打包前將 CUDA/cuDNN 直接裝入 Conda 環境中。

開啟 **Anaconda Prompt**，執行以下指令：

```cmd
# 1. 建立全新的乾淨虛擬環境
conda create -n fuyu_env python=3.10 -y
conda activate fuyu_env

# 2. 【關鍵】將 CUDA 11.8 與 cuDNN 直接裝在環境內（攜帶 DLL 檔）
conda install -c conda-forge cudatoolkit=11.8.0 cudnn=8.9.2.26 -y

# 3. 切換到專案的 backend 目錄，安裝所有 Python 依賴與 PaddleOCR GPU 版本
cd /d c:\Users\705\Desktop\BigOne\paddle\FUYU\backend
pip install -r requirements.txt

# 4. 安裝打包工具並打包
pip install conda-pack
conda pack -n fuyu_env -o ..\fuyu_env.zip
```
*執行完成後，專案根目錄下會生成一個 `fuyu_env.zip` 檔案。*

### 3. 整理移植包 (桌面生成)
在 **PowerShell** 中執行以下腳本，這會自動在您的「桌面」建立 `FUYU_Portable` 移植資料夾，並只複製運行所需的檔案。
我們直接複製壓縮檔 `fuyu_env.zip`，避免在本機解壓後複製數萬個碎檔案（Windows 複製碎檔案極慢）：

```powershell
# 1. 在桌面建立移植資料夾與子目錄
New-Item -ItemType Directory -Path "$HOME\Desktop\FUYU_Portable"
New-Item -ItemType Directory -Path "$HOME\Desktop\FUYU_Portable\frontend"

# 2. 複製後端程式碼與前端編譯後的靜態檔案
# (備註：這步驟實質上就是將運行所需的專案原目錄搬移過去。但只複製後端程式碼與前端編譯出來的 dist 靜態資料夾，完全排除前端極為龐大的 node_modules 與原始原始碼，以達到顯著的瘦身效果)
Copy-Item -Path ".\backend" -Destination "$HOME\Desktop\FUYU_Portable\backend" -Recurse
Copy-Item -Path ".\frontend\dist" -Destination "$HOME\Desktop\FUYU_Portable\frontend\dist" -Recurse

# 3. 複製打包好的環境壓縮檔本身 (不在此處解壓，改由啟動腳本在目標機自動解壓)
Copy-Item -Path ".\fuyu_env.zip" -Destination "$HOME\Desktop\FUYU_Portable\fuyu_env.zip"

# 4. 建立智慧一鍵啟動腳本 (自帶自動解壓功能)
@'
@echo off
title FUYU Document Search System
cd /d "%~dp0"

echo ==================================================
echo   FUYU System Starting (Portable Version)...
echo ==================================================
echo.

:: 1. 自動偵測並解壓縮 Python 環境 (僅在第一次啟動時執行)
if not exist "%~dp0fuyu_env\python.exe" (
    if exist "%~dp0fuyu_env.zip" (
        echo [INFO] 偵測到第一次啟動，正在解壓縮 Python 環境...
        echo 這可能需要 1~2 分鐘，請勿關閉此視窗...
        powershell -Command "Expand-Archive -Path '%~dp0fuyu_env.zip' -DestinationPath '%~dp0fuyu_env' -Force"
        echo [INFO] 解壓縮完成！
        echo.
    ) else (
        echo [ERROR] 找不到 Python 執行環境或 fuyu_env.zip！
        echo 請確認檔案是否完整。
        echo.
        pause
        exit
    )
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

1. 將桌面生成的 **`FUYU_Portable`** 資料夾壓縮成 `.zip` 並複製至目標電腦。
2. 在目標電腦上解壓縮此資料夾。
3. 雙擊 **`啟動服務.bat`**：
   * **第一次啟動**：腳本會自動在背景呼叫 PowerShell 將 `fuyu_env.zip` 解壓縮成 `fuyu_env` 資料夾，並自動啟動服務。
   * **第二次之後**：直接秒開啟動。
4. 使用瀏覽器訪問 `http://localhost:8000` 開始使用系統。

> 📌 **注意**：系統啟動時，若找不到資料庫 `fuyu.sqlite`，系統會自動在根目錄下初始化建立一個全新的空白資料庫；使用者亦可自行於網頁設定欲監控掃描的 PDF 資料夾路徑。
