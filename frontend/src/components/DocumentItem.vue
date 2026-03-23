<template>
  <div class="document-item fade-in">
    <div class="document-content">
      <div class="document-main">
        <div class="document-icon">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
          </svg>
        </div>

        <div class="document-info">
          <h3 class="document-title">{{ document.filename }}</h3>
          <div class="document-meta">
            <span v-if="document.page_number" class="meta-item page-badge">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" width="14" height="14">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
              第 {{ document.page_number }} 頁
            </span>
            <span class="meta-item">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" width="14" height="14">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              {{ formatDate(document.upload_date) }}
            </span>
          </div>

          <div v-if="document.filepath" class="document-path" :title="document.filepath">
            {{ document.filepath }}
          </div>

          <div v-if="document.snippet" class="document-snippet">
            <p v-html="document.snippet"></p>
          </div>
        </div>
      </div>

      <a
        class="pdf-link"
        :href="getPdfUrl()"
        target="_blank"
        rel="noopener noreferrer"
      >
        顯示 PDF
      </a>
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
    getPdfUrl() {
      const docId = this.document.doc_id ?? this.document.id
      const filename = encodeURIComponent(this.document.filename ?? 'PDF Viewer')
      return `${window.location.origin}/pdf-viewer.html?docId=${docId}&filename=${filename}`
    }
  }
}
</script>

<style scoped>
.document-item {
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
  transition: all var(--transition-normal);
  position: relative;
  overflow: hidden;
}

.document-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 3px;
  height: 100%;
  background: var(--gradient-primary);
  transform: scaleY(0);
  transition: transform var(--transition-normal);
}

.document-item:hover {
  border-color: var(--color-primary);
  transform: translateX(4px);
}

.document-item:hover::before {
  transform: scaleY(1);
}

.document-content {
  display: flex;
  gap: var(--spacing-md);
  align-items: flex-start;
  justify-content: space-between;
}

.document-main {
  display: flex;
  gap: var(--spacing-md);
  align-items: flex-start;
  flex: 1;
  min-width: 0;
}

.document-icon {
  width: 36px;
  height: 36px;
  background: var(--gradient-primary);
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.document-icon svg {
  width: 20px;
  height: 20px;
  color: white;
}

.document-info {
  flex: 1;
  min-width: 0;
}

.document-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-xs);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.document-meta {
  display: flex;
  gap: var(--spacing-md);
  align-items: center;
  flex-wrap: wrap;
  margin-bottom: var(--spacing-sm);
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.8125rem;
  color: var(--color-text-muted);
}

.meta-item svg {
  flex-shrink: 0;
}

.page-badge {
  background: var(--color-bg-tertiary);
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  color: var(--color-primary-light);
  font-weight: 500;
}

.document-path {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  margin-top: var(--spacing-xs);
  word-break: break-all;
}

.document-snippet {
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--color-bg-primary);
  border-radius: var(--radius-sm);
  font-size: 0.8125rem;
  line-height: 1.6;
  color: var(--color-text-secondary);
  margin-top: var(--spacing-sm);
}

.document-snippet :deep(b) {
  color: var(--color-primary-light);
  font-weight: 600;
  background: rgba(99, 102, 241, 0.1);
  padding: 2px 4px;
  border-radius: 2px;
}

.pdf-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 96px;
  padding: 10px 14px;
  border-radius: var(--radius-sm);
  background: var(--gradient-primary);
  color: white;
  text-decoration: none;
  font-weight: 600;
  white-space: nowrap;
  flex-shrink: 0;
}

.pdf-link:hover {
  filter: brightness(1.05);
}

@media (max-width: 768px) {
  .document-content {
    flex-direction: column;
  }

  .pdf-link {
    width: 100%;
  }
}
</style>
