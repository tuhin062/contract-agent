import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useContracts } from '@/hooks/useContracts'
import { FilePlus, Shield, FileText, AlertTriangle, CheckCircle2 } from 'lucide-react'

export function Dashboard() {
    const { data: contracts, isLoading } = useContracts()

    const stats = {
        total: contracts?.length || 0,
        pending: contracts?.filter((c) => c.status === 'pending_approval').length || 0,
        active: contracts?.filter((c) => c.status === 'active').length || 0,
        flagged: 3, // Mock flagged validations
    }

    const recentContracts = contracts?.slice(0, 5) || []

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold">Dashboard</h1>
                <p className="text-muted-foreground">Welcome to Contract Agent Platform</p>
            </div>

            {/* KPI Cards */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <Card className="card-enter hover-lift cursor-pointer">
                    <CardHeader className="flex flex-row items-center justify-between pb-2">
                        <CardTitle className="text-sm font-medium">Total Contracts</CardTitle>
                        <FileText className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{stats.total}</div>
                        <p className="text-xs text-muted-foreground">Across all statuses</p>
                    </CardContent>
                </Card>

                <Card className="card-enter hover-lift cursor-pointer" style={{ animationDelay: '0.1s' }}>
                    <CardHeader className="flex flex-row items-center justify-between pb-2">
                        <CardTitle className="text-sm font-medium">Pending Approvals</CardTitle>
                        <AlertTriangle className="h-4 w-4 text-yellow-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{stats.pending}</div>
                        <p className="text-xs text-muted-foreground">Awaiting review</p>
                    </CardContent>
                </Card>

                <Card className="card-enter hover-lift cursor-pointer" style={{ animationDelay: '0.2s' }}>
                    <CardHeader className="flex flex-row items-center justify-between pb-2">
                        <CardTitle className="text-sm font-medium">Active Contracts</CardTitle>
                        <CheckCircle2 className="h-4 w-4 text-green-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{stats.active}</div>
                        <p className="text-xs text-muted-foreground">Currently in force</p>
                    </CardContent>
                </Card>

                <Card className="card-enter hover-lift cursor-pointer" style={{ animationDelay: '0.3s' }}>
                    <CardHeader className="flex flex-row items-center justify-between pb-2">
                        <CardTitle className="text-sm font-medium">Flagged Validations</CardTitle>
                        <Shield className="h-4 w-4 text-destructive" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{stats.flagged}</div>
                        <p className="text-xs text-muted-foreground">Require attention</p>
                    </CardContent>
                </Card>
            </div>

            {/* Quick Actions */}
            <Card className="card-enter" style={{ animationDelay: '0.4s' }}>
                <CardHeader>
                    <CardTitle>Quick Actions</CardTitle>
                </CardHeader>
                <CardContent className="flex flex-wrap gap-3">
                    <Button asChild>
                        <Link to="/generate">
                            <FilePlus className="mr-2 h-4 w-4" />
                            Generate Contract
                        </Link>
                    </Button>
                    <Button variant="outline" asChild>
                        <Link to="/validate">
                            <Shield className="mr-2 h-4 w-4" />
                            Validate Contract
                        </Link>
                    </Button>
                    <Button variant="outline" asChild>
                        <Link to="/contracts">
                            <FileText className="mr-2 h-4 w-4" />
                            View All Contracts
                        </Link>
                    </Button>
                </CardContent>
            </Card>

            {/* Recent Contracts */}
            <Card className="card-enter" style={{ animationDelay: '0.5s' }}>
                <CardHeader>
                    <CardTitle>Recent Contracts</CardTitle>
                </CardHeader>
                <CardContent>
                    {isLoading ? (
                        <div className="flex items-center justify-center h-32">
                            <div className="spinner h-8 w-8 border-primary"></div>
                        </div>
                    ) : (
                        <div className="space-y-3">
                            {recentContracts.map((contract) => (
                                <Link
                                    key={contract.id}
                                    to={`/contracts/${contract.id}`}
                                    className="flex items-center justify-between rounded-lg border p-3 transition-all hover:bg-accent hover:shadow-md"
                                >
                                    <div>
                                        <p className="font-medium">{contract.title}</p>
                                        <p className="text-sm text-muted-foreground">{contract.type}</p>
                                    </div>
                                    <div className="text-right">
                                        <span className={`inline-block rounded px-2 py-1 text-xs font-medium ${contract.status === 'active' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                                            contract.status === 'pending_approval' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' :
                                                'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200'
                                            }`}>
                                            {contract.status}
                                        </span>
                                    </div>
                                </Link>
                            ))}
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    )
}
