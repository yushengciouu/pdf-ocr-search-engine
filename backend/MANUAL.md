# FUYU 後端技術手冊 (Backend Technical Manual)

本手冊詳細說明 FUYU 專案後端的架構、安裝方式、API 接口設計以及核心程式碼邏輯。

---

## 1. 專案概觀 (Project Overview)

FUYU 是一個基於 **FastAPI** 的文件搜尋系統，專注於處理 PDF 文件。它結合了 **PaddleOCR** 進行文字辨識，並使用 **SQLite (FTS5)** 進行高效的全文檢索。

**核心功能：**
* **OCR 處理**：自動掃描 `factory` 資料夾中的 PDF，辨識文字內容。
* **全文搜尋**：支援關鍵字搜尋，包含模糊搜尋 (LIKE) 與全文檢索 (FTS5)。
* **API 服務**：提供 RESTful API 供前端呼叫。

---

## 2. 系統架構 (System Architecture)

### 目錄結構
```
backend/
├── app/
│   ├── api/            # API 路由定義
│   │   ├── documents.py # 文件管理 (列表、刪除)
│   │   ├── search.py    # 搜尋功能
│   │   └── ocr.py       # OCR 觸發入口
│   ├── services/       # 核心業務邏輯
│   │   ├── database.py  # 資料庫操作 (SQLite)
│   │   └── ocr_service.py # OCR 處理 (PaddleOCR)
│   └── main.py         # 程式進入點 (FastAPI App)
├── factory/            # [外部] 放置 PDF 檔案的資料夾
├── fuyu.sqlite         # [外部] SQLite 資料庫檔案
└── requirements.txt    # 專案依賴套件
```

### 資料流 (Data Flow)
1. **OCR 流程**:
   `User` Put PDF in `factory/` -> `API` (POST /api/ocr/scan) -> `OCRService` -> `PaddleOCR` -> `DatabaseService` -> `SQLite`

2. **搜尋流程**:
   `Frontend` -> `API` (GET /api/search) -> `DatabaseService` -> `SQLite (FTS MATCH)` -> `Frontend`

---

## 3. 環境設置與執行 (Setup & Run)

### 前置需求
* Python 3.8+
* Conda (建議使用，因為 PaddlePaddle 環境較複雜)

### 安裝步驟

1. **建立 Conda 環境**
   ```bash
   conda create -n paddle_env python=3.8
   conda activate paddle_env
   ```

2. **安裝依賴**
   ```bash
   # 安裝 PaddlePaddle (CPU版本，若有 GPU 請參考官網)
   pip install paddlepaddle -i https://mirror.baidu.com/pypi/simple
   
   # 安裝 PaddleOCR
   pip install paddleocr

   # 安裝專案依賴
   cd backend
   pip install -r requirements.txt
   ```

### 啟動伺服器

**開發模式 (Development)**
```bash
# 在 backend 目錄下執行
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
* `--reload`: 程式碼修改後自動重啟。
* `--host 0.0.0.0`: 允許外部 IP 連線。

---

## 4. API 文件摘要 (API Reference)

詳細 API 文件在伺服器啟動後可訪問：`http://localhost:8000/docs`

### 文件管理 (Documents)
* `GET /api/documents`: 列出所有已建立索引的文件。
* `GET /api/documents/{id}`: 取得特定文件詳細資訊。
* `DELETE /api/documents/{id}`: 刪除文件索引 (不會刪除實體檔案)。

### 搜尋 (Search)
* `GET /api/search?q={keyword}`: 搜尋文件內容。
  * 邏輯：若關鍵字少於 3 字或含特殊符號，使用 `LIKE` 模糊搜尋；否則使用 `FTS5` 全文檢索。

### 文字辨識 (OCR)
* `POST /api/ocr/scan`: 觸發掃描 `factory` 資料夾。
  * 邏輯：檢查資料夾內所有 PDF -> 比對資料庫是否已存在 -> 若無則進行 OCR -> 存入資料庫。

---

## 5. 核心代碼解析 (Deep Dive)

### `app/services/database.py`
這是與 SQLite 互動的唯一窗口。
* **`search_documents`**: 這是搜尋的核心。它展示了混合式搜尋策略：
  ```python
  if len(keyword) < 3 or has_special_char:
      # 使用 LIKE '%keyword%' (較慢但容錯高)
  else:
      # 使用 FTS5 MATCH (極快，支援分詞)
  ```

### `app/services/ocr_service.py`
負責繁重的 AI 運算。
* 使用 `pdf2image` 將 PDF 轉為圖片。
* 使用 `PaddleOCR` 識別圖片文字。
* **`scan_factory_folder`**: 設計有「增量更新」機制，會檢查 `is_file_in_db`，避免重複跑 OCR 浪費時間。
