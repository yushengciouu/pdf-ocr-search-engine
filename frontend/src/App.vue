<template>
  <div id="app">
    <!-- 頂部導航 -->
    <header class="header">
      <div class="container">
        <div class="header-content">
          <div class="logo">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h1 class="gradient-text">FUYU 文件搜尋系統</h1>
          </div>
          <div class="header-actions">
            <span class="stat-badge">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" width="16" height="16">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              {{ totalDocuments }} 份文件
            </span>
            <button @click="scanFolder" :disabled="scanning" class="btn btn-primary">
              <svg v-if="!scanning" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" width="18" height="18">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <svg v-else class="loading" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" width="18" height="18">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ scanning ? '掃描中...' : '掃描資料夾' }}
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- 主要內容 -->
    <main class="main">
      <div class="container">
        <!-- 搜尋欄 -->
        <SearchBar @search="handleSearch" @clear="handleClear" />

        <!-- 掃描結果通知 -->
        <div v-if="scanResult" class="scan-result" :class="scanResult.type">
          <div class="scan-result-header">
            <svg v-if="scanResult.type === 'success'" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>{{ scanResult.message }}</span>
            <button @click="scanResult = null" class="close-btn">×</button>
          </div>
          <div v-if="scanResult.details" class="scan-result-details">
            <p v-if="scanResult.details.total !== undefined">共掃描 {{ scanResult.details.total || 0 }} 個檔案</p>
            <p v-if="scanResult.details.total_files !== undefined">共掃描 {{ scanResult.details.total_files || 0 }} 個檔案</p>
            <p v-if="scanResult.details.processed !== undefined">✅ 新增: {{ scanResult.details.processed || 0 }} 個</p>
            <p v-if="scanResult.details.skipped !== undefined">⏭️ 跳過: {{ scanResult.details.skipped || 0 }} 個</p>
            <p v-if="scanResult.details.failed && scanResult.details.failed > 0">❌ 失敗: {{ scanResult.details.failed }} 個</p>
          </div>
        </div>

        <!-- OCR 處理中 Toast (右下角非阻擋式) -->
        <div v-if="scanning && scanProgress" class="ocr-progress-toast">
          <div class="ocr-progress-header" style="justify-content: space-between;">
            <div style="display: flex; align-items: center; gap: 8px;">
              <div class="ocr-spinner-small">
                <svg class="loading" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              </div>
              <strong>OCR 處理中 ({{ scanProgress.current }} / {{ scanProgress.total }})</strong>
            </div>
            <button @click="cancelScan" class="btn" style="padding: 4px 8px; font-size: 0.8rem; background: #fee2e2; color: #dc2626; border: none; border-radius: 4px; cursor: pointer;">
              終止掃描
            </button>
          </div>
          <div class="ocr-progress-body">
            <p class="current-file">正在掃描: <span>{{ scanProgress.currentFilename }}</span></p>
            <div class="progress-bar-container">
              <div class="progress-bar-fill" :style="{ width: `${(scanProgress.current / scanProgress.total) * 100}%` }"></div>
            </div>
          </div>
        </div>

        <!-- 確認對話框 -->
        <div v-if="showConfirmDialog" class="confirm-dialog-overlay">
          <div class="confirm-dialog">
            <div class="confirm-dialog-header">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <h3>發現新檔案</h3>
            </div>
            
            <div class="confirm-dialog-content">
              <p class="file-count">找到 <strong>{{ newFilesInfo.new_files_count }}</strong> 個新的 PDF 檔案需要處理</p>
              
              <div class="file-list">
                <div class="file-list-header">檔案清單：</div>
                <ul>
                  <li v-for="(file, index) in newFilesInfo.new_files.slice(0, 10)" :key="index">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <span class="filename">{{ file.filename }}</span>
                    <span class="filesize">({{ formatFileSize(file.size) }})</span>
                  </li>
                  <li v-if="newFilesInfo.new_files.length > 10" class="more-files">
                    ...等 {{ newFilesInfo.new_files.length - 10 }} 個檔案
                  </li>
                </ul>
              </div>
              
              <p class="warning-text">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                OCR 處理可能需要一些時間，是否要開始處理？
              </p>
            </div>
            
            <div class="confirm-dialog-actions">
              <button @click="cancelProcess" class="btn btn-secondary">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
                取消
              </button>
              <button @click="confirmAndProcess" class="btn btn-primary">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                確認處理
              </button>
            </div>
          </div>
        </div>

        <!-- 載入狀態 -->
        <div v-if="loading" class="loading-container">
          <div class="loading-spinner-large">
            <svg class="loading" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <p>載入中...</p>
          </div>
        </div>

        <!-- 錯誤訊息 -->
        <div v-else-if="error" class="error-message">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p>{{ error }}</p>
        </div>

        <!-- 搜尋結果 -->
        <div v-else-if="searchResults.length > 0">
          <div class="results-header">
            <div>
              <h2>搜尋結果</h2>
              <span class="results-count">找到 {{ groupedSearchResults.length }} 份文件 ({{ searchResults.length }} 頁)</span>
            </div>
            
            <div class="results-actions" v-if="selectedDocs.length > 0">
              <button @click="printSelected" class="btn btn-primary btn-print" :disabled="isPrinting">
                <svg v-if="!isPrinting" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" width="18" height="18">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
                </svg>
                <svg v-else class="loading" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" width="18" height="18">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                {{ isPrinting ? '處理列印中...' : `列印已選取 (${selectedDocs.length})` }}
              </button>
            </div>
          </div>
          <div class="documents-list">
            <DocumentItem
              v-for="group in groupedSearchResults"
              :key="`search-group-${group.doc_id}`"
              :document="group"
              :selected="selectedDocs.includes(group.doc_id)"
              @toggle-select="toggleDocumentSelection(group.doc_id)"
            />
          </div>
        </div>



        <!-- 空狀態 -->
        <div v-else class="empty-state">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <h3>請輸入關鍵字搜尋文件</h3>
          <p>或是點擊右上角掃描新資料夾</p>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import SearchBar from './components/SearchBar.vue'
