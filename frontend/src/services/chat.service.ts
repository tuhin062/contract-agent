/**
 * Enhanced Chat Service
 * Handles RAG-powered chat with streaming, persistence, and advanced features
 */
import apiClient from './api'

// ============== Types ==============

export interface ChatMessage {
    role: 'user' | 'assistant' | 'system'
    content: string
}

export interface SourceCitation {
    text: string
    score: number
    file_id?: string
    filename?: string
    page?: number
    chunk_index?: number
}

export interface ExtractedClause {
    type: string
    text: string
    confidence: string
}

export interface RiskHighlight {
    severity: string
    matched_text: string
    context: string
    recommendation: string
}

export interface ChatRequest {
    messages: ChatMessage[]
    context_files: string[]
    conversation_id?: string
    top_k?: number
    stream?: boolean
}

export interface ChatResponse {
    answer: string
    sources: SourceCitation[]
    confidence: string
    retrieved_chunks: number
    model_used?: string
    tokens_used?: number
    follow_up_suggestions: string[]
    extracted_clauses: ExtractedClause[]
    risk_highlights: RiskHighlight[]
    conversation_id?: string
    response_time_ms?: number
}

export interface Conversation {
    id: string
    title?: string
    user_id: string
    status: string
    context_file_ids: string[]
    total_messages: number
    total_tokens_used: number
    model_used?: string
    created_at: string
    updated_at?: string
    last_message_at?: string
    messages?: ConversationMessage[]
}

export interface ConversationMessage {
    id: string
    conversation_id: string
    role: string
    content: string
    sources: SourceCitation[]
    confidence?: string
    retrieved_chunks: number
    follow_up_suggestions: string[]
    extracted_clauses: ExtractedClause[]
    risk_highlights: RiskHighlight[]
    tokens_used: number
    model_used?: string
    user_rating?: number
    user_feedback?: string
    created_at: string
}

export interface StreamEvent {
    type: 'sources' | 'content' | 'done' | 'error'
    data: any
}

// ============== Service ==============

export const chatService = {
    /**
     * Send a chat message (non-streaming)
     */
    async sendMessage(request: ChatRequest): Promise<ChatResponse> {
        const response = await apiClient.post<ChatResponse>('/chat/rag', request)
        return response.data
    },

    /**
     * Send a chat message with streaming response
     */
    async sendMessageStream(
        request: ChatRequest,
        onContent: (chunk: string) => void,
        onSources: (sources: SourceCitation[]) => void,
        onDone: (metadata: {
            confidence: string
            retrieved_chunks: number
            response_time_ms: number
            follow_up_suggestions: string[]
        }) => void,
        onError: (error: string) => void
    ): Promise<void> {
        const token = localStorage.getItem('access_token')
        
        const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'}/chat/rag/stream`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(request)
        })

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
            throw new Error(error.detail || 'Stream request failed')
        }

        const reader = response.body?.getReader()
        if (!reader) {
            throw new Error('No response body')
        }

        const decoder = new TextDecoder()
        let buffer = ''

        try {
            while (true) {
                const { done, value } = await reader.read()
                if (done) break

                buffer += decoder.decode(value, { stream: true })
                const lines = buffer.split('\n')
                buffer = lines.pop() || ''

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const event: StreamEvent = JSON.parse(line.slice(6))
                            
                            switch (event.type) {
                                case 'sources':
                                    onSources(event.data)
                                    break
                                case 'content':
                                    onContent(event.data)
                                    break
                                case 'done':
                                    onDone(event.data)
                                    break
                                case 'error':
                                    onError(event.data)
                                    break
                            }
                        } catch (e) {
                            // Ignore parse errors for incomplete chunks
                        }
                    }
                }
            }
        } finally {
            reader.releaseLock()
        }
    },

    /**
     * Create a new conversation
     */
    async createConversation(title?: string, contextFileIds?: string[]): Promise<Conversation> {
        const response = await apiClient.post<Conversation>('/chat/conversations', {
            title,
            context_file_ids: contextFileIds
        })
        return response.data
    },

    /**
     * Get user's conversations
     */
    async getConversations(status?: string, skip = 0, limit = 50): Promise<Conversation[]> {
        const params: any = { skip, limit }
        if (status) params.status = status
        
        const response = await apiClient.get<Conversation[]>('/chat/conversations', { params })
        return response.data
    },

    /**
     * Get conversation with messages
     */
    async getConversation(id: string): Promise<Conversation> {
        const response = await apiClient.get<Conversation>(`/chat/conversations/${id}`)
        return response.data
    },

    /**
     * Get messages for a conversation
     */
    async getMessages(conversationId: string, skip = 0, limit = 100): Promise<ConversationMessage[]> {
        const response = await apiClient.get<ConversationMessage[]>(
            `/chat/conversations/${conversationId}/messages`,
            { params: { skip, limit } }
        )
        return response.data
    },

    /**
     * Delete a conversation
     */
    async deleteConversation(id: string): Promise<void> {
        await apiClient.delete(`/chat/conversations/${id}`)
    },

    /**
     * Rate a message
     */
    async rateMessage(messageId: string, rating: number, feedback?: string): Promise<ConversationMessage> {
        const response = await apiClient.post<ConversationMessage>(
            `/chat/messages/${messageId}/rate`,
            { rating, feedback }
        )
        return response.data
    },

    /**
     * Check chat service health
     */
    async checkHealth(): Promise<{
        status: string
        pinecone: string
        llm: string
        embeddings: string
        models: {
            chat: string
            reasoning: string
            embeddings: string
        }
    }> {
        const response = await apiClient.get('/chat/health')
        return response.data
    }
}

export default chatService
