import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select'
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from '@/components/ui/dialog'
import {
    Users,
    Settings,
    Shield,
    Activity,
    Plus,
    Search,
    RefreshCw,
    UserPlus,
    Trash2,
    Edit,
    CheckCircle2,
    XCircle,
    AlertTriangle
} from 'lucide-react'
import { toast } from '@/lib/toast'
import { useAuth } from '@/contexts/AuthContext'
import adminService from '@/services/admin.service'
import type { User, UserRole } from '@/types/user'
import { USER_ROLE_LABELS, USER_ROLE_COLORS, canAdmin } from '@/types/user'
import { TableSkeleton, StatsCardSkeleton } from '@/components/loading/Skeleton'

export function AdminPanel() {
    const { user } = useAuth()
    const queryClient = useQueryClient()
    const [activeTab, setActiveTab] = useState('users')
    const [searchQuery, setSearchQuery] = useState('')
    const [roleFilter, setRoleFilter] = useState<string>('all')
    const [isCreateUserOpen, setIsCreateUserOpen] = useState(false)
    const [newUser, setNewUser] = useState({
        name: '',
        email: '',
        password: '',
        role: 'regular' as UserRole
    })

    // Check admin access
    if (!canAdmin(user)) {
        return (
            <div className="flex items-center justify-center h-[60vh]">
                <Card className="max-w-md">
                    <CardContent className="pt-6 text-center">
                        <Shield className="h-12 w-12 mx-auto text-destructive mb-4" />
                        <h2 className="text-xl font-bold mb-2">Access Denied</h2>
                        <p className="text-muted-foreground">
                            You need administrator privileges to access this page.
                        </p>
                    </CardContent>
                </Card>
            </div>
        )
    }

    // Queries
    const { data: users, isLoading: usersLoading, refetch: refetchUsers } = useQuery({
        queryKey: ['admin', 'users', searchQuery, roleFilter],
        queryFn: () => adminService.listUsers({
            search: searchQuery || undefined,
            role: roleFilter !== 'all' ? roleFilter : undefined
        })
    })

    const { data: userStats, isLoading: statsLoading } = useQuery({
        queryKey: ['admin', 'userStats'],
        queryFn: () => adminService.getUserStats()
    })

    const { data: systemHealth } = useQuery({
        queryKey: ['admin', 'health'],
        queryFn: () => adminService.getSystemHealth(),
        refetchInterval: 30000
    })

    const { data: auditStats } = useQuery({
        queryKey: ['admin', 'auditStats'],
        queryFn: () => adminService.getAuditStats(7)
    })

    // Mutations
    const createUserMutation = useMutation({
        mutationFn: (data: typeof newUser) => adminService.createUser(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin', 'users'] })
            queryClient.invalidateQueries({ queryKey: ['admin', 'userStats'] })
            setIsCreateUserOpen(false)
            setNewUser({ name: '', email: '', password: '', role: 'regular' })
            toast.success('User Created', 'New user has been created successfully')
        },
        onError: (error: any) => {
            toast.error('Error', error.response?.data?.detail || 'Failed to create user')
        }
    })

    const toggleUserMutation = useMutation({
        mutationFn: ({ id, isActive }: { id: string; isActive: boolean }) =>
            isActive ? adminService.deactivateUser(id) : adminService.activateUser(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin', 'users'] })
            toast.success('User Updated', 'User status has been updated')
        },
        onError: (error: any) => {
            toast.error('Error', error.response?.data?.detail || 'Failed to update user')
        }
    })

    const deleteUserMutation = useMutation({
        mutationFn: (id: string) => adminService.deleteUser(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin', 'users'] })
            queryClient.invalidateQueries({ queryKey: ['admin', 'userStats'] })
            toast.success('User Deleted', 'User has been permanently deleted')
        },
        onError: (error: any) => {
            toast.error('Error', error.response?.data?.detail || 'Failed to delete user')
        }
    })

    const handleCreateUser = () => {
        if (!newUser.name || !newUser.email || !newUser.password) {
            toast.error('Validation Error', 'Please fill in all required fields')
            return
        }
        if (newUser.password.length < 8) {
            toast.error('Validation Error', 'Password must be at least 8 characters')
            return
        }
        createUserMutation.mutate(newUser)
    }

    return (
        <div className="space-y-6 page-enter">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">Admin Panel</h1>
                    <p className="text-muted-foreground">Manage users, settings, and system configuration</p>
                </div>
                <div className="flex items-center gap-2">
                    <Badge variant={systemHealth?.status === 'healthy' ? 'default' : 'destructive'}>
                        {systemHealth?.status === 'healthy' ? (
                            <><CheckCircle2 className="h-3 w-3 mr-1" /> System Healthy</>
                        ) : (
                            <><AlertTriangle className="h-3 w-3 mr-1" /> System Issues</>
                        )}
                    </Badge>
                </div>
            </div>

            {/* Stats Cards */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                {statsLoading ? (
                    Array.from({ length: 4 }).map((_, i) => <StatsCardSkeleton key={i} />)
                ) : (
                    <>
                        <Card>
                            <CardHeader className="flex flex-row items-center justify-between pb-2">
                                <CardTitle className="text-sm font-medium">Total Users</CardTitle>
                                <Users className="h-4 w-4 text-muted-foreground" />
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">{userStats?.total || 0}</div>
                                <p className="text-xs text-muted-foreground">
                                    {userStats?.active || 0} active
                                </p>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader className="flex flex-row items-center justify-between pb-2">
                                <CardTitle className="text-sm font-medium">Admins</CardTitle>
                                <Shield className="h-4 w-4 text-purple-500" />
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">{userStats?.by_role?.admin || 0}</div>
                                <p className="text-xs text-muted-foreground">System administrators</p>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader className="flex flex-row items-center justify-between pb-2">
                                <CardTitle className="text-sm font-medium">Reviewers</CardTitle>
                                <CheckCircle2 className="h-4 w-4 text-blue-500" />
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">{userStats?.by_role?.reviewer || 0}</div>
                                <p className="text-xs text-muted-foreground">Contract reviewers</p>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader className="flex flex-row items-center justify-between pb-2">
                                <CardTitle className="text-sm font-medium">Events (7d)</CardTitle>
                                <Activity className="h-4 w-4 text-green-500" />
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">{auditStats?.total_events || 0}</div>
                                <p className="text-xs text-muted-foreground">
                                    {auditStats?.logins || 0} logins
                                </p>
                            </CardContent>
                        </Card>
                    </>
                )}
            </div>

            {/* Main Content */}
            <Tabs value={activeTab} onValueChange={setActiveTab}>
                <TabsList>
                    <TabsTrigger value="users">
                        <Users className="h-4 w-4 mr-2" />
                        Users
                    </TabsTrigger>
                    <TabsTrigger value="settings">
                        <Settings className="h-4 w-4 mr-2" />
                        Settings
                    </TabsTrigger>
                    <TabsTrigger value="audit">
                        <Activity className="h-4 w-4 mr-2" />
                        Audit Log
                    </TabsTrigger>
                </TabsList>

                {/* Users Tab */}
                <TabsContent value="users" className="space-y-4">
                    <div className="flex items-center justify-between gap-4">
                        <div className="flex items-center gap-2 flex-1">
                            <div className="relative flex-1 max-w-sm">
                                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                                <Input
                                    placeholder="Search users..."
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    className="pl-9"
                                />
                            </div>
                            <Select value={roleFilter} onValueChange={setRoleFilter}>
                                <SelectTrigger className="w-40">
                                    <SelectValue placeholder="Filter by role" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="all">All Roles</SelectItem>
                                    <SelectItem value="admin">Admin</SelectItem>
                                    <SelectItem value="reviewer">Reviewer</SelectItem>
                                    <SelectItem value="regular">Regular</SelectItem>
                                </SelectContent>
                            </Select>
                            <Button variant="outline" size="icon" onClick={() => refetchUsers()}>
                                <RefreshCw className="h-4 w-4" />
                            </Button>
                        </div>

                        <Dialog open={isCreateUserOpen} onOpenChange={setIsCreateUserOpen}>
                            <DialogTrigger asChild>
                                <Button>
                                    <UserPlus className="h-4 w-4 mr-2" />
                                    Add User
                                </Button>
                            </DialogTrigger>
                            <DialogContent>
                                <DialogHeader>
                                    <DialogTitle>Create New User</DialogTitle>
                                    <DialogDescription>
                                        Add a new user to the system
                                    </DialogDescription>
                                </DialogHeader>
                                <div className="space-y-4 py-4">
                                    <div className="space-y-2">
                                        <label className="text-sm font-medium">Name</label>
                                        <Input
                                            placeholder="John Doe"
                                            value={newUser.name}
                                            onChange={(e) => setNewUser({ ...newUser, name: e.target.value })}
                                        />
                                    </div>
                                    <div className="space-y-2">
                                        <label className="text-sm font-medium">Email</label>
                                        <Input
                                            type="email"
                                            placeholder="john@example.com"
                                            value={newUser.email}
                                            onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                                        />
                                    </div>
                                    <div className="space-y-2">
                                        <label className="text-sm font-medium">Password</label>
                                        <Input
                                            type="password"
                                            placeholder="Minimum 8 characters"
                                            value={newUser.password}
                                            onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                                        />
                                    </div>
                                    <div className="space-y-2">
                                        <label className="text-sm font-medium">Role</label>
                                        <Select
                                            value={newUser.role}
                                            onValueChange={(value) => setNewUser({ ...newUser, role: value as UserRole })}
                                        >
                                            <SelectTrigger>
                                                <SelectValue />
                                            </SelectTrigger>
                                            <SelectContent>
                                                <SelectItem value="regular">Regular User</SelectItem>
                                                <SelectItem value="reviewer">Reviewer</SelectItem>
                                                <SelectItem value="admin">Administrator</SelectItem>
                                            </SelectContent>
                                        </Select>
                                    </div>
                                </div>
                                <DialogFooter>
                                    <Button variant="outline" onClick={() => setIsCreateUserOpen(false)}>
                                        Cancel
                                    </Button>
                                    <Button 
                                        onClick={handleCreateUser}
                                        disabled={createUserMutation.isPending}
                                    >
                                        {createUserMutation.isPending ? 'Creating...' : 'Create User'}
                                    </Button>
                                </DialogFooter>
                            </DialogContent>
                        </Dialog>
                    </div>

                    {usersLoading ? (
                        <TableSkeleton rows={5} columns={5} />
                    ) : (
                        <Card>
                            <CardContent className="p-0">
                                <table className="w-full">
                                    <thead>
                                        <tr className="border-b bg-muted/50">
                                            <th className="p-4 text-left font-medium">User</th>
                                            <th className="p-4 text-left font-medium">Role</th>
                                            <th className="p-4 text-left font-medium">Status</th>
                                            <th className="p-4 text-left font-medium">Created</th>
                                            <th className="p-4 text-left font-medium">Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {users?.map((u: User) => (
                                            <tr key={u.id} className="border-b hover:bg-muted/30">
                                                <td className="p-4">
                                                    <div>
                                                        <p className="font-medium">{u.name}</p>
                                                        <p className="text-sm text-muted-foreground">{u.email}</p>
                                                    </div>
                                                </td>
                                                <td className="p-4">
                                                    <Badge className={USER_ROLE_COLORS[u.role] || ''}>
                                                        {USER_ROLE_LABELS[u.role] || u.role}
                                                    </Badge>
                                                </td>
                                                <td className="p-4">
                                                    {u.is_active ? (
                                                        <Badge variant="outline" className="text-green-600 border-green-600">
                                                            <CheckCircle2 className="h-3 w-3 mr-1" />
                                                            Active
                                                        </Badge>
                                                    ) : (
                                                        <Badge variant="outline" className="text-red-600 border-red-600">
                                                            <XCircle className="h-3 w-3 mr-1" />
                                                            Inactive
                                                        </Badge>
                                                    )}
                                                </td>
                                                <td className="p-4 text-muted-foreground">
                                                    {new Date(u.created_at).toLocaleDateString()}
                                                </td>
                                                <td className="p-4">
                                                    <div className="flex items-center gap-2">
                                                        <Button
                                                            variant="ghost"
                                                            size="sm"
                                                            onClick={() => toggleUserMutation.mutate({ 
                                                                id: u.id, 
                                                                isActive: u.is_active 
                                                            })}
                                                            disabled={u.id === user?.id}
                                                        >
                                                            {u.is_active ? 'Deactivate' : 'Activate'}
                                                        </Button>
                                                        <Button
                                                            variant="ghost"
                                                            size="icon"
                                                            className="text-destructive hover:text-destructive"
                                                            onClick={() => {
                                                                if (confirm('Are you sure you want to delete this user?')) {
                                                                    deleteUserMutation.mutate(u.id)
                                                                }
                                                            }}
                                                            disabled={u.id === user?.id}
                                                        >
                                                            <Trash2 className="h-4 w-4" />
                                                        </Button>
                                                    </div>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                                {(!users || users.length === 0) && (
                                    <div className="text-center py-8 text-muted-foreground">
                                        No users found
                                    </div>
                                )}
                            </CardContent>
                        </Card>
                    )}
                </TabsContent>

                {/* Settings Tab */}
                <TabsContent value="settings" className="space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle>System Health</CardTitle>
                            <CardDescription>Current status of system components</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="grid gap-4 md:grid-cols-3">
                                <div className="flex items-center gap-3 p-4 rounded-lg border">
                                    <div className={`p-2 rounded-full ${
                                        systemHealth?.services?.database === 'connected' 
                                            ? 'bg-green-100 text-green-600' 
                                            : 'bg-red-100 text-red-600'
                                    }`}>
                                        <CheckCircle2 className="h-5 w-5" />
                                    </div>
                                    <div>
                                        <p className="font-medium">Database</p>
                                        <p className="text-sm text-muted-foreground">
                                            {systemHealth?.services?.database || 'Unknown'}
                                        </p>
                                    </div>
                                </div>
                                
                                <div className="flex items-center gap-3 p-4 rounded-lg border">
                                    <div className={`p-2 rounded-full ${
                                        systemHealth?.services?.pinecone === 'connected' 
                                            ? 'bg-green-100 text-green-600' 
                                            : 'bg-yellow-100 text-yellow-600'
                                    }`}>
                                        {systemHealth?.services?.pinecone === 'connected' 
                                            ? <CheckCircle2 className="h-5 w-5" />
                                            : <AlertTriangle className="h-5 w-5" />
                                        }
                                    </div>
                                    <div>
                                        <p className="font-medium">Pinecone</p>
                                        <p className="text-sm text-muted-foreground">
                                            {systemHealth?.services?.pinecone || 'Unknown'}
                                        </p>
                                    </div>
                                </div>
                                
                                <div className="flex items-center gap-3 p-4 rounded-lg border">
                                    <div className="p-2 rounded-full bg-green-100 text-green-600">
                                        <CheckCircle2 className="h-5 w-5" />
                                    </div>
                                    <div>
                                        <p className="font-medium">OpenRouter</p>
                                        <p className="text-sm text-muted-foreground">
                                            {systemHealth?.services?.openrouter || 'Configured'}
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader>
                            <CardTitle>System Information</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="grid gap-4 md:grid-cols-2">
                                <div>
                                    <p className="text-sm text-muted-foreground">Version</p>
                                    <p className="font-medium">{systemHealth?.version || 'Unknown'}</p>
                                </div>
                                <div>
                                    <p className="text-sm text-muted-foreground">Environment</p>
                                    <p className="font-medium capitalize">{systemHealth?.environment || 'Unknown'}</p>
                                </div>
                                <div>
                                    <p className="text-sm text-muted-foreground">Pinecone Vectors</p>
                                    <p className="font-medium">
                                        {systemHealth?.pinecone_stats?.total_vector_count?.toLocaleString() || 0}
                                    </p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Audit Log Tab */}
                <TabsContent value="audit" className="space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle>Recent Activity</CardTitle>
                            <CardDescription>Last 7 days of system activity</CardDescription>
                        </CardHeader>
                        <CardContent>
                            {auditStats && (
                                <div className="grid gap-4 md:grid-cols-4 mb-6">
                                    <div className="text-center p-4 bg-muted/50 rounded-lg">
                                        <p className="text-2xl font-bold">{auditStats.total_events}</p>
                                        <p className="text-sm text-muted-foreground">Total Events</p>
                                    </div>
                                    <div className="text-center p-4 bg-muted/50 rounded-lg">
                                        <p className="text-2xl font-bold">{auditStats.logins}</p>
                                        <p className="text-sm text-muted-foreground">Successful Logins</p>
                                    </div>
                                    <div className="text-center p-4 bg-muted/50 rounded-lg">
                                        <p className="text-2xl font-bold text-red-500">{auditStats.failed_logins}</p>
                                        <p className="text-sm text-muted-foreground">Failed Logins</p>
                                    </div>
                                    <div className="text-center p-4 bg-muted/50 rounded-lg">
                                        <p className="text-2xl font-bold">{Object.keys(auditStats.by_action || {}).length}</p>
                                        <p className="text-sm text-muted-foreground">Action Types</p>
                                    </div>
                                </div>
                            )}
                            
                            {auditStats?.by_action && Object.keys(auditStats.by_action).length > 0 && (
                                <div>
                                    <h4 className="font-medium mb-3">Events by Type</h4>
                                    <div className="grid gap-2 md:grid-cols-2 lg:grid-cols-3">
                                        {Object.entries(auditStats.by_action).map(([action, count]) => (
                                            <div key={action} className="flex justify-between p-2 rounded border">
                                                <span className="text-sm capitalize">{action.replace(/_/g, ' ')}</span>
                                                <Badge variant="secondary">{count as number}</Badge>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>
        </div>
    )
}
