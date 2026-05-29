<template>
  <div class="auth-page">
    <div class="auth-container">
      <div class="auth-form">
        <div class="form-wrapper">
          <div class="form-header">
            <h1 class="form-title">创建账号</h1>
            <p class="form-subtitle">注册后即可使用代码可视化功能</p>
          </div>

          <form @submit.prevent="handleRegister" class="form-content">
            <div class="form-group">
              <label class="form-label">用户名</label>
              <input 
                v-model="form.username" 
                type="text" 
                class="form-control"
                placeholder="请输入用户名"
                required
              />
            </div>

            <div class="form-group">
              <label class="form-label">密码</label>
              <input 
                v-model="form.password" 
                type="password" 
                class="form-control"
                placeholder="请输入密码"
                required
              />
            </div>

            <button type="submit" class="btn btn-primary btn-block" :disabled="loading">
              <span v-if="loading" class="loading-spinner"></span>
              {{ loading ? '注册中...' : '注册' }}
            </button>
          </form>

          <div class="form-footer">
            <span>已有账号？</span>
            <router-link to="/login" class="register-link">立即登录</router-link>
          </div>
        </div>
      </div>

      <div class="auth-illustration">
        <div class="illustration-content">
          <div class="illustration-icon">🚀</div>
          <h2 class="illustration-title">开启学习之旅</h2>
          <p class="illustration-desc">可视化代码执行过程，深入理解内存机制</p>
          <div class="features-list">
            <div class="feature-item">📚 学习资源丰富</div>
            <div class="feature-item">🤝 社区互动</div>
            <div class="feature-item">💾 云端保存</div>
            <div class="feature-item">📈 进度追踪</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { authApi } from '../api'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()

const form = reactive({
  username: '',
  password: ''
})

const loading = ref(false)

const handleRegister = async () => {
  if (!form.username || !form.password) {
    ElMessage.error('请填写用户名和密码')
    return
  }

  loading.value = true
  try {
    await authApi.register({
      username: form.username,
      password: form.password
    })
    
    ElMessage.success('注册成功，请登录')
    router.push('/login')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '注册失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.auth-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  max-width: 900px;
  width: 100%;
  margin: 0 24px;
  background-color: white;
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg);
  overflow: hidden;
}

.auth-form {
  padding: 60px 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.form-wrapper {
  width: 100%;
  max-width: 350px;
}

.form-header {
  text-align: center;
  margin-bottom: 32px;
}

.form-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--primary-color);
  margin-bottom: 8px;
}

.form-subtitle {
  font-size: 14px;
  color: var(--text-secondary);
}

.form-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--primary-color);
}

.form-control {
  width: 100%;
  padding: 14px;
  font-size: 14px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  background-color: var(--card-background);
  outline: none;
  transition: all 0.2s ease;
}

.form-control:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(44, 62, 80, 0.1);
}

.btn-block {
  width: 100%;
}

.form-footer {
  margin-top: 24px;
  text-align: center;
  font-size: 14px;
  color: var(--text-secondary);
}

.register-link {
  color: var(--primary-color);
  font-weight: 600;
  text-decoration: none;
  margin-left: 8px;
}

.register-link:hover {
  text-decoration: underline;
}

.auth-illustration {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  color: white;
  padding: 60px 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.illustration-content {
  text-align: center;
}

.illustration-icon {
  font-size: 80px;
  margin-bottom: 24px;
}

.illustration-title {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 12px;
}

.illustration-desc {
  font-size: 14px;
  opacity: 0.9;
  margin-bottom: 32px;
}

.features-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.feature-item {
  font-size: 14px;
  padding: 10px 20px;
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-md);
}

@media (max-width: 768px) {
  .auth-container {
    grid-template-columns: 1fr;
  }
  
  .auth-form {
    padding: 40px 24px;
    order: 2;
  }
  
  .auth-illustration {
    padding: 40px 24px;
    order: 1;
  }
}
</style>
