/**
 * Authentication Service
 * Handles login, logout, and user management
 */
import apiClient from './api'
import type { User, TokenResponse, LoginCredentials } from '@/types/user'

export const authService = {
    /**
     * Login with email and password
     */
    async login(credentials: LoginCredentials): Promise<TokenResponse> {
        const response = await apiClient.post<TokenResponse>('/auth/login', credentials)
        
        // Store tokens
        localStorage.setItem('access_token', response.data.access_token)
        localStorage.setItem('refresh_token', response.data.refresh_token)
        localStorage.setItem('user', JSON.stringify(response.data.user))
        
        return response.data
    },

    /**
     * Logout current user
     */
    async logout(): Promise<void> {
        try {
            await apiClient.post('/auth/logout')
        } finally {
            // Always clear tokens, even if API call fails
            localStorage.removeItem('access_token')
            localStorage.removeItem('refresh_token')
            localStorage.removeItem('user')
        }
    },

    /**
     * Get current user info from API
     */
    async getCurrentUser(): Promise<User> {
        const response = await apiClient.get<User>('/auth/me')
        return response.data
    },

    /**
     * Get stored user from localStorage
     */
    getStoredUser(): User | null {
        const userStr = localStorage.getItem('user')
        return userStr ? JSON.parse(userStr) : null
    },

    /**
     * Check if user is authenticated
     */
    isAuthenticated(): boolean {
        return !!localStorage.getItem('access_token')
    },

    /**
     * Refresh access token
     */
    async refreshToken(): Promise<string> {
        const refreshToken = localStorage.getItem('refresh_token')
        if (!refreshToken) {
            throw new Error('No refresh token available')
        }

        const response = await apiClient.post<{ access_token: string }>('/auth/refresh', {
            refresh_token: refreshToken
        })

        localStorage.setItem('access_token', response.data.access_token)
        return response.data.access_token
    }
}

export default authService
