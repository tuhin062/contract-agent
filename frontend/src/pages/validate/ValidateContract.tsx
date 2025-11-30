import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Upload, AlertTriangle, CheckCircle2, XCircle } from 'lucide-react'

export function ValidateContract() {
    const [uploaded, setUploaded] = useState(false)
    const [validationResult, setValidationResult] = useState<any>(null)

    const handleUpload = async () => {
        setUploaded(true)
        // Simulate validation
        setTimeout(async () => {
            const response = await fetch('/mock/validationResult.json')
            const data = await response.json()
            setValidationResult(data)
        }, 1500)
    }

    const getSeverityIcon = (severity: string) => {
        switch (severity) {
            case 'critical':
            case 'high':
                return <AlertTriangle className="h-4 w-4 text-red-500" />
            case 'medium':
                return <AlertTriangle className="h-4 w-4 text-yellow-500" />
            default:
                return <CheckCircle2 className="h-4 w-4 text-blue-500" />
        }
    }

    const getMatchIcon = (match: string) => {
        switch (match) {
            case 'exact':
                return <CheckCircle2 className="h-4 w-4 text-green-500" />
            case 'partial':
                return <AlertTriangle className="h-4 w-4 text-yellow-500" />
            case 'mismatch':
            case 'missing':
                return <XCircle className="h-4 w-4 text-red-500" />
            default:
                return null
        }
    }

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold">Validate Contract</h1>
                <p className="text-muted-foreground">
                    Compare contracts against business proposals
                </p>
            </div>

            {!uploaded && (
                <Card>
                    <CardContent className="flex flex-col items-center py-12">
                        <Upload className="mb-4 h-12 w-12 text-muted-foreground" />
                        <h3 className="mb-2 text-lg font-medium">Upload Contract PDF</h3>
                        <p className="mb-4 text-sm text-muted-foreground">
                            Select a contract to validate against proposals
                        </p>
                        <Button onClick={handleUpload}>Upload & Validate</Button>
                    </CardContent>
                </Card>
            )}

            {uploaded && !validationResult && (
                <Card>
                    <CardContent className="py-12 text-center">
                        <p className="text-lg font-medium">Validating contract...</p>
                        <p className="text-sm text-muted-foreground">
                            Analyzing clauses and comparing with proposal
                        </p>
                    </CardContent>
                </Card>
            )}

            {validationResult && (
                <div className="space-y-6">
                    {/* Validation Summary */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Validation Summary</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="grid gap-4 md:grid-cols-3">
                                <div>
                                    <p className="text-sm text-muted-foreground">Overall Score</p>
                                    <p className="text-3xl font-bold">{validationResult.overallScore}%</p>
                                </div>
                                <div>
                                    <p className="text-sm text-muted-foreground">Status</p>
                                    <Badge
                                        variant={
                                            validationResult.status === 'passed'
                                                ? 'default'
                                                : validationResult.status === 'warning'
                                                    ? 'secondary'
                                                    : 'destructive'
                                        }
                                    >
                                        {validationResult.status}
                                    </Badge>
                                </div>
                                <div>
                                    <p className="text-sm text-muted-foreground">Risk Flags</p>
                                    <p className="text-2xl font-bold">{validationResult.riskFlags.length}</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Risk Flags */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Risk Flags</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-3">
                            {validationResult.riskFlags.map((risk: any) => (
                                <div key={risk.id} className="rounded-lg border p-4">
                                    <div className="flex items-start gap-3">
                                        {getSeverityIcon(risk.severity)}
                                        <div className="flex-1">
                                            <div className="flex items-center gap-2">
                                                <h4 className="font-medium">{risk.title}</h4>
                                                <Badge variant="outline">{risk.severity}</Badge>
                                            </div>
                                            <p className="mt-1 text-sm text-muted-foreground">
                                                {risk.description}
                                            </p>
                                            <p className="mt-2 text-sm">
                                                <span className="font-medium">Recommendation: </span>
                                                {risk.recommendation}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </CardContent>
                    </Card>

                    {/* Clause Comparison */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Clause Comparison</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-2">
                                {validationResult.clauseComparisons.map((comparison: any) => (
                                    <div
                                        key={comparison.id}
                                        className="grid grid-cols-[auto_1fr_1fr_auto] gap-4 rounded-lg border p-3 text-sm"
                                    >
                                        <div className="flex items-center">
                                            {getMatchIcon(comparison.match)}
                                        </div>
                                        <div>
                                            <p className="font-medium">{comparison.clauseName}</p>
                                            <p className="text-muted-foreground">Contract: {comparison.contractValue}</p>
                                        </div>
                                        <div>
                                            <p className="text-muted-foreground">Proposal: {comparison.proposalValue}</p>
                                        </div>
                                        <Badge variant="outline">{comparison.match}</Badge>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>

                    <Button>Export Validation Report</Button>
                </div>
            )}
        </div>
    )
}
