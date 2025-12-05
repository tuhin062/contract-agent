import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useAuth } from '@/contexts/AuthContext'
import { toast } from '@/lib/toast'
import { Copy, User, Shield, Users, Key, Eye, EyeOff, CheckCircle2, XCircle, AlertCircle } from 'lucide-react'
import authService from '@/services/auth.service'

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
    const [confirmPassword, setConfirmPassword] = useState('')
    const [error, setError] = useState('')
    const [isResetMode, setIsResetMode] = useState(false)
    const [showPassword, setShowPassword] = useState(false)
    const [showConfirmPassword, setShowConfirmPassword] = useState(false)
    const [isLoading, setIsLoading] = useState(false)
    const { login } = useAuth()
    const navigate = useNavigate()

    // Password strength checker (same as admin reset)
    const getPasswordStrength = (pwd: string) => {
        if (pwd.length === 0) return { strength: 0, label: '', color: '' }
        if (pwd.length < 8) return { strength: 1, label: 'Weak', color: 'text-red-500' }
        if (pwd.length < 12) return { strength: 2, label: 'Medium', color: 'text-yellow-500' }
        if (pwd.length >= 12 && /[A-Z]/.test(pwd) && /[a-z]/.test(pwd) && /[0-9]/.test(pwd)) {
            return { strength: 3, label: 'Strong', color: 'text-green-500' }
        }
        return { strength: 2, label: 'Medium', color: 'text-yellow-500' }
    }

    const passwordStrength = getPasswordStrength(password)
    const passwordsMatch = password && confirmPassword && password === confirmPassword
    const isResetValid = email && password.length >= 8 && passwordsMatch

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setError('')

        if (isResetMode) {
            // Password reset flow
            if (!isResetValid) {
                setError('Please ensure password is at least 8 characters and passwords match')
                return
            }

            setIsLoading(true)
            try {
                await authService.resetPasswordByEmail(email, password)
                toast.success('Password Reset', 'Your password has been reset successfully. Please login with your new password.')
                // Reset form and switch back to login mode
                setIsResetMode(false)
                setPassword('')
                setConfirmPassword('')
            } catch (err: any) {
                const errorMessage = err.response?.data?.detail || err.message || 'Failed to reset password'
                setError(errorMessage)
                toast.error('Reset Failed', errorMessage)
            } finally {
                setIsLoading(false)
            }
        } else {
            // Login flow
            try {
                await login(email, password)
                toast.success('Login successful', 'Welcome back!')
                navigate('/dashboard')
            } catch (err) {
                setError('Invalid credentials')
                toast.error('Login failed', 'Invalid email or password')
            }
        }
    }

    const handleResetModeToggle = () => {
        setIsResetMode(!isResetMode)
        setPassword('')
        setConfirmPassword('')
        setError('')
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

    // Check if in development mode
    const isDevelopment = import.meta.env.DEV || import.meta.env.MODE === 'development'

    return (
        <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-background to-muted p-4">
            <div className="flex w-full max-w-5xl gap-6">
                {/* Login Form */}
                <Card className="w-full max-w-md">
                    <CardHeader className="space-y-1">
                        <CardTitle className="text-3xl font-bold">Contract Agent</CardTitle>
                        <CardDescription>
                            {isResetMode 
                                ? 'Enter your email and set a new password'
                                : 'Enter your credentials to access the platform'
                            }
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div className="space-y-2">
                                <Label htmlFor="email">Email</Label>
                                <Input
                                    id="email"
                                    type="email"
                                    placeholder="your.email@example.com"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    required
                                    disabled={isLoading}
                                />
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="password">
                                    {isResetMode ? 'New Password' : 'Password'}
                                </Label>
                                <div className="relative">
                                    <Input
                                        id="password"
                                        type={showPassword ? 'text' : 'password'}
                                        placeholder={isResetMode ? "Enter new password (min. 8 characters)" : "••••••••"}
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        required
                                        disabled={isLoading}
                                        className="pr-20"
                                    />
                                    <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1">
                                        {isResetMode && (
                                            <button
                                                type="button"
                                                onClick={handleResetModeToggle}
                                                className="p-1.5 text-muted-foreground hover:text-foreground transition-colors rounded hover:bg-muted"
                                                disabled={isLoading}
                                                title="Cancel password reset"
                                            >
                                                <XCircle className="h-4 w-4" />
                                            </button>
                                        )}
                                        <button
                                            type="button"
                                            onClick={() => !isResetMode && handleResetModeToggle()}
                                            className={`p-1.5 transition-colors rounded ${
                                                isResetMode 
                                                    ? 'text-blue-600 hover:text-blue-700 hover:bg-blue-50 dark:hover:bg-blue-950/20' 
                                                    : 'text-muted-foreground hover:text-foreground hover:bg-muted'
                                            }`}
                                            disabled={isLoading}
                                            title={isResetMode ? 'Password reset mode' : 'Reset password'}
                                        >
                                            <Key className="h-4 w-4" />
                                        </button>
                                        <button
                                            type="button"
                                            onClick={() => setShowPassword(!showPassword)}
                                            className="p-1.5 text-muted-foreground hover:text-foreground transition-colors rounded hover:bg-muted"
                                            disabled={isLoading}
                                        >
                                            {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                                        </button>
                                    </div>
                                </div>
                                
                                {/* Password strength indicator (only in reset mode) */}
                                {isResetMode && password && (
                                    <div className="space-y-1">
                                        <div className="flex items-center gap-2 text-xs">
                                            <span className={passwordStrength.color}>{passwordStrength.label}</span>
                                            {password.length >= 8 && (
                                                <CheckCircle2 className="h-3 w-3 text-green-500" />
                                            )}
                                            {password.length < 8 && (
                                                <XCircle className="h-3 w-3 text-red-500" />
                                            )}
                                        </div>
                                        <div className="flex gap-1">
                                            {[1, 2, 3].map((level) => (
                                                <div
                                                    key={level}
                                                    className={`h-1 flex-1 rounded ${
                                                        level <= passwordStrength.strength
                                                            ? passwordStrength.strength === 1
                                                                ? 'bg-red-500'
                                                                : passwordStrength.strength === 2
                                                                ? 'bg-yellow-500'
                                                                : 'bg-green-500'
                                                            : 'bg-muted'
                                                    }`}
                                                />
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {isResetMode && password.length > 0 && password.length < 8 && (
                                    <div className="flex items-start gap-2 p-2 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-md">
                                        <AlertCircle className="h-4 w-4 text-yellow-600 dark:text-yellow-400 mt-0.5 flex-shrink-0" />
                                        <p className="text-xs text-yellow-800 dark:text-yellow-200">
                                            Password must be at least 8 characters long
                                        </p>
                                    </div>
                                )}
                            </div>

                            {/* Confirm Password (only in reset mode) */}
                            {isResetMode && (
                                <div className="space-y-2">
                                    <Label htmlFor="confirm-password">Confirm Password</Label>
                                    <div className="relative">
                                        <Input
                                            id="confirm-password"
                                            type={showConfirmPassword ? 'text' : 'password'}
                                            placeholder="Confirm new password"
                                            value={confirmPassword}
                                            onChange={(e) => setConfirmPassword(e.target.value)}
                                            required
                                            disabled={isLoading}
                                            className="pr-10"
                                        />
                                        <button
                                            type="button"
                                            onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                                            className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                                            disabled={isLoading}
                                        >
                                            {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                                        </button>
                                    </div>
                                    {confirmPassword && (
                                        <div className="flex items-center gap-2 text-xs">
                                            {passwordsMatch ? (
                                                <>
                                                    <CheckCircle2 className="h-3 w-3 text-green-500" />
                                                    <span className="text-green-500">Passwords match</span>
                                                </>
                                            ) : (
                                                <>
                                                    <XCircle className="h-3 w-3 text-red-500" />
                                                    <span className="text-red-500">Passwords do not match</span>
                                                </>
                                            )}
                                        </div>
                                    )}
                                </div>
                            )}

                            {error && (
                                <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-md">
                                    <p className="text-sm text-destructive">{error}</p>
                                </div>
                            )}

                            <Button 
                                type="submit" 
                                className="w-full" 
                                disabled={isLoading || (isResetMode && !isResetValid)}
                            >
                                {isLoading 
                                    ? (isResetMode ? 'Resetting...' : 'Signing in...')
                                    : (isResetMode ? 'Reset Password' : 'Sign In')
                                }
                            </Button>

                            {isResetMode && (
                                <p className="text-xs text-center text-muted-foreground">
                                    After resetting, you'll be able to login with your new password.
                                </p>
                            )}
                        </form>
                    </CardContent>
                </Card>

                {/* Demo Credentials Sidebar - Only show in development */}
                {isDevelopment && (
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
                )}
            </div>
        </div>
    )
}
