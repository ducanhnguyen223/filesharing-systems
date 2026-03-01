<template>
<div class="relative flex min-h-screen flex-col lg:flex-row overflow-hidden bg-background-light dark:bg-background-dark font-display text-slate-900 dark:text-slate-100">

  <!-- Left Sidebar -->
  <aside class="hidden lg:flex w-64 flex-col bg-white dark:bg-slate-900 border-r border-primary/10 p-4 shrink-0 z-10">
    <div class="flex items-center gap-3 px-2 mb-8">
      <div class="bg-primary/10 p-2 rounded-lg text-primary">
        <span class="material-symbols-outlined text-3xl">shield_person</span>
      </div>
      <h2 class="text-xl font-bold tracking-tight">DocuVault</h2>
    </div>

    <nav class="flex-1 space-y-1">
      <RouterLink to="/" class="flex items-center gap-3 px-3 py-2 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-primary/5 transition-colors">
        <span class="material-symbols-outlined">dashboard</span> Dashboard
      </RouterLink>
    </nav>

    <div class="mt-auto border-t border-slate-100 dark:border-slate-800 pt-4 space-y-1 flex flex-col">
      <RouterLink to="/settings" class="flex items-center gap-3 px-3 py-2 bg-primary/10 text-primary font-semibold rounded-lg">
        <span class="material-symbols-outlined">settings</span> Settings
      </RouterLink>
      <a @click="logout" class="flex items-center gap-3 px-3 py-2 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/10 rounded-lg transition-colors cursor-pointer mt-2 font-medium">
        <span class="material-symbols-outlined">logout</span> Sign out
      </a>
    </div>
  </aside>

  <!-- Main Content -->
  <main class="flex-1 flex flex-col min-w-0">
    <header class="p-4 md:p-6 bg-white dark:bg-slate-900 border-b border-primary/5 flex items-center gap-4">
      <RouterLink to="/" class="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors">
        <span class="material-symbols-outlined text-slate-500">arrow_back</span>
      </RouterLink>
      <h1 class="text-xl font-bold">Settings</h1>
    </header>

    <div class="p-4 md:p-8 max-w-2xl w-full mx-auto space-y-6">

      <!-- Profile Section -->
      <section class="bg-white dark:bg-slate-900 rounded-xl border border-primary/5 shadow-sm overflow-hidden">
        <div class="px-6 py-4 border-b border-slate-100 dark:border-slate-800">
          <h2 class="font-bold text-base">Profile</h2>
          <p class="text-sm text-slate-500 mt-0.5">Update your email address</p>
        </div>
        <form @submit.prevent="saveProfile" class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Email</label>
            <input
              v-model="profileForm.email"
              type="email"
              class="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg px-3 py-2.5 text-sm outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all"
            />
          </div>
          <div class="flex items-center gap-3">
            <button type="submit" :disabled="profileSaving" class="bg-primary hover:bg-indigo-600 disabled:opacity-60 text-white font-semibold px-5 py-2 rounded-lg text-sm transition-colors">
              {{ profileSaving ? 'Saving…' : 'Save changes' }}
            </button>
            <transition name="fade">
              <span v-if="profileMsg" :class="profileMsgOk ? 'text-green-600' : 'text-red-500'" class="text-sm font-medium">{{ profileMsg }}</span>
            </transition>
          </div>
        </form>
      </section>

      <!-- Security Section -->
      <section class="bg-white dark:bg-slate-900 rounded-xl border border-primary/5 shadow-sm overflow-hidden">
        <div class="px-6 py-4 border-b border-slate-100 dark:border-slate-800">
          <h2 class="font-bold text-base">Security</h2>
          <p class="text-sm text-slate-500 mt-0.5">Change your password</p>
        </div>
        <form @submit.prevent="savePassword" class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Current password</label>
            <input
              v-model="passwordForm.current"
              type="password"
              autocomplete="current-password"
              class="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg px-3 py-2.5 text-sm outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">New password</label>
            <input
              v-model="passwordForm.next"
              type="password"
              autocomplete="new-password"
              class="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg px-3 py-2.5 text-sm outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all"
            />
          </div>
          <div class="flex items-center gap-3">
            <button type="submit" :disabled="passwordSaving" class="bg-primary hover:bg-indigo-600 disabled:opacity-60 text-white font-semibold px-5 py-2 rounded-lg text-sm transition-colors">
              {{ passwordSaving ? 'Saving…' : 'Update password' }}
            </button>
            <transition name="fade">
              <span v-if="passwordMsg" :class="passwordMsgOk ? 'text-green-600' : 'text-red-500'" class="text-sm font-medium">{{ passwordMsg }}</span>
            </transition>
          </div>
        </form>
      </section>

      <!-- Plan Section -->
      <section class="bg-white dark:bg-slate-900 rounded-xl border border-primary/5 shadow-sm overflow-hidden">
        <div class="px-6 py-4 border-b border-slate-100 dark:border-slate-800">
          <h2 class="font-bold text-base">Plan</h2>
          <p class="text-sm text-slate-500 mt-0.5">Your current subscription</p>
        </div>
        <div class="p-6 flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl flex items-center justify-center" :class="auth.user?.plan_name === 'pro' ? 'bg-amber-100 text-amber-600' : 'bg-slate-100 text-slate-500'">
              <span class="material-symbols-outlined">{{ auth.user?.plan_name === 'pro' ? 'workspace_premium' : 'layers' }}</span>
            </div>
            <div>
              <div class="font-semibold capitalize">{{ auth.user?.plan_name || 'free' }} plan</div>
              <div class="text-sm text-slate-500">{{ formatBytes(auth.user?.storage_used || 0) }} of {{ formatBytes(auth.storageLimitBytes) }} used</div>
            </div>
          </div>
          <button v-if="auth.user?.plan_name !== 'pro'" class="bg-slate-900 dark:bg-primary hover:bg-slate-700 dark:hover:bg-indigo-600 text-white font-semibold px-4 py-2 rounded-lg text-sm transition-colors">
            Upgrade to Pro
          </button>
          <span v-else class="text-sm text-amber-600 font-semibold flex items-center gap-1"><span class="material-symbols-outlined text-base">check_circle</span> Active</span>
        </div>
      </section>

      <!-- Danger Zone -->
      <section class="bg-white dark:bg-slate-900 rounded-xl border border-red-200 dark:border-red-900/40 shadow-sm overflow-hidden">
        <div class="px-6 py-4 border-b border-red-100 dark:border-red-900/30">
          <h2 class="font-bold text-base text-red-600">Danger Zone</h2>
          <p class="text-sm text-slate-500 mt-0.5">Irreversible actions — proceed with caution</p>
        </div>
        <div class="p-6 flex items-center justify-between">
          <div>
            <div class="font-medium text-sm">Delete account</div>
            <div class="text-sm text-slate-500 mt-0.5">Permanently delete your account and all files</div>
          </div>
          <button @click="confirmDeleteAccount" class="bg-red-50 hover:bg-red-100 text-red-600 font-semibold px-4 py-2 rounded-lg text-sm transition-colors border border-red-200">
            Delete account
          </button>
        </div>
      </section>

    </div>
  </main>

