# FUYU 文件搜尋系統

基於 Python + SQLite FTS5 的全文搜尋系統，支援 PDF 文件的 OCR 處理與快速搜尋。

## 功能特色

- ✅ PDF 文件 OCR 處理（多頁支援）
- ✅ SQLite FTS5 全文搜尋引擎
- ✅ 支援中文搜尋（trigram tokenizer）
- ✅ 頁碼定位與內容摘要
- ✅ 命令列介面操作

## 檔案說明

- `search_demo.py` - 搜尋與列表功能（主要程式）
- `database_creation_multipage.py` - 資料庫建立工具
- `delete_doc.py` - 文件刪除工具
- `ocr_try_auto.py` - OCR 處理工具
- `fuyu.sqlite` - SQLite 資料庫

## 使用方式

### 搜尋文件
```bash
python search_demo.py 關鍵字
```

### 列出所有文件
```bash
python search_demo.py --list
```

## 資料庫結構

- `documents` - 文件基本資訊表
- `doc_fts` - FTS5 全文搜尋表（trigram tokenizer）

## 未來規劃

- [ ] Web 介面整合
- [ ] 文件上傳功能
- [ ] PDF 預覽功能
- [ ] 進階搜尋篩選
