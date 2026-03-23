"""
OCR 相關的 API 路由
"""
from fastapi import APIRouter, HTTPException
from ..services.ocr_service import OCRService

router = APIRouter(prefix="/api/ocr", tags=["ocr"])
ocr_service = OCRService()


@router.get("/check")
async def check_new_files():
    """
    檢查 factory 資料夾中有哪些新的 PDF 檔案需要處理
    (不執行 OCR，只返回檔案資訊)
    
    Returns:
        新檔案的數量和詳細資訊
    """
    try:
        result = ocr_service.check_new_files()
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
