import { Component, ErrorInfo, ReactNode } from 'react'
import { AlertTriangle, RefreshCw, Home } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'

interface Props {
    children: ReactNode
    fallback?: ReactNode
}

interface State {
    hasError: boolean
    error: Error | null
    errorInfo: ErrorInfo | null
}

export class ErrorBoundary extends Component<Props, State> {
    public state: State = {
        hasError: false,
        error: null,
        errorInfo: null
    }

    public static getDerivedStateFromError(error: Error): State {
        return { hasError: true, error, errorInfo: null }
    }

    public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        console.error('Error caught by boundary:', error, errorInfo)
        this.setState({ errorInfo })
        
        // In production, send to error tracking service
        // Example: Sentry.captureException(error)
    }

    private handleReset = () => {
        this.setState({ hasError: false, error: null, errorInfo: null })
    }

    private handleReload = () => {
        window.location.reload()
    }

    private handleGoHome = () => {
        window.location.href = '/dashboard'
    }

    public render() {
        if (this.state.hasError) {
            if (this.props.fallback) {
                return this.props.fallback
            }

            return (
                <div className="min-h-[400px] flex items-center justify-center p-6">
                    <Card className="max-w-lg w-full">
                        <CardHeader className="text-center">
                            <div className="mx-auto mb-4 p-3 bg-red-100 dark:bg-red-900/30 rounded-full w-fit">
                                <AlertTriangle className="h-8 w-8 text-red-600 dark:text-red-400" />
                            </div>
                            <CardTitle>Something went wrong</CardTitle>
                            <CardDescription>
                                An unexpected error occurred. We've been notified and are working to fix it.
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            {process.env.NODE_ENV === 'development' && this.state.error && (
                                <div className="p-3 bg-muted rounded-lg text-sm">
                                    <p className="font-mono text-red-600 dark:text-red-400">
                                        {this.state.error.message}
                                    </p>
                                    {this.state.errorInfo && (
                                        <pre className="mt-2 text-xs overflow-auto max-h-32 text-muted-foreground">
                                            {this.state.errorInfo.componentStack}
                                        </pre>
                                    )}
                                </div>
                            )}
                            
                            <div className="flex gap-2 justify-center">
                                <Button variant="outline" onClick={this.handleReset}>
                                    <RefreshCw className="mr-2 h-4 w-4" />
                                    Try Again
                                </Button>
                                <Button variant="outline" onClick={this.handleReload}>
                                    Reload Page
                                </Button>
                                <Button onClick={this.handleGoHome}>
                                    <Home className="mr-2 h-4 w-4" />
                                    Go Home
                                </Button>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            )
        }

        return this.props.children
    }
}

// Functional error fallback component for use with react-error-boundary or similar
export function ErrorFallback({ 
    error, 
    resetErrorBoundary 
}: { 
    error: Error
    resetErrorBoundary: () => void 
}) {
    return (
        <div className="min-h-[400px] flex items-center justify-center p-6">
            <Card className="max-w-lg w-full">
                <CardHeader className="text-center">
                    <div className="mx-auto mb-4 p-3 bg-red-100 dark:bg-red-900/30 rounded-full w-fit">
                        <AlertTriangle className="h-8 w-8 text-red-600 dark:text-red-400" />
                    </div>
                    <CardTitle>Something went wrong</CardTitle>
                    <CardDescription>
                        {error.message || 'An unexpected error occurred.'}
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="flex gap-2 justify-center">
                        <Button variant="outline" onClick={resetErrorBoundary}>
                            <RefreshCw className="mr-2 h-4 w-4" />
                            Try Again
                        </Button>
                        <Button onClick={() => window.location.href = '/dashboard'}>
                            <Home className="mr-2 h-4 w-4" />
                            Go Home
                        </Button>
                    </div>
                </CardContent>
            </Card>
        </div>
    )
}

export default ErrorBoundary

