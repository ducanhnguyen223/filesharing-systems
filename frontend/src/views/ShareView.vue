<template>
  <div class="share-page">
    <div class="share-card" v-if="loading">
      <div class="loading-state"><div class="spinner"></div><p>Retrieving shared file...</p></div>
    </div>

    <div class="share-card" v-else-if="fileData">
      <div class="share-top">
        <div class="brand"><div class="brand-icon"><span class="mi">cloud</span></div><span class="brand-text">DocuVault</span></div>
        <p class="notice">A file has been shared with you</p>
      </div>
      <div class="file-preview"><span class="mi" style="font-size:48px">{{ getFileIcon(fileData.filename) }}</span></div>
      <h1 class="fname" :title="fileData.filename">{{ fileData.filename }}</h1>
      <p class="fmeta">{{ formatBytes(fileData.size) }} · Shared via link</p>
      <button class="btn-dl" @click="handleDownload" :disabled="downloading">
        <span v-if="downloading" class="spinner-sm"></span>
        <span v-else><span class="mi">download</span> Download File</span>
      </button>
      <p class="share-footer">Want your own cloud? <RouterLink to="/register" class="link">Sign up free →</RouterLink></p>
    </div>

    <div class="share-card" v-else>
      <div class="error-state">
        <span class="mi" style="font-size:48px;color:var(--text-muted,#9ca3af)">link_off</span>
        <h2>Link Not Found</h2>
        <p>This share link is invalid or has expired.</p>
        <RouterLink to="/" class="btn-home">Go to DocuVault</RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { sharesApi, filesApi } from '@/api'

const route = useRoute()
const fileData = ref(null)
const loading = ref(true)
const downloading = ref(false)

onMounted(async () => {
  const token = route.params.token
  if (!token) { loading.value = false; return }
  try {
    const res = await sharesApi.get(token)
    fileData.value = res.data
  } catch (err) {
    console.error('Failed to get share info:', err)
    fileData.value = null
  } finally {
    loading.value = false
  }
})

async function handleDownload() {
  if (!fileData.value) return
  downloading.value = true
  try {
    const fileId = fileData.value.file_id || fileData.value.id
    const res = await filesApi.download(fileId)
    window.open(res.data.url, '_blank')
  } catch (err) {
    console.error('Download error:', err)
    alert('Failed to download')
  } finally {
    downloading.value = false
  }
}

function getFileIcon(filename) {
  if (!filename) return 'insert_drive_file'
  const ext = filename.split('.').pop()?.toLowerCase()
  const m = { pdf:'picture_as_pdf', doc:'description', docx:'description', txt:'article',
    jpg:'image', jpeg:'image', png:'image', gif:'image', svg:'image',
    mp4:'videocam', avi:'videocam', mov:'videocam',
    mp3:'audiotrack', wav:'audiotrack',
    zip:'folder_zip', rar:'folder_zip', tar:'folder_zip',
    xls:'table_chart', xlsx:'table_chart', csv:'table_chart',
    ppt:'slideshow', pptx:'slideshow' }
  return m[ext] || 'insert_drive_file'
}

function formatBytes(b) {
  if (!b) return '0 B'
  if (b >= 1024**3) return (b/1024**3).toFixed(1)+' GB'
  if (b >= 1024**2) return (b/1024**2).toFixed(1)+' MB'
  if (b >= 1024) return (b/1024).toFixed(1)+' KB'
  return b+' B'
}
</script>

<style scoped>
.share-page { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #f0ecff, #f5f5f7, #fdf2f8); padding: 32px; }
.share-card { width: 100%; max-width: 460px; background: #fff; border-radius: 20px; padding: 48px; box-shadow: 0 8px 30px rgba(0,0,0,0.06); text-align: center; }

.share-top { margin-bottom: 28px; }
.brand { display: flex; align-items: center; justify-content: center; gap: 8px; margin-bottom: 12px; }
.brand-icon { width: 36px; height: 36px; border-radius: 10px; background: #6c47ff; color: #fff; display: flex; align-items: center; justify-content: center; }
.brand-text { font-size: 1.15rem; font-weight: 700; }
.notice { color: #6b7280; font-size: 0.9rem; }

.file-preview { width: 88px; height: 88px; border-radius: 16px; background: #f0ecff; display: flex; align-items: center; justify-content: center; margin: 0 auto 20px; color: #6c47ff; }
.fname { font-size: 1.2rem; font-weight: 700; margin-bottom: 6px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.fmeta { color: #9ca3af; font-size: 0.9rem; margin-bottom: 28px; }

.btn-dl { width: 100%; padding: 14px; background: #6c47ff; color: #fff; border: none; border-radius: 12px; font-size: 0.95rem; font-weight: 600; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; gap: 8px; transition: all 0.2s; }
.btn-dl:hover { background: #5835db; transform: translateY(-1px); box-shadow: 0 4px 12px rgba(108,71,255,0.3); }
.btn-dl:disabled { opacity: 0.6; cursor: wait; }

.share-footer { margin-top: 28px; font-size: 0.82rem; color: #9ca3af; }
.link { color: #6c47ff; font-weight: 600; text-decoration: none; }
.link:hover { text-decoration: underline; }

.error-state { padding: 16px 0; display: flex; flex-direction: column; align-items: center; gap: 12px; }
.error-state h2 { font-size: 1.3rem; font-weight: 700; }
.error-state p { color: #6b7280; margin-bottom: 12px; }
.btn-home { padding: 10px 24px; background: #f0ecff; color: #6c47ff; border-radius: 10px; font-weight: 600; display: inline-block; transition: background 0.2s; }
.btn-home:hover { background: #e2dcff; }

.loading-state { padding: 32px 0; display: flex; flex-direction: column; align-items: center; gap: 16px; color: #6b7280; }
.spinner { width: 28px; height: 28px; border: 3px solid #e8e8ee; border-top-color: #6c47ff; border-radius: 50%; animation: spin 0.7s linear infinite; }
.spinner-sm { width: 18px; height: 18px; border: 2px solid rgba(255,255,255,0.3); border-top-color: #fff; border-radius: 50%; animation: spin 0.6s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
