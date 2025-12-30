<template>
  <div class="search-bar">
    <div class="search-input-wrapper">
      <svg class="search-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
      <input
        type="text"
        v-model="searchQuery"
        @input="onSearch"
        placeholder="搜尋文件內容..."
        class="search-input"
      />
      <span v-if="isSearching" class="loading-spinner">
        <svg class="loading" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      </span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SearchBar',
  data() {
    return {
      searchQuery: '',
      isSearching: false,
      searchTimeout: null
    }
  },
  methods: {
    onSearch() {
      // 清除之前的計時器
      if (this.searchTimeout) {
        clearTimeout(this.searchTimeout)
      }
      
      // 延遲搜尋（防抖）
      this.searchTimeout = setTimeout(() => {
        if (this.searchQuery.trim()) {
          this.$emit('search', this.searchQuery.trim())
        } else {
          this.$emit('clear')
        }
      }, 300)
    }
  }
}
</script>

<style scoped>
.search-bar {
  width: 100%;
  margin-bottom: var(--spacing-xl);
}

.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: var(--spacing-md);
  width: 20px;
  height: 20px;
  color: var(--color-text-muted);
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: var(--spacing-md) var(--spacing-md) var(--spacing-md) 3rem;
  background: var(--color-bg-secondary);
  border: 2px solid var(--color-border);
  border-radius: var(--radius-xl);
  color: var(--color-text-primary);
  font-size: 1.125rem;
  transition: all var(--transition-normal);
}

.search-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1);
  background: var(--color-bg-primary);
}

.search-input::placeholder {
  color: var(--color-text-muted);
}

.loading-spinner {
  position: absolute;
  right: var(--spacing-md);
  width: 20px;
  height: 20px;
  color: var(--color-primary);
}

.loading-spinner svg {
  width: 100%;
  height: 100%;
}

.opacity-25 {
  opacity: 0.25;
}

.opacity-75 {
  opacity: 0.75;
}
</style>
