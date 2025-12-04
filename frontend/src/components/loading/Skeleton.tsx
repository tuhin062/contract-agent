import { cn } from '@/lib/utils'

interface SkeletonProps {
    className?: string
}

export function Skeleton({ className }: SkeletonProps) {
    return (
        <div
            className={cn(
                'animate-pulse rounded-md bg-muted',
                className
            )}
        />
    )
}

// Card skeleton
export function CardSkeleton({ className }: SkeletonProps) {
    return (
        <div className={cn('rounded-lg border p-6 space-y-4', className)}>
            <div className="flex items-center justify-between">
                <Skeleton className="h-5 w-32" />
                <Skeleton className="h-5 w-20" />
            </div>
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-3/4" />
        </div>
    )
}

// Table row skeleton
export function TableRowSkeleton({ columns = 5 }: { columns?: number }) {
    return (
        <tr className="border-b">
            {Array.from({ length: columns }).map((_, i) => (
                <td key={i} className="p-4">
                    <Skeleton className="h-4 w-full" />
                </td>
            ))}
        </tr>
    )
}

// Table skeleton
export function TableSkeleton({ rows = 5, columns = 5 }: { rows?: number; columns?: number }) {
    return (
        <div className="rounded-md border">
            <table className="w-full">
                <thead>
                    <tr className="border-b bg-muted/50">
                        {Array.from({ length: columns }).map((_, i) => (
                            <th key={i} className="p-4">
                                <Skeleton className="h-4 w-full" />
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    {Array.from({ length: rows }).map((_, i) => (
                        <TableRowSkeleton key={i} columns={columns} />
                    ))}
                </tbody>
            </table>
        </div>
    )
}

// List item skeleton
export function ListItemSkeleton({ className }: SkeletonProps) {
    return (
        <div className={cn('flex items-center gap-4 p-4 border-b', className)}>
            <Skeleton className="h-10 w-10 rounded-full" />
            <div className="flex-1 space-y-2">
                <Skeleton className="h-4 w-1/3" />
                <Skeleton className="h-3 w-1/2" />
            </div>
            <Skeleton className="h-8 w-20" />
        </div>
    )
}

// List skeleton
export function ListSkeleton({ items = 5, className }: { items?: number; className?: string }) {
    return (
        <div className={cn('rounded-md border divide-y', className)}>
            {Array.from({ length: items }).map((_, i) => (
                <ListItemSkeleton key={i} />
            ))}
        </div>
    )
}

// Stats card skeleton
export function StatsCardSkeleton() {
    return (
        <div className="rounded-lg border p-6 space-y-2">
            <div className="flex items-center justify-between">
                <Skeleton className="h-4 w-24" />
                <Skeleton className="h-4 w-4" />
            </div>
            <Skeleton className="h-8 w-16" />
            <Skeleton className="h-3 w-32" />
        </div>
    )
}

// Dashboard skeleton
export function DashboardSkeleton() {
    return (
        <div className="space-y-6">
            <div className="space-y-2">
                <Skeleton className="h-8 w-48" />
                <Skeleton className="h-4 w-64" />
            </div>
            
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                {Array.from({ length: 4 }).map((_, i) => (
                    <StatsCardSkeleton key={i} />
                ))}
            </div>
            
            <div className="grid gap-6 lg:grid-cols-2">
                <CardSkeleton className="h-64" />
                <CardSkeleton className="h-64" />
            </div>
        </div>
    )
}

// Contract card skeleton
export function ContractCardSkeleton() {
    return (
        <div className="rounded-lg border p-4 space-y-3">
            <div className="flex items-center justify-between">
                <Skeleton className="h-5 w-40" />
                <Skeleton className="h-5 w-20 rounded-full" />
            </div>
            <Skeleton className="h-4 w-full" />
            <div className="flex gap-2">
                <Skeleton className="h-4 w-24" />
                <Skeleton className="h-4 w-24" />
            </div>
        </div>
    )
}

// Chat message skeleton
export function ChatMessageSkeleton({ isUser = false }: { isUser?: boolean }) {
    return (
        <div className={cn('flex gap-3', isUser && 'flex-row-reverse')}>
            <Skeleton className="h-8 w-8 rounded-full flex-shrink-0" />
            <div className={cn('flex-1 space-y-2 max-w-[80%]', isUser && 'items-end')}>
                <Skeleton className={cn('h-16 rounded-2xl', isUser ? 'w-48' : 'w-64')} />
                <Skeleton className="h-3 w-16" />
            </div>
        </div>
    )
}

// Form skeleton
export function FormSkeleton({ fields = 4 }: { fields?: number }) {
    return (
        <div className="space-y-6">
            {Array.from({ length: fields }).map((_, i) => (
                <div key={i} className="space-y-2">
                    <Skeleton className="h-4 w-24" />
                    <Skeleton className="h-10 w-full" />
                </div>
            ))}
            <Skeleton className="h-10 w-32" />
        </div>
    )
}

export default Skeleton

