<template>
  <div class="document-item glass-panel fade-in" :class="{ 'is-selected': selected }" @click="$emit('toggle-select')">
    
    <!-- 發光邊框特效 (hover 時展開) -->
    <div class="glow-border"></div>

    <div class="document-content">
      <!-- 選擇框區域 -->
      <div v-if="selected !== undefined" class="document-checkbox" @click.stop="$emit('toggle-select')">
        <div class="custom-checkbox" :class="{ 'checked': selected }">
          <svg v-if="selected" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
          </svg>
        </div>
      </div>

      <!-- 文件圖示 (霓虹感) -->
      <div class="document-icon">
        <div class="icon-glow"></div>
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      </div>

      <!-- 資訊區域 -->
      <div class="document-info">
        <h3 class="document-title" :title="document.filename">{{ document.filename }}</h3>
        
        <div class="document-meta">
          <!-- 多頁模式 -->
          <span v-if="isGrouped" class="meta-item glass-pill badge-primary">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" width="14" height="14">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 002-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            {{ document.pages.length }} 頁命中
          </span>
          <!-- 單頁模式 -->
          <span v-else-if="document.page_number" class="meta-item glass-pill badge-primary">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" width="14" height="14">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
            </svg>
            第 {{ document.page_number }} 頁
          </span>
          
          <!-- 文件日期 -->
          <span v-if="document.doc_date" class="meta-item glass-pill">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" width="14" height="14">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            {{ document.doc_date }}
          </span>
          
          <!-- 上傳日期 -->
          <span class="meta-item glass-pill">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" width="14" height="14">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {{ formatDate(document.upload_date) }}
          </span>
        </div>

        <!-- 內容片段 Snippets -->
        <div class="snippets-container">
          <!-- 多頁模式：每頁一個 snippet 區塊 -->
          <template v-if="isGrouped">
            <div v-for="page in document.pages" :key="page.page_number" class="snippet-box">
              <div class="page-indicator">
                <span>P.{{ page.page_number }}</span>
              </div>
              <p class="snippet-text" v-html="page.snippet"></p>
            </div>
          </template>

          <!-- 單頁模式 -->
          <template v-else-if="document.snippet">
            <div class="snippet-box">
              <p class="snippet-text" v-html="document.snippet"></p>
            </div>
          </template>
        </div>
      </div>

      <!-- 操作按鈕 -->
      <div class="document-actions">
        <button class="btn-view-pdf" @click.stop="openPdf" :title="isOfficeDoc ? '下載文件' : '在新視窗開啟 PDF'">
          <span class="btn-blur-bg"></span>
          <svg v-if="isOfficeDoc" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" width="18" height="18">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" width="18" height="18">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
          <span class="btn-text">{{ isOfficeDoc ? '下載' : '檢視' }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
const API_BASE_URL = window.location.hostname === 'localhost'
  ? 'http://localhost:8000'
  : `http://${window.location.hostname}:8000`

export default {
  name: 'DocumentItem',
  props: {
    document: {
      type: Object,
      required: true
    },
    selected: {
      type: Boolean,
      default: undefined
    }
  },
  computed: {
    isGrouped() {
      return Array.isArray(this.document.pages)
    },
    isOfficeDoc() {
      const filename = this.document.filename || ''
      const ext = filename.split('.').pop().toLowerCase()
      return ext === 'docx' || ext === 'xlsx'
    }
  },
  methods: {
    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-TW', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    openPdf() {
      const docId = this.document.doc_id || this.document.id
      if (!docId) return
      // 加上時間戳記強制解快取，解決 Edge 瀏覽器讀取錯誤快取檔案的問題
      const url = `${API_BASE_URL}/api/documents/${docId}/pdf?t=${Date.now()}`
      
      if (this.isOfficeDoc) {
        // Office 檔案直接觸發下載
        window.open(url, '_blank')
        return
      }
      
      const filename = this.document.filename || 'PDF 文件'
      const win = window.open('', '_blank')
      win.document.write(`<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>${filename}</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    html, body { width: 100%; height: 100%; background: #111827; overflow: hidden; }
    embed { display: block; width: 100%; height: 100%; border: none; }
    .loader { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: #00f2fe; font-family: sans-serif; }
  </style>
</head>
<body>
  <div class="loader">Loading PDF...</div>
  <embed src="${url}" type="application/pdf" width="100%" height="100%" style="position: relative; z-index: 2;" onload="document.querySelector('.loader').style.display='none'" />
</body>
</html>`)
      win.document.close()
    }
  }
}
</script>

<style scoped>
.document-item {
  position: relative;
  padding: var(--spacing-lg);
  border-radius: var(--radius-lg);
  margin-bottom: var(--spacing-md);
  cursor: pointer;
  transition: all var(--transition-smooth);
  overflow: hidden;
}

