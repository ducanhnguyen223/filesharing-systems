<template>
  <div class="dashboard-layout">
    <!-- Persistent Sidebar -->
    <aside class="sidebar">
      <div class="logo">
        <span class="logo-icon">☁️</span>
        <span class="logo-text">FileSharing</span>
      </div>

      <nav class="sidebar-nav">
        <button class="nav-item active">📁 My Files</button>
        <button class="nav-item">🔗 Shared</button>
        <button class="nav-item">🕒 Recent</button>
        <button class="nav-item">🗑 Trash</button>
      </nav>

      <div class="sidebar-footer">
        <!-- Storage Card (Bento Style) -->
        <div class="storage-card glass-card">
          <div class="storage-card-header">
            <span class="text-muted">Storage</span>
            <span class="badge" :class="auth.user?.plan_name === 'pro' ? 'badge-pro' : 'badge-free'">
              {{ auth.user?.plan_name || 'FREE' }}
            </span>
          </div>
          <div class="storage-stats">
            <strong>{{ formatBytes(auth.user?.storage_used || 0) }}</strong>
            <span class="text-muted"> / {{ formatBytes(auth.storageLimitBytes) }}</span>
          </div>
          <div class="progress-bar">
            <div
              class="progress-bar-fill"
              :class="{ warning: auth.storagePercent > 85 }"
              :style="{ width: auth.storagePercent + '%' }"
            ></div>
          </div>
          <button v-if="auth.user?.plan_name !== 'pro'" class="btn btn-primary btn-sm btn-block">
            Upgrade to Pro
          </button>
        </div>
        
        <div class="user-info">
          <div class="avatar">👤</div>
          <div class="user-details">
            <span class="user-email" :title="auth.user?.email">{{ auth.user?.email || 'User' }}</span>
            <button class="logout-link" @click="logout">Logout</button>
          </div>
        </div>
      </div>
    </aside>

    <!-- Main Content Area -->
    <main class="main-content">
      <header class="content-header">
        <h1>Overview</h1>
        <div class="header-actions">
          <div class="search-box">
            <span>🔍</span>
            <input type="text" placeholder="Search knowledge..." />
          </div>
          <button class="btn btn-primary" @click="triggerFileInput">
            <span>+</span> Upload
          </button>
          <input type="file" ref="fileInput" @change="handleFileSelect" multiple hidden />
        </div>
      </header>

      <!-- Bento Grid Section -->
      <section class="bento-grid">
        <!-- Folders Cell (The @kvnkld look) -->
        <div class="bento-cell folder-cell" v-for="folder in ['Onboarding', 'Integrations', 'Technical']" :key="folder">
          <div class="folder-stack icon-tactile">
            <div class="folder-back"></div>
            <div class="folder-paper"></div>
            <div class="folder-front">
              <span class="folder-label">📂</span>
            </div>
          </div>
          <div class="cell-info">
            <h3>{{ folder }}</h3>
            <span class="text-muted">{{ Math.floor(Math.random() * 20) + 1 }} Files</span>
          </div>
        </div>

        <!-- Files Section (Clean List within cells) -->
        <div v-for="file in files" :key="file.id" class="bento-cell file-cell clickable">
          <div class="file-tactile-icon icon-tactile">
             {{ getFileIcon(file.mimetype) }}
          </div>
          <div class="cell-info">
            <h4 class="file-name" :title="file.filename">{{ file.filename }}</h4>
            <span class="text-muted">{{ formatBytes(file.size) }} · {{ formatDate(file.created_at) }}</span>
          </div>
          <div class="cell-actions">
             <button @click.stop="shareFile(file)">🔗</button>
             <button @click.stop="deleteFile(file.id)" style="color: var(--danger)">🗑</button>
          </div>
        </div>
      </section>

      <!-- Upload Progress Overlay (Bento style card) -->
      <transition name="fade">
        <div v-if="uploadProgress > 0" class="upload-toast glass-card">
          <div class="toast-content">
            <span class="spinner-sm"></span>
            <div class="toast-info">
              <span class="toast-title">Uploading...</span>
              <div class="progress-bar mini"><div class="progress-bar-fill" :style="{width: uploadProgress + '%'}"></div></div>
            </div>
          </div>
        </div>
      </transition>

      <!-- Share link modal -->
      <transition name="fade">
        <div v-if="shareModal.show" class="modal-overlay" @click.self="shareModal.show = false">
          <div class="modal glass-card">
            <h2>Share link created</h2>
            <p class="text-muted" style="margin-bottom: 20px;">Anyone with this link can view the file</p>
            <div class="share-url-box">
              <input type="text" :value="shareModal.url" readonly />
              <button class="btn btn-primary" @click="copyShareLink">
                {{ copied ? 'Copied' : 'Copy' }}
              </button>
            </div>
             <button class="btn btn-ghost" @click="shareModal.show = false" style="width: 100%; margin-top: 12px;">Close</button>
          </div>
        </div>
      </transition>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

