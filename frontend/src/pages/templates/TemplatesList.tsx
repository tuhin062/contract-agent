import type { ColumnDef } from '@tanstack/react-table'
import { MoreHorizontal, ArrowUpDown, Plus } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useTemplates } from '@/hooks/useTemplates'
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
import type { Template } from '@/types/template'

export function TemplatesList() {
    const navigate = useNavigate()
    const { data: templates, isLoading } = useTemplates()

    const columns: ColumnDef<Template>[] = [
        {
            accessorKey: 'name',
            header: ({ column }) => {
                return (
                    <Button
                        variant="ghost"
                        onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
                    >
                        Name
                        <ArrowUpDown className="ml-2 h-4 w-4" />
                    </Button>
                )
            },
            cell: ({ row }) => (
                <div
                    className="font-medium cursor-pointer hover:text-primary transition-colors"
                    onClick={() => navigate(`/templates/${row.original.id}`)}
                >
                    {row.getValue('name')}
                </div>
            ),
        },
        {
            accessorKey: 'category',
            header: 'Category',
            cell: ({ row }) => <Badge variant="secondary">{row.getValue('category')}</Badge>,
        },
        {
            accessorKey: 'description',
            header: 'Description',
            cell: ({ row }) => (
                <div className="max-w-[300px] truncate" title={row.getValue('description')}>
                    {row.getValue('description')}
                </div>
            ),
        },
        {
            accessorKey: 'version',
            header: 'Version',
        },
        {
            accessorKey: 'lastUpdated',
            header: ({ column }) => {
                return (
                    <Button
                        variant="ghost"
                        onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
                    >
                        Last Updated
                        <ArrowUpDown className="ml-2 h-4 w-4" />
                    </Button>
                )
            },
            cell: ({ row }) => {
                const date = new Date(row.getValue('lastUpdated'))
                return <div>{date.toLocaleDateString()}</div>
            },
        },
        {
            id: 'actions',
            cell: ({ row }) => {
                const template = row.original

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
                            <DropdownMenuItem onClick={() => navigate(`/templates/${template.id}`)}>
                                View Details
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => navigate(`/generate?template=${template.id}`)}>
                                Use Template
                            </DropdownMenuItem>
                            <DropdownMenuItem>Edit Template</DropdownMenuItem>
                            <DropdownMenuItem className="text-destructive">
                                Delete Template
                            </DropdownMenuItem>
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
                    <h1 className="text-3xl font-bold">Contract Templates</h1>
                    <p className="text-muted-foreground">
                        Pre-configured templates for common contract types
                    </p>
                </div>
                <Button>
                    <Plus className="mr-2 h-4 w-4" />
                    Create Template
                </Button>
            </div>

            <DataTable columns={columns} data={templates || []} loading={isLoading} />
        </div>
    )
}
