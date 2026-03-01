<template>
  <div class="dv-app">
    <!-- LEFT SIDEBAR -->
    <aside class="sidebar">
      <div class="sidebar-top">
        <div class="brand">
          <div class="brand-icon"><span class="mi">cloud</span></div>
          <span class="brand-name">DocuVault</span>
        </div>

        <nav class="nav-menu">
          <a class="nav-item active"><span class="mi">dashboard</span> Dashboard</a>
          <a class="nav-item"><span class="mi">schedule</span> Recent files</a>
          <a class="nav-item"><span class="mi">description</span> Documents</a>
          <a class="nav-item"><span class="mi">image</span> Images</a>
          <a class="nav-item"><span class="mi">videocam</span> Videos</a>
          <a class="nav-item"><span class="mi">audiotrack</span> Audios</a>
          <a class="nav-item"><span class="mi">delete</span> Deleted files</a>
        </nav>
      </div>

      <div class="sidebar-bottom">
        <a class="nav-item"><span class="mi">settings</span> Settings</a>
        <a class="nav-item"><span class="mi">chat_bubble</span> Chat & Support</a>
        <a class="nav-item"><span class="mi">help</span> Help Center</a>
        <div class="user-block">
          <div class="user-avatar">{{ (auth.user?.email || 'U')[0].toUpperCase() }}</div>
          <div class="user-meta">
            <span class="user-name">{{ auth.user?.email || 'User' }}</span>
            <button class="logout-btn" @click="logout">Logout</button>
          </div>
        </div>
      </div>
    </aside>

    <!-- MAIN CONTENT -->
    <main class="main">
      <!-- Search Bar -->
      <div class="search-bar">
        <span class="mi search-icon">search</span>
        <input type="text" placeholder="Search files..." v-model="searchQuery" />
        <button class="btn-upload" @click="triggerFileInput">
          <span class="mi">cloud_upload</span> Upload file
        </button>
        <input type="file" ref="fileInput" @change="handleFileSelect" multiple hidden />
      </div>

      <!-- Recently Modified -->
      <section class="section">
        <h3 class="section-title">Recently modified</h3>
        <div class="recent-grid">
          <div class="recent-card" v-for="file in topRecentFiles" :key="file.id" @click="downloadFile(file.id, file.filename)">
            <div class="recent-preview" :class="getCategoryClass(file.mimetype)">
              <span class="mi" style="font-size:32px">{{ getCategoryIcon(file.mimetype) }}</span>
            </div>
            <div class="recent-info">
              <span class="recent-name">{{ file.filename }}</span>
              <span class="recent-meta">{{ formatBytes(file.size) }} • {{ formatRelative(file.created_at) }}</span>
            </div>
          </div>
          <div v-if="topRecentFiles.length === 0 && !loading" class="recent-card empty-card">
            <span class="mi" style="font-size:32px;color:var(--text-muted)">upload_file</span>
            <span class="recent-meta">Upload your first file</span>
          </div>
        </div>
      </section>

      <!-- File Distribution Bar Chart -->
      <section class="section" v-if="files.length > 0">
        <div class="chart-header">
          <h3 class="section-title">File distribution</h3>
          <span class="chart-label">This Week</span>
        </div>
        <div class="chart-bars">
          <div class="chart-col" v-for="(cat, i) in chartCategories" :key="i">
            <div class="bar-track">
              <div class="bar-fill" :class="cat.cls" :style="{height: cat.percent + '%'}"></div>
            </div>
            <span class="bar-label">{{ cat.name }}</span>
          </div>
        </div>
      </section>

      <!-- All Files Table -->
      <section class="section">
        <div class="table-header">
          <h3 class="section-title">All files</h3>
          <span class="view-all" v-if="files.length > 0">View All ›</span>
        </div>

        <table class="file-table" v-if="!loading && files.length > 0">
          <thead>
            <tr>
              <th width="36"></th>
              <th>NAME</th>
              <th>OWNER</th>
              <th>FILE SIZE</th>
              <th>MODIFIED</th>
              <th width="48"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="file in filteredFiles" :key="file.id" class="file-row" @click="downloadFile(file.id, file.filename)">
              <td><div class="file-icon" :class="getCategoryClass(file.mimetype)"><span class="mi" style="font-size:18px">{{ getCategoryIcon(file.mimetype) }}</span></div></td>
              <td class="fname">{{ file.filename }}</td>
              <td class="text-muted">Me</td>
              <td class="text-muted">{{ formatBytes(file.size) }}</td>
              <td class="text-muted">{{ formatDate(file.created_at) }}</td>
              <td>
                <div class="row-actions">
                  <button class="icon-btn" @click.stop="shareFile(file)" title="Share"><span class="mi">link</span></button>
                  <button class="icon-btn danger" @click.stop="deleteFile(file.id)" title="Delete"><span class="mi">delete</span></button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-else-if="loading" class="empty-msg"><div class="spinner"></div> Loading files...</div>
        <div v-else class="empty-msg">
          <span class="mi" style="font-size:48px;color:var(--text-muted)">folder_open</span>
          <p>No files yet. Upload one to get started!</p>
        </div>
      </section>
    </main>

    <!-- RIGHT PANEL -->
    <aside class="right-panel">
      <!-- Storage Usage -->
      <div class="storage-card">
        <h3>Storage usage</h3>
        <div class="donut-wrap">
          <svg viewBox="0 0 120 120" class="donut-svg">
            <circle cx="60" cy="60" r="50" fill="none" stroke="#f0ecff" stroke-width="12" />
            <circle cx="60" cy="60" r="50" fill="none" stroke="var(--primary)" stroke-width="12"
              stroke-linecap="round"
              :stroke-dasharray="`${auth.storagePercent * 3.14} 314`"
              transform="rotate(-90 60 60)" />
          </svg>
          <div class="donut-center">
            <span class="donut-pct">{{ Math.round(auth.storagePercent) }}%</span>
            <span class="donut-sub">{{ formatBytes(auth.user?.storage_used || 0) }} of {{ formatBytes(auth.storageLimitBytes) }}</span>
          </div>
        </div>

        <ul class="storage-breakdown">
          <li v-for="cat in storageBreakdown" :key="cat.name">
            <span class="cat-dot" :class="cat.cls"></span>
            <span class="cat-name">{{ cat.name }}</span>
            <span class="cat-size">{{ formatBytes(cat.size) }}</span>
          </li>
        </ul>
      </div>

      <!-- Upgrade Card -->
      <div class="upgrade-card" v-if="auth.user?.plan_name !== 'pro'">
        <h4>Upgrade to Pro</h4>
        <p>Get unlimited storage, advanced analytics and 24/7 support.</p>
        <button class="btn-upgrade">Upgrade Now</button>
      </div>
    </aside>

    <!-- Upload Progress Toast -->
    <transition name="fade">
      <div v-if="uploadProgress > 0" class="upload-toast">
        <span class="mi">cloud_upload</span>
        <div class="toast-info">
          <span>Uploading... {{ uploadProgress }}%</span>
          <div class="toast-bar"><div class="toast-fill" :style="{width: uploadProgress+'%'}"></div></div>
        </div>
      </div>
    </transition>

    <!-- Share Modal -->
    <transition name="fade">
      <div v-if="shareModal.show" class="modal-bg" @click.self="shareModal.show = false">
        <div class="modal-card">
          <div class="modal-top">
            <h3>Share link created</h3>
            <button class="close-x" @click="shareModal.show = false"><span class="mi">close</span></button>
          </div>
          <p class="text-muted" style="margin-bottom:16px">Anyone with this link can view the file.</p>
          <div class="share-row">
            <input type="text" :value="shareModal.url" readonly />
            <button class="btn-copy" @click="copyShareLink">{{ copied ? 'Copied!' : 'Copy' }}</button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { filesApi, sharesApi } from '@/api'

