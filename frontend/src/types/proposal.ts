export interface Proposal {
    id: string
    title: string
    uploadDate: string
    uploadedBy: string
    status: 'processed' | 'processing' | 'failed'
    metadata: ProposalMetadata
    pdfUrl?: string
}

export interface ProposalMetadata {
    projectName: string
    budget: number
    currency: string
    timeline: string
    scope: string[]
    requirements: string[]
    deliverables: string[]
    parties: string[]
    startDate?: string
    endDate?: string
}

export interface ProposalKeyInfo {
    totalValue: number
    duration: string
    keyTerms: string[]
    risks: string[]
}
