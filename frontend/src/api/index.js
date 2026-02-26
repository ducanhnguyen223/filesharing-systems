import axios from 'axios'

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
})

api.interceptors.request.use(config => {
    const token = localStorage.getItem('token')
    if (token) config.headers.Authorization = `Bearer ${token}`
    return config
})

api.interceptors.response.use(
    res => res,
    err => {
        if (err.response?.status === 401) {
            localStorage.removeItem('token')
            window.location.href = '/login'
        }
        return Promise.reject(err)
    }
)

export const authApi = {
    register: (email, password) => api.post('/auth/register', { email, password }),
    login: (email, password) => api.post('/auth/login', { email, password }),
    me: () => api.get('/auth/me'),
}

export const filesApi = {
    list: () => api.get('/files/'),
    upload: (formData, onProgress) => api.post('/files/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: onProgress,
    }),
    download: (id) => api.get(`/files/${id}/download`),
    delete: (id) => api.delete(`/files/${id}`),
    share: (id) => api.post(`/files/${id}/share`),
}

export const shareApi = {
    getPublic: (token) => api.get(`/share/${token}`),
}

export default api
