import { Link } from 'react-router-dom'
import type { ColumnDef } from '@tanstack/react-table'
import { MoreHorizontal, ArrowUpDown, Plus, Filter } from 'lucide-react'
import { useContracts } from '@/hooks/useContracts'
import { DataTable } from '@/components/ui/data-table'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select'
import { TableSkeleton } from '@/components/loading/Skeleton'
import type { ContractListItem, ContractStatus } from '@/types/contract'
import { CONTRACT_STATUS_LABELS, CONTRACT_STATUS_COLORS } from '@/types/contract'
import { useState } from 'react'

export function ContractsList() {
    const [statusFilter, setStatusFilter] = useState<ContractStatus | 'all'>('all')
    const { data: contracts, isLoading, error } = useContracts({
        status: statusFilter === 'all' ? undefined : statusFilter
    })

    const columns: ColumnDef<ContractListItem>[] = [
        {
            accessorKey: 'title',
            header: ({ column }) => (
                <Button
                    variant="ghost"
                    onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
                >
                    Title
                    <ArrowUpDown className="ml-2 h-4 w-4" />
                </Button>
            ),
            cell: ({ row }) => (
                <Link
                    to={`/contracts/${row.original.id}`}
                    className="font-medium hover:underline text-primary"
                >
                    {row.getValue('title')}
                </Link>
            ),
        },
        {
            accessorKey: 'status',
            header: 'Status',
            cell: ({ row }) => {
                const status = row.getValue('status') as ContractStatus
                return (
                    <Badge className={CONTRACT_STATUS_COLORS[status] || ''}>
                        {CONTRACT_STATUS_LABELS[status] || status}
                    </Badge>
                )
            },
            filterFn: (row, id, value) => {
                return value === 'all' || row.getValue(id) === value
            },
        },
        {
            accessorKey: 'version',
            header: 'Version',
            cell: ({ row }) => (
                <span className="text-muted-foreground">
                    v{row.getValue('version')}
                </span>
            ),
        },
        {
            accessorKey: 'created_at',
            header: ({ column }) => (
                <Button
                    variant="ghost"
                    onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
                >
                    Created
                    <ArrowUpDown className="ml-2 h-4 w-4" />
                </Button>
            ),
            cell: ({ row }) => {
                const date = new Date(row.getValue('created_at'))
                return (
                    <span className="text-muted-foreground">
                        {date.toLocaleDateString('en-US', {
                            year: 'numeric',
                            month: 'short',
                            day: 'numeric'
                        })}
                    </span>
                )
            },
        },
        {
            accessorKey: 'updated_at',
            header: 'Last Updated',
            cell: ({ row }) => {
                const updatedAt = row.getValue('updated_at') as string | null
                if (!updatedAt) return <span className="text-muted-foreground">—</span>
                
                const date = new Date(updatedAt)
                return (
                    <span className="text-muted-foreground">
                        {date.toLocaleDateString('en-US', {
                            year: 'numeric',
                            month: 'short',
                            day: 'numeric'
                        })}
                    </span>
                )
            },
        },
        {
            id: 'actions',
            cell: ({ row }) => {
                const contract = row.original
                return (
                    <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                            <Button variant="ghost" className="h-8 w-8 p-0">
                                <span className="sr-only">Open menu</span>
                                <MoreHorizontal className="h-4 w-4" />
                            </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                            <DropdownMenuLabel>Actions</DropdownMenuLabel>
                            <DropdownMenuItem
                                onClick={() => navigator.clipboard.writeText(contract.id)}
                            >
                                Copy ID
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem asChild>
                                <Link to={`/contracts/${contract.id}`}>View Details</Link>
                            </DropdownMenuItem>
                            {contract.status === 'draft' && (
                                <DropdownMenuItem asChild>
                                    <Link to={`/contracts/${contract.id}/edit`}>Edit</Link>
                                </DropdownMenuItem>
                            )}
                            <DropdownMenuItem asChild>
                                <Link to={`/validate?contract=${contract.id}`}>Validate</Link>
                            </DropdownMenuItem>
                        </DropdownMenuContent>
                    </DropdownMenu>
                )
            },
        },
    ]

    if (error) {
        return (
            <div className="space-y-6">
                <div>
                    <h1 className="text-3xl font-bold">Contracts</h1>
                    <p className="text-muted-foreground">Manage and explore all contracts</p>
                </div>
                <div className="flex items-center justify-center h-64">
                    <div className="text-center">
                        <p className="text-destructive">Failed to load contracts</p>
                        <p className="text-sm text-muted-foreground mt-1">
                            {(error as any)?.message || 'An error occurred'}
                        </p>
                    </div>
                </div>
            </div>
        )
    }

    return (
        <div className="space-y-6 page-enter">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">Contracts</h1>
                    <p className="text-muted-foreground">Manage and explore all contracts</p>
                </div>
                <Button asChild>
                    <Link to="/generate">
                        <Plus className="mr-2 h-4 w-4" />
                        New Contract
                    </Link>
                </Button>
            </div>

            {/* Filters */}
            <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                    <Filter className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm text-muted-foreground">Filter by status:</span>
                </div>
                <Select
                    value={statusFilter}
                    onValueChange={(value) => setStatusFilter(value as ContractStatus | 'all')}
                >
                    <SelectTrigger className="w-48">
                        <SelectValue placeholder="All statuses" />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="all">All Statuses</SelectItem>
                        <SelectItem value="draft">Draft</SelectItem>
                        <SelectItem value="pending_review">Pending Review</SelectItem>
                        <SelectItem value="approved">Approved</SelectItem>
                        <SelectItem value="rejected">Rejected</SelectItem>
                        <SelectItem value="executed">Executed</SelectItem>
                        <SelectItem value="archived">Archived</SelectItem>
                    </SelectContent>
                </Select>
            </div>

            {isLoading ? (
                <TableSkeleton rows={8} columns={6} />
            ) : (
                <DataTable
                    columns={columns}
                    data={contracts || []}
                    searchKey="title"
                />
            )}
        </div>
    )
}
