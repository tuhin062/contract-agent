import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from '@/components/ui/sheet'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Download, Eye, CheckCircle, XCircle } from 'lucide-react'
import { ProposalKeyInfoCard } from './ProposalKeyInfoCard'

interface ProposalPreviewProps {
    open: boolean
    onOpenChange: (open: boolean) => void
    proposal: {
        id: string
        title: string
        project: string
        budget: string
        timeline: string
        vendor: string
        status: string
        score?: number
        file: string
    }
    onAccept?: () => void
    onReject?: () => void
}

export function ProposalPreview({ open, onOpenChange, proposal, onAccept, onReject }: ProposalPreviewProps) {
    return (
        <Sheet open={open} onOpenChange={onOpenChange}>
            <SheetContent className="w-full sm:max-w-xl overflow-y-auto">
                <SheetHeader>
                    <SheetTitle>{proposal.title}</SheetTitle>
                    <SheetDescription>
                        {proposal.project}
                    </SheetDescription>
                </SheetHeader>

                <div className="space-y-6 mt-6">
                    {/* Key Info Card */}
                    <ProposalKeyInfoCard proposal={proposal} />

                    {/* Document Info */}
                    <div className="space-y-2">
                        <p className="text-sm font-medium">Document</p>
                        <div className="flex items-center justify-between p-3 border rounded-lg">
                            <span className="text-sm font-medium">{proposal.file}</span>
                            <Button variant="outline" size="sm">
                                <Download className="mr-2 h-4 w-4" />
                                Download
                            </Button>
                        </div>
                    </div>

                    {/* Actions */}
                    <div className="flex gap-3">
                        <Button variant="outline" className="flex-1">
                            <Eye className="mr-2 h-4 w-4" />
                            View Full
                        </Button>
                        {proposal.status === 'pending' && (
                            <>
                                <Button
                                    variant="outline"
                                    className="flex-1 text-destructive hover:bg-destructive hover:text-destructive-foreground"
                                    onClick={onReject}
                                >
                                    <XCircle className="mr-2 h-4 w-4" />
                                    Reject
                                </Button>
                                <Button
                                    className="flex-1"
                                    onClick={onAccept}
                                >
                                    <CheckCircle className="mr-2 h-4 w-4" />
                                    Accept
                                </Button>
                            </>
                        )}
                    </div>
                </div>
            </SheetContent>
        </Sheet>
    )
}
