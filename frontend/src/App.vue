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

        <!-- OCR 處理中提示 -->
        <div v-if="scanning && scanProgress && showProgressPanel" class="ocr-progress-panel">
          <div class="ocr-progress-head">
            <div class="ocr-progress-title">
              <svg class="loading" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>OCR 執行中</span>
            </div>
            <button class="close-btn" @click="hideProgressPanel" title="隱藏進度面板">×</button>
          </div>
          <p class="ocr-progress-text">
            {{ scanProgress.current_file ? `目前檔案：${scanProgress.current_file}` : '正在準備 OCR 任務...' }}
          </p>
          <div class="ocr-progress-track">
            <div class="ocr-progress-bar" :style="{ width: `${scanProgress.progress_percent || 0}%` }"></div>
          </div>
          <p class="ocr-progress-meta">
            {{ scanProgress.processed || 0 }} 成功 / {{ scanProgress.skipped || 0 }} 跳過 / {{ scanProgress.failed || 0 }} 失敗 · {{ scanProgress.progress_percent || 0 }}%
          </p>
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
            <h2>搜尋結果</h2>
            <span class="results-count">找到 {{ searchResults.length }} 筆結果</span>
          </div>
          <div class="documents-list">
            <DocumentItem
              v-for="doc in searchResults"
              :key="`search-${doc.doc_id}-${doc.page_number}`"
              :document="doc"
            />
          </div>
        </div>

        <!-- 所有文件列表 -->
        <div v-else-if="documents.length > 0">
          <div class="results-header">
            <h2>所有文件</h2>
            <span class="results-count">共 {{ documents.length }} 份文件</span>
          </div>
          <div class="documents-list">
            <DocumentItem
              v-for="doc in documents"
              :key="`doc-${doc.id}`"
              :document="doc"
            />
          </div>
        </div>

        <!-- 空狀態 -->
        <div v-else class="empty-state">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <h3>尚無文件</h3>
          <p>點擊「掃描資料夾」按鈕來處理 PDF 文件</p>
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
      scanning: false,
      error: null,
      totalDocuments: 0,
      scanResult: null,
      showConfirmDialog: false,
      newFilesInfo: null,
      scanJobId: null,
      scanProgress: null,
      showProgressPanel: true,
      scanPollingTimer: null
    }
  },
  mounted() {
    this.fetchDocuments()
  },
  beforeUnmount() {
    this.stopScanPolling()
  },
  methods: {
    async fetchDocuments() {
      this.loading = true
      this.error = null
      
      try {
        const response = await fetch(`${API_BASE_URL}/api/documents`)
        const data = await response.json()
        
        if (data.success) {
          this.documents = data.data
          this.totalDocuments = data.count
        } else {
          this.error = '無法載入文件列表'
        }
      } catch (err) {
        this.error = '連線失敗，請確認後端伺服器是否運行'
        console.error('Error fetching documents:', err)
      } finally {
        this.loading = false
      }
    },
    
    async handleSearch(keyword) {
      this.loading = true
      this.error = null
      
      try {
        const response = await fetch(`${API_BASE_URL}/api/search?q=${encodeURIComponent(keyword)}`)
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
      this.fetchDocuments()
    },
    
    async scanFolder() {
      this.scanning = true
      this.scanResult = null
      
      try {
        // 第一步：檢查新檔案
        const checkResponse = await fetch(`${API_BASE_URL}/api/ocr/check`)
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
    
    async confirmAndProcess() {
      this.showConfirmDialog = false
      this.scanning = true
      this.scanResult = null
      this.showProgressPanel = true
      this.scanProgress = {
        processed: 0,
        skipped: 0,
        failed: 0,
        total: this.newFilesInfo?.total_files || 0,
        progress_percent: 0,
        current_file: null
      }
      
      try {
        let response = await fetch(`${API_BASE_URL}/api/ocr/scan/start`, {
          method: 'POST'
        })

        // Backward compatibility: backend still running old version without /scan/start
        if (response.status === 404) {
          const legacyResponse = await fetch(`${API_BASE_URL}/api/ocr/scan`, {
            method: 'POST'
          })
          const legacyData = await legacyResponse.json()
          if (!legacyResponse.ok || !legacyData.success) {
            throw new Error(legacyData.detail || '啟動 OCR 任務失敗')
          }

          const result = legacyData.data
          this.scanning = false
          this.newFilesInfo = null
          this.scanProgress = null

          if ((result.processed || 0) > 0) {
            this.scanResult = {
              type: 'success',
              message: `成功處理 ${result.processed} 個新檔案！`,
              details: result
            }
            await this.fetchDocuments()
          } else {
            this.scanResult = {
              type: 'info',
              message: '掃描完成，沒有新檔案需要處理',
              details: result
            }
          }
          return
        }

        const data = await response.json()

        if (!response.ok) {
          throw new Error(data.detail || '啟動 OCR 任務失敗')
        }
        
        if (data.success) {
          this.scanJobId = data.data?.job_id || null
          if (!this.scanJobId) {
            throw new Error('無法取得 OCR 任務 ID')
          }
          this.startScanPolling()
        } else {
          throw new Error(data.detail || '啟動 OCR 任務失敗')
        }
      } catch (err) {
        this.scanResult = {
          type: 'error',
          message: '處理時發生錯誤: ' + err.message
        }
        console.error('Error processing:', err)
        this.scanning = false
        this.newFilesInfo = null
        this.stopScanPolling()
      }
    },

    hideProgressPanel() {
      this.showProgressPanel = false
    },

    startScanPolling() {
      this.stopScanPolling()
      this.scanPollingTimer = setInterval(() => {
        this.fetchScanStatus()
      }, 1500)
      this.fetchScanStatus()
    },

    stopScanPolling() {
      if (this.scanPollingTimer) {
        clearInterval(this.scanPollingTimer)
        this.scanPollingTimer = null
      }
    },

    async fetchScanStatus() {
      if (!this.scanJobId) {
        return
      }

      try {
        const response = await fetch(`${API_BASE_URL}/api/ocr/scan/status/${this.scanJobId}`)
        const data = await response.json()
        if (!data.success) {
          throw new Error('無法取得 OCR 進度')
        }

        this.scanProgress = data.data

        if (data.data.status === 'completed') {
          this.stopScanPolling()
          this.scanning = false
          this.newFilesInfo = null
          this.scanJobId = null

          const result = data.data.result || {
            total: data.data.total,
            processed: data.data.processed,
            skipped: data.data.skipped,
            failed: data.data.failed
          }

          if ((result.processed || 0) > 0) {
            this.scanResult = {
              type: 'success',
              message: `成功處理 ${result.processed} 個新檔案！`,
              details: result
            }
            await this.fetchDocuments()
          } else {
            this.scanResult = {
              type: 'info',
              message: '掃描完成，沒有新檔案需要處理',
              details: result
            }
          }
          return
        }

        if (data.data.status === 'failed') {
          this.stopScanPolling()
          this.scanning = false
          this.newFilesInfo = null
          this.scanJobId = null
          this.scanResult = {
            type: 'error',
            message: `OCR 任務失敗: ${data.data.error || '未知錯誤'}`
          }
        }
      } catch (err) {
        this.stopScanPolling()
        this.scanning = false
        this.newFilesInfo = null
        this.scanJobId = null
        this.scanResult = {
          type: 'error',
          message: '取得 OCR 進度失敗: ' + err.message
        }
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

/* OCR 處理中提示 */
.ocr-progress-panel {
  position: fixed;
  right: 20px;
  bottom: 20px;
  width: min(420px, calc(100vw - 40px));
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xl);
  padding: var(--spacing-md);
  z-index: 950;
}

.ocr-progress-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-sm);
}

.ocr-progress-title {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  color: var(--color-text-primary);
  font-weight: 600;
}

.ocr-progress-title svg {
  width: 18px;
  height: 18px;
}

.ocr-progress-text {
  color: var(--color-text-secondary);
  font-size: 0.875rem;
  margin: 0 0 var(--spacing-sm) 0;
}

.ocr-progress-track {
  width: 100%;
  height: 8px;
  background: var(--color-bg-tertiary);
  border-radius: 999px;
  overflow: hidden;
}

.ocr-progress-bar {
  height: 100%;
  background: var(--gradient-primary);
  transition: width 0.3s ease;
}

.ocr-progress-meta {
  margin: var(--spacing-sm) 0 0 0;
  color: var(--color-text-muted);
  font-size: 0.8125rem;
}
.ocr-progress-head .close-btn {
  margin-left: 0;
  background: transparent;
  border: none;
  color: var(--color-text-muted);
  font-size: 1.2rem;
  cursor: pointer;
  width: 28px;
  height: 28px;
}

.ocr-progress-head .close-btn:hover {
  color: var(--color-text-primary);
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
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
