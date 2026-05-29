<template>
  <div class="history-page">
    <div class="page-header">
      <h1><el-icon><History /></el-icon>分析历史</h1>
    </div>
    
    <div class="history-list" v-loading="loading">
      <el-empty v-if="!loading && records.length === 0" description="暂无历史记录" />
      
      <div v-else class="records-grid">
        <el-card v-for="record in records" :key="record.id" class="record-card" shadow="hover">
          <div class="record-header">
            <el-tag :type="record.language === 'python' ? 'primary' : 'success'" size="small">
              {{ record.language.toUpperCase() }}
            </el-tag>
            <span class="record-time">{{ formatDate(record.created_at) }}</span>
          </div>
          <div class="record-code">
            <pre>{{ record.code_content }}</pre>
          </div>
          <div class="record-actions">
            <el-button size="small" @click="handleReanalyze(record)">
              <el-icon><RefreshLeft /></el-icon>重新分析
            </el-button>
            <el-button size="small" type="danger" @click="handleDelete(record)">
              <el-icon><Delete /></el-icon>删除
            </el-button>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { recordApi } from '../api'
import { useAuthStore, useCodeStore } from '../store'

const router = useRouter()
const authStore = useAuthStore()
const codeStore = useCodeStore()
const records = ref([])
const loading = ref(false)

onMounted(() => {
  loadRecords()
})

async function loadRecords() {
  if (!authStore.user?.id) return
  try {
    loading.value = true
    const res = await recordApi.list(authStore.user.id)
    records.value = res.data
  } catch (error) {
    ElMessage.error('加载历史记录失败')
  } finally {
    loading.value = false
  }
}

function handleReanalyze(record) {
  codeStore.setCode(record.code_content)
  codeStore.setLanguage(record.language)
  router.push(record.language === 'python' ? '/python' : '/c')
}

async function handleDelete(record) {
  try {
    await ElMessageBox.confirm('确定要删除该记录吗?', '提示', {
      type: 'warning'
    })
    await recordApi.delete(record.id)
    ElMessage.success('删除成功')
    loadRecords()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleString()
}
</script>

<style scoped>
.history-page {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 24px;
  color: var(--primary-dark);
  display: flex;
  align-items: center;
  gap: 8px;
}

.records-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
}

.record-card {
  display: flex;
  flex-direction: column;
}

.record-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.record-time {
  color: #64748b;
  font-size: 13px;
}

.record-code {
  background: #f8fafc;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 12px;
  flex: 1;
  overflow: hidden;
}

.record-code pre {
  margin: 0;
  font-size: 13px;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 120px;
  overflow: hidden;
}

.record-actions {
  display: flex;
  gap: 8px;
}
</style>
