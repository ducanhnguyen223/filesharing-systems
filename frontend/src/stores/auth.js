import { defineStore } from 'pinia'
import { authApi } from '@/api/index'

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
        async login(email, password) {
            const res = await authApi.login(email, password)
            this.token = res.data.access_token
            localStorage.setItem('token', this.token)
            await this.fetchUser()
        },

        async register(email, password) {
            const res = await authApi.register(email, password)
            this.token = res.data.access_token
            localStorage.setItem('token', this.token)
            await this.fetchUser()
        },

        async fetchUser() {
            const res = await authApi.me()
            this.user = res.data
        },

        logout() {
            this.token = null
            this.user = null
            localStorage.removeItem('token')
        },

        async updateProfile(data) {
            const res = await authApi.updateMe(data)
            this.user = res.data
        },

        async deleteAccount() {
            await authApi.deleteMe()
            this.logout()
        },
    },
})
