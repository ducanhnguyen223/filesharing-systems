<template>
<div class="relative flex min-h-screen flex-col lg:flex-row overflow-hidden bg-background-light dark:bg-background-dark font-display text-slate-900 dark:text-slate-100">
  
  <!-- Left Sidebar (Drawer Style for Mobile/Fixed for Desktop) -->
  <aside class="hidden lg:flex w-64 flex-col bg-white dark:bg-slate-900 border-r border-primary/10 p-4 shrink-0 z-10">
    <div class="flex items-center gap-3 px-2 mb-8">
      <div class="bg-primary/10 p-2 rounded-lg text-primary">
        <span class="material-symbols-outlined text-3xl">shield_person</span>
      </div>
      <h2 class="text-xl font-bold tracking-tight">DocuVault</h2>
    </div>
    
    <nav class="flex-1 space-y-1">
      <a @click="setCategory('')" :class="activeCategory === '' ? 'bg-primary/10 text-primary font-semibold' : 'text-slate-600 dark:text-slate-400 hover:bg-primary/5 cursor-pointer'" class="flex items-center justify-between px-3 py-2 rounded-lg transition-colors cursor-pointer">
        <div class="flex items-center gap-3"><span class="material-symbols-outlined">dashboard</span> Dashboard</div>
        <span v-if="totalFilesCount" class="bg-slate-200 dark:bg-slate-700 text-xs px-2 py-0.5 rounded-full font-medium">{{ totalFilesCount }}</span>
      </a>
      <a @click="setCategory('document')" :class="activeCategory === 'document' ? 'bg-primary/10 text-primary font-semibold' : 'text-slate-600 dark:text-slate-400 hover:bg-primary/5 cursor-pointer'" class="flex items-center justify-between px-3 py-2 rounded-lg transition-colors cursor-pointer">
        <div class="flex items-center gap-3"><span class="material-symbols-outlined">description</span> Documents</div>
        <span v-if="categoryCounts.document" class="bg-slate-200 dark:bg-slate-700 text-xs px-2 py-0.5 rounded-full font-medium">{{ categoryCounts.document }}</span>
      </a>
      <a @click="setCategory('image')" :class="activeCategory === 'image' ? 'bg-primary/10 text-primary font-semibold' : 'text-slate-600 dark:text-slate-400 hover:bg-primary/5 cursor-pointer'" class="flex items-center justify-between px-3 py-2 rounded-lg transition-colors cursor-pointer">
        <div class="flex items-center gap-3"><span class="material-symbols-outlined">image</span> Images</div>
        <span v-if="categoryCounts.image" class="bg-slate-200 dark:bg-slate-700 text-xs px-2 py-0.5 rounded-full font-medium">{{ categoryCounts.image }}</span>
      </a>
      <a @click="setCategory('video')" :class="activeCategory === 'video' ? 'bg-primary/10 text-primary font-semibold' : 'text-slate-600 dark:text-slate-400 hover:bg-primary/5 cursor-pointer'" class="flex items-center justify-between px-3 py-2 rounded-lg transition-colors cursor-pointer">
        <div class="flex items-center gap-3"><span class="material-symbols-outlined">videocam</span> Videos</div>
        <span v-if="categoryCounts.video" class="bg-slate-200 dark:bg-slate-700 text-xs px-2 py-0.5 rounded-full font-medium">{{ categoryCounts.video }}</span>
      </a>
      <a @click="setCategory('audio')" :class="activeCategory === 'audio' ? 'bg-primary/10 text-primary font-semibold' : 'text-slate-600 dark:text-slate-400 hover:bg-primary/5 cursor-pointer'" class="flex items-center justify-between px-3 py-2 rounded-lg transition-colors cursor-pointer">
        <div class="flex items-center gap-3"><span class="material-symbols-outlined">audiotrack</span> Audios</div>
        <span v-if="categoryCounts.audio" class="bg-slate-200 dark:bg-slate-700 text-xs px-2 py-0.5 rounded-full font-medium">{{ categoryCounts.audio }}</span>
      </a>
      <a @click="setCategory('other')" :class="activeCategory === 'other' ? 'bg-primary/10 text-primary font-semibold' : 'text-slate-600 dark:text-slate-400 hover:bg-primary/5 cursor-pointer'" class="flex items-center justify-between px-3 py-2 rounded-lg transition-colors cursor-pointer">
        <div class="flex items-center gap-3"><span class="material-symbols-outlined">insert_drive_file</span> Others</div>
        <span v-if="categoryCounts.other" class="bg-slate-200 dark:bg-slate-700 text-xs px-2 py-0.5 rounded-full font-medium">{{ categoryCounts.other }}</span>
      </a>
    </nav>
    
    <div class="mt-auto border-t border-slate-100 dark:border-slate-800 pt-4 space-y-1 flex flex-col">
      <a class="flex items-center gap-3 px-3 py-2 text-slate-600 dark:text-slate-400 hover:bg-primary/5 rounded-lg transition-colors cursor-pointer">
        <span class="material-symbols-outlined">settings</span> Settings
      </a>
      <a class="flex items-center gap-3 px-3 py-2 text-slate-600 dark:text-slate-400 hover:bg-primary/5 rounded-lg transition-colors cursor-pointer">
        <span class="material-symbols-outlined">chat_bubble</span> Chat & Support
      </a>
      <a class="flex items-center gap-3 px-3 py-2 text-slate-600 dark:text-slate-400 hover:bg-primary/5 rounded-lg transition-colors cursor-pointer">
        <span class="material-symbols-outlined">help</span> Help Center
      </a>
      <a @click="logout" class="flex items-center gap-3 px-3 py-2 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/10 rounded-lg transition-colors cursor-pointer mt-2 font-medium">
        <span class="material-symbols-outlined">logout</span> Sign out
      </a>
    </div>
  </aside>

  <!-- Main Middle Content -->
  <main class="flex-1 flex flex-col min-w-0 bg-background-light dark:bg-background-dark">
    <!-- Header/Search -->
    <header class="p-4 md:p-6 bg-white dark:bg-slate-900 border-b border-primary/5 flex items-center justify-between">
      <div class="flex-1 max-w-4xl mx-auto flex items-center gap-4">
        <label class="flex-1 relative">
          <span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">search</span>
          <input v-model="searchQuery" class="w-full bg-slate-100 dark:bg-slate-800 border-none rounded-xl pl-10 pr-4 py-2.5 focus:ring-2 focus:ring-primary/20 transition-all text-sm outline-none" placeholder="Search files..." type="text"/>
        </label>
        
        <button @click="triggerFileInput" class="hidden sm:flex items-center gap-2 bg-primary hover:bg-indigo-600 text-white font-semibold py-2.5 px-5 rounded-xl transition-colors shadow-sm cursor-pointer whitespace-nowrap">
            <span class="material-symbols-outlined text-lg">cloud_upload</span>
            <span class="text-sm">Upload file</span>
        </button>
        <input type="file" ref="fileInput" @change="handleFileSelect" multiple hidden />
        
        <button class="p-2.5 bg-slate-100 dark:bg-slate-800 rounded-xl lg:hidden">
          <span class="material-symbols-outlined text-slate-600 dark:text-slate-300">menu</span>
        </button>
      </div>
    </header>

    <div class="p-4 md:p-6 space-y-8 overflow-y-auto max-h-[calc(100vh-80px)] no-scrollbar">
        
      <!-- Upload Progress -->
      <transition name="fade">
        <div v-if="uploadProgress > 0" class="bg-white p-4 rounded-xl border border-primary/10 shadow-sm flex items-center gap-4 sticky top-4 z-50 mb-6">
          <span class="material-symbols-outlined text-primary motion-safe:animate-pulse">cloud_upload</span>
          <div class="flex-1 min-w-0">
            <div class="flex justify-between text-xs font-semibold mb-1">
              <span class="text-slate-700">Uploading...</span>
              <span class="text-primary">{{ uploadProgress }}%</span>
            </div>
            <div class="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
              <div class="h-full bg-primary rounded-full transition-all duration-300" :style="{width: uploadProgress+'%'}"></div>
            </div>
          </div>
        </div>
      </transition>

      <!-- Recently Modified Section (Removed) -->

      <!-- Distribution Chart Section -->
      <section v-if="!loading && chartCategories.length > 0" class="bg-white dark:bg-slate-900 p-6 rounded-xl border border-primary/5 shadow-sm">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-lg font-bold">File distribution</h2>
          <select class="text-xs bg-slate-100 dark:bg-slate-800 border-none rounded-lg focus:ring-0 outline-none px-3 py-1.5 font-medium cursor-pointer">
            <option>This Week</option>
            <option>This Month</option>
          </select>
        </div>
        <div class="flex items-end justify-between h-48 gap-2 pt-4">
          <div v-for="cat in chartCategories" :key="cat.name" class="w-full flex flex-col items-center gap-2 group justify-end h-full">
            <div class="w-full rounded-t-lg transition-all" :class="[cat.bgClass]" :style="{height: Math.max(10, cat.percent) + '%'}"></div>
            <span class="text-[10px] text-slate-400 font-medium whitespace-nowrap">{{ cat.name }}</span>
          </div>
        </div>
      </section>

      <!-- Data Table Section -->
      <section class="bg-white dark:bg-slate-900 rounded-xl border border-primary/5 shadow-sm overflow-hidden flex flex-col">
        <div class="p-4 border-b border-primary/5 bg-white dark:bg-slate-900 z-10 sticky top-0 flex flex-col gap-4">
          <div class="flex justify-between items-center">
            <h2 class="text-lg font-bold">{{ activeCategory ? activeCategory.charAt(0).toUpperCase() + activeCategory.slice(1) : 'All' }} files</h2>
            <div class="flex bg-slate-100 dark:bg-slate-800 p-1 rounded-lg">
              <button @click="viewMode = 'list'" :class="viewMode === 'list' ? 'bg-white dark:bg-slate-700 shadow pointer-events-none text-primary' : 'text-slate-400 hover:text-slate-600 dark:hover:text-slate-300'" class="p-1 rounded flex items-center justify-center transition-all" title="List View"><span class="material-symbols-outlined text-sm">view_list</span></button>
              <button @click="viewMode = 'grid'" :class="viewMode === 'grid' ? 'bg-white dark:bg-slate-700 shadow pointer-events-none text-primary' : 'text-slate-400 hover:text-slate-600 dark:hover:text-slate-300'" class="p-1 rounded flex items-center justify-center transition-all" title="Grid View"><span class="material-symbols-outlined text-sm">grid_view</span></button>
            </div>
          </div>
          
          <!-- Storage Bar -->
          <div v-if="storageBarData && storageBarData.length > 0" class="mb-2">
            <div class="w-full h-2.5 bg-slate-100 dark:bg-slate-800 rounded-full flex overflow-hidden mb-3">
              <div v-for="seg in storageBarData" :key="seg.name" :class="seg.color" :style="{width: seg.percent + '%'}" class="h-full border-r border-white/20 last:border-r-0 transition-all duration-500"></div>
            </div>
            <div class="flex flex-wrap gap-x-4 gap-y-2 text-xs">
              <div v-for="seg in storageBarData" :key="seg.name" class="flex items-center gap-1.5 focus:outline-none">
                <span class="w-2.5 h-2.5 rounded-full" :class="seg.color"></span>
                <span class="font-medium text-slate-700 dark:text-slate-300">{{ seg.name }}</span>
                <span class="text-slate-400">· {{ formatBytes(seg.size) }}</span>
              </div>
            </div>
          </div>
        </div>
        <div v-if="!loading && files.length > 0">
          <!-- List View -->
          <div v-if="viewMode === 'list'" class="overflow-x-auto">
            <table class="w-full text-left text-sm border-collapse">
              <thead>
                <tr class="bg-slate-50 dark:bg-slate-800/50 text-slate-500 font-medium uppercase text-[10px] tracking-wider">
                  <th class="py-3 px-4 w-10 text-center"><input class="rounded border-slate-300 text-primary focus:ring-primary h-4 w-4" type="checkbox"/></th>
                  <th class="py-3 px-4">Name</th>
                  <th class="py-3 px-4 hidden sm:table-cell">Owner</th>
                  <th class="py-3 px-4 hidden md:table-cell">File Size</th>
                  <th class="py-3 px-4">Modified</th>
                  <th class="py-3 px-4"></th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100 dark:divide-slate-800">
                <tr v-for="file in filteredFiles" :key="file.id" @click="downloadFile(file.id, file.filename)" class="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors cursor-pointer group">
                  <td class="py-4 px-4 text-center" @click.stop><input class="rounded border-slate-300 text-primary focus:ring-primary h-4 w-4" type="checkbox"/></td>
                  <td class="py-4 px-4 font-medium">
                    <div class="flex items-center gap-3">
                      <span class="material-symbols-outlined" :class="getIconStyle(file.mimetype).txt">{{ getCategoryIcon(file.mimetype) }}</span>
                      <span class="truncate group-hover:text-primary transition-colors max-w-[200px]">{{ file.filename }}</span>
                    </div>
                  </td>
                  <td class="py-4 px-4 hidden sm:table-cell text-slate-500">Me</td>
                  <td class="py-4 px-4 hidden md:table-cell text-slate-500">{{ formatBytes(file.size) }}</td>
                  <td class="py-4 px-4 text-slate-500 whitespace-nowrap">{{ formatDate(file.created_at) }}</td>
                  <td class="py-4 px-4 text-right" @click.stop>
                    <div class="flex items-center justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button @click="shareFile(file)" class="p-1 hover:bg-slate-200 text-slate-400 hover:text-primary rounded" title="Share"><span class="material-symbols-outlined">share</span></button>
                      <button @click="deleteFile(file.id)" class="p-1 hover:bg-red-50 text-slate-400 hover:text-red-500 rounded" title="Delete"><span class="material-symbols-outlined">delete</span></button>
                      <button class="p-1 hover:bg-slate-200 dark:hover:bg-slate-700 rounded"><span class="material-symbols-outlined text-slate-400">more_vert</span></button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          
          <!-- Grid View -->
          <div v-else-if="viewMode === 'grid'" class="p-4 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
            <div v-for="file in filteredFiles" :key="file.id" @click="downloadFile(file.id, file.filename)" class="bg-white border border-slate-100 dark:bg-slate-800/40 dark:border-slate-800 rounded-xl p-4 cursor-pointer hover:border-primary/30 hover:shadow-md transition-all flex flex-col group relative">
              <div class="h-24 flex items-center justify-center bg-slate-50 dark:bg-slate-900 rounded-lg mb-3 shadow-sm group-hover:bg-slate-100 dark:group-hover:bg-slate-800 transition-colors">
                <span class="material-symbols-outlined text-5xl transition-transform group-hover:scale-110" :class="getIconStyle(file.mimetype).txt">{{ getCategoryIcon(file.mimetype) }}</span>
              </div>
              <div class="truncate text-sm font-semibold group-hover:text-primary transition-colors pb-1" :title="file.filename">{{ file.filename }}</div>
              <div class="flex justify-between items-center mt-auto pt-2 border-t border-slate-50 dark:border-slate-800">
                <div class="text-[11px] text-slate-500">{{ formatBytes(file.size) }}</div>
                <div class="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button @click.stop="shareFile(file)" class="p-1 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-400 hover:text-primary rounded" title="Share"><span class="material-symbols-outlined text-sm">share</span></button>
                  <button @click.stop="deleteFile(file.id)" class="p-1 hover:bg-red-50 dark:hover:bg-red-900/20 text-slate-400 hover:text-red-500 rounded" title="Delete"><span class="material-symbols-outlined text-sm">delete</span></button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-else-if="loading" class="p-16 text-center flex flex-col items-center justify-center gap-4 animate-pulse">
            <div class="w-8 h-8 rounded-full border-2 border-primary border-t-transparent animate-spin"></div>
        </div>
        
        <div v-else class="p-16 text-center flex flex-col items-center justify-center gap-4">
            <div class="w-16 h-16 bg-slate-50 dark:bg-slate-800 rounded-2xl flex items-center justify-center text-slate-300 dark:text-slate-600 mb-2">
                <span class="material-symbols-outlined text-3xl">inbox</span>
            </div>
            <div>
                <h3 class="text-slate-800 dark:text-slate-200 font-bold mb-1">Your vault is empty</h3>
                <p class="text-slate-500 text-sm mb-6">Upload files to securely store them.</p>
            </div>
        </div>
      </section>
    </div>
  </main>

  <!-- Right Column (Storage Sidebar) -->
  <aside class="hidden xl:flex w-80 flex-col bg-white dark:bg-slate-900 border-l border-primary/5 p-6 shrink-0 space-y-8 z-10">
    <div>
      <h2 class="text-lg font-bold mb-6">Storage usage</h2>
      <div class="relative flex items-center justify-center mb-8">
        <!-- Donut Chart -->
        <svg class="w-48 h-48 -rotate-90">
          <circle class="text-slate-100 dark:text-slate-800" cx="96" cy="96" fill="transparent" r="80" stroke="currentColor" stroke-width="12"></circle>
          <circle class="text-primary transition-all duration-1000 ease-out" cx="96" cy="96" fill="transparent" r="80" stroke="currentColor" stroke-dasharray="502.4" :stroke-dashoffset="502.4 - (Math.min(auth.storagePercent, 100) / 100 * 502.4)" stroke-width="12" stroke-linecap="round"></circle>
        </svg>
        <div class="absolute flex flex-col items-center">
          <span class="text-3xl font-bold">{{ Math.round(auth.storagePercent || 0) }}%</span>
          <span class="text-[11px] text-slate-400 font-medium px-2 mt-0.5">{{ formatBytes(auth.user?.storage_used || 0) }} of {{ formatBytes(auth.storageLimitBytes) }}</span>
        </div>
      </div>
      
      <div class="space-y-4">
        <div v-for="cat in storageBreakdown" :key="cat.name" class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-2 h-2 rounded-full" :class="cat.color"></div>
            <span class="text-sm font-medium">{{ cat.name }}</span>
          </div>
          <span class="text-sm text-slate-500">{{ formatBytes(cat.size) }}</span>
        </div>
      </div>
    </div>
    
    <div class="mt-auto bg-slate-900 dark:bg-primary text-white p-6 rounded-2xl relative overflow-hidden group shadow-md">
      <div class="relative z-10">
        <h3 class="font-bold text-lg mb-2">Upgrade to Pro</h3>
        <p class="text-slate-300 dark:text-white/80 text-xs leading-relaxed mb-4">Get unlimited storage, advanced analytics and 24/7 support.</p>
        <button class="w-full bg-white dark:bg-slate-900 text-slate-900 dark:text-white py-2 rounded-lg text-sm font-bold shadow-sm active:scale-95 transition-transform">
            Upgrade Now
        </button>
      </div>
      <!-- Abstract pattern -->
      <div class="absolute -right-8 -bottom-8 w-32 h-32 bg-primary/20 dark:bg-white/10 rounded-full blur-2xl"></div>
      <div class="absolute -left-4 -top-4 w-20 h-20 bg-white/10 rounded-full blur-xl"></div>
    </div>
  </aside>

  <!-- Bottom Mobile Navigation -->
  <div class="lg:hidden fixed bottom-0 left-0 w-full bg-white dark:bg-slate-900 border-t border-slate-100 dark:border-slate-800 flex items-center justify-around py-3 px-2 z-50">
    <a class="flex flex-col items-center gap-1 text-primary cursor-pointer">
      <span class="material-symbols-outlined">home</span>
      <span class="text-[10px] font-medium">Home</span>
    </a>
    <a class="flex flex-col items-center gap-1 text-slate-400 cursor-pointer">
      <span class="material-symbols-outlined">folder</span>
      <span class="text-[10px] font-medium">Files</span>
    </a>
    <a class="flex flex-col items-center gap-1 text-slate-400 cursor-pointer">
      <span class="material-symbols-outlined">group</span>
      <span class="text-[10px] font-medium">Shared</span>
    </a>
    <a class="flex flex-col items-center gap-1 text-slate-400 cursor-pointer">
      <span class="material-symbols-outlined">account_circle</span>
      <span class="text-[10px] font-medium">Profile</span>
    </a>
  </div>

  <!-- Floating Action Button (Mobile) -->
  <button @click="triggerFileInput" class="lg:hidden fixed bottom-20 right-4 w-14 h-14 bg-primary text-white rounded-full shadow-lg shadow-primary/30 flex items-center justify-center z-40 active:scale-95 transition-transform">
      <span class="material-symbols-outlined text-2xl">add</span>
  </button>

  <!-- Share Modal -->
  <transition name="fade">
    <div v-if="shareModal.show" class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center z-[100] p-4" @click.self="shareModal.show = false">
      <div class="bg-white rounded-2xl p-6 w-full max-w-md shadow-2xl animate-scale-in">
        <div class="flex justify-between items-center mb-2">
          <h3 class="text-lg font-bold text-slate-900">Share link created</h3>
          <button @click="shareModal.show = false" class="text-slate-400 hover:text-slate-700 transition-colors p-1 rounded-full border border-transparent hover:border-slate-200"><span class="material-symbols-outlined">close</span></button>
        </div>
        <p class="text-sm text-slate-500 mb-6">Anyone with this link can view and download the file securely.</p>
        <div class="flex gap-2">
          <input type="text" :value="shareModal.url" readonly class="flex-1 bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-700 outline-none focus:border-primary transition-colors" />
          <button @click="copyShareLink" class="bg-primary hover:bg-indigo-600 text-white font-semibold px-4 py-2 rounded-lg text-sm transition-colors whitespace-nowrap">
              {{ copied ? 'Copied!' : 'Copy' }}
          </button>
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

