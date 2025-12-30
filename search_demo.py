import sqlite3
import sys

def list_documents():
    """
    列出資料庫中所有的文件
    """
    db_path = "fuyu.sqlite"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("📚 資料庫中的所有文件：\n")
    
    try:
        cursor.execute('''
            SELECT id, filename, filepath, upload_date
            FROM documents
            ORDER BY upload_date DESC
        ''')
        results = cursor.fetchall()
        
        if not results:
            print("❌ 資料庫中沒有任何文件。")
        else:
            print(f"✅ 共有 {len(results)} 份文件：\n")
            for row in results:
                doc_id, filename, filepath, upload_date = row
                print("=" * 50)
                print(f"ID: {doc_id}")
                print(f"📄 檔名: {filename}")
                print(f"📂 路徑: {filepath}")
                print(f"📅 上傳時間: {upload_date}")
                print("=" * 50)
                print()
                
    except Exception as e:
        print(f"❌ 查詢發生錯誤: {e}")
    finally:
        conn.close()


def search_documents(keyword: str):
    """
    搜尋包含關鍵字的文件（顯示頁碼）
    """
    db_path = "fuyu.sqlite"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"🔍 正在搜尋關鍵字: '{keyword}' ...")
    
    # trigram tokenizer 需要至少 3 個字元
    # 對於短關鍵字（<3字元），使用 LIKE 查詢
    # 對於長關鍵字，使用 FTS5 MATCH 查詢（更快）
    if len(keyword) < 3:
        # 使用 LIKE 查詢支援短關鍵字
        query = '''
            SELECT d.filename, d.filepath, f.page_number, 
                substr(f.content, max(1, instr(f.content, ?) - 50), 150) as snippet
            FROM doc_fts f
            JOIN documents d ON f.doc_id = d.id
            WHERE f.content LIKE ?
        '''
        params = (keyword, f'%{keyword}%')
    else:
        # 使用 FTS5 MATCH 查詢（支援 trigram）
        query = '''
            SELECT d.filename, d.filepath, f.page_number,
                snippet(doc_fts, 0, '<b>', '</b>', '...', 10)
            FROM doc_fts f
            JOIN documents d ON f.doc_id = d.id
            WHERE doc_fts MATCH ?
            ORDER BY rank
        '''
        params = (keyword,)
    
    try:
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        if not results:
            print("❌ 找不到任何匹配的文件。")
        else:
            print(f"✅ 找到 {len(results)} 筆結果：")
            for row in results:
                filename, filepath, page_number, snippet_text = row
                print("-" * 40)
                print(f"📄 檔名: {filename}")
                print(f"📃 頁碼: 第 {page_number} 頁")
                print(f"📂 路徑: {filepath}")
                print(f"📝 摘要: {snippet_text}")
                print("-" * 40)
                
    except Exception as e:
        print(f"❌ 搜尋發生錯誤: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方式:")
        print("  python search_demo.py <關鍵字>   - 搜尋文件")
        print("  [python search_demo.py --list]      - 列出所有文件")
        print()
        # 預設搜尋一個可能存在的詞，方便測試
        default_keyword = "發票" 
        print(f"未輸入關鍵字，將使用預設關鍵字: '{default_keyword}' 進行測試")
        search_documents(default_keyword)
    elif sys.argv[1] == "--list" or sys.argv[1] == "-l":
        list_documents()
    else:
        keyword = sys.argv[1]
        search_documents(keyword)
