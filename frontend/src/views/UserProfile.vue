<template>
  <div class="profile-page">
    <div class="profile-container">
      <div class="profile-sidebar">
        <div class="user-card">
          <div class="avatar-wrapper">
            <div class="avatar">{{ user.nickname?.charAt(0) || user.username?.charAt(0) || 'U' }}</div>
          </div>
          <h3 class="user-name">{{ user.nickname || user.username }}</h3>
          <p class="user-email">{{ user.username }}</p>
        </div>

        <nav class="sidebar-nav">
          <button 
            v-for="item in navItems" 
            :key="item.id"
            @click="activeTab = item.id"
            class="nav-item"
            :class="{ active: activeTab === item.id }"
          >
            <span class="nav-icon">{{ item.icon }}</span>
            <span class="nav-text">{{ item.label }}</span>
          </button>
        </nav>
      </div>

      <div class="profile-content">
        <div v-if="activeTab === 'history'" class="tab-content">
          <div class="tab-header">
            <h2 class="tab-title">📜 历史分析记录</h2>
            <button @click="loadHistory" class="btn btn-outline">刷新</button>
          </div>

          <div v-if="historyLoading" class="loading-state">
            <div class="spinner"></div>
            <span>加载中...</span>
          </div>

          <div v-else-if="historyRecords.length === 0" class="empty-state">
            <div class="empty-state-icon">📝</div>
            <div class="empty-state-title">暂无历史记录</div>
            <div class="empty-state-description">完成代码分析后，记录会自动保存到这里</div>
          </div>

          <div v-else class="records-list">
            <div 
              v-for="record in historyRecords" 
              :key="record.id" 
              class="record-card"
            >
              <div class="record-header">
                <span class="record-language" :class="record.language">
                  {{ record.language === 'python' ? '🐍' : '⚙️' }}
                </span>
                <span class="record-date">{{ formatDate(record.created_at) }}</span>
              </div>
              <div class="record-code">{{ record.code_content.substring(0, 100) }}{{ record.code_content.length > 100 ? '...' : '' }}</div>
              <div class="record-actions">
                <button @click="viewRecord(record)" class="btn btn-sm btn-primary">查看</button>
                <button @click="deleteRecord(record.id)" class="btn btn-sm btn-danger">删除</button>
              </div>
            </div>
          </div>
        </div>

        <div v-if="activeTab === 'files'" class="tab-content">
          <div class="tab-header">
            <h2 class="tab-title">📁 已上传文件</h2>
            <button @click="uploadFile" class="btn btn-primary">上传文件</button>
          </div>

          <div v-if="filesLoading" class="loading-state">
            <div class="spinner"></div>
            <span>加载中...</span>
          </div>

          <div v-else-if="files.length === 0" class="empty-state">
            <div class="empty-state-icon">📂</div>
            <div class="empty-state-title">暂无上传文件</div>
            <div class="empty-state-description">上传代码文件进行分析</div>
          </div>

          <div v-else class="files-grid">
            <div 
              v-for="file in files" 
              :key="file.id" 
              class="file-card"
            >
              <div class="file-icon">{{ getFileIcon(file.filename) }}</div>
              <div class="file-info">
                <div class="file-name">{{ file.filename }}</div>
                <div class="file-size">{{ formatSize(file.size) }}</div>
                <div class="file-date">{{ formatDate(file.created_at) }}</div>
              </div>
              <div class="file-actions">
                <button @click="viewFile(file)" class="btn btn-sm btn-primary">分析</button>
                <button @click="deleteFile(file.id)" class="btn btn-sm btn-danger">删除</button>
              </div>
            </div>
          </div>

          <input 
            ref="fileInput" 
            type="file" 
            accept=".py,.c,.cpp" 
            class="hidden"
            @change="handleFileUpload"
          />
        </div>

        <div v-if="activeTab === 'settings'" class="tab-content">
          <div class="tab-header">
            <h2 class="tab-title">⚙️ 个人设置</h2>
          </div>

          <div class="settings-form">
            <div class="form-group">
              <label class="form-label">昵称</label>
              <input 
                v-model="settings.nickname" 
                type="text" 
                class="form-control"
                placeholder="请输入昵称"
              />
            </div>

            <div class="form-group">
              <label class="form-label">用户名</label>
              <input 
                v-model="settings.username" 
                type="text" 
                class="form-control"
                disabled
                placeholder="当前用户名"
              />
            </div>

            <div class="form-group">
              <label class="form-label">新密码</label>
              <input 
                v-model="settings.password" 
                type="password" 
                class="form-control"
                placeholder="请输入新密码（不填则不修改）"
              />
            </div>

            <div class="form-group">
              <label class="form-label">确认密码</label>
              <input 
                v-model="settings.confirmPassword" 
                type="password" 
                class="form-control"
                placeholder="请确认新密码"
              />
            </div>

            <div class="form-actions">
              <button @click="saveSettings" class="btn btn-primary">保存设置</button>
              <button @click="resetSettings" class="btn btn-outline">重置</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { userApi, recordApi, fileApi } from '../api'
