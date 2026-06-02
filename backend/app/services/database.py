"""
資料庫服務層
負責所有與 SQLite 資料庫的互動
"""
import sqlite3
from typing import List, Dict, Optional
from pathlib import Path

from ..paths import get_database_path


class DatabaseService:
    """資料庫服務類別"""
    
    def __init__(self, db_path: str = None):
        """
        初始化資料庫服務
        
        Args:
            db_path: 資料庫檔案路徑
        """
        # 取得專案根目錄的資料庫路徑
        # __file__ 在 backend/app/services/database.py
        # parent = backend/app/services
        # parent.parent = backend/app
        """
        初始化資料庫服務
        
        Args:
            db_path: 資料庫檔案路徑
        """
        # 取得專案根目錄的資料庫路徑
        # __file__ 在 backend/app/services/database.py
        # parent = backend/app/services
        # parent.parent = backend/app
        # parent.parent.parent = backend
        # parent.parent.parent.parent = FUYU (專案根目錄)
        self.db_path = Path(db_path) if db_path else get_database_path()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """如果資料表不存在，則自動建立"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # 1. 建立 documents 表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            doc_date TEXT DEFAULT NULL,
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

        # 3. 建立 scan_schedules 預約排程表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS scan_schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            folder_path TEXT NOT NULL,
            start_time TEXT NOT NULL,          -- ISO 8601 or YYYY-MM-DD HH:MM:SS
            end_time TEXT NOT NULL,            -- ISO 8601 or YYYY-MM-DD HH:MM:SS
            status TEXT NOT NULL,              -- 'pending', 'scanning', 'completed', 'stopped', 'failed'
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            message TEXT DEFAULT NULL          -- 日誌或錯誤訊息
        )
        ''')
        conn.commit()
        conn.close()
    def get_connection(self) -> sqlite3.Connection:
        """取得資料庫連線並開啟 WAL 模式提升並發效能"""
        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        conn.execute('PRAGMA journal_mode=WAL;')
        return conn
    
    def list_all_documents(self) -> List[Dict]:
        """
        列出所有文件
        
        Returns:
            文件列表，每個文件包含 id, filename, filepath, upload_date
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, filename, filepath, doc_date, upload_date
                FROM documents
                ORDER BY upload_date DESC
            ''')
            results = cursor.fetchall()
            
            documents = []
            for row in results:
                documents.append({
                    "id": row[0],
                    "filename": row[1],
                    "filepath": row[2],
                    "doc_date": row[3],
                    "upload_date": row[4]
                })
            
            return documents
            
        except Exception as e:
            raise Exception(f"查詢文件時發生錯誤: {str(e)}")
        finally:
            conn.close()

    def get_total_documents_count(self) -> int:
        """取得文件總數"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT COUNT(*) FROM documents')
            return cursor.fetchone()[0]
        except Exception as e:
            raise Exception(f"取得文件總數時發生錯誤: {str(e)}")
        finally:
            conn.close()

    def list_documents_paginated(self, limit: int = 20, offset: int = 0) -> List[Dict]:
        """
        分頁列出文件
        
        Args:
            limit: 最大回傳數量
            offset: 位移量
            
        Returns:
            文件列表
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, filename, filepath, doc_date, upload_date
                FROM documents
                ORDER BY upload_date DESC
                LIMIT ? OFFSET ?
            ''', (limit, offset))
            results = cursor.fetchall()
            
            documents = []
            for row in results:
                documents.append({
                    "id": row[0],
                    "filename": row[1],
                    "filepath": row[2],
                    "doc_date": row[3],
                    "upload_date": row[4]
                })
            
            return documents
            
        except Exception as e:
            raise Exception(f"查詢文件時發生錯誤: {str(e)}")
        finally:
            conn.close()
    
    def search_documents(self, keyword: str, start_date: str = None, end_date: str = None) -> List[Dict]:
        """
        搜尋包含關鍵字的文件
        
        Args:
            keyword: 搜尋關鍵字
            
        Returns:
            搜尋結果列表，每個結果包含 filename, filepath, page_number, snippet
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # 檢查關鍵字是否包含 FTS5 特殊字元
            special_chars = ['-', '"', '(', ')', '*', ':', '^']
            has_special_char = any(char in keyword for char in special_chars)
            
            date_filter = ""
            date_params = []
            if start_date:
                date_filter += " AND d.doc_date >= ?"
                date_params.append(start_date)
            if end_date:
                date_filter += " AND d.doc_date <= ?"
                date_params.append(end_date)
            
            # 如果關鍵字太短或包含特殊字元，使用 LIKE 查詢
            if len(keyword) < 3 or has_special_char:
                # 使用 LIKE 查詢支援短關鍵字和特殊字元
                query = f'''
                    SELECT f.doc_id, d.filename, d.filepath, f.page_number, 
                        substr(f.content, max(1, instr(f.content, ?) - 50), 150) as snippet, d.doc_date
                    FROM doc_fts f
                    JOIN documents d ON f.doc_id = d.id
                    WHERE f.content LIKE ?{date_filter}
                '''
                params = [keyword, f'%{keyword}%'] + date_params
            else:
                # 使用 FTS5 MATCH 查詢（更快，支援 trigram）
                query = f'''
                    SELECT f.doc_id, d.filename, d.filepath, f.page_number,
                        snippet(doc_fts, 0, '<b>', '</b>', '...', 10) as snippet, d.doc_date
                    FROM doc_fts f
                    JOIN documents d ON f.doc_id = d.id
                    WHERE doc_fts MATCH ?{date_filter}
                    ORDER BY rank
                '''
                params = [keyword] + date_params
            
            cursor.execute(query, tuple(params))
            results = cursor.fetchall()
            
            search_results = []
            for row in results:
                snippet_text = row[4]
                
                # 如果是 LIKE 查詢，SQLite 不會自動加上 <b>，需要我們透過 Python 手動補上
                if len(keyword) < 3 or has_special_char:
                    # 先逸出關鍵字避免正則錯誤
                    import re
                    escaped_kw = re.escape(keyword)
                    # 不區分大小寫替換
                    snippet_text = re.sub(f'({escaped_kw})', r'<b>\1</b>', snippet_text, flags=re.IGNORECASE)
                    
                search_results.append({
                    "doc_id": row[0],
                    "filename": row[1],
                    "filepath": row[2],
                    "page_number": row[3],
                    "snippet": snippet_text,
                    "doc_date": row[5]
                })
            
            return search_results
            
        except Exception as e:
            raise Exception(f"搜尋時發生錯誤: {str(e)}")
        finally:
            conn.close()
    
    def get_document_by_id(self, doc_id: int) -> Optional[Dict]:
        """
        根據 ID 取得文件資訊
        
        Args:
            doc_id: 文件 ID
            
        Returns:
            文件資訊，如果找不到則回傳 None
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, filename, filepath, doc_date, upload_date
                FROM documents
                WHERE id = ?
            ''', (doc_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "filename": row[1],
                    "filepath": row[2],
                    "doc_date": row[3],
                    "upload_date": row[4]
                }
            return None
            
        except Exception as e:
            raise Exception(f"查詢文件時發生錯誤: {str(e)}")
        finally:
            conn.close()
    
    def delete_document(self, doc_id: int) -> bool:
        """
        刪除文件
        
        Args:
            doc_id: 文件 ID
            
        Returns:
            是否刪除成功
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # 先刪除 FTS 表中的資料
            cursor.execute('DELETE FROM doc_fts WHERE doc_id = ?', (doc_id,))
            
            # 再刪除文件表中的資料
            cursor.execute('DELETE FROM documents WHERE id = ?', (doc_id,))
            
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            conn.rollback()
            raise Exception(f"刪除文件時發生錯誤: {str(e)}")
        finally:
            conn.close()

    def create_schedule(self, folder_path: str, start_time: str, end_time: str) -> int:
        """建立預約掃描排程"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO scan_schedules (folder_path, start_time, end_time, status)
                VALUES (?, ?, ?, 'pending')
            ''', (folder_path, start_time, end_time))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            conn.rollback()
            raise Exception(f"建立排程失敗: {str(e)}")
        finally:
            conn.close()

    def list_schedules(self) -> List[Dict]:
        """列出所有預約排程"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT id, folder_path, start_time, end_time, status, created_at, message
                FROM scan_schedules
                ORDER BY created_at DESC
            ''')
            rows = cursor.fetchall()
            schedules = []
            for r in rows:
                schedules.append({
                    "id": r[0],
                    "folder_path": r[1],
                    "start_time": r[2],
                    "end_time": r[3],
                    "status": r[4],
                    "created_at": r[5],
                    "message": r[6]
                })
            return schedules
        except Exception as e:
            raise Exception(f"取得排程列表失敗: {str(e)}")
        finally:
            conn.close()

    def update_schedule_status(self, schedule_id: int, status: str, message: str = None) -> bool:
        """更新預約排程狀態"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE scan_schedules
                SET status = ?, message = ?
                WHERE id = ?
            ''', (status, message, schedule_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            raise Exception(f"更新排程狀態失敗: {str(e)}")
        finally:
            conn.close()

    def delete_schedule(self, schedule_id: int) -> bool:
        """刪除預約排程"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                DELETE FROM scan_schedules
                WHERE id = ?
            ''', (schedule_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            raise Exception(f"刪除排程失敗: {str(e)}")
        finally:
            conn.close()
