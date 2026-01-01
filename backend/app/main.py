"""
FastAPI 主程式
FUYU 文件搜尋系統的後端 API
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import documents, search, ocr

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


@app.get("/")
async def root():
    """
    API 根路徑
    """
    return {
        "message": "歡迎使用 FUYU 文件搜尋系統 API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "search": "/api/search?q=關鍵字",
            "list_documents": "/api/documents",
            "get_document": "/api/documents/{doc_id}",
            "delete_document": "/api/documents/{doc_id}"
        }
    }


@app.get("/health")
async def health_check():
    """
    健康檢查端點
    """
    return {"status": "healthy"}
