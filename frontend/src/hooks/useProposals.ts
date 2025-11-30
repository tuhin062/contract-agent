import { useQuery } from '@tanstack/react-query'
import type { Proposal } from '@/types/proposal'
import { mockFetch } from '@/lib/mock-api'

export function useProposals() {
    return useQuery({
        queryKey: ['proposals'],
        queryFn: async () => {
            const response = await fetch('/mock/proposals.json')
            const data: Proposal[] = await response.json()
            return mockFetch(data)
        },
    })
}

export function useProposal(id: string) {
    return useQuery({
        queryKey: ['proposal', id],
        queryFn: async () => {
            const response = await fetch('/mock/proposals.json')
            const proposals: Proposal[] = await response.json()
            const proposal = proposals.find((p) => p.id === id)
            return mockFetch(proposal)
        },
        enabled: !!id,
    })
}
