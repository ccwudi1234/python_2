<template>
  <div class="files-page">
    <div class="page-header">
      <h1><el-icon><FolderOpened /></el-icon>我的文件</h1>
      <el-button type="primary" @click="handleUploadClick">
        <el-icon><Upload /></el-icon>上传文件
      </el-button>
    </div>
    
    <el-card>
      <el-table :data="files" v-loading="loading">
        <el-table-column prop="filename" label="文件名" />
        <el-table-column prop="created_at" label="上传时间" width="200">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="handleView(row)">查看</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-empty v-if="!loading && files.length === 0" description="暂无文件" />
    </el-card>
    
    <input
      ref="fileInput"
      type="file"
      style="display: none"
      accept=".py,.c,.cpp"
      @change="handleFileSelect"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { fileApi } from '../api'
import { useAuthStore } from '../store'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()
const files = ref([])
const loading = ref(false)
const fileInput = ref(null)

onMounted(() => {
  loadFiles()
})

async function loadFiles() {
  if (!authStore.user?.id) return
  try {
    loading.value = true
    const res = await fileApi.list(authStore.user.id)
    files.value = res.data
  } catch (error) {
    ElMessage.error('加载文件失败')
  } finally {
    loading.value = false
  }
}

function handleUploadClick() {
  fileInput.value.click()
}

async function handleFileSelect(event) {
  const file = event.target.files[0]
  if (!file || !authStore.user?.id) return
  
  try {
    await fileApi.upload(authStore.user.id, file)
    ElMessage.success('上传成功')
    loadFiles()
  } catch (error) {
    ElMessage.error('上传失败')
  }
}

function handleView(row) {
  ElMessage.info('查看功能开发中')
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm('确定要删除该文件吗?', '提示', {
      type: 'warning'
    })
    await fileApi.delete(row.id)
    ElMessage.success('删除成功')
    loadFiles()
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
.files-page {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h1 {
  font-size: 24px;
  color: var(--primary-dark);
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>
