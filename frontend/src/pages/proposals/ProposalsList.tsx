import { useState } from 'react'
import type { ColumnDef } from '@tanstack/react-table'
import { MoreHorizontal, ArrowUpDown, Upload } from 'lucide-react'
import { useProposals } from '@/hooks/useProposals'
import { DataTable } from '@/components/ui/data-table'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { UploadProposalDrawer } from '@/components/UploadProposalDrawer'
import type { Proposal } from '@/types/proposal'
import { formatDate } from '@/lib/utils'

export function ProposalsList() {
    const { data: proposals, isLoading, refetch } = useProposals()
    const [uploadDrawerOpen, setUploadDrawerOpen] = useState(false)

    const columns: ColumnDef<Proposal>[] = [
        {
            accessorKey: 'title',
            header: ({ column }) => {
                return (
                    <Button
                        variant="ghost"
                        onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
                    >
                        Title
                        <ArrowUpDown className="ml-2 h-4 w-4" />
                    </Button>
                )
            },
        },
        {
            accessorKey: 'metadata.projectName',
            header: 'Project',
        },
        {
            accessorKey: 'metadata.budget',
            header: 'Budget',
            cell: ({ row }) => {
                const amount = row.original.metadata.budget
                const currency = row.original.metadata.currency
                return (
                    <div className="font-medium">
                        {amount.toLocaleString()} {currency}
                    </div>
                )
            },
        },
        {
            accessorKey: 'metadata.timeline',
            header: 'Timeline',
        },
        {
            accessorKey: 'status',
            header: 'Status',
            cell: ({ row }) => {
                const status = row.getValue('status') as string
                return (
                    <Badge variant={status === 'processed' ? 'default' : 'secondary'}>
                        {status}
                    </Badge>
                )
            },
        },
        {
            accessorKey: 'uploadDate',
            header: 'Uploaded',
            cell: ({ row }) => formatDate(row.getValue('uploadDate')),
        },
        {
            id: 'actions',
            cell: ({ row }) => {
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
                                onClick={() => navigator.clipboard.writeText(row.original.id)}
                            >
                                Copy ID
                            </DropdownMenuItem>
                            <DropdownMenuItem>View Details</DropdownMenuItem>
                        </DropdownMenuContent>
                    </DropdownMenu>
                )
            },
        },
    ]

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">Business Proposals</h1>
                    <p className="text-muted-foreground">Manage uploaded proposals</p>
                </div>
                <Button onClick={() => setUploadDrawerOpen(true)}>
                    <Upload className="mr-2 h-4 w-4" />
                    Upload Proposal
                </Button>
            </div>

            {isLoading ? (
                <div className="flex items-center justify-center h-64">
                    <p>Loading proposals...</p>
                </div>
            ) : (
                <DataTable
                    columns={columns}
                    data={proposals || []}
                    searchKey="title"
                />
            )}

            <UploadProposalDrawer
                open={uploadDrawerOpen}
                onOpenChange={setUploadDrawerOpen}
                onSuccess={() => refetch()}
            />
        </div>
    )
}

