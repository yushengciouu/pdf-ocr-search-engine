"""
OCR 相關的 API 路由
"""
from fastapi import APIRouter, HTTPException
from ..services.ocr_service import OCRService

router = APIRouter(prefix="/api/ocr", tags=["ocr"])
ocr_service = OCRService()


@router.post("/scan")
async def scan_factory_folder():
    """
    掃描 factory 資料夾並處理新的 PDF 檔案
    
    Returns:
        處理結果統計
    """
    try:
        result = ocr_service.scan_factory_folder()
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
