import { useState } from 'react'
import type { ColumnDef } from '@tanstack/react-table'
import { MoreHorizontal, ArrowUpDown, Users, Key, Settings, Plus } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { DataTable } from '@/components/ui/data-table'
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'

type User = {
    id: string
    name: string
    email: string
    role: string
}

export function AdminPanel() {
    const [activeTab, setActiveTab] = useState<'users' | 'permissions' | 'api'>('users')

    const mockUsers: User[] = [
        { id: '1', name: 'John Doe', email: 'john.doe@example.com', role: 'admin' },
        { id: '2', name: 'Sarah Wilson', email: 'sarah.wilson@example.com', role: 'legal_team' },
        { id: '3', name: 'Michael Chen', email: 'michael.chen@example.com', role: 'business_user' },
    ]

    const userColumns: ColumnDef<User>[] = [
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
        },
        {
            accessorKey: 'email',
            header: 'Email',
        },
        {
            accessorKey: 'role',
            header: 'Role',
            cell: ({ row }) => <Badge>{row.getValue('role')}</Badge>,
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
                            <DropdownMenuItem>Edit User</DropdownMenuItem>
                            <DropdownMenuItem className="text-red-600">Delete User</DropdownMenuItem>
                        </DropdownMenuContent>
                    </DropdownMenu>
                )
            },
        },
    ]

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold">Admin Panel</h1>
                <p className="text-muted-foreground">System administration and configuration</p>
            </div>

            {/* Tabs */}
            <div className="flex gap-2 border-b">
                <button
                    className={`flex items-center gap-2 px-4 py-2 font-medium ${activeTab === 'users'
                        ? 'border-b-2 border-primary text-primary'
                        : 'text-muted-foreground'
                        }`}
                    onClick={() => setActiveTab('users')}
                >
                    <Users className="h-4 w-4" />
                    Users
                </button>
                <button
                    className={`flex items-center gap-2 px-4 py-2 font-medium ${activeTab === 'permissions'
                        ? 'border-b-2 border-primary text-primary'
                        : 'text-muted-foreground'
                        }`}
                    onClick={() => setActiveTab('permissions')}
                >
                    <Settings className="h-4 w-4" />
                    Permissions
                </button>
                <button
                    className={`flex items-center gap-2 px-4 py-2 font-medium ${activeTab === 'api'
                        ? 'border-b-2 border-primary text-primary'
                        : 'text-muted-foreground'
                        }`}
                    onClick={() => setActiveTab('api')}
                >
                    <Key className="h-4 w-4" />
                    API Keys
                </button>
            </div>

            {/* Tab Content */}
            {activeTab === 'users' && (
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between">
                        <CardTitle>User Management</CardTitle>
                        <Button size="sm">
                            <Plus className="mr-2 h-4 w-4" />
                            Add User
                        </Button>
                    </CardHeader>
                    <CardContent>
                        <DataTable
                            columns={userColumns}
                            data={mockUsers}
                            searchKey="name"
                        />
                    </CardContent>
                </Card>
            )}

            {activeTab === 'permissions' && (
                <Card>
                    <CardHeader>
                        <CardTitle>Role Permissions</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <p className="text-sm text-muted-foreground">
                            Permission matrix configuration would be displayed here
                        </p>
                    </CardContent>
                </Card>
            )}

            {activeTab === 'api' && (
                <Card>
                    <CardHeader>
                        <CardTitle>API Key Settings</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="space-y-2">
                            <label className="text-sm font-medium">OpenRouter API Key</label>
                            <Input type="password" placeholder="sk-or-..." />
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium">Pinecone API Key</label>
                            <Input type="password" placeholder="pc-..." />
                        </div>
                        <Button>Save Settings</Button>
                    </CardContent>
                </Card>
            )}
        </div>
    )
}
