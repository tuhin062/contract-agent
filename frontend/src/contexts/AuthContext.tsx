import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'
import type { User, AuthState } from '@/types/user'
import authService from '@/services/auth.service'

interface AuthContextType extends AuthState {
    login: (email: string, password: string) => Promise<void>
    logout: () => Promise<void>
    refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [authState, setAuthState] = useState<AuthState>({
        user: null,
        token: null,
        isAuthenticated: false,
    })

    useEffect(() => {
        // Check for existing auth on mount
        const storedUser = authService.getStoredUser()
        const token = localStorage.getItem('access_token')

        if (storedUser && token) {
            setAuthState({
                user: storedUser,
                token,
                isAuthenticated: true,
            })
        }
    }, [])

    const login = useCallback(async (email: string, password: string) => {
        try {
            const response = await authService.login({ email, password })

            setAuthState({
                user: response.user,
                token: response.access_token,
                isAuthenticated: true,
            })
        } catch (error: any) {
            console.error('Login error:', error)
            // Preserve original error to allow proper error handling in components
            // Check if it's an axios error with response data
            if (error?.response?.data?.detail) {
                // Create error with backend message
                const backendError = new Error(error.response.data.detail)
                // Attach response for error handling
                ;(backendError as any).response = error.response
                throw backendError
            }
            // For other errors, preserve original error
            throw error
        }
    }, [])

    const logout = useCallback(async () => {
        try {
            await authService.logout()
        } finally {
            setAuthState({
                user: null,
                token: null,
                isAuthenticated: false,
            })
        }
    }, [])

    const refreshUser = useCallback(async () => {
        try {
            const user = await authService.getCurrentUser()
            localStorage.setItem('user', JSON.stringify(user))
            setAuthState(prev => ({
                ...prev,
                user,
            }))
        } catch (error) {
            console.error('Failed to refresh user:', error)
        }
    }, [])

    return (
        <AuthContext.Provider value={{ ...authState, login, logout, refreshUser }}>
            {children}
        </AuthContext.Provider>
    )
}

export function useAuth() {
    const context = useContext(AuthContext)
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider')
    }
    return context
}
