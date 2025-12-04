import { useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { useContract, useSubmitContract, useApproveContract, useRejectContract, useExecuteContract, useArchiveContract, useCreateVersion } from '@/hooks/useContracts'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Textarea } from '@/components/ui/textarea'
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from '@/components/ui/dialog'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
    ArrowLeft, 
    FileText, 
    Clock, 
    User, 
    Send, 
    Check, 
    X, 
    Archive,
    GitBranch,
    Shield,
    Download,
    Edit,
    Loader2
} from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { getStatusColor, formatStatus } from '@/types/contract'
import { canReview } from '@/types/user'
import { format } from 'date-fns'

export function ContractDetail() {
    const { id } = useParams<{ id: string }>()
    const navigate = useNavigate()
    const { user } = useAuth()
    const { data: contract, isLoading, error } = useContract(id || '')
    
    const [rejectDialogOpen, setRejectDialogOpen] = useState(false)
    const [rejectionReason, setRejectionReason] = useState('')
    const [approvalNotes, setApprovalNotes] = useState('')
    const [approvalDialogOpen, setApprovalDialogOpen] = useState(false)

    const submitMutation = useSubmitContract()
    const approveMutation = useApproveContract()
    const rejectMutation = useRejectContract()
    const executeMutation = useExecuteContract()
    const archiveMutation = useArchiveContract()
    const createVersionMutation = useCreateVersion()

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
        )
    }

    if (error || !contract) {
        return (
            <div className="flex flex-col items-center justify-center h-64">
                <p className="text-lg font-medium text-destructive">Contract not found</p>
                <Button variant="link" asChild className="mt-2">
                    <Link to="/contracts">Back to Contracts</Link>
                </Button>
            </div>
        )
    }

    const isReviewer = canReview(user)
    const isOwner = contract.created_by === user?.id

    const handleSubmit = () => {
        submitMutation.mutate(contract.id)
    }

    const handleApprove = () => {
        approveMutation.mutate({ id: contract.id, notes: approvalNotes })
        setApprovalDialogOpen(false)
    }

    const handleReject = () => {
        if (!rejectionReason.trim()) return
        rejectMutation.mutate({ id: contract.id, reason: rejectionReason })
        setRejectDialogOpen(false)
    }

    const handleExecute = () => {
        executeMutation.mutate(contract.id)
    }

    const handleArchive = () => {
        archiveMutation.mutate(contract.id, {
            onSuccess: () => navigate('/contracts')
        })
    }

    const handleCreateVersion = () => {
        createVersionMutation.mutate(contract.id, {
            onSuccess: (newContract) => {
                navigate(`/contracts/${newContract.id}`)
            }
        })
    }

    return (
        <div className="space-y-6 page-enter">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <Button variant="ghost" size="icon" onClick={() => navigate('/contracts')}>
                        <ArrowLeft className="h-4 w-4" />
                    </Button>
                    <div>
                        <div className="flex items-center gap-3">
                            <h1 className="text-2xl font-bold">{contract.title}</h1>
                            <Badge className={getStatusColor(contract.status)}>
                                {formatStatus(contract.status)}
                            </Badge>
                            <Badge variant="outline">v{contract.version}</Badge>
                        </div>
                        {contract.description && (
                            <p className="text-muted-foreground mt-1">{contract.description}</p>
                        )}
                    </div>
                </div>
            </div>

            {/* Action Buttons based on status */}
            <div className="flex flex-wrap gap-3">
                {contract.status === 'draft' && isOwner && (
                    <>
                        <Button onClick={handleSubmit} disabled={submitMutation.isPending}>
                            <Send className="mr-2 h-4 w-4" />
                            Submit for Review
                        </Button>
                        <Button variant="outline" asChild>
                            <Link to={`/contracts/${contract.id}?edit=true`}>
                                <Edit className="mr-2 h-4 w-4" />
                                Edit
                            </Link>
                        </Button>
                    </>
                )}

                {contract.status === 'pending_review' && isReviewer && (
                    <>
                        <Button onClick={() => setApprovalDialogOpen(true)} disabled={approveMutation.isPending}>
                            <Check className="mr-2 h-4 w-4" />
                            Approve
                        </Button>
                        <Button variant="destructive" onClick={() => setRejectDialogOpen(true)}>
                            <X className="mr-2 h-4 w-4" />
                            Reject
                        </Button>
                    </>
                )}

                {contract.status === 'approved' && isOwner && (
                    <Button onClick={handleExecute} disabled={executeMutation.isPending}>
                        <Check className="mr-2 h-4 w-4" />
                        Mark as Executed
                    </Button>
                )}

                {contract.status === 'approved' && (
                    <Button variant="outline" asChild>
                        <Link to={`/validate?contract=${contract.id}`}>
                            <Shield className="mr-2 h-4 w-4" />
                            Validate
                        </Link>
                    </Button>
                )}

                {(contract.status === 'executed' || contract.status === 'approved') && isOwner && (
                    <Button variant="outline" onClick={handleCreateVersion} disabled={createVersionMutation.isPending}>
                        <GitBranch className="mr-2 h-4 w-4" />
                        Create New Version
                    </Button>
                )}

                {contract.status !== 'archived' && isOwner && (
                    <Button variant="ghost" onClick={handleArchive} disabled={archiveMutation.isPending}>
                        <Archive className="mr-2 h-4 w-4" />
                        Archive
                    </Button>
                )}

                <Button variant="outline">
                    <Download className="mr-2 h-4 w-4" />
                    Export PDF
                </Button>
            </div>

            {/* Tabs */}
            <Tabs defaultValue="content">
                <TabsList>
                    <TabsTrigger value="content">
                        <FileText className="mr-2 h-4 w-4" />
                        Content
                    </TabsTrigger>
                    <TabsTrigger value="details">
                        <Clock className="mr-2 h-4 w-4" />
                        Details
                    </TabsTrigger>
                    <TabsTrigger value="history">
                        <GitBranch className="mr-2 h-4 w-4" />
                        History
                    </TabsTrigger>
                </TabsList>

                <TabsContent value="content">
                    <Card>
                        <CardHeader>
                            <CardTitle>Contract Content</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="prose dark:prose-invert max-w-none">
                                <pre className="whitespace-pre-wrap font-sans text-sm bg-muted/30 p-4 rounded-lg">
                                    {contract.content}
                                </pre>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                <TabsContent value="details">
                    <div className="grid gap-4 md:grid-cols-2">
                        <Card>
                            <CardHeader>
                                <CardTitle>Timeline</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="flex items-center gap-3">
                                    <Clock className="h-4 w-4 text-muted-foreground" />
                                    <div>
                                        <p className="text-sm font-medium">Created</p>
                                        <p className="text-sm text-muted-foreground">
                                            {format(new Date(contract.created_at), 'PPpp')}
                                        </p>
                                    </div>
                                </div>
                                {contract.submitted_at && (
                                    <div className="flex items-center gap-3">
                                        <Send className="h-4 w-4 text-muted-foreground" />
                                        <div>
                                            <p className="text-sm font-medium">Submitted</p>
                                            <p className="text-sm text-muted-foreground">
                                                {format(new Date(contract.submitted_at), 'PPpp')}
                                            </p>
                                        </div>
                                    </div>
                                )}
                                {contract.reviewed_at && (
                                    <div className="flex items-center gap-3">
                                        <Check className="h-4 w-4 text-muted-foreground" />
                                        <div>
                                            <p className="text-sm font-medium">Reviewed</p>
                                            <p className="text-sm text-muted-foreground">
                                                {format(new Date(contract.reviewed_at), 'PPpp')}
                                            </p>
                                        </div>
                                    </div>
                                )}
                                {contract.executed_at && (
                                    <div className="flex items-center gap-3">
                                        <Check className="h-4 w-4 text-green-500" />
                                        <div>
                                            <p className="text-sm font-medium">Executed</p>
                                            <p className="text-sm text-muted-foreground">
                                                {format(new Date(contract.executed_at), 'PPpp')}
                                            </p>
                                        </div>
                                    </div>
                                )}
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader>
                                <CardTitle>Review Information</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                {contract.review_notes && (
                                    <div>
                                        <p className="text-sm font-medium">Approval Notes</p>
                                        <p className="text-sm text-muted-foreground mt-1">
                                            {contract.review_notes}
                                        </p>
                                    </div>
                                )}
                                {contract.rejection_reason && (
                                    <div>
                                        <p className="text-sm font-medium text-destructive">Rejection Reason</p>
                                        <p className="text-sm text-muted-foreground mt-1">
                                            {contract.rejection_reason}
                                        </p>
                                    </div>
                                )}
                                {!contract.review_notes && !contract.rejection_reason && (
                                    <p className="text-sm text-muted-foreground">No review information yet.</p>
                                )}
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader>
                                <CardTitle>Metadata</CardTitle>
                            </CardHeader>
                            <CardContent>
                                {contract.custom_metadata && Object.keys(contract.custom_metadata).length > 0 ? (
                                    <div className="space-y-2">
                                        {Object.entries(contract.custom_metadata).map(([key, value]) => (
                                            <div key={key} className="flex justify-between">
                                                <span className="text-sm text-muted-foreground">{key}</span>
                                                <span className="text-sm font-medium">{String(value)}</span>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <p className="text-sm text-muted-foreground">No metadata available.</p>
                                )}
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader>
                                <CardTitle>Version Info</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-2">
                                <div className="flex justify-between">
                                    <span className="text-sm text-muted-foreground">Version</span>
                                    <span className="text-sm font-medium">v{contract.version}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-sm text-muted-foreground">Latest Version</span>
                                    <Badge variant={contract.is_latest_version ? 'default' : 'secondary'}>
                                        {contract.is_latest_version ? 'Yes' : 'No'}
                                    </Badge>
                                </div>
                                {contract.template_id && (
                                    <div className="flex justify-between">
                                        <span className="text-sm text-muted-foreground">From Template</span>
                                        <Badge variant="outline">Yes</Badge>
                                    </div>
                                )}
                            </CardContent>
                        </Card>
                    </div>
                </TabsContent>

                <TabsContent value="history">
                    <Card>
                        <CardHeader>
                            <CardTitle>Version History</CardTitle>
                            <CardDescription>Track changes across different versions</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <p className="text-sm text-muted-foreground">
                                Version history will show all versions of this contract.
                            </p>
                            {/* Future: Show version timeline */}
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>

            {/* Approval Dialog */}
            <Dialog open={approvalDialogOpen} onOpenChange={setApprovalDialogOpen}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Approve Contract</DialogTitle>
                        <DialogDescription>
                            Add any notes for this approval (optional)
                        </DialogDescription>
                    </DialogHeader>
                    <Textarea
                        value={approvalNotes}
                        onChange={(e) => setApprovalNotes(e.target.value)}
                        placeholder="Approval notes..."
                        rows={3}
                    />
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setApprovalDialogOpen(false)}>
                            Cancel
                        </Button>
                        <Button onClick={handleApprove} disabled={approveMutation.isPending}>
                            <Check className="mr-2 h-4 w-4" />
                            Approve
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>

            {/* Rejection Dialog */}
            <Dialog open={rejectDialogOpen} onOpenChange={setRejectDialogOpen}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Reject Contract</DialogTitle>
                        <DialogDescription>
                            Provide a reason for rejecting this contract
                        </DialogDescription>
                    </DialogHeader>
                    <Textarea
                        value={rejectionReason}
                        onChange={(e) => setRejectionReason(e.target.value)}
                        placeholder="Reason for rejection..."
                        rows={4}
                    />
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setRejectDialogOpen(false)}>
                            Cancel
                        </Button>
                        <Button 
                            variant="destructive" 
                            onClick={handleReject} 
                            disabled={!rejectionReason.trim() || rejectMutation.isPending}
                        >
                            <X className="mr-2 h-4 w-4" />
                            Reject
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    )
}
