import { Link, useLocation } from 'react-router-dom'
import {
    LayoutDashboard,
    FileText,
    FilePlus,
    Shield,
    FileCheck,
    FolderOpen,
    Settings,
    Sparkles
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useAuth } from '@/contexts/AuthContext'

const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Contracts', href: '/contracts', icon: FileText },
    { name: 'Generate', href: '/generate', icon: FilePlus },
    { name: 'Validate', href: '/validate', icon: Shield },
    { name: 'Proposals', href: '/proposals', icon: FileCheck },
    { name: 'Templates', href: '/templates', icon: FolderOpen },
    { name: 'Ask AI', href: '/ask-ai', icon: Sparkles, special: true },
]

interface SidebarProps {
    open?: boolean
    onClose?: () => void
}

export function Sidebar({ open = true, onClose }: SidebarProps) {
    const location = useLocation()
    const { user } = useAuth()

    const showAdmin = user?.role === 'admin'

    const handleLinkClick = () => {
        // Close mobile sidebar when link is clicked
        if (onClose) {
            onClose()
        }
    }

    return (
        <>
            {/* Mobile overlay */}
            {open && onClose && (
                <div
                    className="fixed inset-0 z-40 bg-black/50 lg:hidden"
                    onClick={onClose}
                />
            )}

            {/* Sidebar */}
            <div className={cn(
                "flex h-full w-64 flex-col border-r bg-card transition-transform duration-300 ease-in-out lg:translate-x-0",
                // Mobile: absolute positioning and slide-in effect
                "fixed inset-y-0 left-0 z-50 lg:relative",
                open ? "translate-x-0" : "-translate-x-full"
            )}>
                <div className="flex h-16 items-center border-b px-6">
                    <h1 className="text-xl font-bold">Contract Agent</h1>
                </div>

                <nav className="flex-1 space-y-1 p-4">
                    {navigation.map((item) => {
                        const isActive = location.pathname.startsWith(item.href)
                        const Icon = item.icon

                        // Special styling for Ask AI button
                        if (item.special) {
                            return (
                                <Link
                                    key={item.name}
                                    to={item.href}
                                    onClick={handleLinkClick}
                                    className={cn(
                                        'group relative flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-semibold transition-all',
                                        'bg-gradient-to-r from-purple-500 to-pink-500 text-white',
                                        'hover:from-purple-600 hover:to-pink-600',
                                        'shadow-lg hover:shadow-xl',
                                        'ai-glow-button',
                                        isActive && 'ring-2 ring-purple-300 ring-offset-2 ring-offset-background'
                                    )}
                                >
                                    <Icon className="h-5 w-5 animate-pulse" />
                                    <span className="relative">
                                        {item.name}
                                        <span className="absolute -top-1 -right-6 flex h-2 w-2">
                                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-white opacity-75"></span>
                                            <span className="relative inline-flex rounded-full h-2 w-2 bg-white"></span>
                                        </span>
                                    </span>
                                </Link>
                            )
                        }

                        // Regular navigation items
                        return (
                            <Link
                                key={item.name}
                                to={item.href}
                                onClick={handleLinkClick}
                                className={cn(
                                    'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                                    isActive
                                        ? 'bg-primary text-primary-foreground'
                                        : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                                )}
                            >
                                <Icon className="h-5 w-5" />
                                {item.name}
                            </Link>
                        )
                    })}

                    {showAdmin && (
                        <Link
                            to="/admin"
                            onClick={handleLinkClick}
                            className={cn(
                                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                                location.pathname.startsWith('/admin')
                                    ? 'bg-primary text-primary-foreground'
                                    : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                            )}
                        >
                            <Settings className="h-5 w-5" />
                            Admin
                        </Link>
                    )}
                </nav>

                <div className="border-t p-4">
                    <div className="flex items-center gap-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary text-primary-foreground">
                            {user?.name?.charAt(0) || 'U'}
                        </div>
                        <div className="flex-1 overflow-hidden">
                            <p className="truncate text-sm font-medium">{user?.name || 'User'}</p>
                            <p className="truncate text-xs text-muted-foreground">{user?.role || 'Role'}</p>
                        </div>
                    </div>
                </div>
            </div>
        </>
    )
}

