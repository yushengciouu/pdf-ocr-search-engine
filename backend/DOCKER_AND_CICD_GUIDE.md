# 🐳 Docker 與 CI/CD 實戰指南 (Containerization & Automation Guide)

這份指南將詳細說明如何將我們的 PaddleOCR 後端專案升級為 **5.0 架構** 的第一步：**容器化與自動化**。

---

## 🧐 1. 為什麼需要 Docker？ (The "Why")

### 痛苦的現狀
想像你要把這個專案交給新來的同事，或者部署到雲端主機：
1. 他們要安裝 Python 3.10 (不能是 3.11，因為相容性)。
2. 他們要安裝 CUDA 驅動 (如果有的話)。
3. 他們要 `pip install -r requirements.txt`，結果發現 `paddlepaddle` 在 Windows 和 Mac 上安裝指令不一樣。
4. **結果**：你的電腦能跑，他的電腦報錯。

### Docker 的解決方案
Docker 就像一個**「標準貨櫃」**。
我們不只把程式碼 (貨物) 給對方，而是連同作業系統環境、Python、所有套件 (整個貨櫃) 一起打包給對方。
對方只要有 Docker，就能保證跑起來跟你在開發時**一模一樣**。
> 💡 **Windows 用戶注意**: 建議安裝 Docker Desktop 並開啟 WSL 2 整合，以獲得最佳效能。

---

## 🛠️ 2. 實作教學：怎麼做？ (The "How")

我們需要新增三個關鍵檔案。

### 步驟 A: 撰寫 `Dockerfile`
這個檔案是用來**「製作映像檔 (Image)」**的食譜。告訴 Docker 怎麼從零打造出能跑我們程式的環境。

在 `backend/` 目錄下建立一個名為 `Dockerfile` 的檔案 (沒有副檔名)：

```dockerfile
# 1. 選擇基底映像檔 (就像選擇作業系統光碟)
# 使用官方 Python 3.10 瘦身版 (Slim)，體積較小
FROM python:3.10-slim

# 2. 設定工作目錄
# 進到容器內的 /app 資料夾
WORKDIR /app

# 3. 安裝系統依賴 (System Dependencies)
# PaddleOCR 需要一些 C++ 函式庫 (libgomp1 等)，pdf2image 需要 poppler-utils
RUN apt-get update && apt-get install -y \
    libgomp1 \
    libgl1-mesa-glx \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# 4. 複製依賴清單並安裝
# 先只複製 requirements.txt，利用 Docker 快取機制加速建置
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. 複製所有程式碼
COPY . .

# 6. 宣告對外埠號 (只是宣告，實際上還是要看怎麼跑)
EXPOSE 8000

# 7. 啟動指令
# 當這個容器跑起來時，執行這個指令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 步驟 B: 撰寫 `docker-compose.yml`
如果 `Dockerfile` 是單個樂手，`docker-compose` 就是指揮家。它可以定義怎麼同時跑後端、資料庫、Redis 等多個服務。

在專案根目錄 (或 `backend/` 上一層) 建立 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  # 定義我們的後端服務
  api:
    build: ./backend  # 指定 Dockerfile 所在的資料夾
    ports:
      - "8000:8000"   # 把容器內的 8000 對應到電腦的 8000
    volumes:
      - ./backend/storage:/app/storage # (選用) 把上傳檔案掛載出來，避免容器刪除後檔案消失
    restart: always
```

**如何使用？**
只要在終端機輸入一行指令，整個後端就跑起來了，完全不用管 Python 環境：
```bash
docker-compose up -d --build
```

---

## 🤖 3. 自動化部署：CI/CD (GitHub Actions)

### 什麼是 CI/CD？
*   **CI (Continuous Integration)**: 每次你 Push 程式碼，機器人自動幫你跑測試，確保沒把程式改壞。
*   **CD (Continuous Deployment)**: 測試通過後，機器人自動把新版程式推上雲端伺服器。

### 實作教學
在專案根目錄建立 `.github/workflows/main.yml`：

```yaml
name: Backend CI/CD

# 當有人 Push 到 main 分支時觸發
on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

jobs:
  build-and-test:
    runs-on: ubuntu-latest # 使用 GitHub 提供的 Ubuntu 機器

    steps:
    # 1. 把程式碼抓下來
    - uses: actions/checkout@v3

    # 2. 設定 Python 環境
    - name: Set up Python 3.10
      uses: actions/setup-python@v4
      with:
        python-version: "3.10"

    # 3. 安裝依賴
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pytest httpx
        if [ -f backend/requirements.txt ]; then pip install -r backend/requirements.txt; fi

    # 4. 跑測試 (假設你有寫測試)
    # 這裡示範簡單的語法檢查
    - name: Lint with flake8
      run: |
        pip install flake8
        # 檢查語法錯誤
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

    # 5. (進階) 建置 Docker Image 並推送到 Docker Hub
    # - name: Build and push Docker image
    #   ...
```

---

## 💡 總結 (Summary)

1.  **Dockerfile**: 讓環境可攜，解決 "It works on my machine" 問題。
2.  **docker-compose**: 一鍵啟動所有服務。
3.  **CI/CD**: 把重複的測試和部署工作交給機器人，讓你專注寫程式。

這就是邁向 **5.0 架構** 的標準配備。雖然初期設定有點麻煩，但長期來看，它節省的時間是**指數級**的。
