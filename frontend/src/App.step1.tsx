console.log('>>> Step 1: App with Login page loading...')

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ThemeProvider } from './contexts/ThemeContext'
import { AuthProvider } from './contexts/AuthContext'
import { Toaster } from './lib/toast'

// Step 1: Add Login page
import { Login } from './pages/Login'

const queryClient = new QueryClient()

function AppStep1() {
    console.log('=== AppStep1 RENDERING (with Login) ===')
    return (
        <QueryClientProvider client={queryClient}>
            <ThemeProvider>
                <AuthProvider>
                    <BrowserRouter>
                        <Routes>
                            <Route path="/login" element={<Login />} />
                            <Route path="*" element={
                                <div style={{ padding: '40px', maxWidth: '600px', margin: '0 auto' }}>
                                    <h1>App Step 1 - Login Added</h1>
                                    <p>✅ Login page imported successfully!</p>
                                    <p><a href="/login" style={{ color: 'blue', textDecoration: 'underline' }}>Go to Login</a></p>
                                </div>
                            } />
                        </Routes>
                        <Toaster position="top-right" richColors />
                    </BrowserRouter>
                </AuthProvider>
            </ThemeProvider>
        </QueryClientProvider>
    )
}

export default AppStep1
