import { useState } from 'react'
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Key, Eye, EyeOff, CheckCircle2, XCircle, AlertCircle } from 'lucide-react'

interface ResetPasswordDialogProps {
    open: boolean
    onOpenChange: (open: boolean) => void
    userId: string
    userEmail: string
    userName: string
    onSuccess: () => void
    onError: (error: string) => void
    resetPasswordFn: (id: string, password: string) => Promise<void>
}

export function ResetPasswordDialog({
    open,
    onOpenChange,
    userId,
    userEmail,
    userName,
    onSuccess,
    onError,
    resetPasswordFn
}: ResetPasswordDialogProps) {
    const [password, setPassword] = useState('')
    const [confirmPassword, setConfirmPassword] = useState('')
    const [showPassword, setShowPassword] = useState(false)
    const [showConfirmPassword, setShowConfirmPassword] = useState(false)
    const [isLoading, setIsLoading] = useState(false)
    const [requireChangeOnLogin, setRequireChangeOnLogin] = useState(true)

    // Password strength checker
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
    const isValid = password.length >= 8 && passwordsMatch

    const handleReset = async () => {
        if (!isValid) {
            onError('Please ensure password is at least 8 characters and passwords match')
            return
        }

        setIsLoading(true)
        try {
            await resetPasswordFn(userId, password)
            onSuccess()
            // Reset form
            setPassword('')
            setConfirmPassword('')
            setRequireChangeOnLogin(true)
            onOpenChange(false)
        } catch (error: any) {
            const errorMessage = error.response?.data?.detail || error.message || 'Failed to reset password'
            onError(errorMessage)
        } finally {
            setIsLoading(false)
        }
    }

    const handleClose = () => {
        if (!isLoading) {
            setPassword('')
            setConfirmPassword('')
            setRequireChangeOnLogin(true)
            onOpenChange(false)
        }
    }

    return (
        <Dialog open={open} onOpenChange={handleClose}>
            <DialogContent className="sm:max-w-[500px]">
                <DialogHeader>
                    <DialogTitle className="flex items-center gap-2">
                        <Key className="h-5 w-5" />
                        Reset Password
                    </DialogTitle>
                    <DialogDescription>
                        Reset password for <strong>{userName}</strong> ({userEmail})
                    </DialogDescription>
                </DialogHeader>

                <div className="space-y-4 py-4">
                    <div className="space-y-2">
                        <Label htmlFor="new-password">New Password</Label>
                        <div className="relative">
                            <Input
                                id="new-password"
                                type={showPassword ? 'text' : 'password'}
                                placeholder="Enter new password (min. 8 characters)"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                disabled={isLoading}
                                className="pr-10"
                            />
                            <button
                                type="button"
                                onClick={() => setShowPassword(!showPassword)}
                                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                                disabled={isLoading}
                            >
                                {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                            </button>
                        </div>
                        {password && (
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
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="confirm-password">Confirm Password</Label>
                        <div className="relative">
                            <Input
                                id="confirm-password"
                                type={showConfirmPassword ? 'text' : 'password'}
                                placeholder="Confirm new password"
                                value={confirmPassword}
                                onChange={(e) => setConfirmPassword(e.target.value)}
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

                    {password.length > 0 && password.length < 8 && (
                        <div className="flex items-start gap-2 p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-md">
                            <AlertCircle className="h-4 w-4 text-yellow-600 dark:text-yellow-400 mt-0.5" />
                            <p className="text-sm text-yellow-800 dark:text-yellow-200">
                                Password must be at least 8 characters long
                            </p>
                        </div>
                    )}

                    <div className="flex items-center space-x-2 pt-2">
                        <input
                            type="checkbox"
                            id="require-change"
                            checked={requireChangeOnLogin}
                            onChange={(e) => setRequireChangeOnLogin(e.target.checked)}
                            disabled={isLoading}
                            className="h-4 w-4 rounded border-gray-300"
                        />
                        <Label htmlFor="require-change" className="text-sm font-normal cursor-pointer">
                            Require password change on next login
                        </Label>
                    </div>
                </div>

                <DialogFooter>
                    <Button
                        variant="outline"
                        onClick={handleClose}
                        disabled={isLoading}
                    >
                        Cancel
                    </Button>
                    <Button
                        onClick={handleReset}
                        disabled={!isValid || isLoading}
                    >
                        {isLoading ? 'Resetting...' : 'Reset Password'}
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    )
}

