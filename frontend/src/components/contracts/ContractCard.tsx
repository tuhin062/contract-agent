import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { FileText, MoreVertical, Calendar, DollarSign } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

interface ContractCardProps {
    contract: {
        id: string
        title: string
        type: string
        status: string
        parties: string[]
        value?: number
        startDate: string
        endDate: string
    }
}

export function ContractCard({ contract }: ContractCardProps) {
    const navigate = useNavigate()

    const statusColors = {
        active: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
        pending_approval: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
        draft: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200',
        expired: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
    }

    return (
        <Card
            className="hover-lift cursor-pointer transition-all"
            onClick={() => navigate(`/contracts/${contract.id}`)}
        >
            <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3">
                        <div className="p-2 bg-primary/10 rounded-lg">
                            <FileText className="h-5 w-5 text-primary" />
                        </div>
                        <div>
                            <h3 className="font-semibold line-clamp-1">{contract.title}</h3>
                            <p className="text-sm text-muted-foreground">{contract.type}</p>
                        </div>
                    </div>
                    <DropdownMenu>
                        <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                            <Button variant="ghost" size="icon" className="h-8 w-8">
                                <MoreVertical className="h-4 w-4" />
                            </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                            <DropdownMenuItem>View Details</DropdownMenuItem>
                            <DropdownMenuItem>Edit</DropdownMenuItem>
                            <DropdownMenuItem>Download</DropdownMenuItem>
                            <DropdownMenuItem className="text-destructive">Delete</DropdownMenuItem>
                        </DropdownMenuContent>
                    </DropdownMenu>
                </div>
            </CardHeader>
            <CardContent className="space-y-3">
                {/* Status */}
                <div>
                    <Badge className={statusColors[contract.status as keyof typeof statusColors] || statusColors.draft}>
                        {contract.status.replace('_', ' ')}
                    </Badge>
                </div>

                {/* Parties */}
                <div>
                    <p className="text-xs text-muted-foreground mb-1">Parties</p>
                    <p className="text-sm font-medium line-clamp-1">{contract.parties.join(', ')}</p>
                </div>

                {/* Value */}
                {contract.value && (
                    <div className="flex items-center gap-2">
                        <DollarSign className="h-4 w-4 text-muted-foreground" />
                        <span className="font-semibold">
                            ${contract.value.toLocaleString()}
                        </span>
                    </div>
                )}

                {/* Dates */}
                <div className="flex items-center gap-4 text-xs text-muted-foreground">
                    <div className="flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        <span>{new Date(contract.startDate).toLocaleDateString()}</span>
                    </div>
                    <span>→</span>
                    <span>{new Date(contract.endDate).toLocaleDateString()}</span>
                </div>
            </CardContent>
        </Card>
    )
}
