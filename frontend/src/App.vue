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
            <p>共掃描 {{ scanResult.details.total }} 個檔案</p>
            <p>✅ 新增: {{ scanResult.details.processed }} 個</p>
            <p>⏭️ 跳過: {{ scanResult.details.skipped }} 個</p>
            <p v-if="scanResult.details.failed > 0">❌ 失敗: {{ scanResult.details.failed }} 個</p>
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

const API_BASE_URL = 'http://localhost:8000'

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
      scanResult: null
    }
  },
  mounted() {
    this.fetchDocuments()
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
        const response = await fetch(`${API_BASE_URL}/api/ocr/scan`, {
          method: 'POST'
        })
        const data = await response.json()
        
        if (data.success) {
          const result = data.data
          
          if (result.processed > 0) {
            this.scanResult = {
              type: 'success',
              message: `成功處理 ${result.processed} 個新檔案！`,
              details: result
            }
            // 重新載入文件列表
            await this.fetchDocuments()
          } else if (result.total === 0) {
            this.scanResult = {
              type: 'info',
              message: '資料夾中沒有 PDF 檔案',
              details: result
            }
          } else {
            this.scanResult = {
              type: 'info',
              message: '沒有新檔案需要處理',
              details: result
            }
          }
        } else {
          this.scanResult = {
            type: 'error',
            message: '掃描失敗'
          }
        }
      } catch (err) {
        this.scanResult = {
          type: 'error',
          message: '掃描時發生錯誤: ' + err.message
        }
        console.error('Error scanning:', err)
      } finally {
        this.scanning = false
      }
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
