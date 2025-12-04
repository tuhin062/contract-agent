import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, FileText, Clock, X, Loader2 } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import chatService from '@/services/chat.service'
import { useDebounce } from '@/hooks/useDebounce'

interface SearchResult {
    id: string
    title: string
    type: 'contract' | 'template' | 'document'
    snippet: string
    score: number
}

export function SemanticSearch() {
    const navigate = useNavigate()
    const [isOpen, setIsOpen] = useState(false)
    const [query, setQuery] = useState('')
    const [results, setResults] = useState<SearchResult[]>([])
    const [isSearching, setIsSearching] = useState(false)
    const [recentSearches, setRecentSearches] = useState<string[]>([])
    const inputRef = useRef<HTMLInputElement>(null)
    const containerRef = useRef<HTMLDivElement>(null)
    
    const debouncedQuery = useDebounce(query, 300)

    // Load recent searches from localStorage
    useEffect(() => {
        const stored = localStorage.getItem('recentSearches')
        if (stored) {
            setRecentSearches(JSON.parse(stored))
        }
    }, [])

    // Save recent search
    const saveRecentSearch = (searchQuery: string) => {
        const updated = [searchQuery, ...recentSearches.filter(s => s !== searchQuery)].slice(0, 5)
        setRecentSearches(updated)
        localStorage.setItem('recentSearches', JSON.stringify(updated))
    }

    // Search when query changes
    useEffect(() => {
        if (debouncedQuery.length < 2) {
            setResults([])
            return
        }

        const search = async () => {
            setIsSearching(true)
            try {
                // Use RAG to search across documents
                const response = await chatService.sendMessage({
                    messages: [{ role: 'user', content: debouncedQuery }],
                    context_files: [],
                    top_k: 5
                })

                // Convert sources to search results
                const searchResults: SearchResult[] = response.sources.map((source, idx) => ({
                    id: source.file_id || `result-${idx}`,
                    title: `Document Result ${idx + 1}`,
                    type: 'document' as const,
                    snippet: source.text.slice(0, 150) + '...',
                    score: source.score
                }))

                setResults(searchResults)
            } catch (error) {
                console.error('Search error:', error)
                setResults([])
            } finally {
                setIsSearching(false)
            }
        }

        search()
    }, [debouncedQuery])

    // Handle click outside
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
                setIsOpen(false)
            }
        }

        document.addEventListener('mousedown', handleClickOutside)
        return () => document.removeEventListener('mousedown', handleClickOutside)
    }, [])

    // Keyboard shortcut
    useEffect(() => {
        const handleKeyDown = (event: KeyboardEvent) => {
            if ((event.metaKey || event.ctrlKey) && event.key === 'k') {
                event.preventDefault()
                setIsOpen(true)
                setTimeout(() => inputRef.current?.focus(), 100)
            }
            if (event.key === 'Escape') {
                setIsOpen(false)
            }
        }

        document.addEventListener('keydown', handleKeyDown)
        return () => document.removeEventListener('keydown', handleKeyDown)
    }, [])

    const handleSelect = (result: SearchResult) => {
        saveRecentSearch(query)
        setIsOpen(false)
        setQuery('')
        
        if (result.type === 'contract') {
            navigate(`/contracts/${result.id}`)
        } else if (result.type === 'template') {
            navigate(`/templates/${result.id}`)
        } else {
            // For documents, go to Ask AI with context
            navigate('/ask-ai')
        }
    }

    const handleRecentSearch = (search: string) => {
        setQuery(search)
        inputRef.current?.focus()
    }

    const clearRecentSearches = () => {
        setRecentSearches([])
        localStorage.removeItem('recentSearches')
    }

    return (
        <div ref={containerRef} className="relative">
            {/* Search Trigger */}
            <Button
                variant="outline"
                className="w-64 justify-start text-muted-foreground"
                onClick={() => {
                    setIsOpen(true)
                    setTimeout(() => inputRef.current?.focus(), 100)
                }}
            >
                <Search className="mr-2 h-4 w-4" />
                <span>Search contracts...</span>
                <kbd className="ml-auto pointer-events-none inline-flex h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium">
                    <span className="text-xs">⌘</span>K
                </kbd>
            </Button>

            {/* Search Modal */}
            {isOpen && (
                <div className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm flex items-start justify-center pt-[20vh]">
                    <Card className="w-full max-w-2xl shadow-2xl">
                        {/* Search Input */}
                        <div className="flex items-center border-b px-4">
                            {isSearching ? (
                                <Loader2 className="h-4 w-4 text-muted-foreground animate-spin" />
                            ) : (
                                <Search className="h-4 w-4 text-muted-foreground" />
                            )}
                            <Input
                                ref={inputRef}
                                value={query}
                                onChange={(e) => setQuery(e.target.value)}
                                placeholder="Search contracts, templates, and documents..."
                                className="border-0 focus-visible:ring-0 text-lg"
                            />
                            <Button variant="ghost" size="icon" onClick={() => setIsOpen(false)}>
                                <X className="h-4 w-4" />
                            </Button>
                        </div>

                        {/* Results */}
                        <div className="max-h-96 overflow-y-auto p-2">
                            {/* No query - show recent searches */}
                            {query.length < 2 && recentSearches.length > 0 && (
                                <div className="p-2">
                                    <div className="flex items-center justify-between mb-2">
                                        <span className="text-xs text-muted-foreground font-medium">Recent Searches</span>
                                        <Button variant="ghost" size="sm" className="h-6 text-xs" onClick={clearRecentSearches}>
                                            Clear
                                        </Button>
                                    </div>
                                    {recentSearches.map((search, idx) => (
                                        <button
                                            key={idx}
                                            className="flex items-center gap-2 w-full p-2 rounded hover:bg-muted text-left"
                                            onClick={() => handleRecentSearch(search)}
                                        >
                                            <Clock className="h-4 w-4 text-muted-foreground" />
                                            <span className="text-sm">{search}</span>
                                        </button>
                                    ))}
                                </div>
                            )}

                            {/* Search results */}
                            {results.length > 0 && (
                                <div className="p-2">
                                    <span className="text-xs text-muted-foreground font-medium px-2">Results</span>
                                    {results.map((result) => (
                                        <button
                                            key={result.id}
                                            className="flex items-start gap-3 w-full p-3 rounded hover:bg-muted text-left mt-1"
                                            onClick={() => handleSelect(result)}
                                        >
                                            <FileText className="h-4 w-4 text-muted-foreground mt-0.5" />
                                            <div className="flex-1 min-w-0">
                                                <div className="flex items-center gap-2">
                                                    <span className="font-medium text-sm">{result.title}</span>
                                                    <Badge variant="outline" className="text-xs">
                                                        {Math.round(result.score * 100)}%
                                                    </Badge>
                                                </div>
                                                <p className="text-xs text-muted-foreground truncate mt-1">
                                                    {result.snippet}
                                                </p>
                                            </div>
                                        </button>
                                    ))}
                                </div>
                            )}

                            {/* No results */}
                            {query.length >= 2 && results.length === 0 && !isSearching && (
                                <div className="p-8 text-center text-muted-foreground">
                                    <Search className="h-8 w-8 mx-auto mb-2 opacity-50" />
                                    <p>No results found for "{query}"</p>
                                </div>
                            )}
                        </div>

                        {/* Footer */}
                        <div className="border-t px-4 py-2 flex items-center gap-4 text-xs text-muted-foreground">
                            <span>↑↓ to navigate</span>
                            <span>↵ to select</span>
                            <span>esc to close</span>
                        </div>
                    </Card>
                </div>
            )}
        </div>
    )
}

export default SemanticSearch

