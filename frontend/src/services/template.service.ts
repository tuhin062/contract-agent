/**
 * Template Service
 * Handles template CRUD operations
 */
import apiClient from './api'
import type { 
    Template, 
    TemplateListItem, 
    TemplateCreate, 
    TemplateUpdate,
    GenerateFromTemplateRequest 
} from '@/types/template'
import type { Contract } from '@/types/contract'

export const templateService = {
    /**
     * List all templates
     */
    async listTemplates(params?: {
        category?: string
        active_only?: boolean
        skip?: number
        limit?: number
    }): Promise<TemplateListItem[]> {
        const response = await apiClient.get<TemplateListItem[]>('/templates', { params })
        return response.data
    },

    /**
     * Get template by ID
     */
    async getTemplate(id: string): Promise<Template> {
        const response = await apiClient.get<Template>(`/templates/${id}`)
        return response.data
    },

    /**
     * Create a new template (admin only)
     */
    async createTemplate(data: TemplateCreate): Promise<Template> {
        const response = await apiClient.post<Template>('/templates', data)
        return response.data
    },

    /**
     * Update a template (admin only)
     */
    async updateTemplate(id: string, data: TemplateUpdate): Promise<Template> {
        const response = await apiClient.put<Template>(`/templates/${id}`, data)
        return response.data
    },

    /**
     * Delete a template (admin only)
     */
    async deleteTemplate(id: string): Promise<void> {
        await apiClient.delete(`/templates/${id}`)
    },

    /**
     * Generate a contract from a template
     */
    async generateContract(data: GenerateFromTemplateRequest): Promise<Contract> {
        const response = await apiClient.post<Contract>('/contracts/from-template', data)
        return response.data
    }
}

export default templateService
