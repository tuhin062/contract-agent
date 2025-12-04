/**
 * API Client Configuration
 * Axios instance with authentication and error handling
 */
import axios from 'axios'

// Safely load environment variable with fallback
const API_BASE_URL = (() => {
    try {
        const envUrl = import.meta.env.VITE_API_BASE_URL
        if (!envUrl) {
            console.warn('VITE_API_BASE_URL not set, using default: http://localhost:8000')
        }
        return envUrl || 'http://localhost:8000'
    } catch (error) {
        console.error('Error loading VITE_API_BASE_URL:', error)
        return 'http://localhost:8000'
    }
})()

console.log('API Client initialized with base URL:', API_BASE_URL)

export const apiClient = axios.create({
    baseURL: `${API_BASE_URL}/api/v1`,
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 120000, // 2 minute timeout for large file uploads
})

// Request interceptor to add auth token
apiClient.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token')
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }
        // Don't set Content-Type for FormData - let browser set it with boundary
        if (config.data instanceof FormData) {
            delete config.headers['Content-Type']
        }
        return config
    },
    (error) => {
        return Promise.reject(error)
    }
)

// Response interceptor for error handling  
apiClient.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config

        // If 401 and we haven't already tried to refresh
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true

            try {
                const refreshToken = localStorage.getItem('refresh_token')
                if (refreshToken) {
                    const response = await axios.post(`${API_BASE_URL}/api/v1/auth/refresh`, {
                        refresh_token: refreshToken,
                    })

                    const { access_token } = response.data
                    localStorage.setItem('access_token', access_token)

                    // Retry original request with new token
                    originalRequest.headers.Authorization = `Bearer ${access_token}`
                    return apiClient(originalRequest)
                }
            } catch (refreshError) {
                // Refresh failed, clear tokens and redirect to login
                localStorage.removeItem('access_token')
                localStorage.removeItem('refresh_token')
                window.location.href = '/login'
                return Promise.reject(refreshError)
            }
        }

        return Promise.reject(error)
    }
)

export default apiClient
