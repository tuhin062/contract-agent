/**
 * Contract types aligned with backend schemas
 */

// Contract status matching backend enum
export type ContractStatus = 
    | 'draft' 
    | 'pending_review' 
    | 'approved' 
    | 'rejected' 
    | 'executed' 
    | 'archived'

// Contract base interface
export interface Contract {
    id: string
    title: string
    description?: string
    content: string
    status: ContractStatus
    version: number
    is_latest_version: boolean
    parent_contract_id?: string
    template_id?: string
    custom_metadata: Record<string, any>
    created_by: string
    reviewed_by?: string
    approved_by?: string
    review_notes?: string
    rejection_reason?: string
    created_at: string
    updated_at?: string
    submitted_at?: string
    reviewed_at?: string
    executed_at?: string
}

// Contract list item (lighter version)
export interface ContractListItem {
    id: string
    title: string
    status: ContractStatus
    version: number
    is_latest_version: boolean
    created_by: string
    created_at: string
    updated_at?: string
}

// Contract creation request
export interface ContractCreate {
    title: string
    description?: string
    content: string
    template_id?: string
    metadata?: Record<string, any>
}

// Contract update request
export interface ContractUpdate {
    title?: string
    description?: string
    content?: string
    metadata?: Record<string, any>
}

// Generate from template request
export interface GenerateFromTemplate {
    template_id: string
    title: string
    values: Record<string, string>
    description?: string
    metadata?: Record<string, any>
}

// Contract review
export interface ContractReview {
    notes?: string
}

// Contract rejection
export interface ContractRejection {
    reason: string
}

// Contract filters
export interface ContractFilters {
    status?: ContractStatus
    template_id?: string
    latest_only?: boolean
    skip?: number
    limit?: number
}

// Contract version for history
export interface ContractVersion {
    id: string
    version: number
    status: ContractStatus
    created_at: string
    created_by: string
}

// Contract insights (from validation)
export interface ContractInsight {
    summary?: string
    keyClauses: KeyClause[]
    risks: RiskItem[]
    recommendations: string[]
}

export interface KeyClause {
    name: string
    description: string
    location?: string
    risk_level?: string
}

export type ClauseCategory = 
    | 'payment' 
    | 'termination' 
    | 'liability' 
    | 'confidentiality' 
    | 'ip_rights' 
    | 'dispute_resolution' 
    | 'other'

export interface RiskItem {
    severity: 'low' | 'medium' | 'high' | 'critical'
    message: string
    location?: string
    suggestion?: string
}

// Contract with full details
export interface ContractDetail extends Contract {
    insights?: ContractInsight
    versions?: ContractVersion[]
}

// Status display helpers
export const CONTRACT_STATUS_LABELS: Record<ContractStatus, string> = {
    draft: 'Draft',
    pending_review: 'Pending Review',
    approved: 'Approved',
    rejected: 'Rejected',
    executed: 'Executed',
    archived: 'Archived'
}

export const CONTRACT_STATUS_COLORS: Record<ContractStatus, string> = {
    draft: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200',
    pending_review: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
    approved: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    rejected: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
    executed: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    archived: 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400'
}

// Helper functions for status display
export function formatStatus(status: ContractStatus): string {
    return CONTRACT_STATUS_LABELS[status] || status
}

export function getStatusColor(status: ContractStatus): string {
    return CONTRACT_STATUS_COLORS[status] || CONTRACT_STATUS_COLORS.draft
}