</div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

// Profile form
const profileForm = ref({ email: '' })
const profileSaving = ref(false)
const profileMsg = ref('')
const profileMsgOk = ref(true)

// Password form
const passwordForm = ref({ current: '', next: '' })
const passwordSaving = ref(false)
const passwordMsg = ref('')
const passwordMsgOk = ref(true)

onMounted(async () => {
  if (!auth.user) await auth.fetchUser()
  profileForm.value.email = auth.user?.email || ''
})

async function saveProfile() {
  if (!profileForm.value.email) return
  profileSaving.value = true
  profileMsg.value = ''
  try {
    await auth.updateProfile({ email: profileForm.value.email })
    profileMsg.value = 'Saved!'
    profileMsgOk.value = true
  } catch (err) {
    profileMsg.value = err.response?.data?.detail || 'Failed to save'
    profileMsgOk.value = false
  } finally {
    profileSaving.value = false
    setTimeout(() => (profileMsg.value = ''), 3000)
  }
}

async function savePassword() {
  if (!passwordForm.value.current || !passwordForm.value.next) return
  passwordSaving.value = true
  passwordMsg.value = ''
  try {
    await auth.updateProfile({
      current_password: passwordForm.value.current,
      new_password: passwordForm.value.next,
    })
    passwordMsg.value = 'Password updated!'
    passwordMsgOk.value = true
    passwordForm.value = { current: '', next: '' }
  } catch (err) {
    passwordMsg.value = err.response?.data?.detail || 'Failed to update'
    passwordMsgOk.value = false
  } finally {
    passwordSaving.value = false
    setTimeout(() => (passwordMsg.value = ''), 3000)
  }
}

async function confirmDeleteAccount() {
  if (!confirm('This will permanently delete your account and all your files. Are you sure?')) return
  if (!confirm('Last warning — this cannot be undone. Continue?')) return
  try {
    await auth.deleteAccount()
    router.push('/login')
  } catch (err) {
    alert(err.response?.data?.detail || 'Failed to delete account')
  }
}

function logout() { auth.logout(); router.push('/login') }

function formatBytes(b) {
  if (!b) return '0 B'
  if (b >= 1024 ** 3) return (b / 1024 ** 3).toFixed(1) + ' GB'
  if (b >= 1024 ** 2) return (b / 1024 ** 2).toFixed(1) + ' MB'
  if (b >= 1024) return (b / 1024).toFixed(1) + ' KB'
  return b + ' B'
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
