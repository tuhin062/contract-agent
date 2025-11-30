import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { TrendingUp, TrendingDown, DollarSign, AlertTriangle, CheckCircle } from 'lucide-react'

interface ContractInsightsPanelProps {
    insights: {
        totalValue: number
        valueChange: number
        riskScore: number
        complianceScore: number
        recentActivity: {
            action: string
            date: string
        }[]
    }
}

export function ContractInsightsPanel({ insights }: ContractInsightsPanelProps) {
    const isPositiveTrend = insights.valueChange >= 0

    return (
        <Card className="card-enter">
            <CardHeader>
                <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5" />
                    Contract Insights
                </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
                {/* Value Trend */}
                <div className="p-4 bg-gradient-to-br from-primary/10 to-primary/5 rounded-lg">
                    <div className="flex items-center gap-2 mb-1">
                        <DollarSign className="h-4 w-4 text-muted-foreground" />
                        <span className="text-sm text-muted-foreground">Total Value</span>
                    </div>
                    <div className="flex items-baseline gap-2">
                        <span className="text-2xl font-bold">
                            ${insights.totalValue.toLocaleString()}
                        </span>
                        <div className={`flex items-center gap-1 text-sm ${isPositiveTrend ? 'text-green-600' : 'text-red-600'}`}>
                            {isPositiveTrend ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                            {Math.abs(insights.valueChange)}%
                        </div>
                    </div>
                </div>

                {/* Risk & Compliance Grid */}
                <div className="grid grid-cols-2 gap-3">
                    {/* Risk Score */}
                    <div className="p-3 border rounded-lg">
                        <div className="flex items-center gap-2 mb-2">
                            <AlertTriangle className="h-4 w-4 text-orange-500" />
                            <span className="text-xs font-medium text-muted-foreground">Risk Score</span>
                        </div>
                        <p className={`text-xl font-bold ${insights.riskScore >= 70 ? 'text-red-600' :
                                insights.riskScore >= 40 ? 'text-yellow-600' :
                                    'text-green-600'
                            }`}>
                            {insights.riskScore}
                        </p>
                    </div>

                    {/* Compliance Score */}
                    <div className="p-3 border rounded-lg">
                        <div className="flex items-center gap-2 mb-2">
                            <CheckCircle className="h-4 w-4 text-green-500" />
                            <span className="text-xs font-medium text-muted-foreground">Compliance</span>
                        </div>
                        <p className="text-xl font-bold text-green-600">
                            {insights.complianceScore}%
                        </p>
                    </div>
                </div>

                {/* Recent Activity */}
                <div>
                    <h4 className="text-sm font-medium mb-3">Recent Activity</h4>
                    <div className="space-y-2">
                        {insights.recentActivity.map((activity, idx) => (
                            <div key={idx} className="p-2 border rounded-lg hover:bg-accent transition-colors">
                                <p className="text-sm font-medium">{activity.action}</p>
                                <p className="text-xs text-muted-foreground">
                                    {new Date(activity.date).toLocaleDateString()}
                                </p>
                            </div>
                        ))}
                    </div>
                </div>
            </CardContent>
        </Card>
    )
}
