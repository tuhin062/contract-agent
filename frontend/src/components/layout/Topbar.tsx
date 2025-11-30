import { Bell, Moon, Sun, Menu } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useTheme } from '@/contexts/ThemeContext'
import { useAuth } from '@/contexts/AuthContext'
import { useNavigate } from 'react-router-dom'

interface TopbarProps {
    onMenuClick?: () => void
}

export function Topbar({ onMenuClick }: TopbarProps) {
    const { theme, setTheme } = useTheme()
    const { logout } = useAuth()
    const navigate = useNavigate()

    const toggleTheme = () => {
        setTheme(theme === 'dark' ? 'light' : 'dark')
    }

    const handleLogout = () => {
        logout()
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

                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    {/* Breadcrumbs can be added here */}
                </div>
            </div>

            <div className="flex items-center gap-2">
                <Button
                    variant="ghost"
                    size="icon"
                    onClick={toggleTheme}
                >
                    {theme === 'dark' ? (
                        <Sun className="h-5 w-5" />
                    ) : (
                        <Moon className="h-5 w-5" />
                    )}
                </Button>

                <Button variant="ghost" size="icon" className="hidden sm:flex">
                    <Bell className="h-5 w-5" />
                </Button>

                <Button
                    variant="outline"
                    size="sm"
                    onClick={handleLogout}
                    className="hidden sm:flex"
                >
                    Logout
                </Button>
                <Button
                    variant="ghost"
                    size="icon"
                    onClick={handleLogout}
                    className="sm:hidden"
                    title="Logout"
                >
                    <span className="text-xs">Exit</span>
                </Button>
            </div>
        </div>
    )
}

