import sqlite3
import re

def backfill():
    conn = sqlite3.connect('../fuyu.sqlite')
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, filename FROM documents WHERE doc_date IS NULL")
    rows = cursor.fetchall()
    
    updated_count = 0
    
    for row in rows:
        doc_id, filename = row
        date_match = re.search(r'-(20[2-9]\d{5})-?', filename)
        if date_match:
            raw_date = date_match.group(1)
            doc_date = f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:8]}"
            cursor.execute("UPDATE documents SET doc_date = ? WHERE id = ?", (doc_date, doc_id))
            updated_count += 1
            
    conn.commit()
    conn.close()
    
    print(f"Backfill complete. Updated {updated_count} documents.")

if __name__ == "__main__":
    backfill()
