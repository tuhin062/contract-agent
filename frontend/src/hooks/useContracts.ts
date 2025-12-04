import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import contractService from '@/services/contract.service'
import type { ContractCreate, ContractUpdate, ContractStatus, GenerateFromTemplateRequest } from '@/types/contract'
import { toast } from '@/lib/toast'

export function useContracts(params?: {
    status?: ContractStatus
    template_id?: string
    latest_only?: boolean
    skip?: number
    limit?: number
}) {
    return useQuery({
        queryKey: ['contracts', params],
        queryFn: () => contractService.listContracts(params),
    })
}

export function useContract(id: string) {
    return useQuery({
        queryKey: ['contract', id],
        queryFn: () => contractService.getContract(id),
        enabled: !!id,
    })
}

export function useCreateContract() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: (data: ContractCreate) =>
            contractService.createContract(data),

        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['contracts'] })
            toast.success('Contract Created', 'Your contract has been created successfully')
        },

        onError: (error: any) => {
            toast.error('Error', error.response?.data?.detail || 'Failed to create contract')
        },
    })
}

export function useGenerateFromTemplate() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: (data: GenerateFromTemplateRequest) =>
            contractService.generateFromTemplate(data),

        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['contracts'] })
            toast.success('Contract Generated', 'Contract generated from template successfully')
        },

        onError: (error: any) => {
            toast.error('Error', error.response?.data?.detail || 'Failed to generate contract')
        },
    })
}

export function useUpdateContract() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: ({ id, data }: { id: string; data: ContractUpdate }) =>
            contractService.updateContract(id, data),

        onSuccess: (_, variables) => {
            queryClient.invalidateQueries({ queryKey: ['contracts'] })
            queryClient.invalidateQueries({ queryKey: ['contract', variables.id] })
            toast.success('Contract Updated', 'Your contract has been updated successfully')
        },

        onError: (error: any) => {
            toast.error('Error', error.response?.data?.detail || 'Failed to update contract')
        },
    })
}

export function useSubmitContract() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: (id: string) => contractService.submitForReview(id),

        onSuccess: (_, id) => {
            queryClient.invalidateQueries({ queryKey: ['contracts'] })
            queryClient.invalidateQueries({ queryKey: ['contract', id] })
            toast.success('Submitted', 'Contract submitted for review')
        },

        onError: (error: any) => {
            toast.error('Error', error.response?.data?.detail || 'Failed to submit contract')
        },
    })
}

export function useApproveContract() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: ({ id, notes }: { id: string; notes?: string }) =>
            contractService.approveContract(id, notes),

        onSuccess: (_, variables) => {
            queryClient.invalidateQueries({ queryKey: ['contracts'] })
            queryClient.invalidateQueries({ queryKey: ['contract', variables.id] })
            toast.success('Approved', 'Contract has been approved')
        },

        onError: (error: any) => {
            toast.error('Error', error.response?.data?.detail || 'Failed to approve contract')
        },
    })
}

export function useRejectContract() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: ({ id, reason }: { id: string; reason: string }) =>
            contractService.rejectContract(id, reason),

        onSuccess: (_, variables) => {
            queryClient.invalidateQueries({ queryKey: ['contracts'] })
            queryClient.invalidateQueries({ queryKey: ['contract', variables.id] })
            toast.success('Rejected', 'Contract has been rejected')
        },

        onError: (error: any) => {
            toast.error('Error', error.response?.data?.detail || 'Failed to reject contract')
        },
    })
}

export function useExecuteContract() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: (id: string) => contractService.executeContract(id),

        onSuccess: (_, id) => {
            queryClient.invalidateQueries({ queryKey: ['contracts'] })
            queryClient.invalidateQueries({ queryKey: ['contract', id] })
            toast.success('Executed', 'Contract has been marked as executed')
        },

        onError: (error: any) => {
            toast.error('Error', error.response?.data?.detail || 'Failed to execute contract')
        },
    })
}

export function useArchiveContract() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: (id: string) => contractService.archiveContract(id),

        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['contracts'] })
            toast.success('Archived', 'Contract has been archived')
        },

        onError: (error: any) => {
            toast.error('Error', error.response?.data?.detail || 'Failed to archive contract')
        },
    })
}

export function useCreateVersion() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: (id: string) => contractService.createNewVersion(id),

        onSuccess: (newContract) => {
            queryClient.invalidateQueries({ queryKey: ['contracts'] })
            toast.success('Version Created', `New version ${newContract.version} created`)
            return newContract
        },

        onError: (error: any) => {
            toast.error('Error', error.response?.data?.detail || 'Failed to create version')
        },
    })
}
