import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import type { Contract, ContractDetail } from '@/types/contract'
import { mockFetch, mockMutation } from '@/lib/mock-api'

export function useContracts() {
    return useQuery({
        queryKey: ['contracts'],
        queryFn: async () => {
            const response = await fetch('/mock/contracts.json')
            const data: ContractDetail[] = await response.json()
            return mockFetch(data)
        },
    })
}

export function useContract(id: string) {
    return useQuery({
        queryKey: ['contract', id],
        queryFn: async () => {
            const response = await fetch('/mock/contracts.json')
            const contracts: ContractDetail[] = await response.json()
            const contract = contracts.find((c) => c.id === id)
            return mockFetch(contract)
        },
        enabled: !!id,
    })
}

export function useCreateContract() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: async (contract: Partial<Contract>) => {
            return mockMutation(contract, 1200)
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['contracts'] })
        },
    })
}

export function useUpdateContract() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: async ({ id, data }: { id: string; data: Partial<Contract> }) => {
            return mockMutation({ id, ...data }, 1000)
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['contracts'] })
        },
    })
}

export function useDeleteContract() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: async (id: string) => {
            return mockMutation({ id }, 800)
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['contracts'] })
        },
    })
}
