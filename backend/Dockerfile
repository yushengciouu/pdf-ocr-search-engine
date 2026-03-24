# 使用官方 Python 3.10 映像檔
FROM python:3.10-slim

# 設定工作目錄
WORKDIR /app

# 安裝系統層級依賴套件 (供 OpenCV, PaddleOCR 及 pdf2image 使用)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    poppler-utils \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# 複製 python requirements
COPY requirements.txt .

# 為了確保 GPU 版本的 PaddlePaddle 順利安裝，先讀取 requirements.txt 中指定的特殊來源安裝
RUN pip install paddlepaddle-gpu==3.0.0 -i https://www.paddlepaddle.org.cn/packages/stable/cu118/
# 接著安裝其餘套件
RUN pip install --no-cache-dir -r requirements.txt

# 複製整個 backend 目錄到容器內部
COPY . .

# 暴露 FastAPI port
EXPOSE 8000

# 啟動 FastAPI 服務
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
