# 系統架構分析與工程師思維 (Architecture & Engineering Workflow)

這份文件是給想深入了解「為什麼這樣設計」以及「一般工程師如何思考」的讀者。

---

## 🏗️ 1. 這個架構好在哪裡？ (Architecture Review)

目前的架構是典型的 **"Modern Monolith" (現代單體架構)**。對於一個中小型、需要快速迭代的內部工具來說，這是**極佳的選擇**。

### 評分：⭐⭐⭐⭐☆ (4.5/5)

### 優點 (Pros)
1. **技術選型精準 (Right Tool for the Job)**
   - **FastAPI**: 現代 Python 後端的首選。速度快、自動生成文件 (Swagger)、支援非同步 (Async)。相比 Django 輕量，相比 Flask 功能更強大。
   - **SQLite + FTS5**: 非常聰明的選擇。
     - 一般人可能會想架設 PostgreSQL 或 Elasticsearch，但那需要 Docker、需要運維資源。
     - **SQLite** 是內嵌檔案，零配置。
     - **FTS5** (Full-Text Search) 讓 SQLite 擁有接近專業搜尋引擎的能力，對於「文件檢索」這個需求來說，性價比極高。
   - **PaddleOCR**: 百度開源的 OCR，對中文支援度目前業界領先，比 Tesseract 好用很多。

2. **職責分離清晰 (Clean Architecture)**
   - `routers` (API 介面) 只管收發請求。
   - `services` (業務邏輯) 只管處理資料和運算。
   - 這讓程式碼好讀、好改、好測試。

3. **非同步處理 (Async Handling)**
   - 雖然 OCR 是 CPU 密集型 (會卡住)，但 FastAPI 預設會把同步函數 (`def`) 丟到 ThreadPool 執行，避免卡死主執行緒。這是一個進階的細節，目前的寫法正好符合這個最佳實踐。

### 缺點與改進空間 (Cons)
1. **擴展性瓶頸**: 如果有 100 個人同時用，SQLite 的寫入鎖 (Write Lock) 可能會變慢。（但讀取通常夠快）
2. **OCR 阻塞**: 如果一次丟 1000 個 PDF 進去，OCR 會跑很久，這期間伺服器 CPU 會滿載。正式產品通常會搭配 `Celery` 或 `Redis Queue` 來做背景任務佇列。

### 🚀 剩下的 0.5 分去哪了？ (Road to 5.0)
要讓這個架構從 **4.5 (好用)** 變成 **5.0 (完美)**，通常需要補足以下這「最後一哩路」，但這往往會增加 2-3 倍的開發成本：

1. **非同步任務隊列 (Task Queue)**:
   - **問題**: 現在 OCR 是在請求當下跑的 (雖然是非同步 IO，但 CPU 還是會在該行程忙碌)。
   - **解法**: 引入 **Celery + Redis**。使用者上傳後立刻回傳 "Processing"，後端在背景慢慢跑 OCR，跑完再通知前端。

2. **更強的資料庫 (PostgreSQL)**:
   - **問題**: SQLite 在極高併發寫入時會鎖表。
   - **解法**: 換成 PostgreSQL，支援更高併發，且有更強的 Vector Search (pgvector) 功能，為未來 AI RAG 做準備。

3. **容器化與自動部署 (Docker & CI/CD)**:
   - **問題**: 現在要手動 `pip install` 環境。
   - **解法**: 用 Docker 包成映像檔，確保在任何機器跑起來都一樣；加上 GitHub Actions 做自動測試與部署。

> **工程師的抉擇**: 在專案初期 (MVP 階段)，為了這 0.5 分去多花 200% 的時間通常是**不划算的**。這就是為什麼目前的 4.5 分架構是「最佳選擇」。

---

## 👨‍💻 2. 一般工程師是怎麼做這個專案的？ (The Engineer's Workflow)

如果這是一個我接到的任務，我會依照以下步驟進行：

### 第一階段：需求分析 (Requirement Analysis)
* **User Story**: 「使用者想要丟一堆 PDF 進去，然後能搜尋裡面的內容。」
* **關鍵難點 (Tech Spike)**:
  1. PDF 怎麼轉文字？ -> 调研：PyPDF2 (爛) vs PaddleOCR (強)。決定用 PaddleOCR。
  2. 怎麼搜尋？ -> `LIKE %keyword%` 太慢且不準。调研：Elastcisearch (太重) vs SQLite FTS5 (剛好)。決定用 FTS5。

### 第二階段：原型開發 (MVP - Minimum Viable Product)
* 先寫一個 Python Script (不是網頁)，只要能跑通「讀 PDF -> OCR -> Print 文字」就好。
* 驗證 OCR 效果是否能接受。

### 第三階段：後端搭建 (Backend Imp.)
1. **開專案**: `fastapi new` 或手建目錄。
2. **資料庫設計**:
   - 表 `documents`: 存檔名、路徑。
   - 表 `doc_fts` (Virtual Table): 存 OCR 出來的文字，專門給搜尋用。
3. **API 實作**:
   - 先做 Upload/Scan API。
   - 再做 Search API。
4. **Refactor**: 發現 `main.py` 太亂了，於是把邏輯拆出去變成 `services/database.py`。

### 第四階段：前端對接 (Frontend Integration)
* 用 Vue/React 刻畫面。
* 發現搜尋結果沒有「亮點」顯示很難找 -> 回去修改後端 SQL，加上 `snippet()` 函數來做關鍵字高亮 (Highlight)。

### 第五階段：優化 (Optimization)
* 用戶抱怨：「掃描時網頁會卡住」。
* 工程師解法：把 OCR 改成背景執行，或者優化 SQL 查詢速度。

---

## 🧠 總結 (Takeaway)

這個專案展示了一個**資深工程師**的思維：
❌ **不做過度設計** (Over-engineering)：沒有硬上 Microservices 或 Kubernetes。
✅ **選擇最適合的工具**：FastAPI + SQLite FTS5 解決了 90% 的問題，且維護成本極低。

學習這個專案，你學到的不只是 Python 語法，更是**「如何用最低成本解決問題」**的架構智慧。
