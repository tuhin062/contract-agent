import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { DollarSign, Calendar, Building, TrendingUp } from 'lucide-react'

interface ProposalKeyInfoCardProps {
    proposal: {
        budget: string
        timeline: string
        vendor: string
        score?: number
        status: string
    }
}

export function ProposalKeyInfoCard({ proposal }: ProposalKeyInfoCardProps) {
    return (
        <Card className="card-enter">
            <CardHeader>
                <CardTitle>Key Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
                {/* Budget */}
                <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3">
                        <div className="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
                            <DollarSign className="h-5 w-5 text-green-600 dark:text-green-400" />
                        </div>
                        <div>
                            <p className="text-sm font-medium text-muted-foreground">Budget</p>
                            <p className="text-2xl font-bold">{proposal.budget}</p>
                        </div>
                    </div>
                </div>

                {/* Timeline */}
                <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3">
                        <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
                            <Calendar className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                        </div>
                        <div>
                            <p className="text-sm font-medium text-muted-foreground">Timeline</p>
                            <p className="text-lg font-semibold">{proposal.timeline}</p>
                        </div>
                    </div>
                </div>

                {/* Vendor */}
                <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3">
                        <div className="p-2 bg-purple-100 dark:bg-purple-900 rounded-lg">
                            <Building className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                        </div>
                        <div>
                            <p className="text-sm font-medium text-muted-foreground">Vendor</p>
                            <p className="font-semibold">{proposal.vendor}</p>
                        </div>
                    </div>
                </div>

                {/* Score (if available) */}
                {proposal.score && (
                    <div className="flex items-start justify-between">
                        <div className="flex items-start gap-3">
                            <div className="p-2 bg-orange-100 dark:bg-orange-900 rounded-lg">
                                <TrendingUp className="h-5 w-5 text-orange-600 dark:text-orange-400" />
                            </div>
                            <div>
                                <p className="text-sm font-medium text-muted-foreground">Confidence Score</p>
                                <div className="flex items-baseline gap-2">
                                    <p className="text-2xl font-bold">{proposal.score}</p>
                                    <span className="text-sm text-muted-foreground">/ 100</span>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Status */}
                <div className="pt-2 border-t">
                    <p className="text-sm font-medium text-muted-foreground mb-2">Status</p>
                    <Badge variant={proposal.status === 'approved' ? 'default' : 'secondary'}>
                        {proposal.status}
                    </Badge>
                </div>
            </CardContent>
        </Card>
    )
}
