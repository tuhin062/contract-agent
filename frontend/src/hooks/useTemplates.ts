import { useQuery } from '@tanstack/react-query'
import type { Template } from '@/types/template'
import { mockFetch } from '@/lib/mock-api'

export function useTemplates() {
    return useQuery({
        queryKey: ['templates'],
        queryFn: async () => {
            const response = await fetch('/mock/templates.json')
            const data: Template[] = await response.json()
            return mockFetch(data)
        },
    })
}

export function useTemplate(id: string) {
    return useQuery({
        queryKey: ['template', id],
        queryFn: async () => {
            const response = await fetch('/mock/templates.json')
            const templates: Template[] = await response.json()
            const template = templates.find((t) => t.id === id)
            return mockFetch(template)
        },
        enabled: !!id,
    })
}
