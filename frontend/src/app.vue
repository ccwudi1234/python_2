<template>
  <div id="app">
    <Navbar v-if="authStore.isAuthenticated" />
    <div class="main-content">
      <router-view />
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from './store'
import Navbar from './components/Navbar.vue'

const authStore = useAuthStore()
</script>

<style scoped>
.main-content {
  min-height: calc(100vh - 64px);
  padding-top: 64px;
}
</style>