const auth = useAuthStore()
const router = useRouter()

const files = ref([])
const loading = ref(true)
const uploadProgress = ref(0)
const fileInput = ref(null)
const searchQuery = ref('')
const copied = ref(false)
const shareModal = ref({ show: false, url: '' })

// --- API CALLS (REAL, NO MOCK) ---
onMounted(async () => {
  if (auth.isLoggedIn) await auth.fetchUser()
  try {
    const res = await filesApi.list()
    files.value = res.data.files || res.data || []
  } catch (err) {
    console.error('Failed to load files:', err)
  } finally {
    loading.value = false
  }
})

function triggerFileInput() { fileInput.value?.click() }

async function handleFileSelect(e) {
  const selected = Array.from(e.target.files)
  if (!selected.length) return
  uploadProgress.value = 1
  for (const file of selected) {
    const formData = new FormData()
    formData.append('file', file)
    try {
      const res = await filesApi.upload(formData, (ev) => {
        uploadProgress.value = Math.round((ev.loaded * 100) / ev.total)
      })
      files.value.unshift(res.data)
      auth.fetchUser()
    } catch (err) {
      console.error('Upload error:', err)
      alert(err.response?.data?.detail || 'Upload failed')
    }
  }
  uploadProgress.value = 0
  e.target.value = ''
}

