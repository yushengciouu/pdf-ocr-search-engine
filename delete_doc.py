import sqlite3
import sys

def delete_document_by_filename(filename: str):
    """
    根據檔名刪除資料庫中的文件記錄 (包含 documents 和 doc_fts)
    """
    db_path = "fuyu.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. 先找出 doc_id
        cursor.execute("SELECT id FROM documents WHERE filename = ?", (filename,))
        result = cursor.fetchone()
        
        if not result:
            print(f"❌ 找不到檔名為 '{filename}' 的資料。")
            return

        doc_id = result[0]
        print(f"🔍 找到 '{filename}' (Doc ID: {doc_id})，準備刪除...")

        # 2. 刪除 doc_fts (全文檢索資料)
        cursor.execute("DELETE FROM doc_fts WHERE doc_id = ?", (doc_id,))
        
        # 3. 刪除 documents (檔案資訊)
        cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        
        conn.commit()
        print(f"✅ 已成功刪除 '{filename}' 及其相關索引資料。")
        
    except Exception as e:
        print(f"❌ 刪除失敗: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方式: python delete_doc.py <檔名>")
        print("範例: python delete_doc.py test2.pdf")
    else:
        target_filename = sys.argv[1]
        delete_document_by_filename(target_filename)
