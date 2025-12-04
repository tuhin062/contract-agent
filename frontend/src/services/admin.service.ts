/**
 * Admin Service
 * Handles user management, settings, and audit logs
 */
import apiClient from './api'
import type { User, UserCreate, UserUpdate } from '@/types/user'

// User stats response
export interface UserStats {
    total: number
    active: number
    inactive: number
    by_role: {
        admin: number
        reviewer: number
        regular: number
    }
}

// Model configuration
export interface ModelConfig {
    chat_model: string
    reasoning_model: string
    generation_model: string
    embedding_model: string
}

export interface ModelOption {
    id: string
    name: string
    type: string
    cost: string
}

export interface ModelConfigResponse extends ModelConfig {
    available_models: ModelOption[]
}

// System settings
export interface SystemSettings {
    file_max_size_mb: number
    rate_limit_per_minute: number
    rate_limit_llm_per_minute: number
    chunk_size: number
    chunk_overlap: number
    top_k_retrieval: number
    min_similarity_score: number
    pinecone_index: string
    pinecone_namespace: string
    environment: string
    debug: boolean
}

// Audit log
export interface AuditLog {
    id: string
    action: string
    resource_type?: string
    resource_id?: string
    description: string
    details: Record<string, any>
    user_id?: string
    ip_address?: string
    success: string
    error_message?: string
    created_at: string
}

export interface AuditLogListResponse {
    items: AuditLog[]
    total: number
    skip: number
    limit: number
}

export interface AuditStats {
    period_days: number
    total_events: number
    logins: number
    failed_logins: number
    by_action: Record<string, number>
}

// System health
export interface SystemHealth {
    status: string
    version: string
    environment: string
    services: {
        database: string
        pinecone: string
        openrouter: string
    }
    pinecone_stats: {
        total_vector_count?: number
        namespaces?: Record<string, any>
    }
}

export const adminService = {
    // ============ USER MANAGEMENT ============

    /**
     * List all users
     */
    async listUsers(params?: {
        role?: string
        is_active?: boolean
        search?: string
        skip?: number
        limit?: number
    }): Promise<User[]> {
        const response = await apiClient.get<User[]>('/admin/users', { params })
        return response.data
    },

    /**
     * Get user statistics
     */
    async getUserStats(): Promise<UserStats> {
        const response = await apiClient.get<UserStats>('/admin/users/stats')
        return response.data
    },

    /**
     * Create a new user
     */
    async createUser(data: UserCreate): Promise<User> {
        const response = await apiClient.post<User>('/admin/users', data)
        return response.data
    },

    /**
     * Get user by ID
     */
    async getUser(id: string): Promise<User> {
        const response = await apiClient.get<User>(`/admin/users/${id}`)
        return response.data
    },

    /**
     * Update user
     */
    async updateUser(id: string, data: UserUpdate): Promise<User> {
        const response = await apiClient.put<User>(`/admin/users/${id}`, data)
        return response.data
    },

    /**
     * Reset user password
     */
    async resetPassword(id: string, newPassword: string): Promise<void> {
        await apiClient.post(`/admin/users/${id}/reset-password`, null, {
            params: { new_password: newPassword }
        })
    },

    /**
     * Deactivate user
     */
    async deactivateUser(id: string): Promise<User> {
        const response = await apiClient.post<User>(`/admin/users/${id}/deactivate`)
        return response.data
    },

    /**
     * Activate user
     */
    async activateUser(id: string): Promise<User> {
        const response = await apiClient.post<User>(`/admin/users/${id}/activate`)
        return response.data
    },

    /**
     * Delete user
     */
    async deleteUser(id: string): Promise<void> {
        await apiClient.delete(`/admin/users/${id}`)
    },

    // ============ SETTINGS ============

    /**
     * Get model configuration
     */
    async getModelConfig(): Promise<ModelConfigResponse> {
        const response = await apiClient.get<ModelConfigResponse>('/admin/settings/models')
        return response.data
    },

    /**
     * Update model configuration
     */
    async updateModelConfig(config: ModelConfig): Promise<void> {
        await apiClient.put('/admin/settings/models', config)
    },

    /**
     * Get system settings
     */
    async getSystemSettings(): Promise<SystemSettings> {
        const response = await apiClient.get<SystemSettings>('/admin/settings/system')
        return response.data
    },

    /**
     * Update system settings
     */
    async updateSystemSettings(settings: Partial<SystemSettings>): Promise<void> {
        await apiClient.put('/admin/settings/system', settings)
    },

    /**
     * Get system health
     */
    async getSystemHealth(): Promise<SystemHealth> {
        const response = await apiClient.get<SystemHealth>('/admin/settings/health')
        return response.data
    },

    /**
     * Clear cache
     */
    async clearCache(): Promise<void> {
        await apiClient.post('/admin/settings/cache/clear')
    },

    // ============ AUDIT LOGS ============

    /**
     * Get audit logs
     */
    async getAuditLogs(params?: {
        user_id?: string
        action?: string
        resource_type?: string
        resource_id?: string
        start_date?: string
        end_date?: string
        success?: string
        skip?: number
        limit?: number
    }): Promise<AuditLogListResponse> {
        const response = await apiClient.get<AuditLogListResponse>('/admin/audit', { params })
        return response.data
    },

    /**
     * Get audit statistics
     */
    async getAuditStats(days: number = 7): Promise<AuditStats> {
        const response = await apiClient.get<AuditStats>('/admin/audit/stats', {
            params: { days }
        })
        return response.data
    },

    /**
     * Get security audit events
     */
    async getSecurityAudit(hours: number = 24): Promise<{
        period_hours: number
        security_events: AuditLog[]
        failed_logins: AuditLog[]
        failed_login_count: number
    }> {
        const response = await apiClient.get('/admin/audit/security', {
            params: { hours }
        })
        return response.data
    },

    /**
     * Get resource audit history
     */
    async getResourceHistory(
        resourceType: string,
        resourceId: string,
        limit: number = 50
    ): Promise<{ resource_type: string; resource_id: string; history: AuditLog[] }> {
        const response = await apiClient.get(
            `/admin/audit/resource/${resourceType}/${resourceId}`,
            { params: { limit } }
        )
        return response.data
    },

    /**
     * Get user activity
     */
    async getUserActivity(
        userId: string,
        days: number = 30,
        limit: number = 100
    ): Promise<{ user_id: string; period_days: number; activity: AuditLog[] }> {
        const response = await apiClient.get(`/admin/audit/user/${userId}/activity`, {
            params: { days, limit }
        })
        return response.data
    }
}

export default adminService
