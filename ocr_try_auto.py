import os
import numpy as np
from paddleocr import PaddleOCR
from pdf2image import convert_from_path

def ocr_pdf(pdf_path: str):
    """
    將 PDF 的每一頁分別進行 OCR
    返回: list of dict, 每個 dict 包含 page_number 和 content
    """
    ocr = PaddleOCR(use_angle_cls=True, lang="ch")
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


import sqlite3
import glob

DB_PATH = "fuyu.sqlite"

def is_file_in_db(filename: str) -> bool:
    """
    檢查檔名是否已存在資料庫
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT COUNT(*) FROM documents WHERE filename = ?
    ''', (filename,))
    
    count = cursor.fetchone()[0]
    conn.close()
    
    return count > 0


def save_to_db(filename: str, filepath: str, page_results: list):
    """
    將 OCR 結果存入資料庫
    page_results: list of dict, 每個 dict 包含 page_number 和 content
    """
    conn = sqlite3.connect(DB_PATH)
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
        print(f"✅ 資料已成功存入資料庫 (Doc ID: {doc_id}, 共 {len(page_results)} 頁)")
        
    except Exception as e:
        print(f"❌ 存入資料庫失敗: {e}")
        conn.rollback()
    finally:
        conn.close()


def process_factory_folder():
    """
    掃描 factory 資料夾下的所有 PDF 檔案，
    若檔名不在資料庫則進行 OCR 並存入資料庫
    """
    factory_path = os.path.join(os.path.dirname(__file__), "factory")
    
    if not os.path.exists(factory_path):
        print(f"❌ 資料夾不存在: {factory_path}")
        return
    
    # 取得所有 PDF 檔案
    pdf_files = glob.glob(os.path.join(factory_path, "*.pdf"))
    
    if not pdf_files:
        print(f"⚠️ factory 資料夾中沒有 PDF 檔案")
        return
    
    print(f"📂 找到 {len(pdf_files)} 個 PDF 檔案")
    
    processed_count = 0
    skipped_count = 0
    
    for pdf_path in pdf_files:
        filename = os.path.basename(pdf_path)
        filepath = os.path.abspath(pdf_path)
        
        # 檢查是否已在資料庫
        if is_file_in_db(filename):
            print(f"⏭️ 跳過 (已存在資料庫): {filename}")
            skipped_count += 1
            continue
        
        # 進行 OCR
        print(f"🔍 正在處理: {filename} ...")
        try:
            page_results = ocr_pdf(pdf_path)
            save_to_db(filename, filepath, page_results)
            processed_count += 1
        except Exception as e:
            print(f"❌ 處理失敗 {filename}: {e}")
    
    print(f"\n📊 處理完成！新增: {processed_count} 個，跳過: {skipped_count} 個")


if __name__ == "__main__":
    process_factory_folder()

