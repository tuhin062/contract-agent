export interface PaginationParams {
    page: number
    pageSize: number
}

export interface PaginatedResponse<T> {
    data: T[]
    total: number
    page: number
    pageSize: number
    totalPages: number
}

export interface FilterOption {
    label: string
    value: string
}

export interface SortOption {
    field: string
    direction: 'asc' | 'desc'
}

export interface APIError {
    message: string
    code: string
    details?: Record<string, unknown>
}

export type ToastType = 'success' | 'error' | 'warning' | 'info'

export interface Toast {
    id: string
    type: ToastType
    title: string
    description?: string
    duration?: number
}
