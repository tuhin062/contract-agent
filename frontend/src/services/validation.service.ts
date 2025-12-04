/**
 * Validation Service
 * Handles contract validation and proposal management
 */
import apiClient from './api'
import type {
    Proposal,
    ProposalListItem,
    ProposalCreate,
    ProposalStats,
    ValidationResponse,
    ValidateContractRequest
} from '@/types/proposal'

export const validationService = {
    /**
     * Validate a contract
     */
    async validateContract(
        contractId: string,
        request: ValidateContractRequest
    ): Promise<ValidationResponse> {
        const response = await apiClient.post<ValidationResponse>(
            `/validation/contracts/${contractId}/validate`,
            request
        )
        return response.data
    },

    /**
     * Create a new proposal
     */
    async createProposal(data: ProposalCreate): Promise<Proposal> {
        const response = await apiClient.post<Proposal>('/proposals', data)
        return response.data
    },

    /**
     * List proposals
     */
    async listProposals(params?: {
        validation_status?: string
        risk_level?: string
        skip?: number
        limit?: number
    }): Promise<ProposalListItem[]> {
        const response = await apiClient.get<ProposalListItem[]>('/proposals', { params })
        return response.data
    },

    /**
     * Get proposal by ID
     */
    async getProposal(id: string): Promise<Proposal> {
        const response = await apiClient.get<Proposal>(`/proposals/${id}`)
        return response.data
    },

    /**
     * Get proposal statistics
     */
    async getProposalStats(): Promise<ProposalStats> {
        const response = await apiClient.get<ProposalStats>('/proposals/stats')
        return response.data
    },

    /**
     * Get high-risk proposals (reviewer/admin only)
     */
    async getHighRiskProposals(limit: number = 10): Promise<ProposalListItem[]> {
        const response = await apiClient.get<ProposalListItem[]>('/proposals/high-risk', {
            params: { limit }
        })
        return response.data
    },

    /**
     * Delete a proposal
     */
    async deleteProposal(id: string): Promise<void> {
        await apiClient.delete(`/proposals/${id}`)
    }
}

export default validationService