// Category Filter States
const activeCategory = ref('')
const categoryCounts = ref({ document: 0, image: 0, video: 0, audio: 0, other: 0 })
const viewMode = ref('list') // 'list' or 'grid'
const totalFilesCount = ref(0)

const fetchFiles = async () => {
  loading.value = true
  try {
    const res = await filesApi.list(activeCategory.value)
    files.value = res.data.files || res.data || []
    if (res.data.category_counts) {
      categoryCounts.value = { ...categoryCounts.value, ...res.data.category_counts }
      totalFilesCount.value = res.data.total || 0
    } else {
      // Fallback update if API hasn't implemented counts yet
      totalFilesCount.value = files.value.length
    }
  } catch (err) {
    console.error('Failed to load files:', err)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  if (auth.isLoggedIn) await auth.fetchUser()
  await fetchFiles()
})

function setCategory(cat) {
  activeCategory.value = cat
  fetchFiles()
}

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
  if (!confirm('Are you sure you want to delete this file?')) return
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
    window.open(res.data.url, '_blank')
  } catch (err) {
    console.error('Download error:', err)
    alert('Failed to download file securely')
  }
}

function logout() { auth.logout(); router.push('/login') }

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
  if (mimetype.includes('pdf') || mimetype.includes('document') || mimetype.includes('text')) return 'doc'
  if (mimetype.includes('spreadsheet') || mimetype.includes('csv') || mimetype.includes('excel')) return 'sheet'
  return 'other'
}

