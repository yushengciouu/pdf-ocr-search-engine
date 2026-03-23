# FUYU 智慧文件搜尋系統 (Intelligent Document Search System)

FUYU 是一個現代化的全端文件管理與搜尋解決方案，專為高效處理與檢索 PDF 文件而設計。它結合了強大的 **OCR (光學字元辨識)** 技術與 **FTS (全文檢索)** 引擎，讓使用者能夠輕鬆將紙本掃描檔轉化為可搜尋的數位資產。

> **核心理念**: Modern Monolith 架構 - 結合 Python 的強大資料處理能力與 Next.js 的現代化互動體驗。

---

## ✨ 核心功能 (Features)

*   **⚡ 全文檢索 (Full-Text Search)**: 使用 SQLite FTS5 引擎，支援高效的關鍵字搜尋 (包含中文 Trigram 分詞)，毫秒級回應。
*   **🤖 自動化 OCR 處理 (Auto-Ingest)**: 
    *   自動掃描指定目錄 (`backend/factory`) 的 PDF 文件。
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
    *   `pdf2image` (PDF 轉圖片)
*   **Package Manager**: Conda / Pip

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
│   ├── factory/            # [Input] 待處理的 PDF 來源資料夾
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
- **Python 3.10+** (建議使用 Conda)
- **Node.js 18+**
- **Poppler** (用於 pdf2image，Windows 需加入 PATH)

### 2. 啟動後端 (Backend)
```bash
cd backend

# 建立/啟用虛擬環境 (建議)
conda activate paddle_env

# 安裝依賴 (初次執行)
pip install -r requirements.txt

# 啟動 API 伺服器
# 預設位址: http://localhost:8000
# Swagger 文件: http://localhost:8000/docs
uvicorn app.main:app --reload
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

© 2024 FUYU Project. All Rights Reserved.
