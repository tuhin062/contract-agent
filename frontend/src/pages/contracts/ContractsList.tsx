import { Link } from 'react-router-dom'
import type { ColumnDef } from '@tanstack/react-table'
import { MoreHorizontal, ArrowUpDown } from 'lucide-react'
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
import type { ContractDetail } from '@/types/contract'

export function ContractsList() {
    const { data: contracts, isLoading } = useContracts()

    const columns: ColumnDef<ContractDetail>[] = [
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
            cell: ({ row }) => (
                <Link
                    to={`/contracts/${row.original.id}`}
                    className="font-medium hover:underline"
                >
                    {row.getValue('title')}
                </Link>
            ),
        },
        {
            accessorKey: 'type',
            header: 'Type',
        },
        {
            accessorKey: 'status',
            header: 'Status',
            cell: ({ row }) => {
                const status = row.getValue('status') as string
                let color = 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200'

                if (status === 'active') color = 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                if (status === 'pending_approval') color = 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                if (status === 'expired') color = 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'

                return <Badge className={color}>{status}</Badge>
            },
        },
        {
            accessorKey: 'value',
            header: ({ column }) => {
                return (
                    <Button
                        variant="ghost"
                        onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
                    >
                        Value
                        <ArrowUpDown className="ml-2 h-4 w-4" />
                    </Button>
                )
            },
            cell: ({ row }) => {
                const amount = parseFloat(row.getValue('value'))
                const formatted = new Intl.NumberFormat('en-US', {
                    style: 'currency',
                    currency: 'USD',
                }).format(amount)
                return <div className="font-medium">{formatted}</div>
            },
        },
        {
            accessorKey: 'startDate',
            header: 'Start Date',
            cell: ({ row }) => {
                return new Date(row.getValue('startDate')).toLocaleDateString()
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
                            <DropdownMenuItem>Download PDF</DropdownMenuItem>
                        </DropdownMenuContent>
                    </DropdownMenu>
                )
            },
        },
    ]

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold">Contracts</h1>
                <p className="text-muted-foreground">Manage and explore all contracts</p>
            </div>

            {isLoading ? (
                <div className="flex items-center justify-center h-64">
                    <p>Loading contracts...</p>
                </div>
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
