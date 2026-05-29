import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '../api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  const isAuthenticated = computed(() => !!token.value)

  function setToken(newToken) {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }

  async function fetchUser() {
    try {
      const res = await authApi.getProfile()
      user.value = res.data
      localStorage.setItem('user', JSON.stringify(res.data))
    } catch (error) {
      console.error('Failed to fetch user:', error)
    }
  }

  function setAuth(newToken, userData) {
    token.value = newToken
    user.value = userData
    localStorage.setItem('token', newToken)
    localStorage.setItem('user', JSON.stringify(userData))
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  return { token, user, isAuthenticated, setToken, fetchUser, setAuth, logout }
})

export const useCodeStore = defineStore('code', () => {
  const currentCode = ref('')
  const currentLanguage = ref('python')
  const visualData = ref(null)
  const currentStep = ref(0)
  const isPlaying = ref(false)
  const playSpeed = ref(1000)

  function setCode(code) {
    currentCode.value = code
  }

  function setLanguage(lang) {
    currentLanguage.value = lang
  }

  function setVisualData(data) {
    visualData.value = data
    currentStep.value = 0
  }

  function setStep(step) {
    currentStep.value = step
  }

  function nextStep() {
    if (visualData.value && currentStep.value < visualData.value.length - 1) {
      currentStep.value++
    }
  }

  function prevStep() {
    if (currentStep.value > 0) {
      currentStep.value--
    }
  }

  return {
    currentCode,
    currentLanguage,
    visualData,
    currentStep,
    isPlaying,
    playSpeed,
    setCode,
    setLanguage,
    setVisualData,
    setStep,
    nextStep,
    prevStep
  }
})