import DocumentItem from './components/DocumentItem.vue'

// API 位址 - 自動偵測（localhost 和外網都能用）
const API_BASE_URL = window.location.hostname === 'localhost' 
  ? 'http://localhost:8000'  // 本機使用
  : `http://${window.location.hostname}:8000`  // 外網使用當前主機名稱

export default {
  name: 'App',
  components: {
    SearchBar,
    DocumentItem
  },
  data() {
    return {
      documents: [],
      searchResults: [],
      loading: false,
      loadingMore: false,
      scanning: false,
      error: null,
      totalDocuments: 0,
      currentPage: 1,
      hasMore: false,
      scanResult: null,
      showConfirmDialog: false,
      newFilesInfo: null,
      scanProgress: null,
      scanProgressId: null,
      selectedDocs: [],
      isPrinting: false
    }
  },
  computed: {
    groupedSearchResults() {
      const map = new Map()
      for (const item of this.searchResults) {
        const key = item.doc_id
        if (!map.has(key)) {
          map.set(key, {
            doc_id: item.doc_id,
            filename: item.filename,
            upload_date: item.upload_date,
            pages: []
          })
        }
        map.get(key).pages.push({
          page_number: item.page_number,
          snippet: item.snippet
        })
      }
      return Array.from(map.values())
    }
  },
  mounted() {
    this.checkProgress()
    this.scanProgressId = setInterval(this.checkProgress, 2000)
  },
  unmounted() {
    if (this.scanProgressId) clearInterval(this.scanProgressId)
  },
  methods: {
    async fetchDocuments(page = 1) {
      if (page === 1) {
        this.loading = true
      } else {
        this.loadingMore = true
      }
      this.error = null
      
      try {
        const response = await fetch(`${API_BASE_URL}/api/documents?page=${page}&limit=20`)
        const data = await response.json()
        
        if (data.success) {
          if (page === 1) {
            this.documents = data.data
          } else {
            this.documents = [...this.documents, ...data.data]
          }
          this.totalDocuments = data.total_count
          this.currentPage = data.current_page
          this.hasMore = data.current_page < data.total_pages
        } else {
          if (page === 1) this.error = '無法載入文件列表'
        }
      } catch (err) {
        if (page === 1) this.error = '連線失敗，請確認後端伺服器是否運行'
        console.error('Error fetching documents:', err)
      } finally {
        this.loading = false
        this.loadingMore = false
      }
    },
    
    loadMore() {
      if (this.hasMore && !this.loadingMore) {
        this.fetchDocuments(this.currentPage + 1)
      }
    },
    
    async handleSearch(payload) {
      this.loading = true
      this.error = null
      this.selectedDocs = [] // 清除前次搜尋的勾選狀態
      
      // 相容舊的字串傳入或新的物件傳入
      let keyword = '';
      let url = `${API_BASE_URL}/api/search`;
      
      if (typeof payload === 'string') {
        keyword = payload;
        url += `?q=${encodeURIComponent(keyword)}`;
      } else {
        keyword = payload.keyword;
        url += `?q=${encodeURIComponent(keyword)}`;
        if (payload.startDate) url += `&start_date=${encodeURIComponent(payload.startDate)}`;
        if (payload.endDate)   url += `&end_date=${encodeURIComponent(payload.endDate)}`;
      }
      
      try {
        const response = await fetch(url)
        const data = await response.json()
        
        if (data.success) {
          this.searchResults = data.data
        } else {
          this.error = '搜尋失敗'
        }
      } catch (err) {
        this.error = '搜尋時發生錯誤'
        console.error('Error searching:', err)
      } finally {
        this.loading = false
      }
    },
    
    handleClear() {
      this.searchResults = []
      this.selectedDocs = []
    },
    
    toggleDocumentSelection(docId) {
      if (this.selectedDocs.includes(docId)) {
        this.selectedDocs = this.selectedDocs.filter(id => id !== docId)
      } else {
        this.selectedDocs.push(docId)
      }
    },

    async printSelected() {
      if (this.selectedDocs.length === 0) return;
      
      this.isPrinting = true;
      // 先開分頁避免被瀏覽器當成廣告攔截
      const win = window.open('', '_blank');
      if (win) {
        win.document.write(`<!DOCTYPE html><html><head><meta charset="utf-8"><title>準備合併檔案...</title><style>body { font-family: sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; background: #f3f4f6; color: #4f46e5; font-size: 1.2rem; }</style></head><body>正在合併文件，請稍候...</body></html>`);
      } else {
        alert("您的瀏覽器封鎖了彈出視窗，這可能導致無法開啟列印頁面。");
      }

      try {
        const response = await fetch(`${API_BASE_URL}/api/documents/print_merge`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ doc_ids: this.selectedDocs })
        });

        if (!response.ok) {
          throw new Error('無法合併產生 PDF 檔案');
        }

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        
        if (win) {
          // 將 PDF 塞進新分頁的 embed 中
          win.document.open();
          win.document.write(`<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>合併列印檔案</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    html, body { width: 100%; height: 100%; background: #525659; overflow: hidden; }
    embed { display: block; width: 100%; height: 100%; }
  </style>
</head>
<body>
  <embed src="${url}#toolbar=1&navpanes=0&scrollbar=0" type="application/pdf" width="100%" height="100%" />
</body>
</html>`);
          win.document.close();
        } else {
          // 若被擋，改為直接跳轉
          window.location.href = url;
        }
        
      } catch (err) {
        if (win) win.close();
        alert(err.message);
      } finally {
        this.isPrinting = false;
      }
    },
    
    async scanFolder() {
      // 先向後端請求開啟資料夾選擇對話框
      this.scanning = true
      this.scanResult = {
        type: 'info',
        message: '正在開啟資料夾選擇視窗，請在伺服器端畫面選擇路徑...'
      }
      
      let targetPath = '';
      try {
        const pickerResponse = await fetch(`${API_BASE_URL}/api/ocr/select_folder`);
        const pickerData = await pickerResponse.json();
        
        if (!pickerData.success || !pickerData.folder_path) {
          this.scanning = false;
          this.scanResult = {
            type: 'warning',
            message: pickerData.message || '已取消選擇資料夾'
          };
          return;
        }
        
        targetPath = pickerData.folder_path;
      } catch (err) {
        this.scanning = false;
        this.scanResult = {
          type: 'error',
          message: '無法開啟資料夾選擇器: ' + err.message
        };
        return;
      }

      this.scanResult = {
        type: 'info',
        message: '正在讀取資料夾並計算檔案數量中，這可能需要一點時間，請耐心等候...'
      }
      
      try {
        // 第一步：檢查新檔案
        const checkResponse = await fetch(`${API_BASE_URL}/api/ocr/check?folder_path=${encodeURIComponent(targetPath)}`)
        const checkData = await checkResponse.json()
        
        if (checkData.success) {
          const info = checkData.data
          
          // 如果沒有新檔案
          if (info.new_files_count === 0) {
            this.scanResult = {
              type: 'info',
              message: info.total_files === 0 ? '資料夾中沒有 PDF 檔案' : '沒有新檔案需要處理',
              details: info
            }
            this.scanning = false
            return
          }
          
          // 有新檔案，顯示確認對話框
          this.newFilesInfo = info
          this.showConfirmDialog = true
          this.scanning = false
        } else {
          this.scanResult = {
            type: 'error',
            message: '檢查檔案失敗'
          }
          this.scanning = false
        }
      } catch (err) {
        this.scanResult = {
          type: 'error',
          message: '檢查檔案時發生錯誤: ' + err.message
        }
        console.error('Error checking files:', err)
        this.scanning = false
      }
    },
    
    async checkProgress() {
      try {
        const response = await fetch(`${API_BASE_URL}/api/ocr/progress`)
        const data = await response.json()
        
        if (data.is_scanning) {
          // 如果後端正在掃描，同步前台狀態
          if (!this.scanning) this.scanning = true
          this.scanProgress = {
            current: data.progress.current,
            total: data.progress.total,
            currentFilename: data.progress.current_file
          }
        } else if (this.scanning) {
          // 原本在掃描，現在後端回報停止，代表完成
          this.scanning = false
          this.scanProgress = null
          this.scanResult = {
            type: 'success',
            message: '背景 OCR 處理已全部完成！'
          }
          await this.fetchDocuments()
        } else {
          // 沒在掃描
          this.scanning = false
          this.scanProgress = null
        }
      } catch (err) {
        console.error('Error fetching progress:', err)
      }
    },

    async cancelScan() {
      try {
        await fetch(`${API_BASE_URL}/api/ocr/cancel_scan`, { method: 'POST' })
        if (this.scanProgress) {
          this.scanProgress.currentFilename = "正在停止任務中..."
        }
      } catch (err) {
        console.error('Error cancelling scan:', err)
      }
    },

    async confirmAndProcess() {
      // 關閉對話框
      this.showConfirmDialog = false
      this.scanning = true
      this.scanResult = null
      
      const filesToProcess = this.newFilesInfo.new_files || []
      const filepaths = filesToProcess.map(f => f.filepath)
      
      try {
        // 通知後端開始背景掃描
        const response = await fetch(`${API_BASE_URL}/api/ocr/start_scan`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ filepaths: filepaths })
        })
        
        const data = await response.json()
        
        if (data.success) {
          // 立刻呼叫一次 checkProgress 以更新畫面，之後就交給 setInterval
          this.checkProgress()
        } else {
          this.scanResult = {
            type: 'error',
            message: data.message || '啟動掃描失敗，可能已經有任務在進行中'
          }
          this.scanning = false
        }
      } catch (err) {
        this.scanResult = {
          type: 'error',
          message: '請求處理時發生錯誤: ' + err.message
        }
        console.error('Error processing:', err)
        this.scanning = false
      } finally {
        this.newFilesInfo = null
      }
    },
    
    cancelProcess() {
      this.showConfirmDialog = false
      this.newFilesInfo = null
    },
    
    formatFileSize(bytes) {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
    }
  }
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
@import './assets/main.css';

