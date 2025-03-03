<template>
    <div class="report-container">
      <h1>实验报告管理</h1>
      
      <div class="controls">
        <button @click="downloadAll" class="download-all-btn">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
            <path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/>
          </svg>
          下载全部报告
        </button>
      </div>
  
      <div v-if="loading" class="loading">加载中...</div>
      
      <div v-else class="report-list">
        <div 
          v-for="report in reports" 
          :key="report.name"
          class="report-item"
        >
          <div class="report-info">
            <h3>{{ report.name }}</h3>
            <p>大小：{{ formatSize(report.size) }}</p>
            <p>生成时间：{{ formatDate(report.created) }}</p>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script lang="ts" setup >
  import { ref } from 'vue'
  import axios from 'axios'
  
  const loading = ref(true)
  const reports = ref([])
  
  // 获取报告数据
  const fetchReports = async () => {
    try {
      loading.value = true
      const response = await axios.get('/api/ChatGPT/report/')
      reports.value = response.data.reports
    } catch (error) {
      console.error('获取报告失败:', error)
    } finally {
      loading.value = false
    }
  }
  
  // 下载全部
  const downloadAll = async () => {
    try {
      const response = await axios.get('/api/ChatGPT/report/download-all/', {
        responseType: 'blob'
      })
      
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `reports_${new Date().getTime()}.zip`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      
    } catch (error) {
      console.error('下载失败:', error)
    }
  }
  
  // 格式化工具
  const formatSize = (bytes) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }
  
  const formatDate = (timestamp) => {
    return new Date(timestamp * 1000).toLocaleString()
  }
  
  // 初始化加载
  fetchReports()
  </script>
  
  <style scoped>
  .report-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
  }
  
  .controls {
    margin: 2rem 0;
    text-align: right;
  }
  
  .download-all-btn {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 1rem 2rem;
    background: var(--vp-c-brand);
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    transition: background 0.3s;
  }
  

  
  .report-list {
    border: 1px solid var(--vp-c-divider);
    border-radius: 8px;
  }
  
  .report-item {
    padding: 1.5rem;
    border-bottom: 1px solid var(--vp-c-divider);
  }
  
  .report-item:last-child {
    border-bottom: none;
  }
  
  .report-info h3 {
    margin: 0 0 0.5rem;
    color: var(--vp-c-text-1);
  }
  
  .report-info p {
    margin: 0;
    color: var(--vp-c-text-2);
    font-size: 0.9rem;
  }
  
  .loading {
    text-align: center;
    padding: 2rem;
    color: var(--vp-c-text-2);
  }
  </style>