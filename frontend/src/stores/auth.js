import { defineStore } from 'pinia'

// Mock user data — no API calls
const MOCK_USER = {
    id: 1,
    email: 'demo@filesharing.com',
    storage_used: 1.2 * 1024 ** 3, // 1.2 GB
    plan_name: 'free',
    created_at: '2026-02-20T10:00:00Z',
}

export const useAuthStore = defineStore('auth', {
    state: () => ({
        user: null,
        token: localStorage.getItem('token'),
    }),

    getters: {
        isLoggedIn: (state) => !!state.token,
        storagePercent: (state) => {
            if (!state.user) return 0
            const limit = state.user.plan_name === 'pro' ? 50 * 1024 ** 3 : 5 * 1024 ** 3
            return Math.min((state.user.storage_used / limit) * 100, 100)
        },
        storageLimitBytes: (state) => {
            if (!state.user) return 5 * 1024 ** 3
            return state.user.plan_name === 'pro' ? 50 * 1024 ** 3 : 5 * 1024 ** 3
        },
    },

    actions: {
        // Mock login — just set token + user, no API
        async login(email, password) {
            await delay(600) // simulate network
            if (password.length < 3) throw { response: { data: { detail: 'Invalid credentials' } } }
            this.token = 'mock-jwt-token'
            localStorage.setItem('token', this.token)
            this.user = { ...MOCK_USER, email }
        },

        async register(email, password) {
            await delay(600)
            if (password.length < 6) throw { response: { data: { detail: 'Password too short' } } }
            this.token = 'mock-jwt-token'
            localStorage.setItem('token', this.token)
            this.user = { ...MOCK_USER, email, storage_used: 0 }
        },

        async fetchUser() {
            await delay(200)
            if (!this.user) {
                this.user = { ...MOCK_USER }
            }
        },

        logout() {
            this.token = null
            this.user = null
            localStorage.removeItem('token')
        },
    },
})

function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms))
}
