<template>
  <div class="auth-page">
    <div class="auth-container glass-card animate-slide-up">
      <div class="auth-header">
        <div class="logo">
          <span class="logo-icon icon-tactile">☁️</span>
          <span class="logo-text">FileSharing</span>
        </div>
        <h1>Create account</h1>
        <p class="auth-subtitle">Start your journey with 5GB free</p>
      </div>

      <form @submit.prevent="submit" class="auth-form">
        <div class="form-group">
          <input id="email" v-model="email" type="email" placeholder="Email address" required autocomplete="email" />
        </div>

        <div class="form-group">
          <input id="password" v-model="password" type="password" placeholder="Password" required minlength="6" autocomplete="new-password" />
        </div>

        <div class="form-group">
          <input id="confirm" v-model="confirmPassword" type="password" placeholder="Confirm password" required autocomplete="new-password" />
        </div>

        <p v-if="error" class="error-message">{{ error }}</p>

        <button type="submit" class="btn btn-primary btn-full" :disabled="loading">
          <span v-if="loading" class="spinner-sm"></span>
          <span v-else>Create Account</span>
        </button>
      </form>

      <div class="auth-footer">
        <p>Already have an account? <RouterLink to="/login" class="link">Sign in</RouterLink></p>
      </div>

      <!-- Feature Bento (Simplified) -->
      <div class="features-grid">
        <div class="feature-item"><span>📦</span> 5GB Free</div>
        <div class="feature-item"><span>🔗</span> Easy Share</div>
        <div class="feature-item"><span>🔒</span> Encrypted</div>
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
const confirmPassword = ref('')
const error = ref('')
const loading = ref(false)
const auth = useAuthStore()
const router = useRouter()

async function submit() {
  if (password.value !== confirmPassword.value) {
    error.value = 'Passwords do not match'
    return
  }
  loading.value = true
  error.value = ''
  try {
    await auth.register(email.value, password.value)
    router.push('/')
  } catch (e) {
    error.value = 'Registration failed. Try again later.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 24px;
  background: var(--bg-base);
}

.auth-container {
  width: 100%;
  max-width: 440px;
  padding: 48px;
  display: flex;
  flex-direction: column;
}

.auth-header {
  text-align: center;
  margin-bottom: 32px;
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

h1 {
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 8px;
}

.auth-subtitle {
  color: var(--text-secondary);
  font-size: 0.95rem;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.btn-full {
  width: 100%;
  padding: 14px;
  margin-top: 8px;
}

.auth-footer {
  text-align: center;
  margin-top: 24px;
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.link {
  color: var(--primary-400);
  text-decoration: none;
  font-weight: 600;
}

.link:hover {
  text-decoration: underline;
}

.features-grid {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid var(--border-default);
}

.feature-item {
  font-size: 0.75rem;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  gap: 4px;
}

.error-message {
  color: var(--danger);
  font-size: 0.85rem;
  text-align: center;
}

.spinner-sm {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255,255,255,0.2);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }
</style>