async function shareFile(file) {
  try {
    const res = await sharesApi.create(file.id || file.file_id)
    shareModal.value = { show: true, url: res.data.share_url || `${window.location.origin}/share/${res.data.token}` }
  } catch (err) {
    console.error('Share error:', err)
    alert('Failed to create share link')
  }
}

function copyShareLink() {
  navigator.clipboard.writeText(shareModal.value.url)
  copied.value = true
  setTimeout(() => (copied.value = false), 2000)
}

async function deleteFile(id) {
  if (!confirm('Delete this file?')) return
  try {
    await filesApi.delete(id)
    files.value = files.value.filter(f => (f.id || f.file_id) !== id)
    auth.fetchUser()
  } catch (err) {
    console.error('Delete error:', err)
    alert('Failed to delete file')
  }
}

async function downloadFile(id, filename) {
  try {
    const res = await filesApi.download(id)
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  } catch (err) {
    console.error('Download error:', err)
    alert('Failed to download')
  }
}

function logout() { auth.logout(); router.push('/login') }

// --- COMPUTED ---
const filteredFiles = computed(() => {
  if (!searchQuery.value) return files.value
  return files.value.filter(f => f.filename.toLowerCase().includes(searchQuery.value.toLowerCase()))
})
const topRecentFiles = computed(() => [...files.value].slice(0, 3))

function getCategory(mimetype) {
  if (!mimetype) return 'other'
  if (mimetype.includes('image')) return 'img'
  if (mimetype.includes('video')) return 'video'
  if (mimetype.includes('audio')) return 'audio'
  return 'doc'
}
function getCategoryClass(m) { return 'cat-' + getCategory(m) }
function getCategoryIcon(m) {
  const c = getCategory(m)
  return { doc: 'description', img: 'image', video: 'videocam', audio: 'audiotrack', other: 'insert_drive_file' }[c]
}

const storageBreakdown = computed(() => {
  const cats = ['doc', 'img', 'video', 'audio', 'other']
  const names = { doc: 'Documents', img: 'Images', video: 'Videos', audio: 'Audios', other: 'Other' }
  return cats.map(c => ({
    name: names[c],
    cls: 'dot-' + c,
    size: files.value.filter(f => getCategory(f.mimetype) === c).reduce((a, f) => a + f.size, 0),
  })).filter(c => c.size > 0)
})

