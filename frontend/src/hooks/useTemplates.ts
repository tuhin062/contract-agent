import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import templateService from '@/services/template.service'
import type { TemplateCreate, TemplateUpdate } from '@/types/template'
import { toast } from '@/lib/toast'

export function useTemplates(params?: {
    category?: string
    active_only?: boolean
    skip?: number
    limit?: number
}) {
    return useQuery({
        queryKey: ['templates', params],
        queryFn: () => templateService.listTemplates(params),
    })
}

export function useTemplate(id: string) {
    return useQuery({
        queryKey: ['template', id],
        queryFn: () => templateService.getTemplate(id),
        enabled: !!id,
    })
}

export function useCreateTemplate() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: (data: TemplateCreate) => templateService.createTemplate(data),

        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['templates'] })
            toast.success('Template Created', 'Template has been created successfully')
        },

        onError: (error: any) => {
            toast.error('Error', error.response?.data?.detail || 'Failed to create template')
        },
    })
}

export function useUpdateTemplate() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: ({ id, data }: { id: string; data: TemplateUpdate }) =>
            templateService.updateTemplate(id, data),

        onSuccess: (_, variables) => {
            queryClient.invalidateQueries({ queryKey: ['templates'] })
            queryClient.invalidateQueries({ queryKey: ['template', variables.id] })
            toast.success('Template Updated', 'Template has been updated successfully')
        },

        onError: (error: any) => {
            toast.error('Error', error.response?.data?.detail || 'Failed to update template')
        },
    })
}

export function useDeleteTemplate() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: (id: string) => templateService.deleteTemplate(id),

        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['templates'] })
            toast.success('Template Deleted', 'Template has been deleted')
        },

        onError: (error: any) => {
            toast.error('Error', error.response?.data?.detail || 'Failed to delete template')
        },
    })
}
