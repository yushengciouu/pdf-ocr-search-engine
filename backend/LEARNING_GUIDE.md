# FUYU 後端學習系統 (Backend Learning System)

這份指南旨在幫助開發者從零開始掌握 FUYU 後端系統。透過分級任務，你將逐步理解這套系統的運作原理。

---

## 🏃 Level 1: 新手村 (Novice) - 跑起來！

**目標**：成功啟動專案並呼叫第一個 API。

### 任務 1.1：啟動伺服器
1. 確保你已經按照 `MANUAL.md` 完成環境安裝。
2. 開啟終端機，執行：
   ```bash
   conda activate paddle_env
   uvicorn app.main:app --reload
   ```
3. 若看到 `Application startup complete`，恭喜你！

### 任務 1.2：使用 Swagger UI 測試
1. 打開瀏覽器，前往 `http://localhost:8000/docs`。
2. 找到 `GET /` (Root) 端點，點擊 "Try it out" -> "Execute"。
3. 你應該會看到歡迎訊息。

### 任務 1.3：搜尋測試
1. 確保資料庫 (`fuyu.sqlite`) 有資料。
2. 在 Swagger UI 找到 `GET /api/search`。
3. 輸入關鍵字 `test` 或其他你已知的內容，執行搜尋。
4. 觀察 Response Body 的結構。

---

## 🔨 Level 2: 學徒 (Apprentice) - 追蹤程式碼

**目標**：理解一個 Request 如何轉化為 Response。

### 任務 2.1：追蹤「搜尋」請求
當你發送 `/api/search?q=abc` 時，程式碼是怎麼跑的？

1. **進入點**: `app/main.py`
   - 看到 `app.include_router(search.router)`。這告訴我們請求被轉發到了 `search` 模組。
   
2. **路由層**: `app/api/search.py`
   - 找到 `@router.get("")` 裝飾的函式。
   - 參數 `q` 被接收。
   - 呼叫 `db_service.search_documents(q)`。

3. **服務層**: `app/services/database.py`
   - 找到 `search_documents(self, keyword)`。
   - 這裡有核心邏輯：判斷關鍵字長度，決定用 `LIKE` 還是 `FTS MATCH`。
   - 執行 SQL，回傳 List[Dict]。

**思考題**：為什麼要分 `routers` 和 `services`？如果把所有 SQL 都寫在 `api/search.py` 會有什麼壞處？
*(答案：為了職責分離。Service 層可以被重複使用，且不依賴 HTTP 邏輯，方便測試。)*

---

## 🔧 Level 3: 開發者 (Developer) - 動手修改

**目標**：新增一個簡單的 API 功能。

### 任務 3.1：新增 "Echo" 端點
我們來練習加一個 API，回傳你輸入的文字。

1. **修改 `app/api/search.py`**
   在檔案最後加入：
   ```python
   @router.get("/echo/{text}")
   async def echo_text(text: str):
       return {"message": f"你說了: {text}"}
   ```
2. **測試**
   - 儲存檔案（伺服器會自動重啟）。
   - 前往 `http://localhost:8000/docs`。
   - 試用新出現的 `/api/search/echo/{text}` 端點。

### 任務 3.2：修改搜尋邏輯 (進階)
試著修改 `app/services/database.py`，讓搜尋結果只回傳前 3 筆資料。
* 提示：修改 SQL 語句，加入 `LIMIT 3`。

---

## 🏛️ Level 4: 架構師 (Architect) - 深入核心

**目標**：理解非同步與 OCR 流程。

### 任務 4.1：理解 OCR 觸發機制
閱讀 `app/services/ocr_service.py` 的 `scan_factory_folder` 方法。

1. **增量更新 (Incremental Update)**
   - 注意 `is_file_in_db` 檢查。這防止了每次都要重新 OCR 幾百個檔案。
   
2. **PDF 處理**
   - 程式使用了 `pdf2image` 把 PDF 每一頁轉成圖片。
   - 再丟給 `PaddleOCR` 識別。
   - 這是一個非常消耗 CPU 的過程，所以通常這個 API 會跑很久。

### 任務 4.2：FTS5 全文檢索
打開 `fuyu.sqlite` (使用 DB Browser for SQLite)，查看 `doc_fts` 表。
這是 SQLite 的虛擬表 (Virtual Table)，專門為了快速搜尋文字而設計。
我們使用 `snippet()` 函數來自動擷取關鍵字前後的文字，這在 SQL 查詢中可以看到：
```sql
snippet(doc_fts, 0, '<b>', '</b>', '...', 10)
```
這行代碼讓搜尋結果可以直接顯示 **粗體** 的關鍵字。

---

## 🎓 結語
恭喜你！完成以上四個等級，你已經完全掌握了 FUYU 後端的精隨。
接下來你可以嘗試：
1. 優化 OCR 速度 (多執行緒？)。
2. 增加更多過濾條件 (例如依日期搜尋)。
3. 改善前端顯示效果。

祝編碼愉快！