const chartCategories = computed(() => {
  const cats = ['doc', 'img', 'video', 'audio', 'other']
  const names = { doc: 'Docs', img: 'Imgs', video: 'Vids', audio: 'Audio', other: 'Other' }
  const total = files.value.reduce((a, f) => a + f.size, 0)
  if (!total) return []
  return cats.map(c => {
    const size = files.value.filter(f => getCategory(f.mimetype) === c).reduce((a, f) => a + f.size, 0)
    return { name: names[c], cls: 'bar-' + c, percent: Math.max((size / total) * 100, 2) }
  }).filter(c => c.percent > 2)
})

function formatBytes(b) {
  if (!b) return '0 B'
  if (b >= 1024 ** 3) return (b / 1024 ** 3).toFixed(1) + ' GB'
  if (b >= 1024 ** 2) return (b / 1024 ** 2).toFixed(1) + ' MB'
  if (b >= 1024) return (b / 1024).toFixed(1) + ' KB'
  return b + ' B'
}
function formatDate(d) { return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) }
function formatRelative(d) {
  const diff = Date.now() - new Date(d).getTime()
  const min = Math.floor(diff / 60000)
  if (min < 1) return 'just now'
  if (min < 60) return min + 'm ago'
  const hr = Math.floor(min / 60)
  if (hr < 24) return hr + 'h ago'
  return Math.floor(hr / 24) + 'd ago'
}
</script>

<style scoped>
/* ========= LAYOUT ========= */
.dv-app {
  display: flex;
  min-height: 100vh;
  background: var(--bg);
}

/* ========= SIDEBAR ========= */
.sidebar {
  width: 240px;
  background: var(--surface);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 24px 16px;
  position: sticky;
  top: 0;
  height: 100vh;
}
.brand { display: flex; align-items: center; gap: 10px; margin-bottom: 32px; padding: 0 8px; }
.brand-icon {
  width: 36px; height: 36px; border-radius: 10px;
  background: var(--primary); color: #fff;
  display: flex; align-items: center; justify-content: center;
}
.brand-name { font-size: 1.15rem; font-weight: 700; }

.nav-item {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 12px; border-radius: var(--radius-sm);
  font-size: 0.9rem; font-weight: 500; color: var(--text-secondary);
  transition: all 0.15s; cursor: pointer;
}
.nav-item:hover { background: var(--hover); color: var(--text); }
.nav-item.active { background: var(--primary-light); color: var(--primary); font-weight: 600; }

.sidebar-top .nav-menu { display: flex; flex-direction: column; gap: 2px; }
.sidebar-bottom { display: flex; flex-direction: column; gap: 2px; padding-top: 16px; border-top: 1px solid var(--border); }

