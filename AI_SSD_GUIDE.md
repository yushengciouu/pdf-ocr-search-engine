# AI 驅動規格開發指南 (AI-Driven SSD Guide) for Project FUYU

> **核心哲學**: 程式碼只是規格的副產品 (Code is just a byproduct of the Spec)。
> 對於 AI 而言，「精確的上下文 (Context)」就是一切。垃圾進，垃圾出 (Garbage In, Garbage Out)。

本指南旨在標準化如何透過 **規格驅動開發 (Spec-Driven Development, SSD)** 來引導 AI (如 Cursor, Windsurf, Copilot) 高品質地完成 `FUYU` 專案的開發任務。

---

## 第一章：核心思維 (Core Philosophy)

### 1.1 上下文即王 (Context is King)
AI 不是讀心者。它之所以會「幻覺」或「寫出爛 Code」，通常是因為我們給的上下文：
1.  **太少**: AI 被迫猜測你的意圖（例如：猜測資料庫欄位名稱）。
2.  **太多且無關**: AI 的注意力被分散（例如：把整個 `node_modules` 的結構都丟給它）。
3.  **衝突**: 舊的程式碼跟新的需求打架，AI 不知道該聽誰的。

**解決方案**: 我們必須建立一份 **「唯一真理來源 (Single Source of Truth, SSOT)」** 的規格文件。程式碼必須永遠服從於規格。

### 1.2 微規格 (Micro-Specs)
不要試圖一次把整個系統丟給 AI。將任務切分為「微規格」：
*   ❌ "做一個類似 Google 的搜尋功能"
*   ✅ "實作 `SearchService` class，依據 `documents` table 的 `content` 欄位進行關鍵字搜尋，並支援分頁 (limit/offset)。"

### 1.3 先寫測試，後寫程式 (Spec -> Test -> Code)
這是與 AI 協作的最強工作流：
1.  **人類** 撰寫規格 (Spec)。
2.  **AI** 根據規格撰寫測試 (Test)。
3.  **AI** 撰寫程式碼以通過測試 (Code)。

如果 AI 寫不出正確的測試，代表你的規格寫得不夠清楚。**測試代碼是規格的第一個驗證者**。

---

## 第二章：全域環境定義 (Global Context)

在任何 Prompt 的開頭，或是在 `.cursorrules` / `.windsurfrules` 中，必須明確定義以下「世界觀」，防止 AI 自由發揮。

### 2.1 技術堆疊 (Tech Stack)
*   **Language**: Python 3.10+ (Backend), TypeScript/Node.js (Frontend)
*   **Backend Framework**: FastAPI (Async)
*   **Database**: SQLite (`backend/fuyu.sqlite`)
*   **ORM**: 原生 SQL + Pydantic (這很重要！不要讓 AI 引入 SQLAlchemy 除非必要)
*   **Frontend Framework**: Next.js (App Router), React
*   **Styling**: Tailwind CSS
*   **Package Manager**: `uv` (Python), `npm` (Node)

### 2.2 關鍵路徑約定 (Path Conventions)
*   `backend/app/api/`: 所有 API Routes。
*   `backend/app/services/`: 業務邏輯與資料庫操作 (不可直接在 API 層寫 SQL)。
*   `backend/tests/`: Pytest 測試檔。
*   `frontend/components/`: 可重用 UI 元件。

---

## 第三章：數據與介面規格 (Data & Interface Specs)

這是最重要的一章。**在寫任何一行 Code 之前，必須先定義這些。**

### 3.1 規格文件模板 (The Master Spec Template)
請複製以下模板至你的 `.md` 檔案中開始一個新任務：

```markdown
# Spec: [功能名稱]

## 1. 概述 (Overview)
[簡述這個功能要做什麼，以及為什麼要做]

## 2. 資料模型 (Data Model)
### Schema (Mermaid ER Diagram)
[在此定義資料庫結構，這是唯一的真理]
\`\`\`mermaid
erDiagram
    DOCUMENT {
        int id PK
        string title
        string content
        datetime created_at
    }
\`\`\`

## 3. API 合約 (API Contract)
### Endpoint: [METHOD] /api/[path]
*   **Description**: [描述]
*   **Request Body (JSON)**:
    \`\`\`json
    {
      "field": "type // description"
    }
    \`\`\`
*   **Response Body (JSON)**:
    \`\`\`json
    {
      "success": true,
      "data": { ... }
    }
    \`\`\`

## 4. 驗收標準 (Acceptance Criteria / Tests)
*   [ ] 測試案例 1
*   [ ] 測試案例 2
```

