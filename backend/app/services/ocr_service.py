"""
OCR 服務層
負責 PDF 文件的 OCR 處理
"""
import os
import glob
import sqlite3
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional, Callable, Any
from paddleocr import PaddleOCR
from pdf2image import convert_from_path


class OCRService:
    """OCR 服務類別"""
    
    def __init__(self):
        """初始化 OCR 服務"""
        self.ocr = None  # 延遲初始化，避免啟動時載入
        self.db_path = Path(__file__).parent.parent.parent.parent / "fuyu.sqlite"
        self.factory_path = Path(__file__).parent.parent.parent.parent / "factory"
    
    def _get_ocr(self):
        """取得 OCR 實例（延遲初始化）"""
        if self.ocr is None:
            self.ocr = PaddleOCR(use_angle_cls=True, lang="ch", use_gpu=True)
        return self.ocr
    
    def ocr_pdf(self, pdf_path: str) -> List[Dict]:
        """
        將 PDF 的每一頁分別進行 OCR
        
        Args:
            pdf_path: PDF 檔案路徑
            
        Returns:
            list of dict, 每個 dict 包含 page_number 和 content
        """
        ocr = self._get_ocr()
        images = convert_from_path(pdf_path)
        
        page_results = []
        for page_num, image in enumerate(images, start=1):
            result = ocr.predict(np.array(image))
            if result and len(result) > 0:
                page_text = "\n".join(result[0]['rec_texts'])
            else:
                page_text = ""
            
            page_results.append({
                'page_number': page_num,
                'content': page_text
            })
        
        return page_results
    
    def is_file_in_db(self, filename: str) -> bool:
        """
        檢查檔名是否已存在資料庫
        
        Args:
            filename: 檔案名稱
            
        Returns:
            是否存在
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT COUNT(*) FROM documents WHERE filename = ?
            ''', (filename,))
            
            count = cursor.fetchone()[0]
            return count > 0
        finally:
            conn.close()
    
    def save_to_db(self, filename: str, filepath: str, page_results: List[Dict]) -> int:
        """
        將 OCR 結果存入資料庫
        
        Args:
            filename: 檔案名稱
            filepath: 檔案路徑
            page_results: OCR 結果列表
            
        Returns:
            文件 ID
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        try:
            # 1. 插入 documents 表
            cursor.execute('''
                INSERT INTO documents (filename, filepath)
                VALUES (?, ?)
            ''', (filename, filepath))
            
            doc_id = cursor.lastrowid
            
            # 2. 為每一頁插入 doc_fts 表 (全文檢索)
            for page_data in page_results:
                cursor.execute('''
                    INSERT INTO doc_fts (doc_id, content, page_number)
                    VALUES (?, ?, ?)
                ''', (doc_id, page_data['content'], page_data['page_number']))
            
            conn.commit()
            return doc_id
            
        except Exception as e:
            conn.rollback()
            raise Exception(f"存入資料庫失敗: {str(e)}")
        finally:
            conn.close()
    
    def check_new_files(self) -> Dict:
        """
        檢查 factory 資料夾中有哪些新的 PDF 檔案需要處理
        (不執行 OCR，只返回檔案資訊)
        
        Returns:
            新檔案的數量和詳細資訊
        """
        if not self.factory_path.exists():
            raise Exception(f"資料夾不存在: {self.factory_path}")
        
        # 取得所有 PDF 檔案
        pdf_files = list(self.factory_path.glob("*.pdf"))
        
        new_files = []
        for pdf_path in pdf_files:
            filename = pdf_path.name
            filepath = str(pdf_path.absolute())
            
            # 檢查是否已在資料庫
            if not self.is_file_in_db(filename):
                file_size = pdf_path.stat().st_size
                new_files.append({
                    "filename": filename,
                    "filepath": filepath,
                    "size": file_size
                })
        
        return {
            "new_files_count": len(new_files),
            "new_files": new_files,
            "total_files": len(pdf_files)
        }
    
    def scan_factory_folder(self, progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None) -> Dict:
        """
        掃描 factory 資料夾下的所有 PDF 檔案，
        若檔名不在資料庫則進行 OCR 並存入資料庫
        
        Returns:
            處理結果統計
        """
        if not self.factory_path.exists():
            raise Exception(f"資料夾不存在: {self.factory_path}")
        
        # 取得所有 PDF 檔案
        pdf_files = list(self.factory_path.glob("*.pdf"))
        
        if not pdf_files:
            return {
                "total": 0,
                "processed": 0,
                "skipped": 0,
                "failed": 0,
                "details": []
            }
        
        processed_count = 0
        skipped_count = 0
        failed_count = 0
        details = []
        
        total_files = len(pdf_files)

        if progress_callback:
            progress_callback({
                "event": "start",
                "total": total_files,
                "processed": processed_count,
                "skipped": skipped_count,
                "failed": failed_count
            })

        for index, pdf_path in enumerate(pdf_files, start=1):
            filename = pdf_path.name
            filepath = str(pdf_path.absolute())

            if progress_callback:
                progress_callback({
                    "event": "file_started",
                    "index": index,
                    "total": total_files,
                    "current_file": filename,
                    "processed": processed_count,
                    "skipped": skipped_count,
                    "failed": failed_count
                })
            
            # 檢查是否已在資料庫
            if self.is_file_in_db(filename):
                skipped_count += 1
                details.append({
                    "filename": filename,
                    "status": "skipped",
                    "message": "已存在資料庫"
                })

                if progress_callback:
                    progress_callback({
                        "event": "file_done",
                        "index": index,
                        "total": total_files,
                        "current_file": filename,
                        "status": "skipped",
                        "processed": processed_count,
                        "skipped": skipped_count,
                        "failed": failed_count
                    })
                continue
            
            # 進行 OCR
            try:
                page_results = self.ocr_pdf(str(pdf_path))
                doc_id = self.save_to_db(filename, filepath, page_results)
                processed_count += 1
                details.append({
                    "filename": filename,
                    "status": "success",
                    "message": f"成功處理 {len(page_results)} 頁",
                    "doc_id": doc_id,
                    "pages": len(page_results)
                })

                if progress_callback:
                    progress_callback({
                        "event": "file_done",
                        "index": index,
                        "total": total_files,
                        "current_file": filename,
                        "status": "success",
                        "processed": processed_count,
                        "skipped": skipped_count,
                        "failed": failed_count
                    })
            except Exception as e:
                failed_count += 1
                details.append({
                    "filename": filename,
                    "status": "failed",
                    "message": str(e)
                })

                if progress_callback:
                    progress_callback({
                        "event": "file_done",
                        "index": index,
                        "total": total_files,
                        "current_file": filename,
                        "status": "failed",
                        "processed": processed_count,
                        "skipped": skipped_count,
                        "failed": failed_count
                    })

        result = {
            "total": len(pdf_files),
            "processed": processed_count,
            "skipped": skipped_count,
            "failed": failed_count,
            "details": details
        }

        if progress_callback:
            progress_callback({
                "event": "completed",
                "total": total_files,
                "processed": processed_count,
                "skipped": skipped_count,
                "failed": failed_count
            })

        return result