.user-block { display: flex; align-items: center; gap: 10px; margin-top: 16px; padding: 8px; }
.user-avatar {
  width: 32px; height: 32px; border-radius: 50%;
  background: linear-gradient(135deg, var(--primary), #a855f7);
  color: #fff; font-weight: 700; font-size: 0.85rem;
  display: flex; align-items: center; justify-content: center;
}
.user-meta { display: flex; flex-direction: column; overflow: hidden; }
.user-name { font-size: 0.8rem; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.logout-btn { background: none; border: none; font-size: 0.7rem; color: var(--text-muted); text-align: left; padding: 0; }
.logout-btn:hover { color: var(--danger); text-decoration: underline; }

/* ========= MAIN ========= */
.main { flex: 1; padding: 24px 32px; overflow-y: auto; }

.search-bar {
  display: flex; align-items: center; gap: 12px;
  background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius);
  padding: 10px 16px; margin-bottom: 28px; box-shadow: var(--shadow);
}
.search-icon { color: var(--text-muted); }
.search-bar input { flex: 1; border: none; outline: none; font-size: 0.95rem; background: transparent; color: var(--text); }
.btn-upload {
  display: flex; align-items: center; gap: 6px;
  background: var(--primary); color: #fff; border: none;
  padding: 8px 18px; border-radius: var(--radius-sm); font-weight: 600; font-size: 0.85rem;
  white-space: nowrap; transition: background 0.15s;
}
.btn-upload:hover { background: var(--primary-dark); }

.section { margin-bottom: 28px; }
.section-title { font-size: 1rem; font-weight: 600; margin-bottom: 16px; }
.text-muted { color: var(--text-muted); font-size: 0.85rem; }

/* Recently Modified Cards */
.recent-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.recent-card {
  background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 16px;
  cursor: pointer; transition: all 0.2s; display: flex; flex-direction: column; gap: 12px;
}
.recent-card:hover { border-color: var(--primary); box-shadow: var(--shadow-md); transform: translateY(-2px); }
.recent-preview {
  height: 80px; border-radius: var(--radius-sm);
  display: flex; align-items: center; justify-content: center;
}
.cat-doc { background: #ede8ff; color: var(--color-doc); }
.cat-img { background: #fff3e6; color: var(--color-img); }
.cat-video { background: #f3e8ff; color: var(--color-video); }
.cat-audio { background: #e8f0ff; color: var(--color-audio); }
.cat-other { background: #f1f5f9; color: var(--color-other); }

.recent-name { font-size: 0.9rem; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.recent-meta { font-size: 0.78rem; color: var(--text-muted); }
.empty-card { align-items: center; justify-content: center; border-style: dashed; }

/* Chart */
.chart-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.chart-label { font-size: 0.8rem; color: var(--text-muted); background: var(--bg); padding: 4px 12px; border-radius: 99px; }
.chart-bars {
  display: flex; gap: 20px; align-items: flex-end; height: 140px;
  background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 20px;
}
.chart-col { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 8px; height: 100%; }
.bar-track { width: 100%; flex: 1; background: var(--bg); border-radius: 6px; display: flex; align-items: flex-end; }
.bar-fill { width: 100%; border-radius: 6px; transition: height 0.5s ease; }
.bar-doc { background: var(--color-doc); }
.bar-img { background: var(--color-img); }
.bar-video { background: var(--color-video); }
.bar-audio { background: var(--color-audio); }
.bar-other { background: var(--color-other); }
.bar-label { font-size: 0.75rem; color: var(--text-muted); }

/* File Table */
.table-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.view-all { font-size: 0.85rem; color: var(--primary); font-weight: 500; cursor: pointer; }

.file-table {
  width: 100%; border-collapse: collapse;
  background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden;
}
.file-table th {
  text-align: left; padding: 12px 16px;
  font-size: 0.75rem; font-weight: 600; color: var(--text-muted); letter-spacing: 0.04em;
  border-bottom: 1px solid var(--border);
}
.file-table td { padding: 14px 16px; border-bottom: 1px solid var(--border); font-size: 0.9rem; vertical-align: middle; }
.file-table tbody tr:last-child td { border-bottom: none; }
.file-row { cursor: pointer; transition: background 0.1s; }
.file-row:hover { background: var(--hover); }

.file-icon {
  width: 32px; height: 32px; border-radius: 6px;
  display: flex; align-items: center; justify-content: center;
}
.fname { font-weight: 500; }

.row-actions { display: flex; gap: 4px; opacity: 0; transition: opacity 0.15s; }
.file-row:hover .row-actions { opacity: 1; }
.icon-btn { background: none; border: none; padding: 4px; border-radius: 4px; color: var(--text-muted); }
.icon-btn:hover { background: var(--bg); color: var(--text); }
.icon-btn.danger:hover { color: var(--danger); background: #fef2f2; }

.empty-msg { padding: 48px; text-align: center; color: var(--text-muted); display: flex; flex-direction: column; align-items: center; gap: 12px; }
.spinner {
  width: 24px; height: 24px; border: 3px solid var(--border);
  border-top-color: var(--primary); border-radius: 50%; animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ========= RIGHT PANEL ========= */
.right-panel {
  width: 280px; background: var(--surface); border-left: 1px solid var(--border);
  padding: 24px; display: flex; flex-direction: column; gap: 20px;
  position: sticky; top: 0; height: 100vh;
}

.storage-card h3 { font-size: 1rem; font-weight: 600; margin-bottom: 20px; }

.donut-wrap { position: relative; width: 160px; height: 160px; margin: 0 auto 24px; }
.donut-svg { width: 100%; height: 100%; }
.donut-center {
  position: absolute; inset: 0;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
}
.donut-pct { font-size: 1.75rem; font-weight: 700; color: var(--primary); }
.donut-sub { font-size: 0.7rem; color: var(--text-muted); margin-top: 2px; }

.storage-breakdown { display: flex; flex-direction: column; gap: 14px; }
.storage-breakdown li { display: flex; align-items: center; gap: 10px; font-size: 0.85rem; }
.cat-dot { width: 8px; height: 8px; border-radius: 50%; }
.dot-doc { background: var(--color-doc); }
.dot-img { background: var(--color-img); }
.dot-video { background: var(--color-video); }
.dot-audio { background: var(--color-audio); }
.dot-other { background: var(--color-other); }
.cat-name { flex: 1; font-weight: 500; }
.cat-size { color: var(--text-muted); }

/* Upgrade */
.upgrade-card {
  background: linear-gradient(135deg, #1e1b4b, #312e81);
  color: #fff; padding: 24px; border-radius: var(--radius-lg); text-align: center; margin-top: auto;
}
.upgrade-card h4 { font-size: 1rem; margin-bottom: 8px; }
.upgrade-card p { font-size: 0.8rem; opacity: 0.8; margin-bottom: 16px; line-height: 1.5; }
.btn-upgrade {
  background: #fff; color: var(--primary); border: none; padding: 10px 24px;
  border-radius: var(--radius-sm); font-weight: 600; font-size: 0.85rem; cursor: pointer;
  transition: transform 0.15s;
}
.btn-upgrade:hover { transform: scale(1.03); }

/* ========= TOAST ========= */
.upload-toast {
  position: fixed; bottom: 24px; right: 24px;
  background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius);
  padding: 16px 20px; box-shadow: var(--shadow-md); display: flex; align-items: center; gap: 12px;
  z-index: 1000; min-width: 280px;
}
.toast-info { flex: 1; font-size: 0.85rem; }
.toast-bar { height: 4px; background: var(--bg); border-radius: 99px; margin-top: 8px; }
.toast-fill { height: 100%; background: var(--primary); border-radius: 99px; transition: width 0.3s; }

/* ========= MODAL ========= */
.modal-bg {
  position: fixed; inset: 0; background: rgba(0,0,0,0.35); backdrop-filter: blur(2px);
  display: flex; align-items: center; justify-content: center; z-index: 2000;
}
.modal-card {
  background: var(--surface); border-radius: var(--radius-lg); padding: 32px;
  width: 420px; box-shadow: 0 20px 60px rgba(0,0,0,0.15);
}
.modal-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.modal-top h3 { font-size: 1.1rem; }
.close-x { background: none; border: none; color: var(--text-muted); }
.share-row { display: flex; gap: 8px; }
.share-row input { flex: 1; padding: 10px 14px; border: 1px solid var(--border); border-radius: var(--radius-sm); background: var(--bg); outline: none; font-size: 0.85rem; }
.btn-copy {
  background: var(--primary); color: #fff; border: none; padding: 10px 18px;
  border-radius: var(--radius-sm); font-weight: 600; font-size: 0.85rem;
}

/* ========= RESPONSIVE ========= */
@media (max-width: 1100px) { .right-panel { display: none; } }
@media (max-width: 768px) {
  .sidebar { display: none; }
  .main { padding: 16px; }
  .recent-grid { grid-template-columns: 1fr; }
}
</style>