import { useAuthStore } from '../store'
import { ElMessage } from 'element-plus'

const authStore = useAuthStore()
const activeTab = ref('history')
const user = ref({})
const historyRecords = ref([])
const historyLoading = ref(false)
const files = ref([])
const filesLoading = ref(false)
const fileInput = ref(null)

const settings = reactive({
  username: '',
  nickname: '',
  password: '',
  confirmPassword: ''
})

const navItems = [
  { id: 'history', label: '历史记录', icon: '📜' },
  { id: 'files', label: '文件管理', icon: '📁' },
  { id: 'settings', label: '个人设置', icon: '⚙️' }
]

const loadUser = async () => {
  try {
    const res = await userApi.getProfile()
    user.value = res.data
    settings.username = res.data.username || ''
    settings.nickname = res.data.nickname || ''
  } catch (error) {
    console.error('获取用户信息失败', error)
  }
}

const loadHistory = async () => {
  historyLoading.value = true
  try {
    const res = await recordApi.getAll()
    historyRecords.value = res.data
  } catch (error) {
    ElMessage.error('加载历史记录失败')
  } finally {
    historyLoading.value = false
  }
}

const loadFiles = async () => {
  filesLoading.value = true
  try {
    const res = await fileApi.getAll()
    files.value = res.data
  } catch (error) {
    ElMessage.error('加载文件失败')
  } finally {
    filesLoading.value = false
  }
}

const viewRecord = (record) => {
  const path = record.language === 'python' ? '/python-analysis' : '/c-analysis'
  window.location.href = `${path}?code=${encodeURIComponent(record.code_content)}`
}

