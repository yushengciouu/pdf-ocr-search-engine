"""
文件相關的 API 路由
"""

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from ..services.database import DatabaseService

router = APIRouter(prefix="/api/documents", tags=["documents"])
db_service = DatabaseService()


@router.get("")
async def list_documents():
    """
    列出所有文件

    Returns:
        所有文件的列表
    """
    try:
        documents = db_service.list_all_documents()
        return {"success": True, "count": len(documents), "data": documents}
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
                "Content-Disposition": f"inline; filename*=UTF-8''{document['filename']}"
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
