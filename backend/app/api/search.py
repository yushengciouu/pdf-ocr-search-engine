"""
搜尋相關的 API 路由
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from ..services.database import DatabaseService

router = APIRouter(prefix="/api/search", tags=["search"])
db_service = DatabaseService()


@router.get("")
async def search(q: str = Query(..., description="搜尋關鍵字", min_length=1)):
    """
    搜尋文件
    
    Args:
        q: 搜尋關鍵字
        
    Returns:
        搜尋結果列表
    """
    try:
        results = db_service.search_documents(q)
        return {
            "success": True,
            "keyword": q,
            "count": len(results),
            "data": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
