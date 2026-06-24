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
        <!-- 功能切換分頁 -->
        <div class="tab-container" style="margin-bottom: 2rem; display: flex; gap: 12px; border-bottom: 1px solid var(--color-border-glass); padding-bottom: 12px;">
          <button 
            @click="currentTab = 'search'" 
            :class="['btn', currentTab === 'search' ? 'btn-primary' : 'btn-secondary']"
            style="padding: 10px 24px; border-radius: var(--radius-md);"
          >
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" width="18" height="18" style="margin-right: 4px;">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            全文檢索
          </button>
          <button 
            @click="currentTab = 'scheduler'" 
            :class="['btn', currentTab === 'scheduler' ? 'btn-primary' : 'btn-secondary']"
            style="padding: 10px 24px; border-radius: var(--radius-md);"
          >
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" width="18" height="18" style="margin-right: 4px;">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            預約掃描排程
          </button>
        </div>

        <div v-show="currentTab === 'search'">
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
              <p class="file-count">找到 <strong>{{ newFilesInfo.new_files_count }}</strong> 個新的文件檔案需要處理</p>
              
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
              <button @click="clearAllSelections" class="btn btn-secondary" style="margin-right: 8px;">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" width="18" height="18">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
                取消選取
              </button>
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

        <!-- 預約排程頁面 -->
        <div v-if="currentTab === 'scheduler'" class="scheduler-view fade-in">
          <div class="scheduler-layout">
            <!-- 左側：新增排程表單 -->
            <div class="scheduler-card glass-panel" style="padding: 1.5rem; border-radius: var(--radius-md);">
              <div class="card-header" style="display: flex; align-items: center; gap: 8px; margin-bottom: 1.5rem; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 0.75rem;">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" width="24" height="24" style="color: var(--color-primary);">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
                <h2 style="font-size: 1.25rem; font-weight: 600; color: var(--color-text-primary); margin: 0;">新增預約掃描任務</h2>
              </div>
              <form @submit.prevent="addSchedule" class="schedule-form" style="display: flex; flex-direction: column; gap: 1.25rem;">
                <!-- 目標資料夾 -->
                <div class="form-group" style="display: flex; flex-direction: column; gap: 8px;">
                  <label style="font-size: 0.9rem; font-weight: 500; color: var(--color-text-secondary);">目標資料夾路徑</label>
                  <div class="input-with-btn" style="display: flex; gap: 8px;">
                    <input 
                      type="text" 
                      v-model="schedulerForm.folderPath" 
                      placeholder="例如: C:\Users\705\Desktop\BigOne\paddle\FUYU\PDFs" 
                      required
                      class="form-control"
                      style="flex: 1; background: rgba(255, 255, 255, 0.03); border: 1px solid var(--color-border-glass); border-radius: var(--radius-sm); padding: 10px 14px; color: var(--color-text-primary); outline: none;"
                    />
                    <button type="button" @click="selectSchedulerFolder" class="btn btn-secondary" style="padding: 8px 16px; font-size: 0.85rem;">
                      選擇資料夾
                    </button>
                  </div>
                </div>

                <!-- 開始時間 -->
                <div class="form-group" style="display: flex; flex-direction: column; gap: 8px;">
                  <label style="font-size: 0.9rem; font-weight: 500; color: var(--color-text-secondary);">預約開始時間</label>
                  <input 
                    type="datetime-local" 
                    v-model="schedulerForm.startTime" 
                    required 
                    class="form-control"
                    style="background: rgba(255, 255, 255, 0.03); border: 1px solid var(--color-border-glass); border-radius: var(--radius-sm); padding: 10px 14px; color: var(--color-text-primary); outline: none;"
                  />
                </div>

                <!-- 結束時間 -->
                <div class="form-group" style="display: flex; flex-direction: column; gap: 8px;">
                  <label style="font-size: 0.9rem; font-weight: 500; color: var(--color-text-secondary);">預約結束時間 (時間到自動停止)</label>
                  <input 
                    type="datetime-local" 
                    v-model="schedulerForm.endTime" 
                    required 
                    class="form-control"
                    style="background: rgba(255, 255, 255, 0.03); border: 1px solid var(--color-border-glass); border-radius: var(--radius-sm); padding: 10px 14px; color: var(--color-text-primary); outline: none;"
                  />
                  <!-- 快捷時間設定 -->
                  <div class="quick-durations" style="display: flex; flex-wrap: wrap; gap: 6px; align-items: center; margin-top: 6px; font-size: 0.8rem; color: var(--color-text-muted);">
                    <span>快速設定執行時長：</span>
                    <button type="button" @click="setSchedulerDuration(30)" class="duration-tag">30分鐘</button>
                    <button type="button" @click="setSchedulerDuration(60)" class="duration-tag">1小時</button>
                    <button type="button" @click="setSchedulerDuration(120)" class="duration-tag">2小時</button>
                    <button type="button" @click="setSchedulerDuration(240)" class="duration-tag">4小時</button>
                  </div>
                </div>

                <button type="submit" class="btn btn-primary" style="width: 100%; margin-top: 1rem;">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" width="18" height="18" style="margin-right: 4px;">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  排定預約掃描
                </button>
              </form>
            </div>

            <!-- 右側：排程清單 -->
            <div class="scheduler-list glass-panel" style="padding: 1.5rem; border-radius: var(--radius-md); overflow: hidden;">
              <div class="card-header" style="display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-bottom: 1.5rem; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 0.75rem;">
                <div style="display: flex; align-items: center; gap: 8px;">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" width="24" height="24" style="color: var(--color-primary);">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                  <h2 style="font-size: 1.25rem; font-weight: 600; color: var(--color-text-primary); margin: 0;">預約掃描排程清單</h2>
                </div>
                <button @click="fetchSchedules" class="btn btn-secondary" style="padding: 6px 12px; font-size: 0.8rem;">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" width="14" height="14" style="margin-right: 4px;">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 1121.21 7.89H18v3z" />
                  </svg>
                  重新整理
                </button>
              </div>

              <!-- 排程清單表格 -->
              <div class="table-container" style="overflow-x: auto; width: 100%;">
                <table v-if="schedules.length > 0" class="schedules-table" style="width: 100%; border-collapse: collapse; text-align: left; font-size: 0.9rem;">
                  <thead>
                    <tr style="border-bottom: 1px solid var(--color-border-glass);">
                      <th style="padding: 12px 10px; color: var(--color-text-muted); font-weight: 500;">目標資料夾</th>
                      <th style="padding: 12px 10px; color: var(--color-text-muted); font-weight: 500;">排程時間</th>
                      <th style="padding: 12px 10px; color: var(--color-text-muted); font-weight: 500;">狀態</th>
                      <th style="padding: 12px 10px; color: var(--color-text-muted); font-weight: 500;">說明/記錄</th>
                      <th style="padding: 12px 10px; color: var(--color-text-muted); font-weight: 500; text-align: right;">操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="sched in schedules" :key="sched.id" :class="sched.status" style="border-bottom: 1px solid var(--color-border-glass);">
                      <td class="folder-path" :title="sched.folder_path" style="padding: 14px 10px; max-width: 180px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                        {{ sched.folder_path }}
                      </td>
                      <td class="time-col" style="padding: 14px 10px; font-family: monospace; font-size: 0.8rem; line-height: 1.4;">
                        <div>始：{{ formatDateTimeDisplay(sched.start_time) }}</div>
                        <div>止：{{ formatDateTimeDisplay(sched.end_time) }}</div>
                      </td>
                      <td style="padding: 14px 10px;">
                        <span :class="['status-badge', sched.status]">
                          <span v-if="sched.status === 'scanning'" class="scanning-dot"></span>
                          {{ getStatusLabel(sched.status) }}
                        </span>
                      </td>
                      <td class="msg-col" :title="sched.message" style="padding: 14px 10px; font-size: 0.8rem; color: var(--color-text-secondary); max-width: 150px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                        {{ sched.message || '無' }}
                      </td>
                      <td class="action-col" style="padding: 14px 10px; text-align: right;">
                        <button 
                          v-if="sched.status === 'pending' || sched.status === 'scanning'"
                          @click="stopSchedule(sched.id)" 
                          class="btn btn-secondary stop-btn"
                          style="padding: 4px 10px; font-size: 0.75rem;"
                        >
                          {{ sched.status === 'scanning' ? '中止' : '取消' }}
                        </button>
                        <button 
                          v-else
                          @click="deleteSchedule(sched.id)" 
                          class="btn btn-secondary delete-btn"
                          style="padding: 4px 10px; font-size: 0.75rem;"
                        >
                          刪除
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
                <div v-else class="empty-schedules" style="display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 4rem 0; color: var(--color-text-muted); gap: 12px;">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" width="48" height="48">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <p>目前尚無預約排程任務</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- 底部懸浮選取工具列 (當有勾選任何文件時顯示，無視當前搜尋結果是否為空) -->
    <div v-if="selectedDocs.length > 0" class="selection-floating-bar">
      <div class="container selection-bar-content">
        <div class="selection-info">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" width="20" height="20">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          <span>已選取 <strong>{{ selectedDocs.length }}</strong> 份文件</span>
        </div>
        <div class="selection-actions">
          <button @click="clearAllSelections" class="btn btn-secondary">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" width="18" height="18">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
            取消所有選取
          </button>
          <button @click="printSelected" class="btn btn-primary btn-print" :disabled="isPrinting">
            <svg v-if="!isPrinting" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" width="18" height="18">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
            </svg>
            <svg v-else class="loading" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" width="18" height="18">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ isPrinting ? '處理列印中...' : '合併列印已選取' }}
          </button>
        </div>
      </div>
    </div>
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
      isPrinting: false,
      
      // 預約排程相關欄位
      currentTab: 'search',
      schedulerForm: {
        folderPath: '',
        startTime: '',
        endTime: ''
      },
      schedules: [],
      schedulesLoading: false,
      schedulesRefreshIntervalId: null
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
    
    // 預約排程初始化
    this.fetchSchedules()
    this.schedulesRefreshIntervalId = setInterval(this.fetchSchedules, 4000)
  },
  unmounted() {
    if (this.scanProgressId) clearInterval(this.scanProgressId)
    if (this.schedulesRefreshIntervalId) clearInterval(this.schedulesRefreshIntervalId)
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
    },
    
    clearAllSelections() {
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
              message: info.total_files === 0 ? '資料夾中沒有支援的文件檔案' : '沒有新檔案需要處理',
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
    },

    // 預約排程方法
    async fetchSchedules() {
      try {
        const response = await fetch(`${API_BASE_URL}/api/scheduler/schedules`)
        const data = await response.json()
        if (data.success) {
          this.schedules = data.data
        }
      } catch (err) {
        console.error('Error fetching schedules:', err)
      }
    },
    
    async selectSchedulerFolder() {
      try {
        const pickerResponse = await fetch(`${API_BASE_URL}/api/ocr/select_folder`);
        const pickerData = await pickerResponse.json();
        if (pickerData.success && pickerData.folder_path) {
          this.schedulerForm.folderPath = pickerData.folder_path;
        }
      } catch (err) {
        alert('無法開啟資料夾選擇器: ' + err.message);
      }
    },
    
    setSchedulerDuration(minutes) {
      const now = new Date();
      let baseDate = now;
      if (this.schedulerForm.startTime) {
        baseDate = new Date(this.schedulerForm.startTime);
      } else {
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        const hours = String(now.getHours()).padStart(2, '0');
        const mins = String(now.getMinutes()).padStart(2, '0');
        this.schedulerForm.startTime = `${year}-${month}-${day}T${hours}:${mins}`;
      }
      
      const endDate = new Date(baseDate.getTime() + minutes * 60 * 1000);
      const year = endDate.getFullYear();
      const month = String(endDate.getMonth() + 1).padStart(2, '0');
      const day = String(endDate.getDate()).padStart(2, '0');
      const hours = String(endDate.getHours()).padStart(2, '0');
      const mins = String(endDate.getMinutes()).padStart(2, '0');
      this.schedulerForm.endTime = `${year}-${month}-${day}T${hours}:${mins}`;
    },
    
    async addSchedule() {
      if (!this.schedulerForm.folderPath) {
        alert('請填寫或選擇目標資料夾');
        return;
      }
      if (!this.schedulerForm.startTime) {
        alert('請選擇預約開始時間');
        return;
      }
      if (!this.schedulerForm.endTime) {
        alert('請選擇預約結束時間');
        return;
      }
      
      const start = new Date(this.schedulerForm.startTime);
      const end = new Date(this.schedulerForm.endTime);
      
      if (end <= start) {
        alert('結束時間必須晚於開始時間');
        return;
      }
      
      try {
        const formatDateTime = (dtStr) => dtStr.replace('T', ' ') + ':00';
        
        const response = await fetch(`${API_BASE_URL}/api/scheduler/schedule`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            folder_path: this.schedulerForm.folderPath,
            start_time: formatDateTime(this.schedulerForm.startTime),
            end_time: formatDateTime(this.schedulerForm.endTime)
          })
        });
        
        const data = await response.json();
        if (data.success) {
          this.schedulerForm.folderPath = '';
          this.schedulerForm.startTime = '';
          this.schedulerForm.endTime = '';
          await this.fetchSchedules();
          alert('預約掃描已成功排定！');
        } else {
          alert('排定失敗: ' + (data.detail || '未知錯誤'));
        }
      } catch (err) {
        alert('送出預約時發生錯誤: ' + err.message);
      }
    },
    
    async stopSchedule(id) {
      if (!confirm('確認要終止或取消此預約任務？')) return;
      try {
        const response = await fetch(`${API_BASE_URL}/api/scheduler/${id}/stop`, {
          method: 'POST'
        });
        const data = await response.json();
        if (data.success) {
          await this.fetchSchedules();
        } else {
          alert(data.message || '操作失敗');
        }
      } catch (err) {
        alert('停止排程時發生錯誤: ' + err.message);
      }
    },
    
    async deleteSchedule(id) {
      if (!confirm('確認要刪除此預約記錄？')) return;
      try {
        const response = await fetch(`${API_BASE_URL}/api/scheduler/${id}`, {
          method: 'DELETE'
        });
        const data = await response.json();
        if (data.success) {
          await this.fetchSchedules();
        } else {
          alert(data.detail || '刪除失敗');
        }
      } catch (err) {
        alert('刪除排程時發生錯誤: ' + err.message);
      }
    },
    
    formatDateTimeDisplay(dateStr) {
      if (!dateStr) return '';
      return dateStr.replace('T', ' ').substring(0, 16);
    },

    getStatusLabel(status) {
      const labels = {
        'pending': '排程中',
        'scanning': '掃描中',
        'completed': '已完成',
        'stopped': '已停止',
        'failed': '失敗'
      };
      return labels[status] || status;
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

/* 底部懸浮選取工具列 */
.selection-floating-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(15, 23, 42, 0.85);
  backdrop-filter: blur(12px);
  border-top: 1px solid var(--color-border-glass);
  box-shadow: 0 -10px 40px -10px rgba(0, 0, 0, 0.7), 0 0 20px -5px rgba(0, 242, 254, 0.1);
  padding: var(--spacing-md) 0;
  z-index: 99;
  animation: slideUpFloating 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes slideUpFloating {
  from { transform: translateY(100%); }
  to { transform: translateY(0); }
}

.selection-bar-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--spacing-md);
}

