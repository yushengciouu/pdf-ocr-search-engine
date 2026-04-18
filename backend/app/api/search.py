"""
搜尋相關的 API 路由
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from ..services.database import DatabaseService

router = APIRouter(prefix="/api/search", tags=["search"])
db_service = DatabaseService()


@router.get("")
async def search(
    q: str = Query(..., description="搜尋關鍵字", min_length=1),
    start_date: Optional[str] = Query(None, description="開始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="結束日期 (YYYY-MM-DD)")
):
    """
    搜尋文件
    
    Args:
        q: 搜尋關鍵字
        start_date: 開始日期
        end_date: 結束日期
        
    Returns:
        搜尋結果列表
    """
    try:
        results = db_service.search_documents(q, start_date=start_date, end_date=end_date)
        return {
            "success": True,
            "keyword": q,
            "count": len(results),
            "data": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
