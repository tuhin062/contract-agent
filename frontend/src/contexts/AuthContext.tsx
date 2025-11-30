import React, { createContext, useContext, useState, useEffect } from 'react'
import type { User, AuthState } from '@/types/user'
import { storage } from '@/lib/mock-api'

interface AuthContextType extends AuthState {
    login: (email: string, password: string) => Promise<void>
    logout: () => void
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
        const storedUser = storage.get<User>('user')
        const storedToken = storage.get<string>('token')
        if (storedUser && storedToken) {
            setAuthState({
                user: storedUser,
                token: storedToken,
                isAuthenticated: true,
            })
        }
    }, [])

    const login = async (email: string, _password: string) => {
        // Mock login - fetch user from users.json
        const response = await fetch('/mock/users.json')
        const users: User[] = await response.json()
        const user = users.find((u) => u.email === email)

        if (user) {
            const token = `mock-token-${Date.now()}`
            storage.set('user', user)
            storage.set('token', token)
            setAuthState({
                user,
                token,
                isAuthenticated: true,
            })
        } else {
            throw new Error('Invalid credentials')
        }
    }

    const logout = () => {
        storage.remove('user')
        storage.remove('token')
        setAuthState({
            user: null,
            token: null,
            isAuthenticated: false,
        })
    }

    return (
        <AuthContext.Provider value={{ ...authState, login, logout }}>
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
