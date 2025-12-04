console.log('>>> Step 2: App with Login, AppLayout, Dashboard loading...')

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ThemeProvider } from './contexts/ThemeContext'
import { AuthProvider } from './contexts/AuthContext'
import { Toaster } from './lib/toast'

// Layout
import { AppLayout } from './components/layout/AppLayout'

// Pages
import { Login } from './pages/Login'
import { Dashboard } from './pages/Dashboard'

const queryClient = new QueryClient()

function AppStep2() {
    console.log('=== AppStep2 RENDERING (Login + Layout + Dashboard) ===')
    return (
        <QueryClientProvider client={queryClient}>
            <ThemeProvider>
                <AuthProvider>
                    <BrowserRouter>
                        <Routes>
                            <Route path="/login" element={<Login />} />
                            <Route path="/" element={<AppLayout />}>
                                <Route index element={<Navigate to="/dashboard" replace />} />
                                <Route path="dashboard" element={<Dashboard />} />
                            </Route>
                        </Routes>
                        <Toaster position="top-right" richColors />
                    </BrowserRouter>
                </AuthProvider>
            </ThemeProvider>
        </QueryClientProvider>
    )
}

export default AppStep2