.header {
  background: var(--color-bg-secondary);
  border-bottom: 1px solid var(--color-border);
  padding: var(--spacing-lg) 0;
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(10px);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--spacing-lg);
}

.logo {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.logo svg {
  width: 32px;
  height: 32px;
  color: var(--color-primary);
}

.logo h1 {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: var(--spacing-md);
  align-items: center;
}

.stat-badge {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--color-bg-tertiary);
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.main {
  padding: var(--spacing-2xl) 0;
  min-height: calc(100vh - 100px);
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
}

.results-header > div {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.results-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.btn-print {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background-color: var(--color-primary);
  color: white;
  padding: 8px 16px;
  border-radius: var(--radius-md);
  box-shadow: 0 4px 6px -1px rgba(99, 102, 241, 0.2), 0 2px 4px -1px rgba(99, 102, 241, 0.1);
}

.btn-print:hover {
  background-color: var(--color-primary-dark);
}

.results-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.results-count {
  font-size: 0.875rem;
  color: var(--color-text-muted);
  background: var(--color-bg-tertiary);
  padding: var(--spacing-xs) var(--spacing-md);
  border-radius: var(--radius-md);
}

.documents-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.load-more-container {
  display: flex;
  justify-content: center;
  margin-top: var(--spacing-xl);
}

.scan-result {
  margin-bottom: var(--spacing-lg);
  padding: var(--spacing-md);
  border-radius: var(--radius-md);
  border: 1px solid;
  animation: fadeIn var(--transition-normal);
}

.scan-result.success {
  background: rgba(34, 197, 94, 0.1);
  border-color: rgba(34, 197, 94, 0.3);
  color: #86efac;
}

.scan-result.info {
  background: rgba(59, 130, 246, 0.1);
  border-color: rgba(59, 130, 246, 0.3);
  color: #93c5fd;
}

.scan-result.error {
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.3);
  color: #fca5a5;
}

.scan-result-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-weight: 500;
  margin-bottom: var(--spacing-sm);
}

