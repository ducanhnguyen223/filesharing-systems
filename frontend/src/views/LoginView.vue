<template>
  <div class="auth-page">
    <div class="auth-left">
      <div class="auth-brand">
        <div class="brand-icon"><span class="mi">cloud</span></div>
        <span class="brand-name">DocuVault</span>
      </div>
      <h1>Your files.<br/>Anywhere. Securely.</h1>
      <p class="tagline">Upload, share, and manage your documents in one beautiful place.</p>
      <div class="features">
        <div class="feat"><span class="mi">rocket_launch</span> Lightning fast uploads</div>
        <div class="feat"><span class="mi">lock</span> End-to-end encryption</div>
        <div class="feat"><span class="mi">link</span> One-click file sharing</div>
        <div class="feat"><span class="mi">devices</span> Access from any device</div>
      </div>
    </div>
    <div class="auth-right">
      <div class="form-card">
        <h2>Welcome back</h2>
        <p class="subtitle">Sign in to your account</p>
        <form @submit.prevent="submit" class="form">
          <div class="field">
            <label for="email">Email</label>
            <div class="input-wrap">
              <span class="mi input-icon">mail</span>
              <input id="email" v-model="email" type="email" placeholder="you@example.com" required autocomplete="email" />
            </div>
          </div>
          <div class="field">
            <label for="password">Password</label>
            <div class="input-wrap">
              <span class="mi input-icon">lock</span>
              <input id="password" v-model="password" type="password" placeholder="Enter your password" required autocomplete="current-password" />
            </div>
          </div>
          <p v-if="error" class="error">{{ error }}</p>
          <button type="submit" class="btn-submit" :disabled="loading">
            <span v-if="loading" class="spinner"></span>
            <span v-else>Sign In</span>
          </button>
        </form>
        <p class="footer-text">Don't have an account? <RouterLink to="/register" class="link">Create one</RouterLink></p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)
const auth = useAuthStore()
const router = useRouter()

async function submit() {
  loading.value = true
  error.value = ''
  try {
    await auth.login(email.value, password.value)
    router.push('/')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to sign in. Check your credentials.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page { display: flex; min-height: 100vh; }

.auth-left {
  flex: 1; background: linear-gradient(135deg, #6c47ff 0%, #a855f7 100%);
  padding: 64px; display: flex; flex-direction: column; justify-content: center; color: #fff;
  position: relative; overflow: hidden;
}
.auth-left::before {
  content: ''; position: absolute; width: 400px; height: 400px; border-radius: 50%;
  background: rgba(255, 255, 255, 0.06); top: -100px; right: -100px;
}
.auth-left::after {
  content: ''; position: absolute; width: 250px; height: 250px; border-radius: 50%;
  background: rgba(255, 255, 255, 0.06); bottom: -50px; left: -50px;
}
.auth-brand { display: flex; align-items: center; gap: 10px; margin-bottom: 48px; position: relative; z-index: 1; }
.brand-icon {
  width: 36px; height: 36px; border-radius: 10px;
  background: rgba(255, 255, 255, 0.2); backdrop-filter: blur(8px);
  display: flex; align-items: center; justify-content: center; color: #fff;
}
.brand-name { font-size: 1.2rem; font-weight: 700; }
.auth-left h1 { font-size: 2.5rem; font-weight: 800; line-height: 1.2; margin-bottom: 16px; letter-spacing: -0.02em; position: relative; z-index: 1; }
.tagline { font-size: 1.1rem; opacity: 0.85; margin-bottom: 48px; line-height: 1.6; position: relative; z-index: 1; }
.features { display: flex; flex-direction: column; gap: 14px; position: relative; z-index: 1; }
.feat { display: flex; align-items: center; gap: 12px; font-size: 0.95rem; opacity: 0.8; }

.auth-right {
  flex: 1; background: var(--bg, #f5f5f7);
  display: flex; align-items: center; justify-content: center; padding: 48px;
}
.form-card {
  width: 100%; max-width: 400px; background: #fff; padding: 48px;
  border-radius: 20px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.04);
}
h2 { font-size: 1.6rem; font-weight: 700; margin-bottom: 6px; color: var(--text, #1a1a2e); }
.subtitle { color: var(--text-muted, #9ca3af); font-size: 0.9rem; margin-bottom: 32px; }

.form { display: flex; flex-direction: column; gap: 18px; }
.field label { display: block; font-size: 0.82rem; font-weight: 600; margin-bottom: 6px; color: #374151; }
.input-wrap { position: relative; }
.input-icon { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: var(--text-muted, #9ca3af); font-size: 18px; }
.input-wrap input {
  width: 100%; padding: 11px 14px 11px 40px;
  border: 1px solid var(--border, #e8e8ee); border-radius: 10px; font-size: 0.92rem;
  outline: none; transition: all 0.2s; background: #f9fafb; color: var(--text, #1a1a2e);
}
.input-wrap input:focus { border-color: var(--primary, #6c47ff); box-shadow: 0 0 0 3px rgba(108, 71, 255, 0.1); background: #fff; }

.error { color: #ef4444; font-size: 0.82rem; text-align: center; padding: 8px; background: #fef2f2; border-radius: 8px; }

.btn-submit {
  width: 100%; padding: 13px; background: var(--primary, #6c47ff); color: #fff;
  border: none; border-radius: 10px; font-size: 0.95rem; font-weight: 600;
  display: flex; align-items: center; justify-content: center; cursor: pointer; transition: background 0.2s;
}
.btn-submit:hover { background: var(--primary-dark, #5835db); }
.btn-submit:disabled { opacity: 0.6; cursor: not-allowed; }

.footer-text { text-align: center; margin-top: 24px; font-size: 0.85rem; color: var(--text-muted, #9ca3af); }
.link { color: var(--primary, #6c47ff); font-weight: 600; text-decoration: none; }
.link:hover { text-decoration: underline; }

.spinner { width: 18px; height: 18px; border: 2px solid rgba(255,255,255,0.3); border-top-color: #fff; border-radius: 50%; animation: spin 0.6s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 768px) {
  .auth-page { flex-direction: column; }
  .auth-left { padding: 32px; min-height: 200px; }
  .auth-left h1 { font-size: 1.8rem; }
  .features { display: none; }
  .auth-right { padding: 24px; }
  .form-card { padding: 32px; }
}
</style>
