"""
OCR 相關的 API 路由
"""
import threading
import uuid
from copy import deepcopy
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from ..services.ocr_service import OCRService

router = APIRouter(prefix="/api/ocr", tags=["ocr"])
ocr_service = OCRService()
scan_jobs = {}
scan_jobs_lock = threading.Lock()


def _iso_utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _calculate_progress_percent(job: dict) -> float:
    total = max(int(job.get("total", 0) or 0), 0)
    done = int(job.get("processed", 0) or 0) + int(job.get("skipped", 0) or 0) + int(job.get("failed", 0) or 0)
    if total <= 0:
        return 100.0 if job.get("status") == "completed" else 0.0
    return round(min(done / total, 1.0) * 100, 1)


def _get_job_snapshot(job_id: str) -> dict:
    with scan_jobs_lock:
        job = scan_jobs.get(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="找不到指定的 OCR 任務")
        snapshot = deepcopy(job)

    snapshot["progress_percent"] = _calculate_progress_percent(snapshot)
    return snapshot


def _update_job(job_id: str, **updates) -> None:
    with scan_jobs_lock:
        job = scan_jobs.get(job_id)
        if job is None:
            return
        job.update(updates)


def _run_scan_job(job_id: str) -> None:
    _update_job(job_id, status="running", started_at=_iso_utc_now())

    def progress_callback(payload: dict) -> None:
        updates = {
            "total": payload.get("total", 0),
            "processed": payload.get("processed", 0),
            "skipped": payload.get("skipped", 0),
            "failed": payload.get("failed", 0),
        }
        current_file = payload.get("current_file")
        if current_file:
            updates["current_file"] = current_file
        _update_job(job_id, **updates)

    try:
        result = ocr_service.scan_factory_folder(progress_callback=progress_callback)
        _update_job(
            job_id,
            status="completed",
            result=result,
            total=result.get("total", 0),
            processed=result.get("processed", 0),
            skipped=result.get("skipped", 0),
            failed=result.get("failed", 0),
            current_file=None,
            finished_at=_iso_utc_now()
        )
    except Exception as exc:
        _update_job(
            job_id,
            status="failed",
            error=str(exc),
            current_file=None,
            finished_at=_iso_utc_now()
        )


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


@router.post("/scan/start")
async def start_scan_job():
    """
    啟動背景 OCR 任務，立即回傳 job_id。
    前端可透過 /api/ocr/scan/status/{job_id} 輪詢進度。
    """
    try:
        check_info = ocr_service.check_new_files()
        job_id = str(uuid.uuid4())

        initial_job = {
            "job_id": job_id,
            "status": "queued",
            "total": check_info.get("total_files", 0),
            "processed": 0,
            "skipped": 0,
            "failed": 0,
            "current_file": None,
            "result": None,
            "error": None,
            "created_at": _iso_utc_now(),
            "started_at": None,
            "finished_at": None
        }

        with scan_jobs_lock:
            scan_jobs[job_id] = initial_job

        scan_thread = threading.Thread(target=_run_scan_job, args=(job_id,), daemon=True)
        scan_thread.start()

        return {
            "success": True,
            "data": {
                "job_id": job_id,
                "check_info": check_info
            }
        }
    except Exception as e:
        message = str(e)
        lower_message = message.lower()
        if "no module named" in lower_message or "paddle" in lower_message:
            message = f"{message}。請確認後端是用 conda 環境 paddle_env 啟動（例如：conda run -n paddle_env uvicorn app.main:app --reload --host 0.0.0.0 --port 8000）"
        raise HTTPException(status_code=500, detail=message)


@router.get("/scan/status/{job_id}")
async def get_scan_job_status(job_id: str):
    """取得指定 OCR 任務的目前狀態與進度。"""
    return {
        "success": True,
        "data": _get_job_snapshot(job_id)
    }


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
