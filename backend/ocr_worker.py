from fastapi import FastAPI, UploadFile, File, HTTPException
from paddleocr import PaddleOCR
import numpy as np
from PIL import Image
import io
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ocr_worker")

app = FastAPI(
    title="FUYU OCR Worker Service", 
    description="GPU-accelerated PaddleOCR container service"
)

ocr = None

def get_ocr():
    global ocr
    if ocr is None:
        try:
            import paddle
            # 自動偵測是否可以使用 GPU
            use_gpu = paddle.device.is_compiled_with_cuda() and paddle.device.cuda.device_count() > 0
            device_str = "gpu" if use_gpu else "cpu"
            logger.info(f"[OCR Worker] 初始化 PaddleOCR，使用設備: {device_str}")
            ocr = PaddleOCR(use_angle_cls=True, lang="ch", device=device_str)
            logger.info("[OCR Worker] PaddleOCR 初始化成功。")
        except Exception as e:
            logger.error(f"[OCR Worker] 初始化 PaddleOCR 失敗: {e}")
            raise HTTPException(status_code=500, detail=f"OCR引擎初始化失敗: {str(e)}")
    return ocr

@app.get("/health")
def health_check():
    """健康檢查端點，顯示當前 GPU 狀態"""
    try:
        import paddle
        use_gpu = paddle.device.is_compiled_with_cuda() and paddle.device.cuda.device_count() > 0
        return {
            "status": "healthy",
            "device": "gpu" if use_gpu else "cpu",
            "gpu_count": paddle.device.cuda.device_count() if use_gpu else 0
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """接收上傳的頁面圖片，並執行 PaddleOCR 辨識，回傳文字清單"""
    try:
        img_bytes = await file.read()
        image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        
        ocr_engine = get_ocr()
        result = ocr_engine.predict(np.array(image))
        
        rec_texts = []
        if result and len(result) > 0:
            # 比照原本 ocr_service.py 中對 result[0]["rec_texts"] 的解析方式
            if isinstance(result, list) and len(result) > 0:
                first_res = result[0]
                if isinstance(first_res, dict) and "rec_texts" in first_res:
                    rec_texts = first_res["rec_texts"]
                elif hasattr(first_res, "rec_texts"):
                    rec_texts = first_res.rec_texts
        
        return {"rec_texts": rec_texts}
    except Exception as e:
        logger.error(f"[OCR Worker] 執行 OCR 預測出錯: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
