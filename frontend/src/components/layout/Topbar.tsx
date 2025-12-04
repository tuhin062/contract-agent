import { Bell, Moon, Sun, Menu, LogOut } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useTheme } from '@/contexts/ThemeContext'
import { useAuth } from '@/contexts/AuthContext'
import { useNavigate } from 'react-router-dom'
import { SemanticSearch } from '@/components/shared/SemanticSearch'
import { Badge } from '@/components/ui/badge'
import { formatRole } from '@/types/user'

interface TopbarProps {
    onMenuClick?: () => void
}

export function Topbar({ onMenuClick }: TopbarProps) {
    const { theme, setTheme } = useTheme()
    const { logout, user } = useAuth()
    const navigate = useNavigate()

    const toggleTheme = () => {
        setTheme(theme === 'dark' ? 'light' : 'dark')
    }

    const handleLogout = async () => {
        await logout()
        navigate('/login')
    }

    return (
        <div className="flex h-16 items-center justify-between border-b bg-card px-4 sm:px-6">
            <div className="flex items-center gap-4">
                {/* Mobile menu button */}
                <Button
                    variant="ghost"
                    size="icon"
                    onClick={onMenuClick}
                    className="lg:hidden"
                >
                    <Menu className="h-5 w-5" />
                </Button>

                {/* Semantic Search */}
                <div className="hidden md:block">
                    <SemanticSearch />
                </div>
            </div>

            <div className="flex items-center gap-3">
                {/* User info */}
                {user && (
                    <div className="hidden sm:flex items-center gap-2">
                        <span className="text-sm text-muted-foreground">{user.name}</span>
                        <Badge variant="outline" className="text-xs">
                            {formatRole(user.role)}
                        </Badge>
                    </div>
                )}

                <Button
                    variant="ghost"
                    size="icon"
                    onClick={toggleTheme}
                    title={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
                >
                    {theme === 'dark' ? (
                        <Sun className="h-5 w-5" />
                    ) : (
                        <Moon className="h-5 w-5" />
                    )}
                </Button>

                <Button variant="ghost" size="icon" className="hidden sm:flex relative">
                    <Bell className="h-5 w-5" />
                    {/* Notification badge - can be dynamic */}
                    <span className="absolute -top-1 -right-1 h-4 w-4 rounded-full bg-destructive text-[10px] font-medium text-destructive-foreground flex items-center justify-center">
                        3
                    </span>
                </Button>

                <Button
                    variant="outline"
                    size="sm"
                    onClick={handleLogout}
                    className="hidden sm:flex"
                >
                    <LogOut className="h-4 w-4 mr-2" />
                    Logout
                </Button>
                <Button
                    variant="ghost"
                    size="icon"
                    onClick={handleLogout}
                    className="sm:hidden"
                    title="Logout"
                >
                    <LogOut className="h-4 w-4" />
                </Button>
            </div>
        </div>
    )
}


