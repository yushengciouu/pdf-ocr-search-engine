"""
預約排程 API 路由
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from ..services.database import DatabaseService
from ..services.ocr_service import ocr_service

router = APIRouter(prefix="/api/scheduler", tags=["scheduler"])
db_service = DatabaseService()

class CreateScheduleRequest(BaseModel):
    folder_path: str
    start_time: str
    end_time: str

@router.post("/schedule")
def create_schedule(request: CreateScheduleRequest):
    """
    新增預約掃描任務
    """
    try:
        schedule_id = db_service.create_schedule(
            request.folder_path,
            request.start_time,
            request.end_time
        )
        return {
            "success": True,
            "data": {
                "id": schedule_id,
                "folder_path": request.folder_path,
                "start_time": request.start_time,
                "end_time": request.end_time,
                "status": "pending"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/schedules")
def list_schedules():
    """
    獲取所有預約排程列表
    """
    try:
        schedules = db_service.list_schedules()
        return {
            "success": True,
            "data": schedules
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{schedule_id}/stop")
def stop_schedule(schedule_id: int):
    """
    中止或取消預約掃描任務
    """
    try:
        # 尋找當前任務狀態
        schedules = db_service.list_schedules()
        target_schedule = None
        for s in schedules:
            if s["id"] == schedule_id:
                target_schedule = s
                break

        if not target_schedule:
            raise HTTPException(status_code=404, detail="找不到指定的預約任務")

        status = target_schedule["status"]
        if status == "scanning":
            # 如果正在執行，觸發 ocr_service 中斷
            ocr_service.cancel_scan()
            return {"success": True, "message": "已發送中止執行訊號"}
        elif status == "pending":
            # 如果還在等待，直接改成 stopped 狀態
            db_service.update_schedule_status(schedule_id, "stopped", "使用者手動取消預約")
            return {"success": True, "message": "已成功取消預約"}
        else:
            return {"success": False, "message": "此任務已結束，無法中止"}

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{schedule_id}")
def delete_schedule(schedule_id: int):
    """
    刪除指定的預約任務記錄
    """
    try:
        # 如果任務正在進行，拒絕刪除，請先停止
        schedules = db_service.list_schedules()
        for s in schedules:
            if s["id"] == schedule_id and s["status"] == "scanning":
                raise HTTPException(status_code=400, detail="任務正在執行中，請先停止後再刪除")

        success = db_service.delete_schedule(schedule_id)
        return {
            "success": success
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