.scan-result-header svg {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.scan-result-header .close-btn {
  margin-left: auto;
  background: none;
  border: none;
  color: inherit;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  transition: background var(--transition-fast);
}

.scan-result-header .close-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

.scan-result-details {
  font-size: 0.875rem;
  opacity: 0.9;
  padding-left: 28px;
}

.scan-result-details p {
  margin: 2px 0;
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.loading-spinner-large {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-md);
  color: var(--color-primary);
}

.loading-spinner-large svg {
  width: 48px;
  height: 48px;
}

.error-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-2xl);
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: var(--radius-lg);
  color: #fca5a5;
}

.error-message svg {
  width: 48px;
  height: 48px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-2xl);
  text-align: center;
  color: var(--color-text-muted);
}

.empty-state svg {
  width: 64px;
  height: 64px;
  opacity: 0.5;
}

.empty-state h3 {
  font-size: 1.25rem;
  color: var(--color-text-secondary);
}

/* OCR 進度 Toast 卡片 (右下角) */
.ocr-progress-toast {
  position: fixed;
  bottom: var(--spacing-xl);
  right: var(--spacing-xl);
  width: 320px;
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3), 0 8px 10px -6px rgba(0, 0, 0, 0.2);
  z-index: 1000;
  overflow: hidden;
  animation: slideInRight 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes slideInRight {
  from { opacity: 0; transform: translateX(50px); }
  to { opacity: 1; transform: translateX(0); }
}

