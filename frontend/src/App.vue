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
          <div class="header-stats">
            <span class="stat-badge">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" width="16" height="16">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              {{ totalDocuments }} 份文件
            </span>
          </div>
        </div>
      </div>
    </header>

    <!-- 主要內容 -->
    <main class="main">
      <div class="container">
        <!-- 搜尋欄 -->
        <SearchBar @search="handleSearch" @clear="handleClear" />

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
          <div class="documents-grid">
            <DocumentCard
              v-for="doc in searchResults"
              :key="`search-${doc.doc_id}-${doc.page_number}`"
              :document="doc"
              @delete="handleDelete"
            />
          </div>
        </div>

        <!-- 所有文件列表 -->
        <div v-else-if="documents.length > 0">
          <div class="results-header">
            <h2>所有文件</h2>
            <span class="results-count">共 {{ documents.length }} 份文件</span>
          </div>
          <div class="documents-grid">
            <DocumentCard
              v-for="doc in documents"
              :key="`doc-${doc.id}`"
              :document="doc"
              @delete="handleDelete"
            />
          </div>
        </div>

        <!-- 空狀態 -->
        <div v-else class="empty-state">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <h3>尚無文件</h3>
          <p>開始上傳 PDF 文件以使用搜尋功能</p>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import SearchBar from './components/SearchBar.vue'
import DocumentCard from './components/DocumentCard.vue'

const API_BASE_URL = 'http://localhost:8000'

export default {
  name: 'App',
  components: {
    SearchBar,
    DocumentCard
  },
  data() {
    return {
      documents: [],
      searchResults: [],
      loading: false,
      error: null,
      totalDocuments: 0
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
    
    async handleDelete(document) {
      const docId = document.id || document.doc_id
      
      try {
        const response = await fetch(`${API_BASE_URL}/api/documents/${docId}`, {
          method: 'DELETE'
        })
        const data = await response.json()
        
        if (data.success) {
          // 重新載入文件列表
          this.searchResults = []
          await this.fetchDocuments()
          alert('文件已成功刪除')
        } else {
          alert('刪除失敗')
        }
      } catch (err) {
        alert('刪除時發生錯誤')
        console.error('Error deleting document:', err)
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

.header-stats {
  display: flex;
  gap: var(--spacing-md);
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

.documents-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: var(--spacing-lg);
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
  .documents-grid {
    grid-template-columns: 1fr;
  }
  
  .header-content {
    flex-direction: column;
    gap: var(--spacing-md);
  }
  
  .logo h1 {
    font-size: 1.25rem;
  }
}
</style>
