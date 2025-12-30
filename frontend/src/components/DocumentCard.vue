<template>
  <div class="document-card card fade-in">
    <div class="document-header">
      <div class="document-icon">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
        </svg>
      </div>
      <div class="document-info">
        <h3 class="document-title">{{ document.filename }}</h3>
        <p class="document-meta">
          <span v-if="document.page_number" class="page-badge">
            第 {{ document.page_number }} 頁
          </span>
          <span class="upload-date">{{ formatDate(document.upload_date) }}</span>
        </p>
      </div>
    </div>
    
    <div v-if="document.snippet" class="document-snippet">
      <p v-html="document.snippet"></p>
    </div>
    
    <div class="document-footer">
      <button @click="$emit('view', document)" class="btn btn-secondary btn-sm">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" width="16" height="16">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
        </svg>
        查看
      </button>
      <button @click="confirmDelete" class="btn btn-danger btn-sm">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" width="16" height="16">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
        </svg>
        刪除
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DocumentCard',
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
        day: '2-digit'
      })
    },
    confirmDelete() {
      if (confirm(`確定要刪除「${this.document.filename}」嗎？`)) {
        this.$emit('delete', this.document)
      }
    }
  }
}
</script>

<style scoped>
.document-card {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.document-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: var(--gradient-primary);
  transform: scaleY(0);
  transition: transform var(--transition-normal);
}

.document-card:hover::before {
  transform: scaleY(1);
}

.document-header {
  display: flex;
  gap: var(--spacing-md);
  align-items: flex-start;
}

.document-icon {
  width: 40px;
  height: 40px;
  background: var(--gradient-primary);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.document-icon svg {
  width: 24px;
  height: 24px;
  color: white;
}

.document-info {
  flex: 1;
  min-width: 0;
}

.document-title {
  font-size: 1.125rem;
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
  font-size: 0.875rem;
  color: var(--color-text-muted);
}

.page-badge {
  background: var(--color-bg-tertiary);
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--color-primary-light);
}

.document-snippet {
  padding: var(--spacing-md);
  background: var(--color-bg-primary);
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  line-height: 1.6;
  color: var(--color-text-secondary);
}

.document-snippet :deep(b) {
  color: var(--color-primary-light);
  font-weight: 600;
  background: rgba(99, 102, 241, 0.1);
  padding: 2px 4px;
  border-radius: 2px;
}

.document-footer {
  display: flex;
  gap: var(--spacing-sm);
  margin-top: auto;
}

.btn-sm {
  padding: var(--spacing-xs) var(--spacing-md);
  font-size: 0.8125rem;
}

.upload-date {
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>
