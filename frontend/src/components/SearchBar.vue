<template>
  <div class="search-bar-container">
    <div class="search-bar glass-panel">
      
      <!-- 主搜尋框區域 -->
      <div class="search-input-wrapper">
        <div class="search-icon-wrapper">
          <svg class="search-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        
        <input
          type="text"
          v-model="searchQuery"
          @input="onSearch"
          placeholder="輸入關鍵字以搜尋文件內容..."
          class="search-input"
        />
        
        <div v-if="isSearching" class="loading-spinner">
          <svg class="loading" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </div>
      </div>

      <!-- 分隔線 -->
      <div class="divider"></div>

      <!-- 日期過濾器區域 -->
      <div class="date-filters">
        <div class="date-input-group">
          <label>起始</label>
          <div class="date-picker-wrapper glass-pill">
            <input type="date" v-model="startDate" @change="onSearch" class="date-input" />
          </div>
        </div>
        
        <div class="date-input-group">
          <label>結束</label>
          <div class="date-picker-wrapper glass-pill">
            <input type="date" v-model="endDate" @change="onSearch" class="date-input" />
          </div>
        </div>
      </div>
      
    </div>
  </div>
</template>

<script>
export default {
  name: 'SearchBar',
  data() {
    return {
      searchQuery: '',
      startDate: '',
      endDate: '',
      isSearching: false,
      searchTimeout: null
    }
  },
  methods: {
    onSearch() {
      if (this.searchTimeout) {
        clearTimeout(this.searchTimeout)
      }
      
      this.isSearching = true;
      
      this.searchTimeout = setTimeout(() => {
        if (this.searchQuery.trim()) {
          this.$emit('search', {
            keyword: this.searchQuery.trim(),
            startDate: this.startDate || undefined,
            endDate: this.endDate || undefined
          })
        } else {
          this.$emit('clear')
        }
        
        // 模擬短暫加載動畫感，讓 UX 更好
        setTimeout(() => {
          this.isSearching = false;
        }, 400);
      }, 400)
    }
  }
}
</script>

<style scoped>
.search-bar-container {
  width: 100%;
  margin-bottom: var(--spacing-2xl);
  display: flex;
  justify-content: center;
  position: relative;
  z-index: 10;
}

/* 核心毛玻璃容器縮放與樣式 */
.search-bar {
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 900px;
  border-radius: var(--radius-lg);
  padding: 8px;
  transition: all var(--transition-smooth);
}

.search-bar:focus-within {
  border-color: var(--color-primary-light);
  box-shadow: 0 15px 40px rgba(0, 242, 254, 0.15), 0 0 0 1px rgba(0, 242, 254, 0.2);
  transform: translateY(-2px);
}

/* 搜尋框輸入區 */
.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
}

.search-icon-wrapper {
  position: absolute;
  left: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-smooth);
}

.search-icon {
  width: 24px;
  height: 24px;
  color: var(--color-text-muted);
}

.search-bar:focus-within .search-icon {
  color: var(--color-primary);
  filter: drop-shadow(0 0 5px rgba(0, 242, 254, 0.5));
}

.search-input {
  width: 100%;
  padding: 20px 24px 20px 56px;
  background: transparent;
  border: none;
  color: var(--color-text-primary);
  font-size: 1.25rem;
  font-weight: 500;
  outline: none;
}

.search-input::placeholder {
  color: rgba(203, 213, 225, 0.4);
  font-weight: 400;
}

.loading-spinner {
  position: absolute;
  right: 20px;
  width: 24px;
  height: 24px;
  color: var(--color-primary);
}

.loading-spinner svg {
  width: 100%;
  height: 100%;
}

.opacity-25 { opacity: 0.25; }
.opacity-75 { opacity: 0.75; }

/* 分隔線 */
.divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--color-border-glass), transparent);
  margin: 4px 16px;
  opacity: 0.5;
}

/* 日期過濾器區域 */
.date-filters {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: var(--spacing-lg);
  padding: 12px 16px;
}

.date-input-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.date-input-group label {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.date-picker-wrapper {
  padding: 6px 14px;
  display: flex;
  align-items: center;
  transition: all var(--transition-short);
}

.date-picker-wrapper:focus-within {
  border-color: var(--color-primary-light);
  box-shadow: inset 0 0 0 1px rgba(0, 242, 254, 0.2), 0 0 10px rgba(0, 242, 254, 0.1);
}

.date-input {
  background: transparent;
  border: none;
  color: var(--color-text-secondary);
  font-family: inherit;
  font-size: 0.9rem;
  outline: none;
  cursor: pointer;
  color-scheme: dark;
}

.date-input::-webkit-calendar-picker-indicator {
  cursor: pointer;
  opacity: 0.6;
  transition: opacity 0.2s;
  padding-left: 8px;
}

.date-input::-webkit-calendar-picker-indicator:hover {
  opacity: 1;
}

/* 響應式 */
@media (max-width: 768px) {
  .search-input {
    font-size: 1.1rem;
    padding: 16px 16px 16px 48px;
  }
  
  .date-filters {
    flex-wrap: wrap;
    justify-content: flex-start;
  }
  
  .date-input-group {
    width: 100%;
    justify-content: space-between;
  }
}
</style>