/* 核心特效：光暈邊框 */
.glow-border {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: inherit;
  border: 1px solid transparent;
  background: var(--gradient-neon) border-box;
  -webkit-mask: linear-gradient(#fff 0 0) padding-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: destination-out;
  mask-composite: exclude;
  opacity: 0;
  transition: opacity var(--transition-smooth);
  pointer-events: none;
}

.document-item:hover, .document-item.is-selected {
  transform: translateY(-3px) scale(1.005);
  background: rgba(31, 41, 55, 0.85); /* 稍微變亮 */
  box-shadow: 0 10px 40px -10px rgba(0, 0, 0, 0.5), 0 0 20px -5px rgba(0, 242, 254, 0.15);
}

.document-item:hover .glow-border, .document-item.is-selected .glow-border {
  opacity: 1;
}

.document-content {
  display: flex;
  gap: var(--spacing-md);
  align-items: flex-start;
  position: relative;
  z-index: 1;
}

/* 客製化 Checkbox */
.document-checkbox {
  display: flex;
  align-items: center;
  justify-content: center;
  padding-top: 10px;
}

.custom-checkbox {
  width: 22px;
  height: 22px;
  border-radius: 6px;
  border: 2px solid var(--color-border-glass);
  background: rgba(0,0,0,0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  color: #000;
}

.custom-checkbox.checked {
  background: var(--gradient-neon);
  border-color: transparent;
  box-shadow: 0 0 10px rgba(0, 242, 254, 0.4);
}

.custom-checkbox svg {
  width: 16px;
  height: 16px;
}

/* 霓虹文件圖示 */
.document-icon {
  position: relative;
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  background: linear-gradient(135deg, rgba(0, 242, 254, 0.1) 0%, rgba(79, 172, 254, 0.05) 100%);
  border: 1px solid rgba(0, 242, 254, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.icon-glow {
  position: absolute;
  width: 100%;
  height: 100%;
  background: var(--gradient-neon);
  filter: blur(15px);
  opacity: 0.15;
  border-radius: inherit;
  transition: opacity var(--transition-smooth);
}

.document-item:hover .icon-glow {
  opacity: 0.3;
}

.document-icon svg {
  width: 24px;
  height: 24px;
  color: var(--color-primary);
  z-index: 1;
}

/* 內容區塊 */
.document-info {
  flex: 1;
  min-width: 0;
}

.document-title {
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  letter-spacing: 0.02em;
}

.document-meta {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.8rem;
  color: var(--color-text-secondary);
  padding: 4px 10px;
}

.badge-primary {
  background: rgba(0, 242, 254, 0.1);
  border-color: rgba(0, 242, 254, 0.2);
  color: var(--color-primary);
  font-weight: 600;
}

/* Snippets 高光片段 */
.snippets-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.snippet-box {
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.03);
  border-radius: var(--radius-sm);
  padding: 12px 16px;
  position: relative;
  overflow: hidden;
}

.snippet-box::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: var(--gradient-neon);
  opacity: 0.5;
}

.page-indicator {
  display: inline-block;
  font-size: 0.7rem;
  font-weight: 700;
  color: var(--color-accent);
  background: rgba(192, 132, 252, 0.15);
  padding: 2px 8px;
  border-radius: 4px;
  margin-bottom: 6px;
  letter-spacing: 0.05em;
}

.snippet-text {
  font-size: 0.85rem;
  line-height: 1.6;
  color: var(--color-text-secondary);
}

.snippet-text :deep(b) {
  color: var(--color-primary);
  font-weight: 600;
  background: rgba(0, 242, 254, 0.15);
  padding: 0 4px;
  border-radius: 3px;
  box-shadow: 0 0 5px rgba(0, 242, 254, 0.2);
}

/* 檢視按鈕 */
.document-actions {
  display: flex;
  align-items: flex-start;
  flex-shrink: 0;
  padding-top: 6px;
}

.btn-view-pdf {
  position: relative;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-full);
  color: var(--color-text-primary);
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  overflow: hidden;
  transition: all var(--transition-smooth);
}

.btn-blur-bg {
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(4px);
  z-index: -1;
  transition: opacity 0.3s;
}

.btn-view-pdf:hover {
  border-color: rgba(0, 242, 254, 0.5);
  color: var(--color-primary);
  box-shadow: 0 0 15px rgba(0, 242, 254, 0.2);
  transform: translateY(-1px);
}

.btn-view-pdf:hover .btn-blur-bg {
  background: rgba(0, 242, 254, 0.1);
}

@media (max-width: 640px) {
  .document-content {
    flex-direction: column;
  }
  .document-actions {
    width: 100%;
    margin-top: 10px;
  }
  .btn-view-pdf {
    width: 100%;
    justify-content: center;
  }
}
</style>
