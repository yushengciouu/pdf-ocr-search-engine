"""
文件相關的 API 路由
"""

from pathlib import Path
import io
from typing import List

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
import pypdf
import urllib.parse

from ..services.database import DatabaseService

router = APIRouter(prefix="/api/documents", tags=["documents"])
db_service = DatabaseService()

class PrintMergeRequest(BaseModel):
    doc_ids: List[int]


@router.get("")
async def list_documents(page: int = 1, limit: int = 20):
    """
    分頁列出文件

    Args:
        page: 頁碼，從 1 開始
        limit: 每頁顯示數量

    Returns:
        包含文件列表及分頁資訊的回傳結果
    """
    try:
        if page < 1:
            page = 1
        if limit < 1:
            limit = 20
        offset = (page - 1) * limit
        total_count = db_service.get_total_documents_count()
        documents = db_service.list_documents_paginated(limit=limit, offset=offset)
        total_pages = (total_count + limit - 1) // limit
        
        return {
            "success": True, 
            "count": len(documents),
            "total_count": total_count,
            "total_pages": total_pages,
            "current_page": page,
            "limit": limit,
            "data": documents
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{doc_id}")
async def get_document(doc_id: int):
    """
    取得單一文件資訊

    Args:
        doc_id: 文件 ID

    Returns:
        文件資訊
    """
    try:
        document = db_service.get_document_by_id(doc_id)
        if not document:
            raise HTTPException(status_code=404, detail="找不到該文件")

        return {"success": True, "data": document}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{doc_id}/pdf")
async def get_document_pdf(doc_id: int):
    """
    取得文件對應的 PDF 檔案

    Args:
        doc_id: 文件 ID

    Returns:
        PDF 檔案串流
    """
    try:
        document = db_service.get_document_by_id(doc_id)
        if not document:
            raise HTTPException(status_code=404, detail="找不到該文件")

        pdf_path = Path(document["filepath"])
        
        # 跨平台相容處理：如果絕對路徑 (例如 Windows 路徑在 Docker 內) 找不到檔案，
        # 就嘗試直接從 factory 資料夾尋找該檔名的檔案。
        if not pdf_path.exists() or not pdf_path.is_file():
            factory_path = Path(__file__).parent.parent.parent.parent / "factory"
            pdf_path = factory_path / document["filename"]
            
        if not pdf_path.exists() or not pdf_path.is_file():
            raise HTTPException(status_code=404, detail="找不到對應的 PDF 檔案")

        return FileResponse(
            path=str(pdf_path),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"inline; filename*=UTF-8''{urllib.parse.quote(document['filename'])}"
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{doc_id}")
async def delete_document(doc_id: int):
    """
    刪除文件

    Args:
        doc_id: 文件 ID

    Returns:
        刪除結果
    """
    try:
        success = db_service.delete_document(doc_id)
        if not success:
            raise HTTPException(status_code=404, detail="找不到該文件")

        return {"success": True, "message": "文件已成功刪除"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/print_merge")
async def print_merge(request: PrintMergeRequest):
    """
    將多份 PDF 檔案合併為一份，以便於前端列印
    """
    try:
        if not request.doc_ids:
            raise HTTPException(status_code=400, detail="未提供任何文件 ID")

        merger = pypdf.PdfWriter()
        
        for doc_id in request.doc_ids:
            document = db_service.get_document_by_id(doc_id)
            if not document:
                continue

            pdf_path = Path(document["filepath"])
            if not pdf_path.exists() or not pdf_path.is_file():
                # 跨平台相容處理
                factory_path = Path(__file__).parent.parent.parent.parent / "factory"
                pdf_path = factory_path / document["filename"]

            if pdf_path.exists() and pdf_path.is_file():
                merger.append(str(pdf_path))

        if len(merger.pages) == 0:
            raise HTTPException(status_code=404, detail="找不到有效的 PDF 檔案進行合併")

        output_pdf_stream = io.BytesIO()
        merger.write(output_pdf_stream)
        merger.close()
        
        output_pdf_stream.seek(0)

        return StreamingResponse(
            output_pdf_stream, 
            media_type="application/pdf",
            headers={
                "Content-Disposition": "inline; filename*=UTF-8''merged_for_print.pdf"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"合併 PDF 時發生錯誤: {str(e)}")
