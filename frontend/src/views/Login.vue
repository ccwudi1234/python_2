<template>
  <div class="auth-page">
    <div class="auth-container">
      <div class="auth-illustration">
        <div class="illustration-content">
          <div class="illustration-icon">💻</div>
          <h2 class="illustration-title">代码内存可视化</h2>
          <p class="illustration-desc">探索代码背后的内存世界，让编程更直观</p>
          <div class="features-list">
            <div class="feature-item">🐍 Python代码分析</div>
            <div class="feature-item">⚙️ C/C++内存解析</div>
            <div class="feature-item">📊 动态可视化</div>
            <div class="feature-item">🔄 单步执行</div>
          </div>
        </div>
      </div>

      <div class="auth-form">
        <div class="form-wrapper">
          <div class="form-header">
            <h1 class="form-title">欢迎回来</h1>
            <p class="form-subtitle">登录您的账号，开始代码分析之旅</p>
          </div>

          <form @submit.prevent="handleLogin" class="form-content">
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

            <div class="form-options">
              <label class="checkbox-label">
                <input type="checkbox" v-model="rememberMe" />
                <span class="checkmark"></span>
                <span>记住我</span>
              </label>
              <a href="#" class="forgot-link">忘记密码？</a>
            </div>

            <button type="submit" class="btn btn-primary btn-block" :disabled="loading">
              <span v-if="loading" class="loading-spinner"></span>
              {{ loading ? '登录中...' : '登录' }}
            </button>
          </form>

          <div class="form-footer">
            <span>还没有账号？</span>
            <router-link to="/register" class="register-link">立即注册</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { authApi } from '../api'
import { useAuthStore } from '../store'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const authStore = useAuthStore()
const router = useRouter()

const form = reactive({
  username: '',
  password: ''
})

const rememberMe = ref(false)
const loading = ref(false)

const handleLogin = async () => {
  loading.value = true
  try {
    const res = await authApi.login({
      username: form.username,
      password: form.password
    })
    
    authStore.setToken(res.data.access_token)
    await authStore.fetchUser()
    
    if (rememberMe.value) {
      localStorage.setItem('remember_username', form.username)
    }
    
    ElMessage.success('登录成功')
    router.push('/')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '登录失败')
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

.auth-illustration {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--text-secondary);
  cursor: pointer;
}

.checkbox-label input {
  display: none;
}

.checkmark {
  width: 18px;
  height: 18px;
  border: 2px solid var(--border-color);
  border-radius: 4px;
  position: relative;
  transition: all 0.2s ease;
}

.checkbox-label input:checked + .checkmark {
  background-color: var(--primary-color);
  border-color: var(--primary-color);
}

.checkbox-label input:checked + .checkmark::after {
  content: '';
  position: absolute;
  left: 6px;
  top: 2px;
  width: 5px;
  height: 10px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.forgot-link {
  font-size: 14px;
  color: var(--primary-color);
  text-decoration: none;
}

.forgot-link:hover {
  text-decoration: underline;
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

@media (max-width: 768px) {
  .auth-container {
    grid-template-columns: 1fr;
  }
  
  .auth-illustration {
    padding: 40px 24px;
  }
  
  .auth-form {
    padding: 40px 24px;
  }
}
</style>