.selection-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  color: var(--color-text-secondary);
  font-size: 0.95rem;
}

.selection-info svg {
  color: var(--color-primary);
}

.selection-info strong {
  color: var(--color-primary);
  font-size: 1.2rem;
  margin: 0 4px;
}

.selection-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.selection-actions .btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
}

/* 補償主區域底部邊距，防止內容被懸浮列遮擋 */
.main {
  padding-bottom: 120px !important;
}

/* ===== 預約排程樣式 (Cyber-Glassmorphism Scheduler) ===== */
.scheduler-layout {
  display: grid;
  grid-template-columns: 1.2fr 1.8fr;
  gap: 2rem;
  align-items: start;
  margin-top: 1rem;
}

@media (max-width: 1024px) {
  .scheduler-layout {
    grid-template-columns: 1fr;
  }
}

.duration-tag {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--color-border-glass);
  padding: 4px 10px;
  border-radius: var(--radius-sm);
  color: var(--color-text-secondary);
  cursor: pointer;
  font-size: 0.8rem;
  transition: all var(--transition-fast);
}

.duration-tag:hover {
  background: rgba(0, 242, 254, 0.15);
  border-color: var(--color-primary);
  color: var(--color-primary);
  transform: translateY(-1px);
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: var(--radius-full);
  font-size: 0.75rem;
  font-weight: 600;
}

