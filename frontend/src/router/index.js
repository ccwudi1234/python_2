import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue')
  },
  {
    path: '/python',
    name: 'PythonAnalysis',
    component: () => import('../views/PythonAnalysis.vue')
  },
  {
    path: '/c',
    name: 'CAnalysis',
    component: () => import('../views/CAnalysis.vue')
  },
  {
    path: '/files',
    name: 'Files',
    component: () => import('../views/Files.vue')
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('../views/History.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
