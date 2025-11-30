import { useParams, Link } from 'react-router-dom'
import { useContract } from '@/hooks/useContracts'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { PDFViewer } from '@/components/ui/pdf-viewer'
import { ArrowLeft, AlertTriangle } from 'lucide-react'
import { formatDate } from '@/lib/utils'

export function ContractDetail() {
    const { id } = useParams<{ id: string }>()
    const { data: contract, isLoading } = useContract(id!)

    if (isLoading) {
        return <div>Loading...</div>
    }

    if (!contract) {
        return <div>Contract not found</div>
    }

    const getSeverityColor = (severity: string) => {
        switch (severity) {
            case 'critical':
                return 'text-red-500'
            case 'high':
                return 'text-orange-500'
            case 'medium':
                return 'text-yellow-500'
            default:
                return 'text-blue-500'
        }
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center gap-4">
                <Button variant="ghost" size="icon" asChild>
                    <Link to="/contracts">
                        <ArrowLeft className="h-5 w-5" />
                    </Link>
                </Button>
                <div>
                    <h1 className="text-3xl font-bold">{contract.title}</h1>
                    <p className="text-muted-foreground">{contract.type}</p>
                </div>
            </div>

            <div className="grid gap-6 lg:grid-cols-3">
                {/* Left Column - PDF Viewer */}
                <div className="lg:col-span-2">
                    <Card className="h-full">
                        <CardHeader>
                            <CardTitle>Document</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <PDFViewer url={contract.fileUrl || 'https://pdfobject.com/pdf/sample.pdf'} />
                        </CardContent>
                    </Card>
                </div>

                {/* Right Column - Metadata & Insights */}
                <div className="space-y-6">
                    {/* Metadata */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Metadata</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-3 text-sm">
                            <div>
                                <span className="text-muted-foreground">Status:</span>
                                <Badge className="ml-2">{contract.status}</Badge>
                            </div>
                            <div>
                                <span className="text-muted-foreground">Parties:</span>
                                <p className="mt-1 font-medium">{contract.parties.join(', ')}</p>
                            </div>
                            <div>
                                <span className="text-muted-foreground">Start Date:</span>
                                <p className="mt-1 font-medium">{formatDate(contract.startDate)}</p>
                            </div>
                            {contract.endDate && (
                                <div>
                                    <span className="text-muted-foreground">End Date:</span>
                                    <p className="mt-1 font-medium">{formatDate(contract.endDate)}</p>
                                </div>
                            )}
                            <div>
                                <span className="text-muted-foreground">Owner:</span>
                                <p className="mt-1 font-medium">{contract.owner}</p>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Insights */}
                    <Card>
                        <CardHeader>
                            <CardTitle>AI Insights</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div>
                                <h4 className="mb-2 font-medium">Summary</h4>
                                <p className="text-sm text-muted-foreground">
                                    {contract.insights.summary}
                                </p>
                            </div>

                            {contract.insights.risks.length > 0 && (
                                <div>
                                    <h4 className="mb-2 font-medium">Risks</h4>
                                    <div className="space-y-2">
                                        {contract.insights.risks.map((risk) => (
                                            <div
                                                key={risk.id}
                                                className="rounded-lg border p-3"
                                            >
                                                <div className="flex items-start gap-2">
                                                    <AlertTriangle className={`mt-0.5 h-4 w-4 ${getSeverityColor(risk.severity)}`} />
                                                    <div className="flex-1">
                                                        <p className="font-medium text-sm">{risk.title}</p>
                                                        <p className="text-xs text-muted-foreground mt-1">
                                                            {risk.description}
                                                        </p>
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    )
}
