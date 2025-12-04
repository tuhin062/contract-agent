/**
 * Template types aligned with backend schemas
 */

// Template placeholder
export interface TemplatePlaceholder {
    key: string
    label: string
    type: 'text' | 'number' | 'date' | 'select' | 'textarea'
    required?: boolean
    default?: string
    options?: string[]
    description?: string
}

// Template interface
export interface Template {
    id: string
    name: string
    description?: string
    content: string
    category?: string
    placeholders: TemplatePlaceholder[]
    is_active: boolean
    custom_metadata: Record<string, any>
    created_by: string
    created_at: string
    updated_at?: string
}

// Template list item
export interface TemplateListItem {
    id: string
    name: string
    description?: string
    category?: string
    is_active: boolean
    created_at: string
}

// Template creation
export interface TemplateCreate {
    name: string
    description?: string
    content: string
    category?: string
    placeholders?: TemplatePlaceholder[]
    metadata?: Record<string, any>
}

// Template update
export interface TemplateUpdate {
    name?: string
    description?: string
    content?: string
    category?: string
    placeholders?: TemplatePlaceholder[]
    is_active?: boolean
    metadata?: Record<string, any>
}

// Generate from template request
export interface GenerateFromTemplateRequest {
    template_id: string
    title: string
    values: Record<string, string>
    description?: string
    metadata?: Record<string, any>
}

// Template categories
export const TEMPLATE_CATEGORIES = [
    { value: 'nda', label: 'Non-Disclosure Agreement' },
    { value: 'service_agreement', label: 'Service Agreement' },
    { value: 'employment', label: 'Employment Contract' },
    { value: 'purchase_order', label: 'Purchase Order' },
    { value: 'lease', label: 'Lease Agreement' },
    { value: 'partnership', label: 'Partnership Agreement' },
    { value: 'vendor', label: 'Vendor Agreement' },
    { value: 'other', label: 'Other' }
] as const

export type TemplateCategory = typeof TEMPLATE_CATEGORIES[number]['value']

// Category display helpers
export const CATEGORY_COLORS: Record<string, string> = {
    nda: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
    service_agreement: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    employment: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    purchase_order: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
    lease: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
    partnership: 'bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-200',
    vendor: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200',
    other: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200'
}

// Helper function to get category color
export function getCategoryColor(category: string | undefined): string {
    if (!category) return CATEGORY_COLORS.other
    return CATEGORY_COLORS[category] || CATEGORY_COLORS.other
}

// Helper function to get category label
export function getCategoryLabel(category: string | undefined): string {
    if (!category) return 'Other'
    const found = TEMPLATE_CATEGORIES.find(c => c.value === category)
    return found?.label || category
}