const deleteRecord = async (id) => {
  if (!confirm('确定要删除这条记录吗？')) return
  try {
    await recordApi.delete(id)
    historyRecords.value = historyRecords.value.filter(r => r.id !== id)
    ElMessage.success('删除成功')
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

const uploadFile = () => {
  fileInput.value?.click()
}

const handleFileUpload = async (event) => {
  const file = event.target.files?.[0]
  if (!file) return

  const formData = new FormData()
  formData.append('file', file)

  try {
    await fileApi.upload(formData)
    ElMessage.success('上传成功')
    loadFiles()
    event.target.value = ''
  } catch (error) {
    ElMessage.error('上传失败')
  }
}

const viewFile = (file) => {
  const lang = file.filename.endsWith('.py') ? 'python' : 'c'
  const path = lang === 'python' ? '/python-analysis' : '/c-analysis'
  window.location.href = `${path}?file=${file.id}`
}

const deleteFile = async (id) => {
  if (!confirm('确定要删除这个文件吗？')) return
  try {
    await fileApi.delete(id)
    files.value = files.value.filter(f => f.id !== id)
    ElMessage.success('删除成功')
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

const saveSettings = async () => {
  if (settings.password && settings.password !== settings.confirmPassword) {
    ElMessage.error('两次输入的密码不一致')
    return
  }

  try {
    await userApi.updateProfile({
      nickname: settings.nickname,
      password: settings.password || undefined
    })
    ElMessage.success('保存成功')
    loadUser()
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const resetSettings = () => {
  settings.username = user.value.username || ''
  settings.nickname = user.value.nickname || ''
  settings.password = ''
  settings.confirmPassword = ''
}

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

const formatSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

const getFileIcon = (filename) => {
  if (filename.endsWith('.py')) return '🐍'
  if (filename.endsWith('.c') || filename.endsWith('.cpp')) return '⚙️'
  return '📄'
}

onMounted(() => {
  loadUser()
  loadHistory()
})

const watchActiveTab = () => {
  if (activeTab.value === 'files') {
    loadFiles()
  }
}
</script>

<style scoped>
.profile-page {
  min-height: calc(100vh - 60px);
  background-color: var(--page-background);
  padding: 24px;
}

.profile-container {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 24px;
}

.profile-sidebar {
  background-color: white;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  padding: 24px;
}

.user-card {
  text-align: center;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--border-color);
  margin-bottom: 24px;
}

.avatar-wrapper {
  margin-bottom: 16px;
}

.avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 32px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
}

.user-name {
  font-size: 18px;
  font-weight: 600;
  color: var(--primary-color);
  margin-bottom: 4px;
}

.user-email {
  font-size: 14px;
  color: var(--text-secondary);
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: var(--radius-md);
  background-color: transparent;
  border: none;
  cursor: pointer;
  font-size: 14px;
  color: var(--text-secondary);
  transition: all 0.2s ease;
}

.nav-item:hover {
  background-color: var(--card-background);
}

.nav-item.active {
  background-color: var(--primary-color);
  color: white;
}

.nav-icon {
  font-size: 16px;
}

.nav-text {
  font-weight: 500;
}

.profile-content {
  background-color: white;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  padding: 24px;
  min-height: 500px;
}

.tab-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
}

.tab-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--primary-color);
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--border-color);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px;
}

.empty-state-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-state-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--primary-color);
  margin-bottom: 8px;
}

.empty-state-description {
  font-size: 14px;
  color: var(--text-secondary);
}

.records-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.record-card {
  background-color: var(--card-background);
  border-radius: var(--radius-md);
  padding: 16px;
  transition: all 0.2s ease;
}

.record-card:hover {
  box-shadow: var(--shadow-sm);
}

.record-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.record-language {
  font-size: 20px;
}

.record-date {
  font-size: 12px;
  color: var(--text-muted);
}

.record-code {
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 12px;
  word-break: break-all;
}

.record-actions {
  display: flex;
  gap: 8px;
}

.files-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.file-card {
  background-color: var(--card-background);
  border-radius: var(--radius-md);
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  transition: all 0.2s ease;
}

.file-card:hover {
  box-shadow: var(--shadow-sm);
}

.file-icon {
  font-size: 32px;
}

.file-info {
  flex: 1;
}

.file-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--primary-color);
  margin-bottom: 4px;
}

.file-size,
.file-date {
  font-size: 12px;
  color: var(--text-muted);
}

.file-actions {
  display: flex;
  gap: 8px;
}

.settings-form {
  max-width: 500px;
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: var(--primary-color);
  margin-bottom: 8px;
}

.form-control {
  width: 100%;
  padding: 12px;
  font-size: 14px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  background-color: var(--card-background);
  outline: none;
  transition: border-color 0.2s ease;
}

.form-control:focus {
  border-color: var(--primary-color);
}

.form-control:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.hidden {
  display: none;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 13px;
}

@media (max-width: 768px) {
  .profile-container {
    grid-template-columns: 1fr;
  }
}
</style>