---

## 第四章：前端元件規格 (UI/UX Specs)

針對前端任務，我們使用 **Atomic Design** 思維。

### 4.1 元件規格模板
```markdown
# UI Spec: [Component Name]

## 1. 視覺描述 (Visual Description)
*   使用 Tailwind CSS。
*   深色模式 (Dark Mode) 支援。
*   [描述佈局，例如：Flex row, centered]

## 2. Props 定義 (Interface)
| Prop Name | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `title` | `string` | Yes | 卡片標題 |
| `isLoading`| `boolean`| No | 是否顯示載入動畫 |

## 3. 狀態邏輯 (State Logic)
*   Click `Delete` button -> Show Confirmation Modal.
*   If `isLoading` is true -> Disable all buttons.

## 4. Mock Data
[提供一段 JSON 作為開發用的假資料]
```

---

## 第五章：實戰工作流 (The "Pro" Workflow)

請嚴格遵守此步驟來以此專案開發新功能：

### Step 1: 建立規格檔
在 `backend/specs/` (你需要建立這個資料夾) 中建立一個 `.md` 檔案，填入第三/四章的模板。

### Step 2: 生成測試 (Prompting AI for Tests)
**Prompt:**
> "Reference @[SpecFile.md]. You are a QA Engineer. Write a pytest file `tests/test_[feature].py` that covers all the Acceptance Criteria in the spec. Do NOT write the implementation code yet. Mock the database calls if necessary."

### Step 3: 生成實作 (Prompting AI for Implementation)
**Prompt:**
> "Reference @[SpecFile.md] and @[test_feature.py]. You are a Senior Backend Engineer. Implement the necessary code in `backend/app/` to pass the tests. Follow the project structure: API routes in `api/`, business logic in `services/`. Use raw SQL for SQLite."

### Step 4: 迴圈驗證 (Refine Loop)
執行測試。如果失敗，將錯誤訊息貼回給 AI。
**Prompt:**
> "The tests failed with the following error. Fix the implementation code. Do NOT change the test code unless the spec was demonstrated to be wrong."

---

## 附錄：完整實戰範例 - 「智能搜尋系統」

以下示範如何為 `search.py` 撰寫一份完美的 Spec。

---

# Spec: Document Search System

## 1. 概述
實作一個全文搜尋 API，允許使用者透過關鍵字搜尋文件內容。

## 2. 資料模型 (Existing)
我們使用現有的 `documents` 表。

\`\`\`mermaid
erDiagram
    documents {
        int id PK
        string filename
        string content "Text content for searching"
        string upload_time
    }
\`\`\`

## 3. API 合約

### GET /api/search
*   **Query Parameters**:
    *   `q` (string, required): 搜尋關鍵字。
*   **Response**:
    \`\`\`json
    {
      "success": true,
      "results": [
        {
          "id": 1,
          "filename": "report.pdf",
          "snippet": "...found text...",
          "score": 0.0  // Optional irrelevant for simple search
        }
      ]
    }
    \`\`\`

## 4. 服務層邏輯 (Service Layer)
*   Class: `SearchService` in `backend/app/services/search_service.py`
*   Method: `search(query: str) -> List[dict]`
*   Logic:
    *   使用 SQL `LIKE %query%` 進行搜尋 (簡易版)。
    *   回傳包含 `snippet` (關鍵字前後 50 字)。

## 5. 測試案例 (Tests)
1.  **test_search_empty**: 搜尋不存在的關鍵字，應回傳空列表。
2.  **test_search_hit**: 搜尋 "factory"，應回傳包含 "factory" 的文件。
3.  **test_snippet**: 確認回傳的 snippet 確實包含關鍵字。
