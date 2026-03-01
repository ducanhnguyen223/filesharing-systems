<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-50 via-slate-50 to-purple-50 p-6 font-display">
    
    <!-- Loading State -->
    <div v-if="loading" class="w-full max-w-md bg-white rounded-2xl p-12 shadow-xl shadow-primary/5 text-center flex flex-col items-center gap-4">
      <div class="w-10 h-10 border-4 border-slate-100 border-t-primary rounded-full animate-spin"></div>
      <p class="text-slate-500 font-medium">Retrieving shared file...</p>
    </div>

    <!-- Success State -->
    <div v-else-if="fileData" class="w-full max-w-md bg-white rounded-2xl p-10 shadow-xl shadow-primary/5 text-center relative overflow-hidden group">
      
      <!-- Decorative BG -->
      <div class="absolute -top-10 -right-10 w-32 h-32 bg-primary/5 rounded-full blur-2xl group-hover:bg-primary/10 transition-colors duration-500"></div>

      <div class="relative z-10 mb-8">
        <div class="flex items-center justify-center gap-3 mb-3">
          <div class="w-10 h-10 rounded-xl bg-primary text-white flex items-center justify-center">
            <span class="material-symbols-outlined text-xl">cloud</span>
          </div>
          <span class="text-xl font-bold tracking-tight text-slate-800">DocuVault</span>
        </div>
        <p class="text-slate-500 text-sm font-medium">A file has been shared with you</p>
      </div>

      <div class="relative z-10 flex flex-col items-center mb-8">
        <div class="w-24 h-24 rounded-2xl bg-indigo-50 flex items-center justify-center mb-5 text-primary shadow-inner">
          <span class="material-symbols-outlined text-[48px]">{{ getFileIcon(fileData.filename) }}</span>
        </div>
        <h1 class="text-xl font-bold text-slate-900 mb-1 w-full truncate px-4" :title="fileData.filename">{{ fileData.filename }}</h1>
        <p class="text-slate-400 text-sm">{{ formatBytes(fileData.size) }} • Shared via link</p>
      </div>

      <div class="relative z-10">
        <button @click="handleDownload" :disabled="downloading" class="w-full bg-primary hover:bg-indigo-600 text-white font-bold py-3.5 px-6 rounded-xl transition-all flex items-center justify-center gap-2 disabled:opacity-70 disabled:cursor-wait shadow-md shadow-primary/20 hover:shadow-lg hover:shadow-primary/30 active:scale-[0.98]">
          <span v-if="downloading" class="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
          <template v-else>
            <span class="material-symbols-outlined text-lg">download</span>
            <span>Download File</span>
          </template>
        </button>
      </div>

      <p class="relative z-10 mt-8 text-xs text-slate-400 font-medium">
        Want your own secure cloud? 
        <RouterLink to="/register" class="text-primary hover:text-indigo-600 hover:underline font-bold transition-colors">Sign up free →</RouterLink>
      </p>
    </div>

    <!-- Error State -->
    <div v-else class="w-full max-w-md bg-white rounded-2xl p-10 shadow-xl shadow-primary/5 text-center flex flex-col items-center gap-4">
      <div class="w-20 h-20 rounded-2xl bg-red-50 text-red-400 flex items-center justify-center mb-2">
        <span class="material-symbols-outlined text-[48px]">link_off</span>
      </div>
      <h2 class="text-xl font-bold text-slate-900">Link Not Found</h2>
      <p class="text-slate-500 text-sm mb-4 leading-relaxed">This share link is invalid, has expired, or the file was deleted by the owner.</p>
      <RouterLink to="/" class="bg-slate-50 hover:bg-slate-100 text-slate-700 font-bold py-2.5 px-6 rounded-xl transition-colors border border-slate-200">
        Go to DocuVault
      </RouterLink>
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
    alert('Failed to download file securely')
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
