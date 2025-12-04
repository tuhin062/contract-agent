/**
 * Common types used across the application
 */

// Pagination parameters
export interface PaginationParams {
    skip?: number
    limit?: number
}

// Paginated response
export interface PaginatedResponse<T> {
    items: T[]
    total: number
    skip: number
    limit: number
    has_more: boolean
}

// API error response
export interface APIError {
    detail: string
    status_code?: number
}

// Upload response
export interface UploadResponse {
    id: string
    filename: string
    file_type: 'pdf' | 'docx' | 'txt' | 'other'
    size: number
    path: string
    text_extraction_status: 'pending' | 'processing' | 'completed' | 'failed'
    pages_count?: number
    uploaded_by: string
    uploaded_at: string
}

// Extracted text response
export interface ExtractedTextResponse {
    file_id: string
    status: 'pending' | 'processing' | 'completed' | 'failed'
    pages_count?: number
    text?: string
    chunks?: TextChunk[]
    error?: string
}

// Text chunk from extraction
export interface TextChunk {
    chunk_index: number
    text: string
    char_count: number
    token_estimate: number
    metadata?: {
        page?: number
        file_id?: string
    }
}

// Chat message
export interface ChatMessage {
    role: 'user' | 'assistant' | 'system'
    content: string
}

// Source citation from RAG
export interface SourceCitation {
    text: string
    score: number
    file_id?: string
    page?: number
    chunk_index?: number
}

// Chat request
export interface ChatRequest {
    session_id?: string
    messages: ChatMessage[]
    context_files: string[]
    top_k?: number
    model?: string
}

// Chat response
export interface ChatResponse {
    answer: string
    sources: SourceCitation[]
    confidence: 'high' | 'medium' | 'low' | 'error'
    retrieved_chunks: number
    model_used?: string
    tokens_used?: number
    session_id?: string
}

// Audit log entry
export interface AuditLogEntry {
    id: string
    user_id: string
    action: string
    resource_type: string
    resource_id?: string
    details: Record<string, any>
    ip_address?: string
    user_agent?: string
    created_at: string
}

// System statistics
export interface SystemStats {
    total_users: number
    active_users: number
    total_contracts: number
    pending_contracts: number
    total_audit_logs: number
    users_by_role: Record<string, number>
    contracts_by_status: Record<string, number>
}

// Model configuration
export interface ModelConfig {
    chat_model: string
    reasoning_model: string
    generation_model: string
    embedding_model: string
}
