<template>
  <div class="share-page">
    <!-- Mock: show a sample shared file -->
    <div class="share-container glass-card animate-slide-up" v-if="file">
      <div class="share-header">
        <div class="logo">
          <span class="logo-icon icon-tactile">☁️</span>
          <span class="logo-text">FileSharing</span>
        </div>
        <p class="share-subtitle">A file has been shared with you</p>
      </div>

      <div class="shared-file bento-cell">
        <div class="shared-file-icon icon-tactile">{{ getFileIcon(file.filename) }}</div>
        <div class="shared-file-info">
          <h1 class="shared-filename" :title="file.filename">{{ file.filename }}</h1>
          <p class="shared-meta text-muted">{{ formatBytes(file.size) }} · Shared via link</p>
        </div>
      </div>

      <button class="btn btn-primary btn-full" @click="mockDownload">
        Continue to Download
      </button>

      <div class="share-footer">
        <p class="text-muted">
          Need secure cloud storage?
          <RouterLink to="/register" class="link">Get started for free</RouterLink>
        </p>
      </div>
    </div>

    <!-- Loading -->
    <div class="share-container glass-card" v-else-if="loading">
      <div class="loading-state">
        <div class="spinner-sm"></div>
        <p class="text-muted">Retrieving shared object...</p>
      </div>
    </div>

    <!-- Error -->
    <div class="share-container glass-card animate-slide-up" v-else>
      <div class="error-state">
        <div class="error-icon icon-tactile">🔗</div>
        <h1>Link Inactive</h1>
        <p class="text-muted">This share link is invalid or has reached its lifecycle end.</p>
        <RouterLink to="/" class="btn btn-ghost btn-full" style="margin-top: 24px;">
          Go to FileSharing
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const file = ref(null)
const loading = ref(true)

onMounted(() => {
  setTimeout(() => {
    const token = route.params.token
    if (token && token !== 'invalid') {
      file.value = {
        filename: 'project-proposal.pdf',
        size: 2.4 * 1024 ** 2,
      }
    }
    loading.value = false
  }, 1200)
})

function mockDownload() {
  alert('[Mock] Secure download initiated.')
}

function getFileIcon(filename) {
  if (!filename) return '📄'
  const ext = filename.split('.').pop()?.toLowerCase()
  const icons = {
    pdf: '📕', doc: '📝', docx: '📝',
    jpg: '🖼️', jpeg: '🖼️', png: '🖼️',
    mp4: '🎬', zip: '📦',
  }
  return icons[ext] || '📄'
}

function formatBytes(b) {
  if (b < 1024) return b + ' B'
  if (b < 1024 ** 2) return (b / 1024).toFixed(1) + ' KB'
  return (b / 1024 ** 2).toFixed(1) + ' MB'
}
</script>

<style scoped>
.share-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 24px;
  background: var(--bg-base);
}

.share-container {
  width: 100%;
  max-width: 480px;
  padding: 48px;
  display: flex;
  flex-direction: column;
}

.share-header {
  text-align: center;
  margin-bottom: 40px;
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 24px;
}

.logo-icon {
  font-size: 2.2rem;
}

.logo-text {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -0.03em;
}

.share-subtitle {
  color: var(--text-secondary);
  font-size: 1rem;
}

.shared-file {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 24px;
  margin-bottom: 32px;
  text-align: left;
}

.shared-file-icon {
  font-size: 2.5rem;
}

.shared-file-info {
  min-width: 0;
}

.shared-filename {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.btn-full {
  width: 100%;
  padding: 14px;
}

.share-footer {
  text-align: center;
  margin-top: 32px;
  font-size: 0.9rem;
}

.link {
  color: var(--primary-400);
  text-decoration: none;
  font-weight: 600;
}

.link:hover {
  text-decoration: underline;
}

.loading-state, .error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 24px 0;
}

.error-icon {
  font-size: 3rem;
  margin-bottom: 12px;
}

.error-state h1 {
  font-size: 1.5rem;
  font-weight: 700;
}

.spinner-sm {
  width: 24px;
  height: 24px;
  border: 2px solid var(--border-default);
  border-top-color: var(--primary-400);
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }
</style>

