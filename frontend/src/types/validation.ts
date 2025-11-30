export interface ValidationResult {
    id: string
    contractId?: string
    contractName: string
    proposalId: string
    proposalName: string
    validatedAt: string
    overallScore: number
    status: 'passed' | 'failed' | 'warning'
    extractedClauses: ExtractedClause[]
    riskFlags: RiskFlag[]
    clauseComparisons: ClauseComparison[]
}

export interface ExtractedClause {
    id: string
    title: string
    content: string
    page: number
    confidence: number
    category: string
}

export interface RiskFlag {
    id: string
    severity: 'low' | 'medium' | 'high' | 'critical'
    category: string
    title: string
    description: string
    clause: string
    recommendation: string
    impact: string
}

export interface ClauseComparison {
    id: string
    clauseName: string
    contractValue: string
    proposalValue: string
    match: 'exact' | 'partial' | 'mismatch' | 'missing'
    notes: string
}

export interface ValidationReport {
    validationId: string
  generated At: string
summary: string
details: ValidationResult
}
