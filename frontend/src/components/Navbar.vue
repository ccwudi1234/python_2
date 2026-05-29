<template>
  <nav class="navbar">
    <div class="navbar-left">
      <div class="navbar-logo">
        <span class="logo-icon">📊</span>
        <span class="logo-text">CodeVis</span>
      </div>
      <div class="navbar-nav">
        <router-link 
          v-for="item in navItems" 
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: $route.path === item.path }"
        >
          <span class="nav-icon">{{ item.icon }}</span>
          <span class="nav-text">{{ item.name }}</span>
        </router-link>
      </div>
    </div>
    <div class="navbar-right">
      <div class="nav-links">
        <router-link to="/history" class="nav-link">
          <span>📋</span> 历史记录
        </router-link>
        <router-link to="/files" class="nav-link">
          <span>📁</span> 文件管理
        </router-link>
      </div>
    </div>
  </nav>
</template>

<script setup>
const navItems = [
  { path: '/', name: '首页', icon: '🏠' },
  { path: '/python', name: 'Python分析', icon: '🐍' },
  { path: '/c', name: 'C/C++分析', icon: '⚙️' },
  { path: '/examples', name: '可视化示例', icon: '✨' },
]
</script>

<style scoped>
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  height: 64px;
  background-color: var(--primary-color);
  color: white;
  box-shadow: var(--shadow-md);
  position: relative;
  z-index: 100;
}

.navbar-left {
  display: flex;
  align-items: center;
  gap: 32px;
}

.navbar-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.logo-icon {
  font-size: 28px;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.navbar-nav {
  display: flex;
  gap: 4px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: var(--radius-md);
  text-decoration: none;
  color: rgba(255, 255, 255, 0.8);
  transition: all 0.2s ease;
}

.nav-item:hover {
  background-color: rgba(255, 255, 255, 0.1);
  color: white;
}

.nav-item.active {
  background-color: rgba(255, 255, 255, 0.15);
  color: white;
}

.nav-icon {
  font-size: 16px;
}

.nav-text {
  font-size: 14px;
  font-weight: 500;
}

.navbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.nav-links {
  display: flex;
  gap: 16px;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border-radius: var(--radius-md);
  text-decoration: none;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  transition: all 0.2s ease;
}

.nav-link:hover {
  background-color: rgba(255, 255, 255, 0.1);
  color: white;
}
</style>
