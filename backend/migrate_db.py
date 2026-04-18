import sqlite3
import sys

def migrate():
    try:
        conn = sqlite3.connect("../fuyu.sqlite")
        cursor = conn.cursor()
        
        # Check if doc_date already exists
        cursor.execute("PRAGMA table_info(documents)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if "doc_date" not in columns:
            print("Adding doc_date column to documents table...")
            cursor.execute("ALTER TABLE documents ADD COLUMN doc_date TEXT;")
            conn.commit()
            print("Migration successful.")
        else:
            print("Migration already applied. doc_date exists.")
            
    except Exception as e:
        print(f"Migration error: {e}")
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
