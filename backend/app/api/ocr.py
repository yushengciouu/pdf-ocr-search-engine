"""
OCR 相關的 API 路由
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from ..services.ocr_service import OCRService

router = APIRouter(prefix="/api/ocr", tags=["ocr"])
ocr_service = OCRService()

class ScanFileRequest(BaseModel):
    filename: str

class StartScanRequest(BaseModel):
    files: List[str]


@router.get("/check")
def check_new_files():
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
def scan_factory_folder():
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

@router.post("/scan_file")
def scan_single_file(request: ScanFileRequest):
    """
    掃描單一 PDF 檔案
    """
    try:
        result = ocr_service.scan_single_file(request.filename)
        return {
            "success": result["success"],
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/start_scan")
def start_scan(request: StartScanRequest):
    """開始背景掃描多個檔案"""
    success = ocr_service.start_background_scan(request.files)
    if not success:
        return {"success": False, "message": "掃描正在進行中"}
    return {"success": True}

@router.post("/cancel_scan")
def cancel_scan():
    """中斷背景掃描"""
    ocr_service.cancel_scan()
    return {"success": True, "message": "已發送中斷要求"}

@router.get("/progress")
def get_progress():
    """取得背景掃描進度"""
    return ocr_service.get_progress()
