"""
預約掃描排程服務
在背景執行緒中定時檢查並執行預約掃描任務
"""

import time
import datetime
import threading
from pathlib import Path
from .ocr_service import ocr_service
from .database import DatabaseService

class SchedulerService:
    """預約掃描排程服務類別"""

    def __init__(self):
        self.db_service = DatabaseService()
        self.running = False
        self.thread = None
        self._active_schedule_id = None
        self._lock = threading.Lock()

    def start(self):
        """啟動排程服務背景執行緒"""
        with self._lock:
            if self.running:
                return
            self.running = True
            self.thread = threading.Thread(target=self._scheduler_loop, daemon=True)
            self.thread.start()
            print("FUYU 預約掃描排程服務已啟動。")

    def stop(self):
        """停止排程服務背景執行緒"""
        with self._lock:
            self.running = False
            # 如果有正在運行的預約，也要將 ocr_service 中斷
            if self._active_schedule_id is not None:
                ocr_service.cancel_scan()
            print("FUYU 預約掃描排程服務已停止。")

    def _scheduler_loop(self):
        """排程服務主迴圈"""
        while self.running:
            try:
                # 查詢狀態為 'pending' 的預約任務
                schedules = self.db_service.list_schedules()
                pending_schedules = [s for s in schedules if s["status"] == "pending"]

                # 依據 start_time 排序，先到的先執行
                pending_schedules.sort(key=lambda s: s["start_time"])

                now = datetime.datetime.now()
                for sched in pending_schedules:
                    sched_id = sched["id"]
                    folder_path = sched["folder_path"]
                    start_time_str = sched["start_time"]
                    end_time_str = sched["end_time"]

                    try:
                        # 支援 ISO 8601 與一般 YYYY-MM-DD HH:MM:SS 格式
                        start_time = datetime.datetime.fromisoformat(start_time_str.replace(" ", "T"))
                        end_time = datetime.datetime.fromisoformat(end_time_str.replace(" ", "T"))
                    except Exception as e:
                        print(f"[Scheduler] 預約任務 #{sched_id} 時間格式解析錯誤: {e}")
                        self.db_service.update_schedule_status(sched_id, "failed", f"時間格式錯誤: {e}")
                        continue

                    # 檢查是否已到開始時間
                    if now >= start_time:
                        # 檢查結束時間是否已經過了
                        if now >= end_time:
                            self.db_service.update_schedule_status(sched_id, "stopped", "預約未執行：已超出設定的結束時間")
                            continue

                        # 檢查當前是否有其他 OCR 掃描任務正在運行
                        if ocr_service.is_scanning:
                            # 稍後重試，先更新訊息
                            self.db_service.update_schedule_status(sched_id, "pending", "排程等待中：目前系統正在執行其他掃描工作")
                            continue

                        # 啟動背景執行緒執行此預約掃描
                        with self._lock:
                            self._active_schedule_id = sched_id

                        scan_thread = threading.Thread(
                            target=self._run_scheduled_scan,
                            args=(sched_id, folder_path, end_time),
                            daemon=True
                        )
                        scan_thread.start()
                        break  # 一次只啟動一個，等下一個迴圈再說

            except Exception as e:
                print(f"[Scheduler] 排程主迴圈異常: {e}")

            time.sleep(5)

    def _run_scheduled_scan(self, sched_id: int, folder_path: str, end_time: datetime.datetime):
        """執行指定的預約掃描"""
        print(f"[Scheduler] 開始執行預約任務 #{sched_id}。資料夾: {folder_path}，結束時間: {end_time}")
        self.db_service.update_schedule_status(sched_id, "scanning", "正在掃描資料夾並執行 OCR...")

        try:
            path = Path(folder_path)
            if not path.exists() or not path.is_dir():
                raise Exception(f"目標資料夾不存在或無效: {folder_path}")

            # 獲取所有 PDF
            pdf_files = list(path.glob("*.pdf"))
            if not pdf_files:
                self.db_service.update_schedule_status(sched_id, "completed", "掃描完成：資料夾中沒有 PDF 檔案")
                return

            # 過濾未處理的檔案
            files_to_scan = []
            for pdf_path in pdf_files:
                if not ocr_service.is_file_in_db(pdf_path.name):
                    files_to_scan.append(pdf_path)

            if not files_to_scan:
                self.db_service.update_schedule_status(sched_id, "completed", "掃描完成：所有檔案均已存在於資料庫中")
                return

            # 初始化 ocr_service 狀態以利前端呈現進度
            ocr_service.is_scanning = True
            ocr_service.cancel_requested = False
            ocr_service.scan_progress = {
                "current": 0,
                "total": len(files_to_scan),
                "current_file": ""
            }
            ocr_service.scheduled_end_time = end_time

            processed = 0
            failed = 0
            timeout_occurred = False

            for i, pdf_path in enumerate(files_to_scan):
                # 1. 檢查是否超時
                if datetime.datetime.now() >= end_time:
                    timeout_occurred = True
                    break

                # 2. 檢查手動取消
                if ocr_service.cancel_requested:
                    break

                filename = pdf_path.name
                filepath = str(pdf_path.absolute())

                ocr_service.scan_progress["current"] = i + 1
                ocr_service.scan_progress["current_file"] = filename

                try:
                    # 執行 OCR 且自動寫入資料庫
                    page_results = ocr_service.ocr_pdf(filepath)
                    ocr_service.save_to_db(filename, filepath, page_results)
                    processed += 1
                except Exception as e:
                    # 判斷是否為超時造成的強制中斷
                    if "任務已被強制中斷" in str(e) and datetime.datetime.now() >= end_time:
                        timeout_occurred = True
                        break
                    elif "任務已被強制中斷" in str(e):
                        # 代表手動終止
                        break
                    else:
                        print(f"[Scheduler] 掃描 {filename} 時發生錯誤: {e}")
                        failed += 1

            # 掃描結束，清除 ocr_service 預約狀態
            ocr_service.is_scanning = False
            if hasattr(ocr_service, 'scheduled_end_time'):
                delattr(ocr_service, 'scheduled_end_time')

            # 更新排程狀態
            if timeout_occurred:
                msg = f"時間到自動停止。已成功處理: {processed}，失敗: {failed}，剩餘未處理: {len(files_to_scan) - processed - failed}"
                self.db_service.update_schedule_status(sched_id, "stopped", msg)
                print(f"[Scheduler] 預約任務 #{sched_id} 已自動超時停止。")
            elif ocr_service.cancel_requested:
                msg = f"使用者手動中止。已成功處理: {processed}，失敗: {failed}"
                self.db_service.update_schedule_status(sched_id, "stopped", msg)
                print(f"[Scheduler] 預約任務 #{sched_id} 被使用者手動中止。")
            else:
                msg = f"處理完成。成功: {processed} 份檔案"
                if failed > 0:
                    msg += f"，失敗: {failed} 份檔案"
                self.db_service.update_schedule_status(sched_id, "completed", msg)
                print(f"[Scheduler] 預約任務 #{sched_id} 已執行完畢。")

        except Exception as e:
            ocr_service.is_scanning = False
            if hasattr(ocr_service, 'scheduled_end_time'):
                try:
                    delattr(ocr_service, 'scheduled_end_time')
                except AttributeError:
                    pass
            self.db_service.update_schedule_status(sched_id, "failed", f"執行失敗: {str(e)}")
            print(f"[Scheduler] 預約任務 #{sched_id} 執行失敗: {e}")

        finally:
            with self._lock:
                self._active_schedule_id = None

# 全域單一排程服務實例
scheduler_service = SchedulerService()
