/**
 * User types aligned with backend schemas
 */

// User role matching backend enum
export type UserRole = 'regular' | 'reviewer' | 'admin'

// User interface
export interface User {
    id: string
    email: string
    name: string
    role: UserRole
    is_active: boolean
    created_at: string
    last_login?: string
}

// User creation
export interface UserCreate {
    email: string
    name: string
    password: string
    role?: UserRole
}

// User update
export interface UserUpdate {
    name?: string
    email?: string
    role?: UserRole
    is_active?: boolean
}

// Auth state
export interface AuthState {
    user: User | null
    token: string | null
    isAuthenticated: boolean
}

// Login credentials
export interface LoginCredentials {
    email: string
    password: string
}

// Token response
export interface TokenResponse {
    access_token: string
    refresh_token: string
    token_type: string
    user: User
}

// Role display helpers
export const USER_ROLE_LABELS: Record<UserRole, string> = {
    regular: 'Regular User',
    reviewer: 'Reviewer',
    admin: 'Administrator'
}

export const USER_ROLE_COLORS: Record<UserRole, string> = {
    regular: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200',
    reviewer: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    admin: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200'
}

// Permission check helpers
export function canReview(user: User | null): boolean {
    return user?.role === 'reviewer' || user?.role === 'admin'
}

export function canAdmin(user: User | null): boolean {
    return user?.role === 'admin'
}

export function canCreateUsers(user: User | null): boolean {
    return user?.role === 'admin'
}

// Format role for display
export function formatRole(role: UserRole): string {
    return USER_ROLE_LABELS[role] || role
}