.status-badge.pending {
  background: rgba(0, 242, 254, 0.1);
  color: var(--color-primary);
  border: 1px solid rgba(0, 242, 254, 0.2);
}

.status-badge.scanning {
  background: rgba(192, 132, 252, 0.1);
  color: var(--color-accent);
  border: 1px solid rgba(192, 132, 252, 0.2);
  animation: glow-pulse 2s infinite;
}

.status-badge.completed {
  background: rgba(52, 211, 153, 0.1);
  color: var(--color-success);
  border: 1px solid rgba(52, 211, 153, 0.2);
}

.status-badge.stopped {
  background: rgba(251, 191, 36, 0.1);
  color: var(--color-warning);
  border: 1px solid rgba(251, 191, 36, 0.2);
}

.status-badge.failed {
  background: rgba(248, 113, 113, 0.1);
  color: var(--color-danger);
  border: 1px solid rgba(248, 113, 113, 0.2);
}

.scanning-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--color-accent);
  display: inline-block;
  animation: spin 1.5s linear infinite;
  box-shadow: 0 0 6px var(--color-accent);
}

.schedules-table tr.scanning {
  background: rgba(192, 132, 252, 0.03);
}

.stop-btn {
  background: rgba(248, 113, 113, 0.15) !important;
  color: #f87171 !important;
  border: 1px solid rgba(248, 113, 113, 0.25) !important;
}

.stop-btn:hover {
  background: #f87171 !important;
  color: #000 !important;
  border-color: #f87171 !important;
  box-shadow: 0 0 10px rgba(248, 113, 113, 0.3);
}

.delete-btn {
  color: var(--color-text-muted) !important;
}

.delete-btn:hover {
  background: rgba(248, 113, 113, 0.15) !important;
  color: #f87171 !important;
  border-color: rgba(248, 113, 113, 0.25) !important;
}
</style>