.ocr-progress-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-md);
  background: rgba(99, 102, 241, 0.1);
  border-bottom: 1px solid var(--color-border);
}

.ocr-spinner-small {
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ocr-spinner-small svg {
  width: 100%;
  height: 100%;
  color: var(--color-primary);
}

.ocr-progress-header strong {
  font-size: 0.875rem;
  color: var(--color-primary-light);
  font-weight: 600;
}

.ocr-progress-body {
  padding: var(--spacing-md);
}

.current-file {
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-sm);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.current-file span {
  color: var(--color-text-primary);
  font-weight: 500;
}

.progress-bar-container {
  height: 6px;
  background: var(--color-bg-tertiary);
  border-radius: 3px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  background: var(--gradient-primary);
  border-radius: 3px;
  transition: width 0.3s ease-out;
}

/* 確認對話框 */
.confirm-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn var(--transition-normal);
}

.confirm-dialog {
  background: var(--color-bg-secondary);
  border-radius: var(--radius-xl);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-xl);
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  animation: slideUp 0.3s ease-out;
}

.confirm-dialog-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-xl);
  border-bottom: 1px solid var(--color-border);
}

.confirm-dialog-header svg {
  width: 32px;
  height: 32px;
  color: var(--color-primary);
  flex-shrink: 0;
}

.confirm-dialog-header h3 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.confirm-dialog-content {
  padding: var(--spacing-xl);
}

.file-count {
  font-size: 1.125rem;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-lg);
  text-align: center;
}

.file-count strong {
  color: var(--color-primary);
  font-size: 1.5rem;
}

.file-list {
  background: var(--color-bg-tertiary);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
  max-height: 300px;
  overflow-y: auto;
}

.file-list-header {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  font-weight: 500;
  margin-bottom: var(--spacing-sm);
}

.file-list ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.file-list li {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm);
  border-radius: var(--radius-sm);
  transition: background var(--transition-fast);
}

.file-list li:hover {
  background: rgba(255, 255, 255, 0.05);
}

.file-list li svg {
  width: 16px;
  height: 16px;
  color: var(--color-primary);
  flex-shrink: 0;
}

.file-list .filename {
  color: var(--color-text-primary);
  font-size: 0.875rem;
  flex: 1;
}

.file-list .filesize {
  color: var(--color-text-muted);
  font-size: 0.75rem;
}

.file-list .more-files {
  color: var(--color-text-muted);
  font-style: italic;
  justify-content: center;
  margin-top: var(--spacing-xs);
}

.warning-text {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-md);
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: var(--radius-md);
  color: #93c5fd;
  font-size: 0.875rem;
}

.warning-text svg {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.confirm-dialog-actions {
  display: flex;
  gap: var(--spacing-md);
  padding: var(--spacing-xl);
  border-top: 1px solid var(--color-border);
  justify-content: flex-end;
}

.confirm-dialog-actions .btn {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-md) var(--spacing-lg);
}

.confirm-dialog-actions .btn svg {
  width: 18px;
  height: 18px;
}

.btn-secondary {
  background: var(--color-bg-tertiary);
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
}

.btn-secondary:hover {
  background: var(--color-bg-secondary);
  color: var(--color-text-primary);
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: var(--spacing-md);
  }
  
  .logo h1 {
    font-size: 1.25rem;
  }
  
  .header-actions {
    width: 100%;
    justify-content: space-between;
  }
}
</style>
