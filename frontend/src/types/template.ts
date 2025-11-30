export type TemplateCategory = 'employment' | 'vendor' | 'partnership' | 'legal' | 'real_estate' | 'other'

export interface Template {
    id: string
    name: string
    category: TemplateCategory
    description: string
    version: string
    lastUpdated: string
    fields: TemplateField[]
    previewUrl?: string
}

export interface TemplateField {
    id: string
    name: string
    label: string
    type: 'text' | 'textarea' | 'date' | 'number' | 'select' | 'multiselect'
    required: boolean
    placeholder?: string
    options?: string[]
    defaultValue?: string | number
    validation?: FieldValidation
}

export interface FieldValidation {
    min?: number
    max?: number
    pattern?: string
    errorMessage?: string
}

export interface GeneratedContract {
    templateId: string
    templateName: string
    generatedContent: string
    fieldValues: Record<string, unknown>
    generatedAt: string
}
