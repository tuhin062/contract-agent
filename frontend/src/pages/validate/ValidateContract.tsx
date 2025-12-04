import { useState, useRef } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { 
    Upload, 
    AlertTriangle, 
    CheckCircle2, 
    XCircle, 
    Loader2, 
    FileText,
    Shield,
    Download,
    RefreshCw
} from 'lucide-react'
import { toast } from '@/lib/toast'
import { useContracts } from '@/hooks/useContracts'
import validationService from '@/services/validation.service'
import uploadService from '@/services/upload.service'
import type { ValidationResponse, ValidationIssue, DetectedClause } from '@/types/proposal'
import { RISK_LEVEL_COLORS, RISK_LEVEL_LABELS } from '@/types/proposal'

export function ValidateContract() {
    const { data: contracts } = useContracts()
    const [selectedContractId, setSelectedContractId] = useState<string | null>(null)
    const [uploadedFile, setUploadedFile] = useState<File | null>(null)
    const [isUploading, setIsUploading] = useState(false)
    const [isValidating, setIsValidating] = useState(false)
    const [validationResult, setValidationResult] = useState<ValidationResponse | null>(null)
    const [contractType, setContractType] = useState<string>('')
    const fileInputRef = useRef<HTMLInputElement>(null)

    const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0]
        if (!file) return

        // Validate file type
        const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain']
        const validExtensions = ['.pdf', '.docx', '.txt']
        const hasValidExtension = validExtensions.some(ext => file.name.toLowerCase().endsWith(ext))

        if (!validTypes.includes(file.type) && !hasValidExtension) {
            toast.error('Invalid File', 'Please upload a PDF, DOCX, or TXT document')
            return
        }

        setIsUploading(true)
        try {
            await uploadService.uploadFile(file)
            setUploadedFile(file)
            toast.success('Document Uploaded', `${file.name} is ready for validation`)
        } catch (error: any) {
            console.error('Upload error:', error)
            toast.error('Upload Failed', error.response?.data?.detail || 'Failed to upload file')
        } finally {
            setIsUploading(false)
        }
    }

    const handleValidate = async () => {
        if (!selectedContractId) {
            toast.error('Select Contract', 'Please select a contract to validate')
            return
        }

        setIsValidating(true)
        setValidationResult(null)

        try {
            const result = await validationService.validateContract(selectedContractId, {
                contract_type: contractType || undefined,
                create_proposal: true
            })

            setValidationResult(result)
            toast.success('Validation Complete', `Risk level: ${result.risk_level}`)
        } catch (error: any) {
            console.error('Validation error:', error)
            toast.error('Validation Failed', error.response?.data?.detail || 'Failed to validate contract')
        } finally {
            setIsValidating(false)
        }
    }

    const getSeverityIcon = (severity: string) => {
        switch (severity.toLowerCase()) {
            case 'critical':
            case 'high':
                return <AlertTriangle className="h-4 w-4 text-red-500" />
            case 'medium':
                return <AlertTriangle className="h-4 w-4 text-yellow-500" />
            default:
                return <CheckCircle2 className="h-4 w-4 text-blue-500" />
        }
    }

    const getSeverityColor = (severity: string) => {
        switch (severity.toLowerCase()) {
            case 'critical':
                return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
            case 'high':
                return 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200'
            case 'medium':
                return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
            default:
                return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
        }
    }

    const getRiskScoreColor = (score: number) => {
        if (score >= 0.7) return 'text-red-500'
        if (score >= 0.4) return 'text-yellow-500'
        return 'text-green-500'
    }

    const resetValidation = () => {
        setSelectedContractId(null)
        setUploadedFile(null)
        setValidationResult(null)
        setContractType('')
    }

    return (
        <div className="space-y-6 page-enter">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">Validate Contract</h1>
                    <p className="text-muted-foreground">
                        AI-powered contract analysis and risk assessment
                    </p>
                </div>
                {validationResult && (
                    <Button variant="outline" onClick={resetValidation}>
                        <RefreshCw className="mr-2 h-4 w-4" />
                        New Validation
                    </Button>
                )}
            </div>

            {!validationResult ? (
                <div className="grid gap-6 lg:grid-cols-2">
                    {/* Contract Selection */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <FileText className="h-5 w-5" />
                                Select Contract
                            </CardTitle>
                            <CardDescription>
                                Choose an existing contract to validate
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="max-h-64 overflow-y-auto space-y-2">
                                {contracts?.map((contract) => (
                                    <div
                                        key={contract.id}
                                        className={`p-3 rounded-lg border cursor-pointer transition-all ${
                                            selectedContractId === contract.id
                                                ? 'border-primary bg-primary/5'
                                                : 'hover:border-primary/50 hover:bg-muted/50'
                                        }`}
                                        onClick={() => setSelectedContractId(contract.id)}
                                    >
                                        <div className="flex items-center justify-between">
                                            <div>
                                                <p className="font-medium">{contract.title}</p>
                                                <p className="text-sm text-muted-foreground">
                                                    Version {contract.version} • {contract.status}
                                                </p>
                                            </div>
                                            {selectedContractId === contract.id && (
                                                <CheckCircle2 className="h-5 w-5 text-primary" />
                                            )}
                                        </div>
                                    </div>
                                ))}
                                {(!contracts || contracts.length === 0) && (
                                    <p className="text-center text-muted-foreground py-8">
                                        No contracts found. Create a contract first.
                                    </p>
                                )}
                            </div>
                        </CardContent>
                    </Card>

                    {/* Upload Option */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <Upload className="h-5 w-5" />
                                Or Upload Document
                            </CardTitle>
                            <CardDescription>
                                Upload a PDF, DOCX, or TXT file for analysis
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            <input
                                ref={fileInputRef}
                                type="file"
                                accept=".pdf,.docx,.txt"
                                onChange={handleFileUpload}
                                className="hidden"
                                disabled={isUploading}
                            />
                            <div
                                className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors cursor-pointer ${
                                    uploadedFile 
                                        ? 'border-green-500 bg-green-50 dark:bg-green-950/20' 
                                        : 'hover:border-primary hover:bg-muted/50'
                                }`}
                                onClick={() => fileInputRef.current?.click()}
                            >
                                {isUploading ? (
                                    <div className="flex flex-col items-center gap-2">
                                        <Loader2 className="h-8 w-8 animate-spin text-primary" />
                                        <p>Uploading...</p>
                                    </div>
                                ) : uploadedFile ? (
                                    <div className="flex flex-col items-center gap-2">
                                        <CheckCircle2 className="h-8 w-8 text-green-500" />
                                        <p className="font-medium">{uploadedFile.name}</p>
                                        <p className="text-sm text-muted-foreground">
                                            Click to upload a different file
                                        </p>
                                    </div>
                                ) : (
                                    <div className="flex flex-col items-center gap-2">
                                        <Upload className="h-8 w-8 text-muted-foreground" />
                                        <p>Click to upload or drag and drop</p>
                                        <p className="text-sm text-muted-foreground">
                                            PDF, DOCX, or TXT (max 100MB)
                                        </p>
                                    </div>
                                )}
                            </div>
                        </CardContent>
                    </Card>

                    {/* Validation Options */}
                    <Card className="lg:col-span-2">
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <Shield className="h-5 w-5" />
                                Validation Options
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div>
                                <label className="text-sm font-medium">Contract Type (Optional)</label>
                                <Input
                                    placeholder="e.g., NDA, Service Agreement, Employment"
                                    value={contractType}
                                    onChange={(e) => setContractType(e.target.value)}
                                    className="mt-1"
                                />
                                <p className="text-xs text-muted-foreground mt-1">
                                    Specifying the type helps improve validation accuracy
                                </p>
                            </div>

                            <Button
                                onClick={handleValidate}
                                disabled={!selectedContractId || isValidating}
                                className="w-full"
                                size="lg"
                            >
                                {isValidating ? (
                                    <>
                                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                        Analyzing Contract...
                                    </>
                                ) : (
                                    <>
                                        <Shield className="mr-2 h-4 w-4" />
                                        Validate Contract
                                    </>
                                )}
                            </Button>
                        </CardContent>
                    </Card>
                </div>
            ) : (
                <div className="space-y-6">
                    {/* Validation Summary */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Validation Summary</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="grid gap-6 md:grid-cols-4">
                                <div>
                                    <p className="text-sm text-muted-foreground">Risk Score</p>
                                    <p className={`text-4xl font-bold ${getRiskScoreColor(validationResult.risk_score)}`}>
                                        {Math.round(validationResult.risk_score * 100)}%
                                    </p>
                                </div>
                                <div>
                                    <p className="text-sm text-muted-foreground">Risk Level</p>
                                    <Badge className={RISK_LEVEL_COLORS[validationResult.risk_level.toLowerCase() as keyof typeof RISK_LEVEL_COLORS] || ''}>
                                        {RISK_LEVEL_LABELS[validationResult.risk_level.toLowerCase() as keyof typeof RISK_LEVEL_LABELS] || validationResult.risk_level}
                                    </Badge>
                                </div>
                                <div>
                                    <p className="text-sm text-muted-foreground">Issues Found</p>
                                    <p className="text-2xl font-bold">{validationResult.issues.length}</p>
                                </div>
                                <div>
                                    <p className="text-sm text-muted-foreground">Clauses Detected</p>
                                    <p className="text-2xl font-bold">{validationResult.clauses.length}</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Issues */}
                    {validationResult.issues.length > 0 && (
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <AlertTriangle className="h-5 w-5 text-yellow-500" />
                                    Issues ({validationResult.issues.length})
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-3">
                                {validationResult.issues.map((issue: ValidationIssue, idx) => (
                                    <div key={idx} className="rounded-lg border p-4">
                                        <div className="flex items-start gap-3">
                                            {getSeverityIcon(issue.severity)}
                                            <div className="flex-1">
                                                <div className="flex items-center gap-2 mb-1">
                                                    <Badge className={getSeverityColor(issue.severity)}>
                                                        {issue.severity}
                                                    </Badge>
                                                    {issue.location && (
                                                        <span className="text-xs text-muted-foreground">
                                                            {issue.location}
                                                        </span>
                                                    )}
                                                </div>
                                                <p className="text-sm">{issue.message}</p>
                                                {issue.suggestion && (
                                                    <p className="text-sm text-muted-foreground mt-2">
                                                        <span className="font-medium">Suggestion: </span>
                                                        {issue.suggestion}
                                                    </p>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </CardContent>
                        </Card>
                    )}

                    {/* Suggestions */}
                    {validationResult.suggestions.length > 0 && (
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <CheckCircle2 className="h-5 w-5 text-green-500" />
                                    Recommendations ({validationResult.suggestions.length})
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <ul className="space-y-2">
                                    {validationResult.suggestions.map((suggestion, idx) => (
                                        <li key={idx} className="flex items-start gap-2">
                                            <CheckCircle2 className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                                            <span className="text-sm">{suggestion}</span>
                                        </li>
                                    ))}
                                </ul>
                            </CardContent>
                        </Card>
                    )}

                    {/* Detected Clauses */}
                    {validationResult.clauses.length > 0 && (
                        <Card>
                            <CardHeader>
                                <CardTitle>Detected Clauses ({validationResult.clauses.length})</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="grid gap-3 md:grid-cols-2">
                                    {validationResult.clauses.map((clause: DetectedClause, idx) => (
                                        <div key={idx} className="rounded-lg border p-3">
                                            <div className="flex items-center justify-between mb-1">
                                                <p className="font-medium">{clause.name}</p>
                                                {clause.risk_level && (
                                                    <Badge variant="outline" className="text-xs">
                                                        {clause.risk_level}
                                                    </Badge>
                                                )}
                                            </div>
                                            <p className="text-sm text-muted-foreground">
                                                {clause.description}
                                            </p>
                                            {clause.location && (
                                                <p className="text-xs text-muted-foreground mt-1">
                                                    Location: {clause.location}
                                                </p>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            </CardContent>
                        </Card>
                    )}

                    {/* Compliance */}
                    {Object.keys(validationResult.compliance).length > 0 && (
                        <Card>
                            <CardHeader>
                                <CardTitle>Compliance Check</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="grid gap-2 md:grid-cols-2 lg:grid-cols-3">
                                    {Object.entries(validationResult.compliance).map(([key, value]) => (
                                        <div key={key} className="flex items-center justify-between p-2 rounded border">
                                            <span className="text-sm">{key}</span>
                                            {String(value).toLowerCase().includes('present') || 
                                             String(value).toLowerCase().includes('yes') ||
                                             String(value).toLowerCase().includes('found') ? (
                                                <CheckCircle2 className="h-4 w-4 text-green-500" />
                                            ) : (
                                                <XCircle className="h-4 w-4 text-red-500" />
                                            )}
                                        </div>
                                    ))}
                                </div>
                            </CardContent>
                        </Card>
                    )}

                    {/* Actions */}
                    <div className="flex gap-3">
                        <Button variant="outline" onClick={resetValidation}>
                            <RefreshCw className="mr-2 h-4 w-4" />
                            Validate Another
                        </Button>
                        <Button>
                            <Download className="mr-2 h-4 w-4" />
                            Export Report
                        </Button>
                    </div>
                </div>
            )}
        </div>
    )
}
