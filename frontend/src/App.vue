<template>
  <div class="app-layout">
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

onMounted(async () => {
  if (auth.isLoggedIn) {
    await auth.fetchUser()
  }
})
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
}
</style>
