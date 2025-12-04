import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ThemeProvider } from './contexts/ThemeContext'
import { AuthProvider } from './contexts/AuthContext'
import { Toaster } from './lib/toast'
import { ErrorBoundary } from './components/error/ErrorBoundary'

// Layout
import { AppLayout } from './components/layout/AppLayout'

// Pages
import { Login } from './pages/Login'
import { Dashboard } from './pages/Dashboard'
import { ContractsList } from './pages/contracts/ContractsList'
import { ContractDetail } from './pages/contracts/ContractDetail'
import { GenerateContract } from './pages/generate/GenerateContract'
import { ValidateContract } from './pages/validate/ValidateContract'
import { ProposalsList } from './pages/proposals/ProposalsList'
import { TemplatesList } from './pages/templates/TemplatesList'
import { TemplateDetail } from './pages/templates/TemplateDetail'
import { AdminPanel } from './pages/admin/AdminPanel'
import { AskAI } from './pages/AskAI'
import { NotFound } from './pages/NotFound'


const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={<AppLayout />}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="contracts" element={<ContractsList />} />
        <Route path="contracts/:id" element={<ContractDetail />} />
        <Route path="generate" element={<GenerateContract />} />
        <Route path="validate" element={<ValidateContract />} />
        <Route path="proposals" element={<ProposalsList />} />
        <Route path="templates" element={<TemplatesList />} />
        <Route path="templates/:id" element={<TemplateDetail />} />
        <Route path="ask-ai" element={<AskAI />} />
        <Route path="admin" element={<AdminPanel />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  )
}

function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider>
          <AuthProvider>
            <BrowserRouter>
              <AppRoutes />
              <Toaster position="top-right" richColors />
            </BrowserRouter>
          </AuthProvider>
        </ThemeProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  )
}

export default App