function getIconStyle(mimetype) {
  const cat = getCategory(mimetype)
  const map = {
    doc: { bg: 'bg-blue-50 text-blue-500', txt: 'text-blue-500' },
    img: { bg: 'bg-orange-50 text-orange-500', txt: 'text-orange-500' },
    video: { bg: 'bg-purple-50 text-purple-500', txt: 'text-purple-500' },
    audio: { bg: 'bg-pink-50 text-pink-500', txt: 'text-pink-500' },
    sheet: { bg: 'bg-green-50 text-green-500', txt: 'text-green-500' },
    other: { bg: 'bg-slate-100 text-slate-500', txt: 'text-slate-500' }
  }
  return map[cat] || map.other
}

function getCategoryIcon(m) {
  const cat = getCategory(m)
  return { doc: 'description', img: 'image', video: 'movie', audio: 'audiotrack', sheet: 'table_view', other: 'article' }[cat]
}

const storageBreakdown = computed(() => {
  const cats = ['doc', 'img', 'video', 'sheet', 'other']
  const names = { doc: 'Documents', img: 'Images', video: 'Videos', sheet: 'Spreadsheets', other: 'Other' }
  const colors = { doc: 'bg-blue-500', img: 'bg-orange-500', video: 'bg-purple-500', sheet: 'bg-green-500', other: 'bg-slate-300' }
  
  return cats.map(c => ({
    name: names[c],
    color: colors[c],
    size: files.value.filter(f => getCategory(f.mimetype) === c).reduce((a, f) => a + f.size, 0)
  })).filter(c => c.size > 0).sort((a,b) => b.size - a.size)
})

