import { Card, CardContent } from '@/components/ui/card'
import { cn } from '@/lib/utils'
import { AlertTriangle, CheckCircle2, Info, AlertCircle } from 'lucide-react'
import { useState } from 'react'

interface RiskFlagItemProps {
    risk: {
        severity: 'low' | 'medium' | 'high' | 'critical'
        title: string
        description: string
        clause?: string
        suggestion?: string
    }
}

const severityConfig = {
    low: {
        color: 'text-blue-600 dark:text-blue-400',
        bg: 'bg-blue-50 dark:bg-blue-950',
        border: 'border-blue-200 dark:border-blue-800',
        icon: Info,
        label: 'Low Risk'
    },
    medium: {
        color: 'text-yellow-600 dark:text-yellow-400',
        bg: 'bg-yellow-50 dark:bg-yellow-950',
        border: 'border-yellow-200 dark:border-yellow-800',
        icon: AlertCircle,
        label: 'Medium Risk'
    },
    high: {
        color: 'text-orange-600 dark:text-orange-400',
        bg: 'bg-orange-50 dark:bg-orange-950',
        border: 'border-orange-200 dark:border-orange-800',
        icon: AlertTriangle,
        label: 'High Risk'
    },
    critical: {
        color: 'text-red-600 dark:text-red-400',
        bg: 'bg-red-50 dark:bg-red-950',
        border: 'border-red-200 dark:border-red-800',
        icon: AlertTriangle,
        label: 'Critical'
    }
}

export function RiskFlagItem({ risk }: RiskFlagItemProps) {
    const [expanded, setExpanded] = useState(false)
    const config = severityConfig[risk.severity]
    const Icon = config.icon

    return (
        <Card
            className={cn(
                "cursor-pointer transition-all hover:shadow-md",
                config.border,
                config.bg
            )}
            onClick={() => setExpanded(!expanded)}
        >
            <CardContent className="p-4">
                <div className="flex items-start gap-3">
                    <div className={cn("p-2 rounded-lg", config.bg)}>
                        <Icon className={cn("h-5 w-5", config.color)} />
                    </div>
                    <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between mb-1">
                            <h4 className="font-semibold">{risk.title}</h4>
                            <span className={cn("text-xs font-medium px-2 py-1 rounded", config.bg, config.color)}>
                                {config.label}
                            </span>
                        </div>
                        <p className="text-sm text-muted-foreground">{risk.description}</p>

                        {expanded && (
                            <div className="mt-4 space-y-3 animate-in slide-in-from-top-2">
                                {risk.clause && (
                                    <div className="p-3 bg-background border rounded-lg">
                                        <p className="text-xs font-medium text-muted-foreground mb-1">Affected Clause:</p>
                                        <p className="text-sm italic">"{risk.clause}"</p>
                                    </div>
                                )}
                                {risk.suggestion && (
                                    <div className="p-3 bg-green-50 dark:bg-green-950 border border-green-200 dark:border-green-800 rounded-lg">
                                        <div className="flex items-start gap-2">
                                            <CheckCircle2 className="h-4 w-4 text-green-600 dark:text-green-400 mt-0.5" />
                                            <div>
                                                <p className="text-xs font-medium text-green-800 dark:text-green-200 mb-1">
                                                    Suggested Resolution:
                                                </p>
                                                <p className="text-sm text-green-700 dark:text-green-300">
                                                    {risk.suggestion}
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                </div>
            </CardContent>
        </Card>
    )
}