// ============ MOCK DATA ============
const MOCK_FILES = [
  { id: 1, filename: 'Onboarding-Guide.pdf', size: 2.4 * 1024 ** 2, mimetype: 'application/pdf', created_at: new Date(Date.now() - 3600000).toISOString() },
  { id: 2, filename: 'Product-Roadmap.docx', size: 5.1 * 1024 ** 2, mimetype: 'image/jpeg', created_at: new Date(Date.now() - 86400000).toISOString() },
  { id: 3, filename: 'design-specs.fig', size: 18.7 * 1024 ** 2, mimetype: 'application/vnd.figma', created_at: new Date(Date.now() - 172800000).toISOString() },
  { id: 4, filename: 'budget-2026.xlsx', size: 340 * 1024, mimetype: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', created_at: new Date(Date.now() - 259200000).toISOString() },
  { id: 5, filename: 'source-code.zip', size: 45.2 * 1024 ** 2, mimetype: 'application/zip', created_at: new Date(Date.now() - 604800000).toISOString() },
  { id: 6, filename: 'meeting-notes.md', size: 12 * 1024, mimetype: 'text/markdown', created_at: new Date(Date.now() - 1209600000).toISOString() },
]

const files = ref([])
const loading = ref(true)
const uploadProgress = ref(0)
const uploadError = ref('')
const fileInput = ref(null)
const copied = ref(false)
const shareModal = ref({ show: false, url: '' })
let nextId = 100

onMounted(async () => {
  if (auth.isLoggedIn) await auth.fetchUser()
  setTimeout(() => {
    files.value = [...MOCK_FILES]
    loading.value = false
  }, 1200)
})

function triggerFileInput() {
  fileInput.value?.click()
}

function handleFileSelect(e) {
  const selected = Array.from(e.target.files)
  if (selected.length) mockUpload(selected)
  e.target.value = ''
}

function mockUpload(fileList) {
  uploadProgress.value = 1
  let progress = 1
  const interval = setInterval(() => {
    progress += Math.random() * 20
    if (progress >= 100) {
      clearInterval(interval)
      uploadProgress.value = 100
      setTimeout(() => {
        for (const f of fileList) {
          files.value.unshift({
            id: nextId++,
            filename: f.name,
            size: f.size,
            mimetype: f.type || 'application/octet-stream',
            created_at: new Date().toISOString(),
          })
        }
        uploadProgress.value = 0
      }, 500)
    } else {
      uploadProgress.value = Math.round(progress)
    }
  }, 200)
}

function shareFile(file) {
  const fakeToken = btoa(file.filename).replace(/[^a-zA-Z0-9]/g, '').slice(0, 16)
  shareModal.value = {
    show: true,
    url: `${window.location.origin}/share/${fakeToken}`,
  }
}

function copyShareLink() {
  navigator.clipboard.writeText(shareModal.value.url)
  copied.value = true
  setTimeout(() => (copied.value = false), 2000)
}

function deleteFile(id) {
  if (confirm('Delete this file?')) {
    files.value = files.value.filter(f => f.id !== id)
  }
}

function logout() {
  auth.logout()
  router.push('/login')
}

function getFileIcon(mimetype) {
  if (mimetype?.includes('pdf')) return '📕'
  if (mimetype?.includes('image')) return '🖼️'
  if (mimetype?.includes('video')) return '🎬'
  if (mimetype?.includes('zip')) return '📦'
  return '📄'
}

function formatBytes(b) {
  if (b < 1024) return b + ' B'
  if (b < 1024 ** 2) return (b / 1024).toFixed(1) + ' KB'
  return (b / 1024 ** 2).toFixed(1) + ' MB'
}

function formatDate(dateStr) {
  const d = new Date(dateStr)
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}
</script>

<style scoped>
/* Sidebar Refinements */
.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.nav-item {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  padding: 12px 16px;
  text-align: left;
  border-radius: var(--radius-md);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.nav-item:hover, .nav-item.active {
  background: rgba(255, 255, 255, 0.03);
  color: var(--text-primary);
}

.sidebar-footer {
  margin-top: auto;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.storage-card {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.storage-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.8rem;
}

.storage-stats {
  font-size: 0.9rem;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px;
}

.avatar {
  width: 40px;
  height: 40px;
  background: var(--bg-elevated);
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
}

.user-details {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.user-email {
  font-size: 0.85rem;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.logout-link {
  background: none;
  border: none;
  color: var(--text-muted);
  font-size: 0.75rem;
  text-align: left;
  cursor: pointer;
  padding: 0;
}

.logout-link:hover {
  text-decoration: underline;
  color: var(--danger);
}

/* Header */
.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 16px;
}

.search-box {
  background: var(--bg-input);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  padding: 8px 16px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.search-box input {
  background: transparent;
  border: none;
  padding: 0;
  width: 200px;
}

/* Bento Cells */
.folder-cell {
  display: flex;
  flex-direction: column;
  gap: 16px;
  align-items: flex-start;
}

.cell-info h3, .cell-info h4 {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 4px;
}

.file-cell {
  position: relative;
  display: flex;
  align-items: center;
  gap: 16px;
}

.cell-actions {
  margin-left: auto;
  display: flex;
  gap: 8px;
  opacity: 0;
  transition: opacity var(--transition-base);
}

.file-cell:hover .cell-actions {
  opacity: 1;
}

.cell-actions button {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.2rem;
  transition: transform var(--transition-fast);
}

.cell-actions button:hover {
  transform: scale(1.2);
}

/* Tactile Icon Styles */
.folder-stack {
  position: relative;
  width: 60px;
  height: 48px;
}

.folder-back {
  position: absolute;
  inset: 0;
  background: #2a2a2a;
  border-radius: 4px;
}

.folder-paper {
  position: absolute;
  left: 4px;
  right: 4px;
  top: -4px;
  height: 20px;
  background: white;
  border-radius: 2px;
  box-shadow: 0 -2px 4px rgba(0,0,0,0.2);
}

.folder-front {
  position: absolute;
  inset: 0;
  top: 6px;
  background: #3a3a3a;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 -1px 0 rgba(255,255,255,0.1) inset;
}

/* Toast */
.upload-toast {
  position: fixed;
  bottom: 24px;
  right: 24px;
  padding: 16px 24px;
  z-index: 2000;
}

.toast-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.spinner-sm {
  width: 20px;
  height: 20px;
  border: 2px solid var(--border-default);
  border-top-color: var(--primary-400);
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.mini { height: 4px; margin-top: 4px; }
</style>

