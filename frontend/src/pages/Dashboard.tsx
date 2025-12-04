import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { useContracts } from '@/hooks/useContracts'
import { useAuth } from '@/contexts/AuthContext'
import validationService from '@/services/validation.service'
import { 
    FilePlus, 
    Shield, 
    FileText, 
    AlertTriangle, 
    CheckCircle2,
    Clock,
    TrendingUp,
    Users,
    Sparkles,
    ArrowRight
} from 'lucide-react'
import { DashboardSkeleton, StatsCardSkeleton } from '@/components/loading/Skeleton'
import { CONTRACT_STATUS_COLORS, CONTRACT_STATUS_LABELS } from '@/types/contract'
import type { ContractStatus } from '@/types/contract'

export function Dashboard() {
    const { user } = useAuth()
    const { data: contracts, isLoading: contractsLoading } = useContracts()
    
    const { data: proposalStats, isLoading: statsLoading } = useQuery({
        queryKey: ['proposalStats'],
        queryFn: () => validationService.getProposalStats(),
        retry: false,
        staleTime: 60000
    })

    const isLoading = contractsLoading || statsLoading

    // Calculate stats
    const stats = {
        total: contracts?.length || 0,
        draft: contracts?.filter((c) => c.status === 'draft').length || 0,
        pending: contracts?.filter((c) => c.status === 'pending_review').length || 0,
        approved: contracts?.filter((c) => c.status === 'approved').length || 0,
        executed: contracts?.filter((c) => c.status === 'executed').length || 0,
        validations: proposalStats?.completed || 0,
        highRisk: 0 // Will come from proposals
    }

    const recentContracts = contracts?.slice(0, 5) || []

    if (isLoading) {
        return <DashboardSkeleton />
    }

    return (
        <div className="space-y-6 page-enter">
            {/* Welcome Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">
                        Welcome back, {user?.name?.split(' ')[0] || 'User'}
                    </h1>
                    <p className="text-muted-foreground">
                        Here's what's happening with your contracts today
                    </p>
                </div>
                <Button asChild size="lg" className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700">
                    <Link to="/ask-ai">
                        <Sparkles className="mr-2 h-5 w-5" />
                        Ask AI
                    </Link>
                </Button>
            </div>

            {/* KPI Cards */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <Card className="card-enter hover-lift cursor-pointer group">
                    <CardHeader className="flex flex-row items-center justify-between pb-2">
                        <CardTitle className="text-sm font-medium">Total Contracts</CardTitle>
                        <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg group-hover:scale-110 transition-transform">
                            <FileText className="h-4 w-4 text-blue-600 dark:text-blue-400" />
                        </div>
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold">{stats.total}</div>
                        <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
                            <TrendingUp className="h-3 w-3 text-green-500" />
                            {stats.executed} executed
                        </p>
                    </CardContent>
                </Card>

                <Card className="card-enter hover-lift cursor-pointer group" style={{ animationDelay: '0.1s' }}>
                    <CardHeader className="flex flex-row items-center justify-between pb-2">
                        <CardTitle className="text-sm font-medium">Pending Review</CardTitle>
                        <div className="p-2 bg-yellow-100 dark:bg-yellow-900/30 rounded-lg group-hover:scale-110 transition-transform">
                            <Clock className="h-4 w-4 text-yellow-600 dark:text-yellow-400" />
                        </div>
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold">{stats.pending}</div>
                        <p className="text-xs text-muted-foreground mt-1">Awaiting approval</p>
                    </CardContent>
                </Card>

                <Card className="card-enter hover-lift cursor-pointer group" style={{ animationDelay: '0.2s' }}>
                    <CardHeader className="flex flex-row items-center justify-between pb-2">
                        <CardTitle className="text-sm font-medium">Approved</CardTitle>
                        <div className="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg group-hover:scale-110 transition-transform">
                            <CheckCircle2 className="h-4 w-4 text-green-600 dark:text-green-400" />
                        </div>
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold">{stats.approved}</div>
                        <p className="text-xs text-muted-foreground mt-1">Ready for execution</p>
                    </CardContent>
                </Card>

                <Card className="card-enter hover-lift cursor-pointer group" style={{ animationDelay: '0.3s' }}>
                    <CardHeader className="flex flex-row items-center justify-between pb-2">
                        <CardTitle className="text-sm font-medium">Validations</CardTitle>
                        <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg group-hover:scale-110 transition-transform">
                            <Shield className="h-4 w-4 text-purple-600 dark:text-purple-400" />
                        </div>
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold">{stats.validations}</div>
                        <p className="text-xs text-muted-foreground mt-1">Completed analyses</p>
                    </CardContent>
                </Card>
            </div>

            {/* Main Content Grid */}
            <div className="grid gap-6 lg:grid-cols-3">
                {/* Quick Actions */}
                <Card className="card-enter lg:col-span-1" style={{ animationDelay: '0.4s' }}>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Sparkles className="h-5 w-5 text-primary" />
                            Quick Actions
                        </CardTitle>
                        <CardDescription>Common tasks at your fingertips</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-3">
                        <Button asChild className="w-full justify-start" variant="outline">
                            <Link to="/generate">
                                <FilePlus className="mr-3 h-4 w-4 text-blue-500" />
                                Generate New Contract
                                <ArrowRight className="ml-auto h-4 w-4" />
                            </Link>
                        </Button>
                        <Button asChild className="w-full justify-start" variant="outline">
                            <Link to="/validate">
                                <Shield className="mr-3 h-4 w-4 text-green-500" />
                                Validate Contract
                                <ArrowRight className="ml-auto h-4 w-4" />
                            </Link>
                        </Button>
                        <Button asChild className="w-full justify-start" variant="outline">
                            <Link to="/templates">
                                <FileText className="mr-3 h-4 w-4 text-purple-500" />
                                Browse Templates
                                <ArrowRight className="ml-auto h-4 w-4" />
                            </Link>
                        </Button>
                        <Button asChild className="w-full justify-start" variant="outline">
                            <Link to="/ask-ai">
                                <Sparkles className="mr-3 h-4 w-4 text-pink-500" />
                                Chat with AI
                                <ArrowRight className="ml-auto h-4 w-4" />
                            </Link>
                        </Button>
                    </CardContent>
                </Card>

                {/* Recent Contracts */}
                <Card className="card-enter lg:col-span-2" style={{ animationDelay: '0.5s' }}>
                    <CardHeader className="flex flex-row items-center justify-between">
                        <div>
                            <CardTitle>Recent Contracts</CardTitle>
                            <CardDescription>Your latest contract activity</CardDescription>
                        </div>
                        <Button variant="ghost" size="sm" asChild>
                            <Link to="/contracts">View All</Link>
                        </Button>
                    </CardHeader>
                    <CardContent>
                        {recentContracts.length === 0 ? (
                            <div className="flex flex-col items-center justify-center py-8 text-center">
                                <FileText className="h-12 w-12 text-muted-foreground/50 mb-4" />
                                <p className="text-muted-foreground">No contracts yet</p>
                                <Button asChild className="mt-4" variant="outline">
                                    <Link to="/generate">Create your first contract</Link>
                                </Button>
                            </div>
                        ) : (
                            <div className="space-y-3">
                                {recentContracts.map((contract) => (
                                    <Link
                                        key={contract.id}
                                        to={`/contracts/${contract.id}`}
                                        className="flex items-center justify-between rounded-lg border p-4 transition-all hover:bg-accent hover:shadow-md group"
                                    >
                                        <div className="flex items-center gap-3">
                                            <div className="p-2 bg-muted rounded-lg group-hover:bg-background transition-colors">
                                                <FileText className="h-4 w-4 text-primary" />
                                            </div>
                                            <div>
                                                <p className="font-medium">{contract.title}</p>
                                                <p className="text-sm text-muted-foreground">
                                                    Version {contract.version} • {new Date(contract.created_at).toLocaleDateString()}
                                                </p>
                                            </div>
                                        </div>
                                        <Badge className={CONTRACT_STATUS_COLORS[contract.status as ContractStatus] || ''}>
                                            {CONTRACT_STATUS_LABELS[contract.status as ContractStatus] || contract.status}
                                        </Badge>
                                    </Link>
                                ))}
                            </div>
                        )}
                    </CardContent>
                </Card>
            </div>

            {/* Status Overview */}
            <Card className="card-enter" style={{ animationDelay: '0.6s' }}>
                <CardHeader>
                    <CardTitle>Contract Status Overview</CardTitle>
                    <CardDescription>Distribution of contracts by status</CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="grid gap-4 md:grid-cols-5">
                        {[
                            { status: 'draft', count: stats.draft, color: 'bg-gray-500' },
                            { status: 'pending_review', count: stats.pending, color: 'bg-yellow-500' },
                            { status: 'approved', count: stats.approved, color: 'bg-green-500' },
                            { status: 'executed', count: stats.executed, color: 'bg-blue-500' },
                            { status: 'archived', count: contracts?.filter((c) => c.status === 'archived').length || 0, color: 'bg-gray-400' },
                        ].map((item) => (
                            <div key={item.status} className="text-center p-4 rounded-lg bg-muted/50">
                                <div className={`w-3 h-3 rounded-full ${item.color} mx-auto mb-2`} />
                                <p className="text-2xl font-bold">{item.count}</p>
                                <p className="text-xs text-muted-foreground capitalize">
                                    {item.status.replace('_', ' ')}
                                </p>
                            </div>
                        ))}
                    </div>
                </CardContent>
            </Card>
        </div>
    )
}
