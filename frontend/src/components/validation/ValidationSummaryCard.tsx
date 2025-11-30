import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { AlertTriangle, CheckCircle, Shield, AlertCircle } from 'lucide-react'
import { cn } from '@/lib/utils'

interface ValidationSummaryCardProps {
    summary: {
        overallRisk: 'low' | 'medium' | 'high' | 'critical'
        totalFlags: number
        flagsBySeverity: {
            low: number
            medium: number
            high: number
            critical: number
        }
        compliancePercentage: number
    }
}

const riskConfig = {
    low: {
        color: 'text-green-600 dark:text-green-400',
        bg: 'bg-green-100 dark:bg-green-900',
        label: 'Low Risk'
    },
    medium: {
        color: 'text-yellow-600 dark:text-yellow-400',
        bg: 'bg-yellow-100 dark:bg-yellow-900',
        label: 'Medium Risk'
    },
    high: {
        color: 'text-orange-600 dark:text-orange-400',
        bg: 'bg-orange-100 dark:bg-orange-900',
        label: 'High Risk'
    },
    critical: {
        color: 'text-red-600 dark:text-red-400',
        bg: 'bg-red-100 dark:bg-red-900',
        label: 'Critical Risk'
    }
}

export function ValidationSummaryCard({ summary }: ValidationSummaryCardProps) {
    const config = riskConfig[summary.overallRisk]
    const complianceColor = summary.compliancePercentage >= 80 ? 'text-green-600' :
        summary.compliancePercentage >= 60 ? 'text-yellow-600' : 'text-red-600'

    return (
        <Card className="card-enter">
            <CardHeader>
                <CardTitle className="flex items-center gap-2">
                    <Shield className="h-5 w-5" />
                    Validation Summary
                </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
                {/* Overall Risk Score */}
                <div className="text-center p-6 bg-muted rounded-lg">
                    <p className="text-sm text-muted-foreground mb-2">Overall Risk Level</p>
                    <div className={cn(
                        "text-4xl font-bold mb-2",
                        config.color
                    )}>
                        {config.label.split(' ')[0]}
                    </div>
                    <Badge className={config.bg}>
                        {config.label}
                    </Badge>
                </div>

                {/* Statistics Grid */}
                <div className="grid grid-cols-2 gap-4">
                    {/* Total Flags */}
                    <div className="p-4 border rounded-lg text-center">
                        <p className="text-2xl font-bold">{summary.totalFlags}</p>
                        <p className="text-sm text-muted-foreground">Total Flags</p>
                    </div>

                    {/* Compliance */}
                    <div className="p-4 border rounded-lg text-center">
                        <p className={cn("text-2xl font-bold", complianceColor)}>
                            {summary.compliancePercentage}%
                        </p>
                        <p className="text-sm text-muted-foreground">Compliance</p>
                    </div>
                </div>

                {/* Flags by Severity */}
                <div className="space-y-3">
                    <p className="text-sm font-medium">Flags by Severity</p>

                    <div className="space-y-2">
                        {/* Critical */}
                        {summary.flagsBySeverity.critical > 0 && (
                            <div className="flex items-center justify-between p-2 bg-red-50 dark:bg-red-950 border border-red-200 dark:border-red-800 rounded">
                                <div className="flex items-center gap-2">
                                    <AlertTriangle className="h-4 w-4 text-red-600" />
                                    <span className="text-sm font-medium">Critical</span>
                                </div>
                                <Badge variant="destructive">{summary.flagsBySeverity.critical}</Badge>
                            </div>
                        )}

                        {/* High */}
                        {summary.flagsBySeverity.high > 0 && (
                            <div className="flex items-center justify-between p-2 bg-orange-50 dark:bg-orange-950 border border-orange-200 dark:border-orange-800 rounded">
                                <div className="flex items-center gap-2">
                                    <AlertTriangle className="h-4 w-4 text-orange-600" />
                                    <span className="text-sm font-medium">High</span>
                                </div>
                                <Badge className="bg-orange-100 text-orange-800">{summary.flagsBySeverity.high}</Badge>
                            </div>
                        )}

                        {/* Medium */}
                        {summary.flagsBySeverity.medium > 0 && (
                            <div className="flex items-center justify-between p-2 bg-yellow-50 dark:bg-yellow-950 border border-yellow-200 dark:border-yellow-800 rounded">
                                <div className="flex items-center gap-2">
                                    <AlertCircle className="h-4 w-4 text-yellow-600" />
                                    <span className="text-sm font-medium">Medium</span>
                                </div>
                                <Badge className="bg-yellow-100 text-yellow-800">{summary.flagsBySeverity.medium}</Badge>
                            </div>
                        )}

                        {/* Low */}
                        {summary.flagsBySeverity.low > 0 && (
                            <div className="flex items-center justify-between p-2 bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 rounded">
                                <div className="flex items-center gap-2">
                                    <CheckCircle className="h-4 w-4 text-blue-600" />
                                    <span className="text-sm font-medium">Low</span>
                                </div>
                                <Badge className="bg-blue-100 text-blue-800">{summary.flagsBySeverity.low}</Badge>
                            </div>
                        )}
                    </div>
                </div>
            </CardContent>
        </Card>
    )
}
