import { Card, CardContent } from '@/components/ui/card'
import { cn } from '@/lib/utils'
import { ArrowRight } from 'lucide-react'

interface ClauseComparisonRowProps {
    title: string
    standardClause: string
    currentClause: string
    hasRisk?: boolean
}

export function ClauseComparisonRow({ title, standardClause, currentClause, hasRisk }: ClauseComparisonRowProps) {
    return (
        <Card className={cn(
            "transition-all hover:shadow-md",
            hasRisk && "border-orange-200 dark:border-orange-800"
        )}>
            <CardContent className="p-4">
                <h4 className="font-semibold mb-3 flex items-center gap-2">
                    {title}
                    {hasRisk && (
                        <span className="text-xs bg-orange-100 dark:bg-orange-900 text-orange-800 dark:text-orange-200 px-2 py-0.5 rounded">
                            Differs from Standard
                        </span>
                    )}
                </h4>
                <div className="grid md:grid-cols-2 gap-4">
                    {/* Standard Clause */}
                    <div className="space-y-2">
                        <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                            Standard Version
                        </p>
                        <div className="p-3 bg-green-50 dark:bg-green-950 border border-green-200 dark:border-green-800 rounded-lg">
                            <p className="text-sm leading-relaxed">{standardClause}</p>
                        </div>
                    </div>

                    {/* Arrow indicator on desktop */}
                    <div className="hidden md:flex items-center justify-center absolute left-1/2 -translate-x-1/2">
                        <ArrowRight className="h-5 w-5 text-muted-foreground" />
                    </div>

                    {/* Current Clause */}
                    <div className="space-y-2">
                        <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                            Current Version
                        </p>
                        <div className={cn(
                            "p-3 border rounded-lg",
                            hasRisk
                                ? "bg-orange-50 dark:bg-orange-950 border-orange-200 dark:border-orange-800"
                                : "bg-muted"
                        )}>
                            <p className="text-sm leading-relaxed">{currentClause}</p>
                        </div>
                    </div>
                </div>
            </CardContent>
        </Card>
    )
}
