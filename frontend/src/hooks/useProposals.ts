import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import validationService from '@/services/validation.service'
import type { ProposalCreate, ValidateContractRequest } from '@/types/proposal'
import { toast } from '@/lib/toast'

export function useProposals(params?: {
    validation_status?: string
    risk_level?: string
    skip?: number
    limit?: number
}) {
    return useQuery({
        queryKey: ['proposals', params],
        queryFn: () => validationService.listProposals(params),
    })
}

export function useProposal(id: string) {
    return useQuery({
        queryKey: ['proposal', id],
        queryFn: () => validationService.getProposal(id),
        enabled: !!id,
    })
}

export function useProposalStats() {
    return useQuery({
        queryKey: ['proposalStats'],
        queryFn: () => validationService.getProposalStats(),
    })
}

export function useHighRiskProposals(limit: number = 10) {
    return useQuery({
        queryKey: ['proposals', 'high-risk', limit],
        queryFn: () => validationService.getHighRiskProposals(limit),
    })
}

export function useCreateProposal() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: (data: ProposalCreate) =>
            validationService.createProposal(data),

        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['proposals'] })
            queryClient.invalidateQueries({ queryKey: ['proposalStats'] })
            toast.success('Proposal Created', 'New proposal has been created')
        },

        onError: (error: any) => {
            toast.error('Error', error.response?.data?.detail || 'Failed to create proposal')
        },
    })
}

export function useValidateContract() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: ({ contractId, request }: { contractId: string; request: ValidateContractRequest }) =>
            validationService.validateContract(contractId, request),

        onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: ['proposals'] })
            queryClient.invalidateQueries({ queryKey: ['proposalStats'] })
            toast.success('Validation Complete', `Risk level: ${data.risk_level}`)
        },

        onError: (error: any) => {
            toast.error('Validation Failed', error.response?.data?.detail || 'Failed to validate contract')
        },
    })
}

export function useDeleteProposal() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: (id: string) => validationService.deleteProposal(id),

        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['proposals'] })
            queryClient.invalidateQueries({ queryKey: ['proposalStats'] })
            toast.success('Deleted', 'Proposal has been deleted')
        },

        onError: (error: any) => {
            toast.error('Error', error.response?.data?.detail || 'Failed to delete proposal')
        },
    })
}
