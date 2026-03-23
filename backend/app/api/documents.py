"""
文件相關的 API 路由
"""

import html
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from ..services.database import DatabaseService

router = APIRouter(prefix="/api/documents", tags=["documents"])
db_service = DatabaseService()


@router.get("")
async def list_documents():
    """
    列出所有文件

    Returns:
        所有文件的列表
    """
    try:
        documents = db_service.list_all_documents()
        return {"success": True, "count": len(documents), "data": documents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{doc_id}")
async def get_document(doc_id: int):
    """
    取得單一文件資訊

    Args:
        doc_id: 文件 ID

    Returns:
        文件資訊
    """
    try:
        document = db_service.get_document_by_id(doc_id)
        if not document:
            raise HTTPException(status_code=404, detail="找不到該文件")

        return {"success": True, "data": document}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{doc_id}/pdf")
async def get_document_pdf(doc_id: int):
    """
    取得文件對應的 PDF 檔案

    Args:
        doc_id: 文件 ID

    Returns:
        PDF 檔案串流
    """
    try:
        document = db_service.get_document_by_id(doc_id)
        if not document:
            raise HTTPException(status_code=404, detail="找不到該文件")

        pdf_path = Path(document["filepath"])
        if not pdf_path.exists() or not pdf_path.is_file():
            raise HTTPException(status_code=404, detail="找不到對應的 PDF 檔案")

        return FileResponse(
            path=str(pdf_path),
            media_type="application/pdf",
            filename=document["filename"],
            content_disposition_type="inline",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{doc_id}/viewer", response_class=HTMLResponse)
async def view_document_pdf(doc_id: int):
    """
    以網頁方式顯示文件 PDF

    Args:
        doc_id: 文件 ID

    Returns:
        內嵌 PDF 的 HTML 頁面
    """
    try:
        document = db_service.get_document_by_id(doc_id)
        if not document:
            raise HTTPException(status_code=404, detail="找不到該文件")

        pdf_path = Path(document["filepath"])
        if not pdf_path.exists() or not pdf_path.is_file():
            raise HTTPException(status_code=404, detail="找不到對應的 PDF 檔案")

        safe_title = html.escape(document["filename"])
        pdf_url = f"/api/documents/{doc_id}/pdf"

        return HTMLResponse(
            content=f"""
<!doctype html>
<html lang=\"zh-Hant\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>{safe_title}</title>
    <style>
      :root {{
        color-scheme: light;
        font-family: "Segoe UI", sans-serif;
        background: #eef2f7;
        color: #1f2937;
      }}
      * {{ box-sizing: border-box; }}
      body {{ margin: 0; }}
      .layout {{
        min-height: 100vh;
        display: grid;
        grid-template-rows: auto 1fr;
      }}
      .topbar {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
        padding: 14px 20px;
        background: linear-gradient(135deg, #1d4ed8, #0f766e);
        color: #fff;
      }}
      .title {{
        font-size: 16px;
        font-weight: 600;
        word-break: break-all;
      }}
      .actions a {{
        color: #fff;
        text-decoration: none;
        padding: 8px 12px;
        border: 1px solid rgba(255, 255, 255, 0.35);
        border-radius: 999px;
      }}
      .viewer {{
        padding: 16px;
        height: calc(100vh - 68px);
      }}
      iframe {{
        width: 100%;
        height: 100%;
        border: 0;
        border-radius: 14px;
        background: #fff;
        box-shadow: 0 18px 50px rgba(15, 23, 42, 0.12);
      }}
    </style>
  </head>
  <body>
    <div class=\"layout\">
      <header class=\"topbar\">
        <div class=\"title\">{safe_title}</div>
        <div class=\"actions\">
          <a href=\"{pdf_url}\" target=\"_blank\" rel=\"noopener noreferrer\">新分頁開啟 PDF</a>
        </div>
      </header>
      <main class=\"viewer\">
        <iframe src=\"{pdf_url}#toolbar=1&navpanes=0\" title=\"{safe_title}\"></iframe>
      </main>
    </div>
  </body>
</html>
"""
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{doc_id}")
async def delete_document(doc_id: int):
    """
    刪除文件

    Args:
        doc_id: 文件 ID

    Returns:
        刪除結果
    """
    try:
        success = db_service.delete_document(doc_id)
        if not success:
            raise HTTPException(status_code=404, detail="找不到該文件")

        return {"success": True, "message": "文件已成功刪除"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
