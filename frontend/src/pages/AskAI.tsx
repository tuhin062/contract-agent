import { useState, useRef, useEffect, useCallback } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { 
    Send, 
    Upload, 
    FileText, 
    Sparkles, 
    Loader2, 
    X, 
    MessageSquare,
    History,
    ChevronRight,
    AlertTriangle,
    CheckCircle2,
    Shield,
    ThumbsUp,
    ThumbsDown,
    Download,
    Trash2,
    RefreshCw
} from 'lucide-react'
import { toast } from '@/lib/toast'
import uploadService from '@/services/upload.service'
import chatService from '@/services/chat.service'
import type { 
    SourceCitation, 
    ExtractedClause, 
    RiskHighlight,
    Conversation
} from '@/services/chat.service'
import { cn } from '@/lib/utils'

interface Message {
    id: string
    role: 'user' | 'assistant'
    content: string
    timestamp: Date
    sources?: SourceCitation[]
    confidence?: string
    followUpSuggestions?: string[]
    extractedClauses?: ExtractedClause[]
    riskHighlights?: RiskHighlight[]
    isStreaming?: boolean
    responseTimeMs?: number
}

interface UploadedFile {
    id: string
    name: string
    size: number
}

export function AskAI() {
    // State
    const [messages, setMessages] = useState<Message[]>([
        {
            id: '1',
            role: 'assistant',
            content: "Hello! I'm your AI legal document assistant powered by Claude. Upload contracts or legal documents and ask me anything - I'll provide precise, fact-based answers with source citations.\n\n**What I can help with:**\n• Analyze contract terms and clauses\n• Identify potential risks and concerns\n• Explain legal terminology\n• Compare contract sections\n• Answer specific questions about your documents",
            timestamp: new Date()
        }
    ])
    const [input, setInput] = useState('')
    const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([])
    const [isUploading, setIsUploading] = useState(false)
    const [isTyping, setIsTyping] = useState(false)
    const [conversations, setConversations] = useState<Conversation[]>([])
    const [currentConversationId, setCurrentConversationId] = useState<string | null>(null)
    const [showHistory, setShowHistory] = useState(false)
    const [useStreaming, setUseStreaming] = useState(true)
    
    const messagesEndRef = useRef<HTMLDivElement>(null)
    const fileInputRef = useRef<HTMLInputElement>(null)

    // Auto-scroll to bottom
    const scrollToBottom = useCallback(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [])

    useEffect(() => {
        scrollToBottom()
    }, [messages, scrollToBottom])

    // Load conversation history
    useEffect(() => {
        // Only load if we have a user (after auth)
        if (currentConversationId === null) {
            loadConversations().catch(() => {
                // Silently fail - conversations are optional
            })
        }
    }, [])

    const loadConversations = async () => {
        try {
            // Use lowercase 'active' to match backend enum
            const convs = await chatService.getConversations('active')
            setConversations(convs)
        } catch (error) {
            // Silently fail - conversations are optional
            console.debug('Failed to load conversations:', error)
        }
    }

    // File upload handler
    const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = e.target.files
        if (!files || files.length === 0) return

        setIsUploading(true)
        const newFiles: UploadedFile[] = []

        for (const file of Array.from(files)) {
            // Validate file type
            const validExtensions = ['.pdf', '.docx', '.txt', '.doc']
            const hasValidExtension = validExtensions.some(ext => 
                file.name.toLowerCase().endsWith(ext)
            )

            if (!hasValidExtension) {
                toast.error('Invalid File', `${file.name} is not a supported format`)
                continue
            }

            try {
                const response = await uploadService.uploadFile(file)
                newFiles.push({
                    id: response.id,
                    name: file.name,
                    size: file.size
                })
                toast.success('Document Uploaded', `${file.name} is ready for analysis`)
            } catch (error: any) {
                console.error('Upload error:', error)
                let errorMessage = `Failed to upload ${file.name}`
                
                if (error.response) {
                    // Server responded with error
                    errorMessage = error.response.data?.detail || error.response.data?.message || errorMessage
                } else if (error.request) {
                    // Request made but no response
                    errorMessage = 'Network error: Could not reach server. Please check your connection.'
                } else {
                    // Error in request setup
                    errorMessage = error.message || errorMessage
                }
                
                toast.error('Upload Failed', errorMessage)
            }
        }

        if (newFiles.length > 0) {
            setUploadedFiles(prev => [...prev, ...newFiles])
            
            // Add system message
            const fileNames = newFiles.map(f => f.name).join(', ')
            const systemMessage: Message = {
                id: Date.now().toString(),
                role: 'assistant',
                content: `📄 **Documents Ready**\n\nI've received: ${fileNames}\n\nThe documents are being indexed for analysis. You can now ask questions about them!`,
                timestamp: new Date()
            }
            setMessages(prev => [...prev, systemMessage])
        }

        setIsUploading(false)
        if (fileInputRef.current) {
            fileInputRef.current.value = ''
        }
    }

    // Remove uploaded file
    const removeFile = (fileId: string) => {
        setUploadedFiles(prev => prev.filter(f => f.id !== fileId))
        toast.info('File Removed', 'The document has been removed from context')
    }

    // Send message handler
    const handleSend = async () => {
        if (!input.trim() || isTyping) return

        const userMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: input,
            timestamp: new Date()
        }
        setMessages(prev => [...prev, userMessage])
        setInput('')
        setIsTyping(true)

        // Create placeholder for streaming response
        const aiMessageId = (Date.now() + 1).toString()
        
        if (useStreaming) {
            // Streaming response
            setMessages(prev => [...prev, {
                id: aiMessageId,
                role: 'assistant',
                content: '',
                timestamp: new Date(),
                isStreaming: true
            }])

            try {
                await chatService.sendMessageStream(
                    {
                        messages: messages.slice(-10).map(m => ({
                            role: m.role,
                            content: m.content
                        })).concat([{ role: 'user', content: input }]),
                        context_files: uploadedFiles.map(f => f.id),
                        conversation_id: currentConversationId || undefined,
                        top_k: 8
                    },
                    // onContent
                    (chunk) => {
                        setMessages(prev => prev.map(m => 
                            m.id === aiMessageId
                                ? { ...m, content: m.content + chunk }
                                : m
                        ))
                    },
                    // onSources
                    (sources) => {
                        setMessages(prev => prev.map(m =>
                            m.id === aiMessageId
                                ? { ...m, sources }
                                : m
                        ))
                    },
                    // onDone
                    (metadata) => {
                        setMessages(prev => prev.map(m =>
                            m.id === aiMessageId
                                ? {
                                    ...m,
                                    isStreaming: false,
                                    confidence: metadata.confidence,
                                    followUpSuggestions: metadata.follow_up_suggestions,
                                    responseTimeMs: metadata.response_time_ms
                                }
                                : m
                        ))
                        setIsTyping(false)
                    },
                    // onError
                    (error) => {
                        setMessages(prev => prev.map(m =>
                            m.id === aiMessageId
                                ? { ...m, content: `Error: ${error}`, isStreaming: false }
                                : m
                        ))
                        setIsTyping(false)
                        toast.error('Chat Error', error)
                    }
                )
            } catch (error: any) {
                setMessages(prev => prev.map(m =>
                    m.id === aiMessageId
                        ? { ...m, content: 'Failed to get response. Please try again.', isStreaming: false }
                        : m
                ))
                setIsTyping(false)
                toast.error('Connection Error', error.message)
            }
        } else {
            // Non-streaming response
            try {
                const response = await chatService.sendMessage({
                    messages: messages.slice(-10).map(m => ({
                        role: m.role,
                        content: m.content
                    })).concat([{ role: 'user', content: input }]),
                    context_files: uploadedFiles.map(f => f.id),
                    conversation_id: currentConversationId || undefined,
                    top_k: 8
                })

                const aiMessage: Message = {
                    id: aiMessageId,
                    role: 'assistant',
                    content: response.answer,
                    timestamp: new Date(),
                    sources: response.sources,
                    confidence: response.confidence,
                    followUpSuggestions: response.follow_up_suggestions,
                    extractedClauses: response.extracted_clauses,
                    riskHighlights: response.risk_highlights,
                    responseTimeMs: response.response_time_ms
                }
                setMessages(prev => [...prev, aiMessage])

                if (response.conversation_id) {
                    setCurrentConversationId(response.conversation_id)
                }
            } catch (error: any) {
                const errorMessage: Message = {
                    id: aiMessageId,
                    role: 'assistant',
                    content: error.response?.data?.detail || 'Failed to process your request. Please try again.',
                    timestamp: new Date()
                }
                setMessages(prev => [...prev, errorMessage])
                toast.error('Error', 'Failed to get AI response')
            } finally {
                setIsTyping(false)
            }
        }
    }

    // Handle follow-up click
    const handleFollowUp = (question: string) => {
        setInput(question)
    }

    // Handle keyboard
    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            handleSend()
        }
    }

    // New conversation
    const startNewConversation = () => {
        setMessages([{
            id: '1',
            role: 'assistant',
            content: "Starting a fresh conversation. How can I help you with your legal documents today?",
            timestamp: new Date()
        }])
        setCurrentConversationId(null)
        setShowHistory(false)
    }

    // Load conversation from history
    const loadConversation = async (conv: Conversation) => {
        try {
            const fullConv = await chatService.getConversation(conv.id)
            if (fullConv.messages) {
                setMessages(fullConv.messages.map(m => ({
                    id: m.id,
                    role: m.role as 'user' | 'assistant',
                    content: m.content,
                    timestamp: new Date(m.created_at),
                    sources: m.sources,
                    confidence: m.confidence,
                    followUpSuggestions: m.follow_up_suggestions,
                    extractedClauses: m.extracted_clauses,
                    riskHighlights: m.risk_highlights
                })))
            }
            setCurrentConversationId(conv.id)
            setShowHistory(false)
        } catch (error) {
            toast.error('Error', 'Failed to load conversation')
        }
    }

    // Get confidence badge
    const getConfidenceBadge = (confidence?: string) => {
        if (!confidence) return null
        
        const colors = {
            high: 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300',
            medium: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300',
            low: 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300'
        }
        
        const icons = {
            high: <CheckCircle2 className="h-3 w-3" />,
            medium: <AlertTriangle className="h-3 w-3" />,
            low: <AlertTriangle className="h-3 w-3" />
        }
        
        return (
            <Badge className={cn('gap-1', colors[confidence as keyof typeof colors])}>
                {icons[confidence as keyof typeof icons]}
                {confidence} confidence
            </Badge>
        )
    }

    return (
        <div className="flex h-[calc(100vh-8rem)] gap-4 page-enter">
            {/* Conversation History Sidebar */}
            {showHistory && (
                <Card className="w-80 flex-shrink-0 flex flex-col">
                    <CardHeader className="pb-3">
                        <div className="flex items-center justify-between">
                            <CardTitle className="text-lg">Conversations</CardTitle>
                            <Button variant="ghost" size="icon" onClick={() => setShowHistory(false)}>
                                <X className="h-4 w-4" />
                            </Button>
                        </div>
                    </CardHeader>
                    <CardContent className="flex-1 overflow-y-auto space-y-2">
                        {conversations.length === 0 ? (
                            <p className="text-sm text-muted-foreground text-center py-4">
                                No previous conversations
                            </p>
                        ) : (
                            conversations.map(conv => (
                                <button
                                    key={conv.id}
                                    onClick={() => loadConversation(conv)}
                                    className={cn(
                                        "w-full text-left p-3 rounded-lg hover:bg-accent transition-colors",
                                        currentConversationId === conv.id && "bg-accent"
                                    )}
                                >
                                    <p className="font-medium truncate">
                                        {conv.title || 'Untitled Conversation'}
                                    </p>
                                    <p className="text-xs text-muted-foreground">
                                        {conv.total_messages} messages • {new Date(conv.created_at).toLocaleDateString()}
                                    </p>
                                </button>
                            ))
                        )}
                    </CardContent>
                </Card>
            )}

            {/* Main Chat Area */}
            <div className="flex-1 flex flex-col min-w-0">
                {/* Header */}
                <div className="mb-4">
                    <div className="flex items-center justify-between gap-4">
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg">
                                <Sparkles className="h-6 w-6 text-white" />
                            </div>
                            <div>
                                <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                                    Ask AI
                                </h1>
                                <p className="text-sm text-muted-foreground">
                                    Powered by Claude 3.5 Sonnet • Legal-grade accuracy
                                </p>
                            </div>
                        </div>

                        <div className="flex items-center gap-2">
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={() => setShowHistory(!showHistory)}
                            >
                                <History className="h-4 w-4 mr-2" />
                                History
                            </Button>
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={startNewConversation}
                            >
                                <MessageSquare className="h-4 w-4 mr-2" />
                                New Chat
                            </Button>
                        </div>
                    </div>

                    {/* Uploaded Files */}
                    {uploadedFiles.length > 0 && (
                        <div className="mt-4 flex flex-wrap gap-2">
                            {uploadedFiles.map(file => (
                                <Badge
                                    key={file.id}
                                    variant="secondary"
                                    className="gap-2 py-1.5 px-3"
                                >
                                    <FileText className="h-3.5 w-3.5" />
                                    <span className="max-w-[150px] truncate">{file.name}</span>
                                    <button
                                        onClick={() => removeFile(file.id)}
                                        className="hover:text-destructive"
                                    >
                                        <X className="h-3 w-3" />
                                    </button>
                                </Badge>
                            ))}
                        </div>
                    )}
                </div>

                {/* Upload Area (when no files) */}
                {uploadedFiles.length === 0 && (
                    <Card className="mb-4 p-4 border-2 border-dashed hover:border-primary transition-all cursor-pointer bg-gradient-to-br from-purple-50/50 to-pink-50/50 dark:from-purple-950/20 dark:to-pink-950/20">
                        <input
                            ref={fileInputRef}
                            type="file"
                            accept=".pdf,.docx,.txt,.doc"
                            onChange={handleFileUpload}
                            className="hidden"
                            multiple
                            disabled={isUploading}
                        />
                        <div
                            className="flex items-center justify-center gap-4"
                            onClick={() => fileInputRef.current?.click()}
                        >
                            <div className="p-3 bg-purple-100 dark:bg-purple-900 rounded-full">
                                {isUploading ? (
                                    <Loader2 className="h-6 w-6 text-purple-600 dark:text-purple-400 animate-spin" />
                                ) : (
                                    <Upload className="h-6 w-6 text-purple-600 dark:text-purple-400" />
                                )}
                            </div>
                            <div>
                                <p className="font-medium">
                                    {isUploading ? 'Uploading...' : 'Upload documents to get started'}
                                </p>
                                <p className="text-sm text-muted-foreground">
                                    PDF, DOCX, DOC, TXT • Multiple files supported
                                </p>
                            </div>
                        </div>
                    </Card>
                )}

                {/* Chat Messages */}
                <Card className="flex-1 flex flex-col overflow-hidden">
                    <div className="flex-1 overflow-y-auto p-4 space-y-4">
                        {messages.map((message) => (
                            <div
                                key={message.id}
                                className={cn(
                                    'flex gap-3',
                                    message.role === 'user' && 'flex-row-reverse'
                                )}
                            >
                                {/* Avatar */}
                                <div className={cn(
                                    'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center',
                                    message.role === 'user'
                                        ? 'bg-gradient-to-br from-blue-500 to-cyan-500'
                                        : 'bg-gradient-to-br from-purple-500 to-pink-500'
                                )}>
                                    {message.role === 'user' ? (
                                        <span className="text-white text-sm font-medium">U</span>
                                    ) : (
                                        <Sparkles className="h-4 w-4 text-white" />
                                    )}
                                </div>

                                {/* Message Content */}
                                <div className={cn(
                                    'flex-1 max-w-[85%] flex flex-col gap-2',
                                    message.role === 'user' && 'items-end'
                                )}>
                                    <div className={cn(
                                        'rounded-2xl px-4 py-3',
                                        message.role === 'user'
                                            ? 'bg-gradient-to-br from-blue-500 to-cyan-500 text-white'
                                            : 'bg-muted'
                                    )}>
                                        <div className="text-sm whitespace-pre-wrap prose prose-sm dark:prose-invert max-w-none">
                                            {message.content}
                                            {message.isStreaming && (
                                                <span className="inline-block w-2 h-4 ml-1 bg-current animate-pulse" />
                                            )}
                                        </div>
                                    </div>

                                    {/* Metadata for assistant messages */}
                                    {message.role === 'assistant' && !message.isStreaming && (
                                        <div className="space-y-2 ml-2">
                                            {/* Confidence & Response Time */}
                                            <div className="flex items-center gap-2 flex-wrap">
                                                {getConfidenceBadge(message.confidence)}
                                                {message.responseTimeMs && (
                                                    <span className="text-xs text-muted-foreground">
                                                        {message.responseTimeMs}ms
                                                    </span>
                                                )}
                                            </div>

                                            {/* Sources */}
                                            {message.sources && message.sources.length > 0 && (
                                                <div className="text-xs space-y-1">
                                                    <p className="font-medium text-muted-foreground">
                                                        📚 Sources ({message.sources.length}):
                                                    </p>
                                                    <div className="flex flex-wrap gap-1">
                                                        {message.sources.slice(0, 4).map((src, idx) => (
                                                            <Badge
                                                                key={idx}
                                                                variant="outline"
                                                                className="text-[10px]"
                                                            >
                                                                {src.filename || `Source ${idx + 1}`}
                                                                {src.page && ` p.${src.page}`}
                                                                • {(src.score * 100).toFixed(0)}%
                                                            </Badge>
                                                        ))}
                                                    </div>
                                                </div>
                                            )}

                                            {/* Risk Highlights */}
                                            {message.riskHighlights && message.riskHighlights.length > 0 && (
                                                <div className="text-xs">
                                                    <p className="font-medium text-muted-foreground flex items-center gap-1">
                                                        <Shield className="h-3 w-3" />
                                                        Risks Identified:
                                                    </p>
                                                    <div className="flex flex-wrap gap-1 mt-1">
                                                        {message.riskHighlights.slice(0, 3).map((risk, idx) => (
                                                            <Badge
                                                                key={idx}
                                                                variant={risk.severity === 'high' ? 'destructive' : 'secondary'}
                                                                className="text-[10px]"
                                                            >
                                                                {risk.matched_text}
                                                            </Badge>
                                                        ))}
                                                    </div>
                                                </div>
                                            )}

                                            {/* Follow-up Suggestions */}
                                            {message.followUpSuggestions && message.followUpSuggestions.length > 0 && (
                                                <div className="space-y-1">
                                                    <p className="text-xs font-medium text-muted-foreground">
                                                        💡 Suggested follow-ups:
                                                    </p>
                                                    <div className="flex flex-wrap gap-1">
                                                        {message.followUpSuggestions.map((q, idx) => (
                                                            <button
                                                                key={idx}
                                                                onClick={() => handleFollowUp(q)}
                                                                className="text-xs px-2 py-1 rounded-full border hover:bg-accent transition-colors flex items-center gap-1"
                                                            >
                                                                <ChevronRight className="h-3 w-3" />
                                                                {q}
                                                            </button>
                                                        ))}
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    )}

                                    <span className="text-xs text-muted-foreground ml-2">
                                        {message.timestamp.toLocaleTimeString()}
                                    </span>
                                </div>
                            </div>
                        ))}

                        {/* Typing Indicator */}
                        {isTyping && !messages.some(m => m.isStreaming) && (
                            <div className="flex gap-3">
                                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                                    <Sparkles className="h-4 w-4 text-white" />
                                </div>
                                <div className="bg-muted rounded-2xl px-4 py-3">
                                    <div className="flex gap-1">
                                        <div className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce" style={{ animationDelay: '0ms' }} />
                                        <div className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce" style={{ animationDelay: '150ms' }} />
                                        <div className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce" style={{ animationDelay: '300ms' }} />
                                    </div>
                                </div>
                            </div>
                        )}

                        <div ref={messagesEndRef} />
                    </div>

                    {/* Input Area */}
                    <div className="border-t p-4">
                        <div className="flex gap-3">
                            <Button
                                variant="outline"
                                size="icon"
                                onClick={() => fileInputRef.current?.click()}
                                disabled={isUploading}
                                title="Upload more documents"
                            >
                                {isUploading ? (
                                    <Loader2 className="h-4 w-4 animate-spin" />
                                ) : (
                                    <Upload className="h-4 w-4" />
                                )}
                            </Button>
                            
                            <Textarea
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={handleKeyPress}
                                placeholder={uploadedFiles.length > 0 
                                    ? "Ask a question about your documents..." 
                                    : "Upload a document first, or ask a general legal question..."
                                }
                                className="min-h-[50px] max-h-[120px] resize-none"
                                disabled={isTyping}
                            />
                            
                            <Button
                                onClick={handleSend}
                                disabled={!input.trim() || isTyping}
                                size="icon"
                                className="h-[50px] w-[50px] bg-gradient-to-br from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600"
                            >
                                {isTyping ? (
                                    <Loader2 className="h-5 w-5 animate-spin" />
                                ) : (
                                    <Send className="h-5 w-5" />
                                )}
                            </Button>
                        </div>
                        
                        <div className="flex items-center justify-between mt-2 text-xs text-muted-foreground">
                            <span>
                                {uploadedFiles.length} document{uploadedFiles.length !== 1 ? 's' : ''} in context
                            </span>
                            <span>
                                Press Enter to send • Shift+Enter for new line
                            </span>
                        </div>
                    </div>
                </Card>
            </div>
        </div>
    )
}
