"""
FastAPI 主程式
FUYU 文件搜尋系統的後端 API
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from .api import documents, search, ocr, scheduler

# 建立 FastAPI 應用程式
app = FastAPI(
    title="FUYU 文件搜尋系統 API",
    description="基於 FastAPI 的 PDF 文件搜尋系統",
    version="1.0.0"
)

# 設定 CORS（讓前端可以呼叫 API）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 開發時允許所有來源，正式環境應該限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 註冊路由
app.include_router(documents.router)
app.include_router(search.router)
app.include_router(ocr.router)
app.include_router(scheduler.router)


@app.get("/health")
async def health_check():
    """健康檢查端點"""
    return {"status": "healthy"}

@app.on_event("startup")
def startup_event():
    from .services.scheduler_service import scheduler_service
    scheduler_service.start()

@app.on_event("shutdown")
def shutdown_event():
    from .services.scheduler_service import scheduler_service
    scheduler_service.stop()

# 取得 frontend/dist 的絕對路徑
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "dist")

if os.path.exists(frontend_dist):
    # 掛載靜態資源 (JS, CSS, 圖片等)
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")
    
    # 攔截所有其他路由，交由 Vue 處理 (SPA)
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # 排除 API 請求，避免 API 404 時回傳 HTML
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API endpoint not found")
            
        file_path = os.path.join(frontend_dist, full_path)
        # 如果請求的是特定存在的檔案 (例如 favicon.ico)
        if os.path.isfile(file_path) and not os.path.isdir(file_path):
            return FileResponse(file_path)
            
        # 否則一律回傳 index.html
        return FileResponse(os.path.join(frontend_dist, "index.html"))
else:
    @app.get("/")
    async def root():
        return {"message": "歡迎使用 FUYU API (前端尚未打包，請在 frontend 目錄執行 npm run build)"}
