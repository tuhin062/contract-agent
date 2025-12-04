/**
 * Contract Service
 * Handles contract CRUD operations and workflow
 */
import apiClient from './api'
import type { 
    Contract, 
    ContractListItem, 
    ContractCreate, 
    ContractUpdate,
    ContractStatus,
    GenerateFromTemplateRequest 
} from '@/types/contract'

export const contractService = {
    /**
     * List contracts with optional filters
     */
    async listContracts(params?: {
        status?: ContractStatus
        template_id?: string
        latest_only?: boolean
        skip?: number
        limit?: number
    }): Promise<ContractListItem[]> {
        const response = await apiClient.get<ContractListItem[]>('/contracts', { params })
        return response.data
    },

    /**
     * Get a single contract by ID
     */
    async getContract(id: string): Promise<Contract> {
        const response = await apiClient.get<Contract>(`/contracts/${id}`)
        return response.data
    },

    /**
     * Create a new contract
     */
    async createContract(data: ContractCreate): Promise<Contract> {
        const response = await apiClient.post<Contract>('/contracts', data)
        return response.data
    },

    /**
     * Generate a contract from a template
     */
    async generateFromTemplate(data: GenerateFromTemplateRequest): Promise<Contract> {
        const response = await apiClient.post<Contract>('/contracts/from-template', data)
        return response.data
    },

    /**
     * Update an existing contract
     */
    async updateContract(id: string, data: ContractUpdate): Promise<Contract> {
        const response = await apiClient.put<Contract>(`/contracts/${id}`, data)
        return response.data
    },

    /**
     * Create a new version of a contract
     */
    async createNewVersion(id: string): Promise<Contract> {
        const response = await apiClient.post<Contract>(`/contracts/${id}/new-version`)
        return response.data
    },

    /**
     * Submit contract for review
     */
    async submitForReview(id: string): Promise<Contract> {
        const response = await apiClient.post<Contract>(`/contracts/${id}/submit`)
        return response.data
    },

    /**
     * Approve a contract (reviewer/admin only)
     */
    async approveContract(id: string, notes?: string): Promise<Contract> {
        const response = await apiClient.post<Contract>(`/contracts/${id}/approve`, { notes })
        return response.data
    },

    /**
     * Reject a contract (reviewer/admin only)
     */
    async rejectContract(id: string, reason: string): Promise<Contract> {
        const response = await apiClient.post<Contract>(`/contracts/${id}/reject`, { reason })
        return response.data
    },

    /**
     * Mark contract as executed
     */
    async executeContract(id: string): Promise<Contract> {
        const response = await apiClient.post<Contract>(`/contracts/${id}/execute`)
        return response.data
    },

    /**
     * Archive a contract
     */
    async archiveContract(id: string): Promise<void> {
        await apiClient.delete(`/contracts/${id}`)
    },

    /**
     * Get contract version history
     */
    async getVersionHistory(id: string): Promise<ContractListItem[]> {
        // Get all versions including non-latest
        const response = await apiClient.get<ContractListItem[]>('/contracts', {
            params: { latest_only: false }
        })
        // Filter to find parent chain
        // This is a simplified version - a real implementation would use parent_contract_id
        return response.data.filter(c => c.id === id || c.title === response.data.find(x => x.id === id)?.title)
    }
}

export default contractService
