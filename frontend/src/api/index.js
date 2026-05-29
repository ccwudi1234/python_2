import axios from 'axios'

const api = axios.create({
  baseURL: 'http://127.0.0.1:9999',
  timeout: 10000
})

// 添加认证 token 拦截器
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

export const authApi = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  getProfile: () => api.get('/auth/profile'),
  updateProfile: (data) => api.put('/auth/profile', data)
}

export const userApi = authApi

export const parseApi = {
  parsePython: (code) => api.post('/parse/python', { code, language: 'python' }),
  parseC: (code) => api.post('/parse/c', { code, language: 'c' }),
  getCopyComparison: (code) => api.post('/parse/copy-comparison', { code, language: 'python' })
}

export const fileApi = {
  upload: (formData) => api.post('/files/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  getAll: () => api.get('/files'),
  delete: (fileId) => api.delete(`/files/${fileId}`)
}

export const recordApi = {
  create: (data) => api.post('/records', data),
  getAll: () => api.get('/records'),
  get: (recordId) => api.get(`/records/${recordId}`),
  delete: (recordId) => api.delete(`/records/${recordId}`)
}

export default api
