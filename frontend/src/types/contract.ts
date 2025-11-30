export type ContractStatus = 'draft' | 'active' | 'expired' | 'terminated' | 'pending_approval'
export type ContractType = 'nda' | 'employment' | 'vendor' | 'partnership' | 'service_agreement' | 'lease' | 'other'

export interface Contract {
    id: string
    title: string
    type: ContractType
    status: ContractStatus
    parties: string[]
    startDate: string
    endDate: string | null
    owner: string
    pdfUrl: string
    createdAt: string
    updatedAt: string
    tags: string[]
}

export interface ContractMetadata {
    contractValue?: number
    currency?: string
    renewalTerms?: string
    terminationClause?: string
    governingLaw?: string
    signatories?: string[]
}

export interface ContractInsight {
    summary: string
    keyClauses: KeyClause[]
    risks: RiskItem[]
    recommendations: string[]
}

export interface KeyClause {
    title: string
    content: string
    page: number
    category: ClauseCategory
}

export type ClauseCategory = 'payment' | 'termination' | 'liability' | 'confidentiality' | 'ip_rights' | 'dispute_resolution' | 'other'

export interface RiskItem {
    id: string
    severity: 'low' | 'medium' | 'high' | 'critical'
    title: string
    description: string
    recommendation: string
}

export interface ContractVersion {
    id: string
    version: string
    uploadedBy: string
    uploadedAt: string
    changes: string
    pdfUrl: string
}

export interface ContractDetail extends Contract {
    metadata: ContractMetadata
    insights: ContractInsight
    versions: ContractVersion[]
}
