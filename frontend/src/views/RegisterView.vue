<template>
<div class="flex flex-col lg:flex-row min-h-screen w-full overflow-hidden font-display">
  <!-- Left Side: Branding & Features -->
  <div class="relative flex w-full lg:w-1/2 flex-col justify-between bg-primary p-8 lg:p-16 overflow-hidden">
    <!-- Abstract Background Shapes -->
    <div class="absolute top-[-10%] left-[-10%] w-96 h-96 bg-white/10 rounded-full blur-3xl"></div>
    <div class="absolute bottom-[-10%] right-[-10%] w-[500px] h-[500px] bg-purple-900/20 rounded-full blur-3xl"></div>
    <div class="absolute top-[40%] right-[-5%] w-64 h-64 bg-indigo-400/20 rounded-full blur-2xl"></div>
    
    <div class="relative z-10">
      <!-- Logo -->
      <div class="flex items-center gap-3 mb-12">
        <div class="flex items-center justify-center w-10 h-10 rounded-lg bg-white/20 text-white backdrop-blur-sm">
          <span class="material-symbols-outlined text-2xl">cloud</span>
        </div>
        <h1 class="text-white text-2xl font-black tracking-tight">DocuVault</h1>
      </div>

      <!-- Hero Text -->
      <div class="mb-12">
        <h2 class="text-white text-4xl lg:text-5xl font-bold leading-tight tracking-tight mb-4">
            Your files, anywhere, <br/>securely.
        </h2>
        <p class="text-indigo-100 text-lg font-medium max-w-md opacity-90">
            Experience the next generation of cloud storage. Unmatched speed, military-grade security.
        </p>
      </div>

      <!-- Feature List -->
      <div class="grid gap-6">
        <div class="flex items-start gap-4">
          <div class="flex items-center justify-center w-12 h-12 rounded-xl bg-white/10 text-white backdrop-blur-sm shrink-0">
            <span class="material-symbols-outlined">bolt</span>
          </div>
          <div class="flex flex-col">
            <h3 class="text-white text-lg font-bold">Lightning fast uploads</h3>
            <p class="text-indigo-200 text-sm">Upload large files in seconds with optimized routing.</p>
          </div>
        </div>
        <div class="flex items-start gap-4">
          <div class="flex items-center justify-center w-12 h-12 rounded-xl bg-white/10 text-white backdrop-blur-sm shrink-0">
            <span class="material-symbols-outlined">lock</span>
          </div>
          <div class="flex flex-col">
            <h3 class="text-white text-lg font-bold">End-to-end encryption</h3>
            <p class="text-indigo-200 text-sm">Your data is encrypted before it leaves your device.</p>
          </div>
        </div>
        <div class="flex items-start gap-4">
          <div class="flex items-center justify-center w-12 h-12 rounded-xl bg-white/10 text-white backdrop-blur-sm shrink-0">
            <span class="material-symbols-outlined">share</span>
          </div>
          <div class="flex flex-col">
            <h3 class="text-white text-lg font-bold">One-click sharing</h3>
            <p class="text-indigo-200 text-sm">Securely share folders with granular permissions.</p>
          </div>
        </div>
        <div class="flex items-start gap-4">
          <div class="flex items-center justify-center w-12 h-12 rounded-xl bg-white/10 text-white backdrop-blur-sm shrink-0">
            <span class="material-symbols-outlined">devices</span>
          </div>
          <div class="flex flex-col">
            <h3 class="text-white text-lg font-bold">Access from any device</h3>
            <p class="text-indigo-200 text-sm">Seamless sync across desktop, mobile, and web.</p>
          </div>
        </div>
      </div>
    </div>
    
    <div class="relative z-10 mt-12 text-indigo-200 text-sm font-medium">
        © 2026 DocuVault Inc. All rights reserved.
    </div>
  </div>

  <!-- Right Side: Register Form -->
  <div class="flex w-full lg:w-1/2 flex-col justify-center items-center bg-background-light p-6 lg:p-12">
    <div class="w-full max-w-[480px] bg-white rounded-2xl shadow-xl p-8 lg:p-10 border border-slate-100">
      <div class="text-center mb-8">
        <h1 class="text-slate-900 text-3xl font-bold tracking-tight mb-2">Create an account</h1>
        <p class="text-slate-500 text-base">Get started with DocuVault today</p>
      </div>

      <div v-if="error" class="mb-6 bg-red-50 border border-red-200 text-red-600 p-4 rounded-lg text-sm font-medium flex items-center gap-2">
        <span class="material-symbols-outlined text-red-500">error</span>
        <span>{{ error }}</span>
      </div>

      <form @submit.prevent="submit" class="flex flex-col gap-5">
        <!-- Email Input -->
        <div class="flex flex-col gap-2">
          <label class="text-slate-900 text-sm font-semibold" for="email">Email address</label>
          <div class="relative">
            <div class="absolute inset-y-0 left-0 flex items-center pl-4 pointer-events-none text-slate-400">
              <span class="material-symbols-outlined text-xl">mail</span>
            </div>
            <input v-model="email" id="email" type="email" required placeholder="name@company.com" 
                   class="w-full pl-11 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-lg text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all" />
          </div>
        </div>

        <!-- Password Input -->
        <div class="flex flex-col gap-2">
          <label class="text-slate-900 text-sm font-semibold" for="password">Password</label>
          <div class="relative">
            <div class="absolute inset-y-0 left-0 flex items-center pl-4 pointer-events-none text-slate-400">
              <span class="material-symbols-outlined text-xl">lock</span>
            </div>
            <input v-model="password" id="password" type="password" required placeholder="Create a password" minlength="8"
                   class="w-full pl-11 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-lg text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all" />
          </div>
        </div>
        
        <!-- Confirm Password Input -->
        <div class="flex flex-col gap-2">
          <label class="text-slate-900 text-sm font-semibold" for="confirmPassword">Confirm Password</label>
          <div class="relative">
            <div class="absolute inset-y-0 left-0 flex items-center pl-4 pointer-events-none text-slate-400">
              <span class="material-symbols-outlined text-xl">lock_reset</span>
            </div>
            <input v-model="confirmPassword" id="confirmPassword" type="password" required placeholder="Confirm your password" minlength="8"
                   class="w-full pl-11 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-lg text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all" />
          </div>
        </div>

        <!-- Submit Button -->
        <button type="submit" :disabled="loading" 
                class="mt-2 w-full bg-primary hover:bg-indigo-600 text-white font-bold py-3.5 px-6 rounded-lg transition-colors flex items-center justify-center gap-2 group disabled:opacity-70 disabled:cursor-not-allowed">
          <span>{{ loading ? 'Creating account...' : 'Create Account' }}</span>
          <span v-if="!loading" class="material-symbols-outlined text-sm transition-transform group-hover:translate-x-1">person_add</span>
          <span v-else class="material-symbols-outlined text-sm animate-spin">refresh</span>
        </button>

        <div class="mt-4 text-center">
            <p class="text-slate-500 text-xs">
              By creating an account, you agree to our <a href="#" class="text-primary hover:underline">Terms of Service</a> and <a href="#" class="text-primary hover:underline">Privacy Policy</a>.
            </p>
        </div>
      </form>

      <div class="mt-8 text-center pt-6 border-t border-slate-100">
        <p class="text-slate-500 text-sm">
          Already have an account? 
          <router-link to="/login" class="text-primary font-bold hover:underline">Sign in</router-link>
        </p>
      </div>
    </div>
  </div>
</div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const error = ref('')
const loading = ref(false)

const submit = async () => {
  error.value = ''
  if (password.value !== confirmPassword.value) {
    error.value = 'Passwords do not match'
    return
  }

  loading.value = true
  try {
    await authStore.register(email.value, password.value)
    router.push('/')
  } catch (err) {
    error.value = err.response?.data?.detail || 'Registration failed'
  } finally {
    loading.value = false
  }
}
</script>
