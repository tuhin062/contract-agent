console.log('>>> Minimal App.tsx loading...')

import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ThemeProvider } from './contexts/ThemeContext'
import { AuthProvider } from './contexts/AuthContext'
import { Toaster } from './lib/toast'

const queryClient = new QueryClient()

function MinimalApp() {
    console.log('=== MinimalApp RENDERING ===')
    return (
        <QueryClientProvider client={queryClient}>
            <ThemeProvider>
                <AuthProvider>
                    <BrowserRouter>
                        <div style={{ padding: '40px', maxWidth: '600px', margin: '0 auto' }}>
                            <h1>Contract Agent - System Check</h1>
                            <p>✅ React is rendering</p>
                            <p>✅ Providers loaded successfully</p>
                            <p>✅ Router working</p>
                            <p style={{ marginTop: '20px', padding: '20px', background: '#f0f0f0', borderRadius: '8px' }}>
                                <strong>Next Step:</strong> If you see this message, the core application structure is working.
                                The blank page was caused by one of the page component imports.
                            </p>
                        </div>
                        <Toaster position="top-right" richColors />
                    </BrowserRouter>
                </AuthProvider>
            </ThemeProvider>
        </QueryClientProvider>
    )
}

export default MinimalApp
