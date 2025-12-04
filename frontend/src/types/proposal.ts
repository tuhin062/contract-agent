/**
 * Proposal types aligned with backend schemas
 */

// Validation status
export type ValidationStatus = 'pending' | 'in_progress' | 'completed' | 'failed'

// Risk level
export type RiskLevel = 'low' | 'medium' | 'high' | 'critical'

// Proposal interface
export interface Proposal {
    id: string
    title: string
    description?: string
    contract_id?: string
    validation_status: ValidationStatus
    risk_level?: RiskLevel
    risk_score?: number
    validation_report: ValidationReport
    detected_clauses: DetectedClause[]
    compliance_checks: Record<string, any>
    created_by: string
    created_at: string
    updated_at?: string
    validated_at?: string
}

// Proposal list item
export interface ProposalListItem {
    id: string
    title: string
    validation_status: ValidationStatus
    risk_level?: RiskLevel
    risk_score?: number
    created_by: string
    created_at: string
    validated_at?: string
}

// Proposal creation
export interface ProposalCreate {
    title: string
    description?: string
    contract_id?: string
    upload_id?: string
}

// Proposal statistics
export interface ProposalStats {
    total: number
    pending: number
    in_progress: number
    completed: number
    failed: number
}

// Validation request
export interface ValidateContractRequest {
    contract_type?: string
    create_proposal?: boolean
    custom_checks?: string[]
}

// Validation issue
export interface ValidationIssue {
    severity: 'low' | 'medium' | 'high' | 'critical'
    message: string
    location?: string
    suggestion?: string
}

// Detected clause
export interface DetectedClause {
    name: string
    description: string
    location?: string
    risk_level?: string
}

// Validation report
export interface ValidationReport {
    issues?: ValidationIssue[]
    suggestions?: string[]
    clauses?: DetectedClause[]
    compliance?: Record<string, any>
    raw_analysis?: string
    error?: string
}

// Full validation response
export interface ValidationResponse {
    proposal_id?: string
    risk_score: number
    risk_level: string
    issues: ValidationIssue[]
    suggestions: string[]
    clauses: DetectedClause[]
    compliance: Record<string, any>
    raw_analysis?: string
}

// Status display helpers
export const VALIDATION_STATUS_LABELS: Record<ValidationStatus, string> = {
    pending: 'Pending',
    in_progress: 'In Progress',
    completed: 'Completed',
    failed: 'Failed'
}

export const VALIDATION_STATUS_COLORS: Record<ValidationStatus, string> = {
    pending: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200',
    in_progress: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    completed: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    failed: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
}

export const RISK_LEVEL_LABELS: Record<RiskLevel, string> = {
    low: 'Low Risk',
    medium: 'Medium Risk',
    high: 'High Risk',
    critical: 'Critical Risk'
}

export const RISK_LEVEL_COLORS: Record<RiskLevel, string> = {
    low: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    medium: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
    high: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
    critical: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
}
