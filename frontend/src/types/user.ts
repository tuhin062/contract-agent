export type UserRole = 'admin' | 'legal_team' | 'business_user' | 'viewer'

export interface User {
    id: string
    name: string
    email: string
    role: UserRole
    avatar?: string
    createdAt: string
    lastLogin?: string
    permissions: Permission[]
}

export interface Permission {
    id: string
    name: string
    resource: string
    actions: ('create' | 'read' | 'update' | 'delete')[]
}

export interface AuthState {
    user: User | null
    token: string | null
    isAuthenticated: boolean
}

export interface LoginCredentials {
    email: string
    password: string
}
