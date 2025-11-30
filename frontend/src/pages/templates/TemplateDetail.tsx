import { useParams, Link, useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { PDFViewer } from '@/components/ui/pdf-viewer'
import { useTemplates } from '@/hooks/useTemplates'
import {
    ArrowLeft,
    FileEdit,
    Trash2,
    Download,
    Copy,
    Calendar,
    Tag,
    FileText,
    TrendingUp
} from 'lucide-react'
import { toast } from '@/lib/toast'
import { useState } from 'react'
import { ConfirmDialog } from '@/components/ui/confirm-dialog'

export function TemplateDetail() {
    const { id } = useParams()
    const navigate = useNavigate()
    const { data: templates } = useTemplates()
    const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)

    const template = templates?.find((t) => t.id === id)

    if (!template) {
        return (
            <div className="flex items-center justify-center h-[60vh]">
                <div className="text-center">
                    <h2 className="text-2xl font-bold mb-2">Template Not Found</h2>
                    <p className="text-muted-foreground mb-4">
                        The template you're looking for doesn't exist.
                    </p>
                    <Button asChild>
                        <Link to="/templates">Back to Templates</Link>
                    </Button>
                </div>
            </div>
        )
    }

    const handleUseTemplate = () => {
        toast.success('Template Selected', `Using template: ${template.name}`)
        navigate(`/generate?template=${template.id}`)
    }

    const handleDelete = () => {
        toast.success('Template Deleted', 'Template has been removed')
        navigate('/templates')
    }

    const handleDownload = () => {
        toast.success('Download Started', 'Template is being downloaded')
    }

    const handleDuplicate = () => {
        toast.success('Template Duplicated', 'A copy of the template has been created')
    }

    // Mock usage statistics
    const stats = {
        timesUsed: Math.floor(Math.random() * 50) + 10,
        successRate: Math.floor(Math.random() * 20) + 80,
        avgCompletionTime: `${Math.floor(Math.random() * 10) + 5} minutes`,
        lastUsed: '2 days ago'
    }

    return (
        <div className="space-y-6 page-enter">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <Button variant="ghost" size="icon" asChild>
                        <Link to="/templates">
                            <ArrowLeft className="h-5 w-5" />
                        </Link>
                    </Button>
                    <div>
                        <h1 className="text-3xl font-bold">{template.name}</h1>
                        <p className="text-muted-foreground">{template.description}</p>
                    </div>
                </div>

                <div className="flex gap-2">
                    <Button onClick={handleDuplicate} variant="outline">
                        <Copy className="mr-2 h-4 w-4" />
                        Duplicate
                    </Button>
                    <Button onClick={handleDownload} variant="outline">
                        <Download className="mr-2 h-4 w-4" />
                        Download
                    </Button>
                    <Button onClick={handleUseTemplate}>
                        <FileEdit className="mr-2 h-4 w-4" />
                        Use Template
                    </Button>
                </div>
            </div>

            <div className="grid md:grid-cols-3 gap-6">
                {/* Main Content - PDF Preview */}
                <div className="md:col-span-2 space-y-6">
                    <Card>
                        <CardHeader>
                            <CardTitle>Template Preview</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <PDFViewer url="/mock/sample.pdf" />
                        </CardContent>
                    </Card>

                    {/* Template Fields */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Required Fields ({template.fields?.length || 0})</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-3">
                                {template.fields?.map((field) => (
                                    <div
                                        key={field.id}
                                        className="p-3 border rounded-lg hover:bg-accent transition-colors"
                                    >
                                        <div className="flex items-center justify-between">
                                            <div>
                                                <p className="font-medium">{field.label}</p>
                                                <p className="text-sm text-muted-foreground">
                                                    Type: {field.type}
                                                    {field.required && (
                                                        <span className="text-destructive ml-2">* Required</span>
                                                    )}
                                                </p>
                                            </div>
                                            <Badge variant="outline">{field.type}</Badge>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>
                </div>

                {/* Sidebar - Metadata & Stats */}
                <div className="space-y-6">
                    {/* Template Info */}
                    <Card className="card-enter">
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <Tag className="h-5 w-5" />
                                Template Information
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div>
                                <p className="text-sm font-medium text-muted-foreground">Category</p>
                                <Badge className="mt-1">{template.category}</Badge>
                            </div>
                            <div>
                                <p className="text-sm font-medium text-muted-foreground">Version</p>
                                <p className="font-medium">{template.version}</p>
                            </div>
                            <div>
                                <p className="text-sm font-medium text-muted-foreground">Last Updated</p>
                                <div className="flex items-center gap-2 mt-1">
                                    <Calendar className="h-4 w-4 text-muted-foreground" />
                                    <p className="text-sm">
                                        {new Date(template.lastUpdated).toLocaleDateString()}
                                    </p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Usage Statistics */}
                    <Card className="card-enter" style={{ animationDelay: '0.1s' }}>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <TrendingUp className="h-5 w-5" />
                                Usage Statistics
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <p className="text-2xl font-bold">{stats.timesUsed}</p>
                                    <p className="text-sm text-muted-foreground">Times Used</p>
                                </div>
                                <div>
                                    <p className="text-2xl font-bold text-green-600">{stats.successRate}%</p>
                                    <p className="text-sm text-muted-foreground">Success Rate</p>
                                </div>
                            </div>
                            <div>
                                <p className="text-sm font-medium text-muted-foreground">Avg. Completion Time</p>
                                <p className="font-medium">{stats.avgCompletionTime}</p>
                            </div>
                            <div>
                                <p className="text-sm font-medium text-muted-foreground">Last Used</p>
                                <p className="font-medium">{stats.lastUsed}</p>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Recent Contracts Using This Template */}
                    <Card className="card-enter" style={{ animationDelay: '0.2s' }}>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <FileText className="h-5 w-5" />
                                Recent Usage
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-2">
                                <div className="p-2 border rounded hover:bg-accent transition-colors cursor-pointer">
                                    <p className="text-sm font-medium">Marketing Partnership</p>
                                    <p className="text-xs text-muted-foreground">Created 3 days ago</p>
                                </div>
                                <div className="p-2 border rounded hover:bg-accent transition-colors cursor-pointer">
                                    <p className="text-sm font-medium">Vendor Agreement</p>
                                    <p className="text-xs text-muted-foreground">Created 1 week ago</p>
                                </div>
                                <div className="p-2 border rounded hover:bg-accent transition-colors cursor-pointer">
                                    <p className="text-sm font-medium">Strategic Alliance</p>
                                    <p className="text-xs text-muted-foreground">Created 2 weeks ago</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Danger Zone */}
                    <Card className="border-destructive/50 card-enter" style={{ animationDelay: '0.3s' }}>
                        <CardHeader>
                            <CardTitle className="text-destructive">Danger Zone</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <Button
                                variant="destructive"
                                className="w-full"
                                onClick={() => setDeleteDialogOpen(true)}
                            >
                                <Trash2 className="mr-2 h-4 w-4" />
                                Delete Template
                            </Button>
                        </CardContent>
                    </Card>
                </div>
            </div>

            <ConfirmDialog
                open={deleteDialogOpen}
                onOpenChange={setDeleteDialogOpen}
                title="Delete Template?"
                description="This action cannot be undone. This will permanently delete the template and remove it from all associated contracts."
                confirmText="Delete"
                variant="destructive"
                onConfirm={handleDelete}
            />
        </div>
    )
}
