import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useAuth } from '@/contexts/AuthContext'
import { toast } from '@/lib/toast'
import { Copy, User, Shield, Users } from 'lucide-react'

const demoUsers = [
    {
        role: 'Admin',
        email: 'admin@contractagent.com',
        password: 'admin123',
        icon: Shield,
        color: 'text-purple-500',
        bgColor: 'bg-purple-50 dark:bg-purple-950/20',
        description: 'Full access to all features'
    },
    {
        role: 'Reviewer',
        email: 'reviewer@contractagent.com',
        password: 'reviewer123',
        icon: User,
        color: 'text-blue-500',
        bgColor: 'bg-blue-50 dark:bg-blue-950/20',
        description: 'Can review and approve contracts',
        note: 'Create this user first'
    },
    {
        role: 'Regular User',
        email: 'user@contractagent.com',
        password: 'user123',
        icon: Users,
        color: 'text-green-500',
        bgColor: 'bg-green-50 dark:bg-green-950/20',
        description: 'Can create and view contracts',
        note: 'Create this user first'
    }
]

export function Login() {
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState('')
    const { login } = useAuth()
    const navigate = useNavigate()

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setError('')

        try {
            await login(email, password)
            toast.success('Login successful', 'Welcome back!')
            navigate('/dashboard')
        } catch (err) {
            setError('Invalid credentials')
            toast.error('Login failed', 'Invalid email or password')
        }
    }

    const fillCredentials = (userEmail: string, userPassword: string) => {
        setEmail(userEmail)
        setPassword(userPassword)
        toast.success('Filled', 'Credentials filled. Click Sign In.')
    }

    const copyToClipboard = (text: string, label: string) => {
        navigator.clipboard.writeText(text)
        toast.success('Copied', `${label} copied to clipboard`)
    }

    return (
        <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-background to-muted p-4">
            <div className="flex w-full max-w-5xl gap-6">
                {/* Login Form */}
                <Card className="w-full max-w-md">
                    <CardHeader className="space-y-1">
                        <CardTitle className="text-3xl font-bold">Contract Agent</CardTitle>
                        <CardDescription>
                            Enter your credentials to access the platform
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div className="space-y-2">
                                <label className="text-sm font-medium">Email</label>
                                <Input
                                    type="email"
                                    placeholder="your.email@example.com"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    required
                                />
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-medium">Password</label>
                                <Input
                                    type="password"
                                    placeholder="••••••••"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    required
                                />
                            </div>

                            {error && (
                                <p className="text-sm text-destructive">{error}</p>
                            )}

                            <Button type="submit" className="w-full">
                                Sign In
                            </Button>
                        </form>
                    </CardContent>
                </Card>

                {/* Demo Credentials Sidebar */}
                <Card className="w-full max-w-sm border-dashed">
                    <CardHeader>
                        <CardTitle className="text-lg">Demo Credentials</CardTitle>
                        <CardDescription>
                            Click to auto-fill login credentials
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-3">
                        {demoUsers.map((user) => {
                            const Icon = user.icon
                            return (
                                <div
                                    key={user.email}
                                    className={`rounded-lg border p-3 ${user.bgColor} transition-all hover:shadow-md cursor-pointer`}
                                    onClick={() => fillCredentials(user.email, user.password)}
                                >
                                    <div className="flex items-start justify-between gap-2">
                                        <div className="flex items-start gap-2 flex-1">
                                            <Icon className={`h-5 w-5 mt-0.5 ${user.color}`} />
                                            <div className="flex-1 min-w-0">
                                                <div className="flex items-center gap-2">
                                                    <h4 className="font-semibold text-sm">{user.role}</h4>
                                                    {user.note && (
                                                        <span className="text-xs text-muted-foreground bg-background px-1.5 py-0.5 rounded">
                                                            {user.note}
                                                        </span>
                                                    )}
                                                </div>
                                                <p className="text-xs text-muted-foreground mt-1">
                                                    {user.description}
                                                </p>
                                                <div className="mt-2 space-y-1">
                                                    <div className="flex items-center justify-between gap-2">
                                                        <code className="text-xs bg-background px-2 py-1 rounded truncate flex-1">
                                                            {user.email}
                                                        </code>
                                                        <button
                                                            type="button"
                                                            onClick={(e) => {
                                                                e.stopPropagation()
                                                                copyToClipboard(user.email, 'Email')
                                                            }}
                                                            className="p-1 hover:bg-background rounded"
                                                        >
                                                            <Copy className="h-3 w-3" />
                                                        </button>
                                                    </div>
                                                    <div className="flex items-center justify-between gap-2">
                                                        <code className="text-xs bg-background px-2 py-1 rounded">
                                                            {user.password}
                                                        </code>
                                                        <button
                                                            type="button"
                                                            onClick={(e) => {
                                                                e.stopPropagation()
                                                                copyToClipboard(user.password, 'Password')
                                                            }}
                                                            className="p-1 hover:bg-background rounded"
                                                        >
                                                            <Copy className="h-3 w-3" />
                                                        </button>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )
                        })}

                        <div className="mt-4 p-3 bg-muted rounded-lg">
                            <p className="text-xs text-muted-foreground">
                                💡 <strong>Tip:</strong> Click any card to auto-fill credentials, or use the copy buttons to copy individual fields.
                            </p>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    )
}
