import { useState } from 'react'
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from '@/components/ui/sheet'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { toast } from '@/lib/toast'
import { Upload } from 'lucide-react'

interface UploadProposalDrawerProps {
    open: boolean
    onOpenChange: (open: boolean) => void
    onSuccess?: () => void
}

export function UploadProposalDrawer({ open, onOpenChange, onSuccess }: UploadProposalDrawerProps) {
    const [formData, setFormData] = useState({
        title: '',
        project: '',
        budget: '',
        timeline: '',
    })
    const [file, setFile] = useState<File | null>(null)
    const [uploading, setUploading] = useState(false)

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0])
        }
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()

        if (!file) {
            toast.error('File required', 'Please select a proposal file to upload')
            return
        }

        setUploading(true)

        // Simulate upload
        await new Promise((resolve) => setTimeout(resolve, 2000))

        toast.success('Proposal uploaded', `${formData.title} has been uploaded successfully`)
        setUploading(false)
        onOpenChange(false)
        onSuccess?.()

        // Reset form
        setFormData({ title: '', project: '', budget: '', timeline: '' })
        setFile(null)
    }

    return (
        <Sheet open={open} onOpenChange={onOpenChange}>
            <SheetContent className="w-full sm:max-w-lg overflow-y-auto">
                <SheetHeader>
                    <SheetTitle>Upload Proposal</SheetTitle>
                    <SheetDescription>
                        Upload a business proposal for review and comparison
                    </SheetDescription>
                </SheetHeader>

                <form onSubmit={handleSubmit} className="space-y-6 mt-6">
                    <div className="space-y-4">
                        <div className="space-y-2">
                            <Label htmlFor="title">Proposal Title *</Label>
                            <Input
                                id="title"
                                placeholder="e.g., Q1 Marketing Campaign"
                                value={formData.title}
                                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                                required
                            />
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="project">Project Name *</Label>
                            <Input
                                id="project"
                                placeholder="e.g., Digital Transformation"
                                value={formData.project}
                                onChange={(e) => setFormData({ ...formData, project: e.target.value })}
                                required
                            />
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <Label htmlFor="budget">Budget</Label>
                                <Input
                                    id="budget"
                                    placeholder="$50,000"
                                    value={formData.budget}
                                    onChange={(e) => setFormData({ ...formData, budget: e.target.value })}
                                />
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="timeline">Timeline</Label>
                                <Input
                                    id="timeline"
                                    placeholder="3 months"
                                    value={formData.timeline}
                                    onChange={(e) => setFormData({ ...formData, timeline: e.target.value })}
                                />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="file">Proposal Document *</Label>
                            <Input
                                id="file"
                                type="file"
                                accept=".pdf,.doc,.docx"
                                onChange={handleFileChange}
                                required
                            />
                            {file && (
                                <p className="text-sm text-muted-foreground">
                                    Selected: {file.name}
                                </p>
                            )}
                        </div>
                    </div>

                    <div className="flex gap-3">
                        <Button
                            type="button"
                            variant="outline"
                            onClick={() => onOpenChange(false)}
                            disabled={uploading}
                            className="flex-1"
                        >
                            Cancel
                        </Button>
                        <Button type="submit" disabled={uploading} className="flex-1">
                            <Upload className="mr-2 h-4 w-4" />
                            {uploading ? 'Uploading...' : 'Upload'}
                        </Button>
                    </div>
                </form>
            </SheetContent>
        </Sheet>
    )
}
