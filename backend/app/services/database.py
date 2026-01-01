"""
資料庫服務層
負責所有與 SQLite 資料庫的互動
"""
import sqlite3
from typing import List, Dict, Optional
from pathlib import Path


class DatabaseService:
    """資料庫服務類別"""
    
    def __init__(self, db_path: str = "../fuyu.sqlite"):
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
        self.db_path = Path(__file__).parent.parent.parent.parent / "fuyu.sqlite"
        
    def get_connection(self) -> sqlite3.Connection:
        """取得資料庫連線"""
        return sqlite3.connect(str(self.db_path))
    
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
                SELECT id, filename, filepath, upload_date
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
                    "upload_date": row[3]
                })
            
            return documents
            
        except Exception as e:
            raise Exception(f"查詢文件時發生錯誤: {str(e)}")
        finally:
            conn.close()
    
    def search_documents(self, keyword: str) -> List[Dict]:
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
            
            # 如果關鍵字太短或包含特殊字元，使用 LIKE 查詢
            if len(keyword) < 3 or has_special_char:
                # 使用 LIKE 查詢支援短關鍵字和特殊字元
                query = '''
                    SELECT f.doc_id, d.filename, d.filepath, f.page_number, 
                        substr(f.content, max(1, instr(f.content, ?) - 50), 150) as snippet
                    FROM doc_fts f
                    JOIN documents d ON f.doc_id = d.id
                    WHERE f.content LIKE ?
                '''
                params = (keyword, f'%{keyword}%')
            else:
                # 使用 FTS5 MATCH 查詢（更快，支援 trigram）
                query = '''
                    SELECT f.doc_id, d.filename, d.filepath, f.page_number,
                        snippet(doc_fts, 0, '<b>', '</b>', '...', 10) as snippet
                    FROM doc_fts f
                    JOIN documents d ON f.doc_id = d.id
                    WHERE doc_fts MATCH ?
                    ORDER BY rank
                '''
                params = (keyword,)
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            search_results = []
            for row in results:
                search_results.append({
                    "doc_id": row[0],
                    "filename": row[1],
                    "filepath": row[2],
                    "page_number": row[3],
                    "snippet": row[4]
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
                SELECT id, filename, filepath, upload_date
                FROM documents
                WHERE id = ?
            ''', (doc_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "filename": row[1],
                    "filepath": row[2],
                    "upload_date": row[3]
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
