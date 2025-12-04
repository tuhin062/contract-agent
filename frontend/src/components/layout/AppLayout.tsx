import { useState, useEffect } from 'react'
import { Outlet, useNavigate } from 'react-router-dom'
import { Sidebar } from './Sidebar'
import { Topbar } from './Topbar'
import { useAuth } from '@/contexts/AuthContext'

export function AppLayout() {
    const [sidebarOpen, setSidebarOpen] = useState(false)
    const { isAuthenticated } = useAuth()
    const navigate = useNavigate()

    useEffect(() => {
        if (!isAuthenticated) {
            navigate('/login')
        }
    }, [isAuthenticated, navigate])

    if (!isAuthenticated) {
        return null // Don't render anything while redirecting
    }

    return (
        <div className="flex h-screen overflow-hidden">
            <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
            <div className="flex flex-1 flex-col overflow-hidden">
                <Topbar onMenuClick={() => setSidebarOpen(!sidebarOpen)} />
                <main className="flex-1 overflow-y-auto bg-background p-4 sm:p-6 page-enter">
                    <Outlet />
                </main>
            </div>
        </div>
    )
}

