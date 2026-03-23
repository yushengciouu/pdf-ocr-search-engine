"""
資料庫重置腳本
用途：刪除舊資料庫並重新建立全新的資料庫
"""
import os
import sqlite3
from pathlib import Path

# 資料庫檔案路徑
DB_PATH = Path(__file__).parent / "fuyu.sqlite"

def reset_database():
    """重置資料庫"""
    print("=" * 50)
    print("  FUYU 資料庫重置工具")
    print("=" * 50)
    print()
    
    # 檢查資料庫是否存在
    if DB_PATH.exists():
        print(f"⚠️  發現現有資料庫: {DB_PATH}")
        
        # 顯示當前資料統計
        try:
            conn = sqlite3.connect(str(DB_PATH))
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM documents")
            doc_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM doc_fts")
            page_count = cursor.fetchone()[0]
            
            conn.close()
            
            print(f"   - 文件數量: {doc_count}")
            print(f"   - 頁面數量: {page_count}")
        except Exception as e:
            print(f"   - 無法讀取資料庫統計: {e}")
        
        print()
        confirm = input("❓ 確定要刪除並重建資料庫嗎？(yes/no): ")
        
        if confirm.lower() not in ['yes', 'y']:
            print("❌ 取消重置")
            return
        
        # 刪除舊資料庫
        print("🗑️  刪除舊資料庫...")
        DB_PATH.unlink()
        print("✅ 舊資料庫已刪除")
    else:
        print("ℹ️  未發現現有資料庫，將建立新資料庫")
    
    print()
    print("🔨 建立新資料庫...")
    
    # 建立新資料庫
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # 1. 建立 documents 表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        filepath TEXT NOT NULL,
        upload_date TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 2. 建立 doc_fts 全文檢索表
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
    
    print("✅ 新資料庫建立完成！")
    print()
    print("=" * 50)
    print("  重置完成")
    print("=" * 50)
    print()
    print("📌 下一步：")
    print("   1. 確保後端服務正在運行")
    print("   2. 在前端點擊「掃描資料夾」重新處理 PDF")
    print()

if __name__ == "__main__":
    reset_database()