const chartCategories = computed(() => {
  const cats = ['doc', 'img', 'video', 'sheet', 'other']
  const names = { doc: 'Mon', img: 'Tue', video: 'Wed', sheet: 'Thu', other: 'Fri' }
  const colors = { doc: 'bg-primary/20 hover:bg-primary/40', img: 'bg-primary/30 hover:bg-primary/40', video: 'bg-primary/40 hover:bg-primary/60', sheet: 'bg-primary/20 hover:bg-primary/40', other: 'bg-primary/20 hover:bg-primary/40' }
  const total = files.value.reduce((a, f) => a + f.size, 0)
  if (!total) return []
  
  return ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((day, ix) => {
    // Generate some deterministic sizes based on current files
    const sz = files.value.reduce((a,f) => a + (f.filename.length % (ix+1)) * f.size, 0)
    return { name: day, bgClass: ['bg-primary/20', 'bg-primary/30', 'bg-primary/50', 'bg-primary/20', 'bg-primary/30', 'bg-primary/20', 'bg-primary/20'][ix], percent: total ? Math.min((sz/(total*3))*100, 100) : 0 }
  })
})

const storageBarData = computed(() => {
  if (files.value.length === 0) return null
  
  const cats = ['doc', 'img', 'video', 'audio', 'other']
  const mapCat = {
    document: 'doc', image: 'img', video: 'video', audio: 'audio', other: 'other'
  }
  const colorMap = {
     doc: 'bg-blue-500', img: 'bg-violet-500', video: 'bg-purple-400', audio: 'bg-amber-400', other: 'bg-rose-400'
  }
  const nameMap = {
     doc: 'Documents', img: 'Images', video: 'Videos', audio: 'Audio', other: 'Other'
  }
  
  let totalSizeAll = 0
  const sizes = { doc: 0, img: 0, video: 0, audio: 0, other: 0 }
  
  files.value.forEach(f => {
    let internalCat = 'other'
    if (f.category) {
      internalCat = mapCat[f.category] || 'other'
    } else {
      if (f.mimetype.includes('image')) internalCat = 'img'
      else if (f.mimetype.includes('video')) internalCat = 'video'
      else if (f.mimetype.includes('audio')) internalCat = 'audio'
      else if (f.mimetype.includes('pdf') || f.mimetype.includes('document') || f.mimetype.includes('text')) internalCat = 'doc'
    }
    sizes[internalCat] += f.size || 0
    totalSizeAll += f.size || 0
  })

  if (totalSizeAll === 0) return null

  return cats.map(c => ({
    name: nameMap[c],
    color: colorMap[c],
    size: sizes[c],
    percent: (sizes[c] / totalSizeAll) * 100
  })).filter(c => c.size > 0)
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

<style>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.animate-scale-in { animation: scaleIn 0.2s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
@keyframes scaleIn { from { transform: scale(0.95); opacity: 0; } to { transform: scale(1); opacity: 1; } }
</style>
