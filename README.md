# 智慧文件搜尋系統 (Intelligent Document Search System)

FUYU 是一個現代化的全端文件管理與搜尋解決方案，專為高效處理與檢索 PDF 文件而設計。它結合了強大的 **OCR (光學字元辨識)** 技術與 **FTS (全文檢索)** 引擎，讓使用者能夠輕鬆將紙本掃描檔轉化為可搜尋的數位資產。

> **核心理念**: Modern Monolith 架構 - 結合 Python 的強大資料處理能力與 Next.js 的現代化互動體驗。

---

## ✨ 核心功能 (Features)

*   **⚡ 全文檢索 (Full-Text Search)**: 使用 SQLite FTS5 引擎，支援高效的關鍵字搜尋 (包含中文 Trigram 分詞)，毫秒級回應。
*   **🤖 自動化 OCR 處理 (Auto-Ingest)**: 
    *   自動掃描指定目錄的 PDF 文件。
    *   整合 **PaddleOCR** 進行高精準度文字辨識。
    *   智慧增量更新，只處理新增或修改的檔案。
*   **🖥️ 現代化 Web 介面**:
    *   基於 **Next.js 14 (App Router)** 打造的響應式介面。
    *   **Tailwind CSS** 設計系統，提供 Premium 級的視覺體驗。
    *   即時搜尋預覽與關鍵字高亮 (Highlighting)。
*   **📂 文件管理**: 支援查看文件列表、原始 PDF 路徑對照及刪除功能。

---

## 🛠️ 技術堆疊 (Tech Stack)

### Backend (後端)
*   **Runtime**: Python 3.10+
*   **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (高效能 Async Web 框架)
*   **Database**: SQLite + FTS5 (輕量級全文檢索，無需額外 DB 服務)
*   **AI/OCR**: 
    *   [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) (文字辨識)
    *   [PyMuPDF (fitz)](https://github.com/pymupdf/PyMuPDF) (PDF 轉圖片，免除 Poppler 系統依賴)
*   **Package Manager**: uv

### Frontend (前端)
*   **Framework**: [Next.js 14](https://nextjs.org/) (React 18)
*   **Language**: TypeScript
*   **Styling**: [Tailwind CSS](https://tailwindcss.com/)
*   **Icons**: Lucide React

---

## 📂 專案結構 (Project Structure)

```text
/
├── backend/                # 後端核心程式碼
│   ├── app/
│   │   ├── api/            # API 端點 (Controllers)
│   │   ├── services/       # 業務邏輯與 OCR 核心
│   │   └── main.py         # 伺服器入口點
│   ├── fuyu.sqlite         # SQLite 資料庫檔案
│   └── requirements.txt    # Python 依賴列表
├── frontend/               # 前端 Web 應用
│   ├── app/                # Next.js 頁面與路由
│   ├── components/         # React 元件
│   └── package.json        # 前端依賴列表
├── PDFs/                   # 範例或存檔的 PDF 文件
└── *.py                    # (根目錄下的 Legacy 工具腳本)
```

---

## 🚀 快速開始 (Getting Started)

### 1. 環境準備
請確保您的系統已安裝：
- **uv** (Python 套件與環境管理工具，[安裝說明](https://docs.astral.sh/uv/getting-started/installation/))
- **Node.js 18+**

### 2. 啟動後端 (Backend)
```bash
cd backend

# 1. 建立虛擬環境與安裝依賴 (初次執行)
uv venv --python 3.10
uv pip install -r requirements.txt

# 2. 啟動 API 伺服器 (開發模式帶熱重載)
# 預設位址: http://localhost:8000
# Swagger 文件: http://localhost:8000/docs
uv run uvicorn app.main:app --reload
```

### 3. 啟動前端 (Frontend)
```bash
cd frontend

# 安裝依賴 (初次執行)
npm install

# 啟動開發伺服器
# 預設位址: http://localhost:3000
npm run dev
```

---

## 🌐 部署方式 (Deployment Guides)

本系統支援以下兩種部署方式：

### 部署方式 A：綠色免安裝包移植
適合沒有配置 Python / Node.js 環境的目標 Windows 電腦。請參閱 **[PACKAGING_GUIDE.md](./PACKAGING_GUIDE.md)** 進行虛擬環境封裝與移植。

---

### 部署方式 B：原始碼全新部署 (宿主機控制端 + 容器 OCR 運算端)
適合擁有 NVIDIA 顯示卡，且希望以最輕量的方式部署並保留原生 Windows 資料夾選擇視窗。
* **容器端**：使用 Docker 運行自帶 CUDA/cuDNN + PaddlePaddle-GPU 的 OCR 微服務（不需在 Windows 本地配置繁雜的 GPU 驅動與 CUDA）。
* **宿主機端**：使用 `uv` 構建極其輕量的 Python 環境，執行 FastAPI 主程式與 Windows 原生資料夾選擇器（`tkinter`）。

#### 步驟 1：Clone 專案並進入根目錄
開啟終端機（CMD 或 PowerShell），複製本專案並進入目錄：
```bash
git clone <your-repo-url>
cd FUYU
```

#### 步驟 2：編譯並打包前端
在根目錄下進入 `frontend` 目錄，安裝套件並進行靜態編譯：
```bash
cd frontend
npm install
npm run build
```
*這會生成 `frontend/dist` 目錄。後端服務在啟動時會自動偵測並託管此目錄下的前端 SPA 應用。*

#### 步驟 3：啟動 Docker OCR 容器服務
確保您的 Windows 已安裝 Docker Desktop 與 NVIDIA Container Toolkit，並在專案根目錄下執行以下指令：
```bash
docker-compose up -d --build
```
這會自動建置並啟動運行於 `http://localhost:5000` 的 GPU 加速 OCR 微服務。

#### 步驟 4：使用 uv 建立宿主機輕量化 Python 環境
在根目錄下進入 `backend` 目錄，使用 `uv` 建立虛擬環境並安裝宿主機依賴：
```bash
cd backend
uv venv --python 3.10
uv pip install -r requirements.txt
```
*(由於在此部署模式下，宿主機的 `requirements.txt` 已經移除了龐大的 GPU 版 Paddle 套件，此環境的安裝極其迅速且僅佔用數十 MB 的空間)*

#### 步驟 5：啟動宿主機核心服務
在 `backend` 目錄下啟動後端：
```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```
啟動後即可透過瀏覽器訪問 `http://localhost:8000` 來使用完整的系統。所有 heavy 的 OCR 辨識會自動傳送給容器內的 Docker Worker 調用 GPU 運算，且能完美保有原生的 Windows 選擇資料夾視窗！

---

## 📖 開發指南與文件
本專案包含詳細的內部文件，歡迎參考：
*   **[FUYU_MASTER_SDD.md](./FUYU_MASTER_SDD.md)**: 系統設計規格書 (System Design Document)，包含詳細 API 定義與架構圖。
*   **[backend/LEARNING_GUIDE.md](./backend/LEARNING_GUIDE.md)**: 後端學習指南，適合新加入的開發者循序漸進了解系統。
*   **[backend/DOCKER_AND_CICD_GUIDE.md](./backend/DOCKER_AND_CICD_GUIDE.md)**: 部署與 CI/CD 相關說明。

---

## 📝 工具腳本 (Utility Scripts)
根目錄下保留了一些獨立運行的工具腳本，可用於快速測試或無服務器操作：
*   `search_demo.py`: 純命令列搜尋測試工具。
*   `ocr_try_auto.py`: 獨立執行 OCR 的測試腳本。
*   `database_creation_multipage.py`: 初始化資料庫結構工具。

---


