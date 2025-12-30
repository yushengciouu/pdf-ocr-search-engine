"""
文件相關的 API 路由
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List
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
        return {
            "success": True,
            "count": len(documents),
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
        
        return {
            "success": True,
            "data": document
        }
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
        
        return {
            "success": True,
            "message": "文件已成功刪除"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
