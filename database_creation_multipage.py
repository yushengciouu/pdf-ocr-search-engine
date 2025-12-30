import sqlite3

DB_NAME = "fuyu.sqlite"

def initialize_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    print("正在初始化簡易版資料庫...")

    # 1. 【檔案總表】documents
    # 用途：只存 PDF 檔案的資訊，讓我們搜到文字後，知道要去哪裡開檔案。
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,       -- 例如：test2.pdf
        filepath TEXT NOT NULL,       -- 例如：D:/data/test2.pdf
        upload_date TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    #upload_date TEXT DEFAULT CURRENT_TIMESTAMP
    # 2. 【全文檢索表】doc_fts (核心中的核心)
    # 用途：把 OCR 辨識出來的所有文字，不管順序，全部丟進來這裡。
    # SQLite 會自動建立索引，讓你可以秒搜。
    # page_number: 記錄第幾頁的內容
    # 使用 trigram tokenizer 支援中文子字串搜尋
    cursor.execute('''
    CREATE VIRTUAL TABLE IF NOT EXISTS doc_fts USING fts5(
        content, 
        doc_id UNINDEXED,
        page_number UNINDEXED,
        tokenize='trigram'
    )
    ''')
    
    conn.commit()
    conn.close()
    print(f"✅ 簡易版資料庫 {DB_NAME} 建立完成！")
    print("👉 現在可以把 PDF 每一頁的 OCR 文字分別存入 doc_fts，並記錄頁碼。")

if __name__ == "__main__":
    initialize_database()