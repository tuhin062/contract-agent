import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { FileText, ArrowRight, ArrowLeft, Check, Loader2, Sparkles } from 'lucide-react'
import { toast } from '@/lib/toast'
import templateService from '@/services/template.service'
import contractService from '@/services/contract.service'
import type { Template, TemplatePlaceholder } from '@/types/template'
import { getCategoryColor } from '@/types/template'

type Step = 1 | 2 | 3 | 4

export function GenerateContract() {
    const navigate = useNavigate()
    const [step, setStep] = useState<Step>(1)
    const [selectedTemplateId, setSelectedTemplateId] = useState<string | null>(null)
    const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null)
    const [formData, setFormData] = useState<Record<string, string>>({})
    const [contractTitle, setContractTitle] = useState('')
    const [contractDescription, setContractDescription] = useState('')
    const [isGenerating, setIsGenerating] = useState(false)
    const [generatedContractId, setGeneratedContractId] = useState<string | null>(null)

    // Fetch templates
    const { data: templates, isLoading: templatesLoading } = useQuery({
        queryKey: ['templates'],
        queryFn: () => templateService.listTemplates({ active_only: true })
    })

    // Fetch selected template details
    const handleSelectTemplate = async (templateId: string) => {
        setSelectedTemplateId(templateId)
        try {
            const template = await templateService.getTemplate(templateId)
            setSelectedTemplate(template)
            setContractTitle(`${template.name} - ${new Date().toLocaleDateString()}`)
            setStep(2)
        } catch (error) {
            toast.error('Error', 'Failed to load template details')
        }
    }

    const handleGenerate = async () => {
        if (!selectedTemplateId || !selectedTemplate) return

        // Validate required fields
        const missingFields = selectedTemplate.placeholders
            .filter(p => p.required && !formData[p.key])
            .map(p => p.label)

        if (missingFields.length > 0) {
            toast.error('Missing Fields', `Please fill in: ${missingFields.join(', ')}`)
            return
        }

        setIsGenerating(true)
        setStep(3)

        try {
            const contract = await contractService.generateFromTemplate({
                template_id: selectedTemplateId,
                title: contractTitle,
                description: contractDescription,
                values: formData
            })

            setGeneratedContractId(contract.id)
            setStep(4)
            toast.success('Contract Generated', 'Your contract has been created successfully')
        } catch (error: any) {
            console.error('Generation error:', error)
            toast.error('Generation Failed', error.response?.data?.detail || 'Failed to generate contract')
            setStep(2)
        } finally {
            setIsGenerating(false)
        }
    }

    const renderPlaceholderInput = (placeholder: TemplatePlaceholder) => {
        const value = formData[placeholder.key] || ''
        const onChange = (val: string) => setFormData({ ...formData, [placeholder.key]: val })

        switch (placeholder.type) {
            case 'textarea':
                return (
                    <Textarea
                        value={value}
                        onChange={(e) => onChange(e.target.value)}
                        placeholder={placeholder.description || `Enter ${placeholder.label}`}
                        rows={4}
                    />
                )
            case 'date':
                return (
                    <Input
                        type="date"
                        value={value}
                        onChange={(e) => onChange(e.target.value)}
                    />
                )
            case 'number':
                return (
                    <Input
                        type="number"
                        value={value}
                        onChange={(e) => onChange(e.target.value)}
                        placeholder={placeholder.description || `Enter ${placeholder.label}`}
                    />
                )
            case 'select':
                return (
                    <select
                        value={value}
                        onChange={(e) => onChange(e.target.value)}
                        className="w-full rounded-md border border-input bg-background px-3 py-2"
                    >
                        <option value="">Select...</option>
                        {placeholder.options?.map((option) => (
                            <option key={option} value={option}>{option}</option>
                        ))}
                    </select>
                )
            default:
                return (
                    <Input
                        type="text"
                        value={value}
                        onChange={(e) => onChange(e.target.value)}
                        placeholder={placeholder.description || `Enter ${placeholder.label}`}
                    />
                )
        }
    }

    return (
        <div className="space-y-6 page-enter">
            <div className="flex items-center gap-3">
                <div className="p-2 bg-gradient-to-br from-green-500 to-emerald-500 rounded-lg">
                    <Sparkles className="h-6 w-6 text-white" />
                </div>
                <div>
                    <h1 className="text-3xl font-bold">Generate Contract</h1>
                    <p className="text-muted-foreground">Create a new contract from templates</p>
                </div>
            </div>

            {/* Step Indicator */}
            <div className="flex items-center gap-2">
                {[1, 2, 3, 4].map((s) => (
                    <div key={s} className="flex items-center gap-2">
                        <div
                            className={`flex h-8 w-8 items-center justify-center rounded-full text-sm font-medium transition-all ${
                                step >= s
                                    ? 'bg-primary text-primary-foreground'
                                    : 'bg-muted text-muted-foreground'
                            }`}
                        >
                            {step > s ? <Check className="h-4 w-4" /> : s}
                        </div>
                        {s < 4 && (
                            <div className={`h-0.5 w-12 ${step > s ? 'bg-primary' : 'bg-muted'}`} />
                        )}
                    </div>
                ))}
            </div>

            {/* Step 1: Template Selection */}
            {step === 1 && (
                <div>
                    <h2 className="mb-4 text-xl font-semibold">Step 1: Select Template</h2>
                    {templatesLoading ? (
                        <div className="flex items-center justify-center h-64">
                            <Loader2 className="h-8 w-8 animate-spin text-primary" />
                        </div>
                    ) : templates && templates.length > 0 ? (
                        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                            {templates.map((template) => (
                                <Card
                                    key={template.id}
                                    className="cursor-pointer transition-all hover:shadow-md hover:border-primary"
                                    onClick={() => handleSelectTemplate(template.id)}
                                >
                                    <CardHeader>
                                        <div className="flex items-center justify-between">
                                            <FileText className="h-5 w-5 text-muted-foreground" />
                                            {template.category && (
                                                <Badge className={getCategoryColor(template.category)}>
                                                    {template.category}
                                                </Badge>
                                            )}
                                        </div>
                                        <CardTitle className="text-lg">{template.name}</CardTitle>
                                        <CardDescription>{template.description}</CardDescription>
                                    </CardHeader>
                                </Card>
                            ))}
                        </div>
                    ) : (
                        <Card className="border-dashed">
                            <CardContent className="flex flex-col items-center justify-center py-12">
                                <FileText className="h-12 w-12 text-muted-foreground mb-4" />
                                <h3 className="text-lg font-medium">No Templates Available</h3>
                                <p className="text-sm text-muted-foreground">
                                    Contact an administrator to create templates
                                </p>
                            </CardContent>
                        </Card>
                    )}
                </div>
            )}

            {/* Step 2: Fill Template Fields */}
            {step === 2 && selectedTemplate && (
                <div>
                    <h2 className="mb-4 text-xl font-semibold">Step 2: Fill Template Fields</h2>
                    <Card>
                        <CardHeader>
                            <CardTitle>{selectedTemplate.name}</CardTitle>
                            <CardDescription>{selectedTemplate.description}</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            {/* Contract Title */}
                            <div className="space-y-2">
                                <label className="text-sm font-medium">
                                    Contract Title <span className="text-destructive">*</span>
                                </label>
                                <Input
                                    value={contractTitle}
                                    onChange={(e) => setContractTitle(e.target.value)}
                                    placeholder="Enter contract title"
                                />
                            </div>

                            {/* Contract Description */}
                            <div className="space-y-2">
                                <label className="text-sm font-medium">Description (Optional)</label>
                                <Textarea
                                    value={contractDescription}
                                    onChange={(e) => setContractDescription(e.target.value)}
                                    placeholder="Brief description of this contract"
                                    rows={2}
                                />
                            </div>

                            <hr className="my-4" />

                            {/* Template Placeholders */}
                            {selectedTemplate.placeholders.length > 0 ? (
                                selectedTemplate.placeholders.map((placeholder) => (
                                    <div key={placeholder.key} className="space-y-2">
                                        <label className="text-sm font-medium">
                                            {placeholder.label}
                                            {placeholder.required && <span className="text-destructive">*</span>}
                                        </label>
                                        {renderPlaceholderInput(placeholder)}
                                        {placeholder.description && (
                                            <p className="text-xs text-muted-foreground">{placeholder.description}</p>
                                        )}
                                    </div>
                                ))
                            ) : (
                                <p className="text-sm text-muted-foreground">
                                    This template has no customizable fields.
                                </p>
                            )}

                            <div className="flex gap-2 pt-4">
                                <Button variant="outline" onClick={() => setStep(1)}>
                                    <ArrowLeft className="mr-2 h-4 w-4" />
                                    Back
                                </Button>
                                <Button onClick={handleGenerate} disabled={!contractTitle}>
                                    Generate <ArrowRight className="ml-2 h-4 w-4" />
                                </Button>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            )}

            {/* Step 3: Generating */}
            {step === 3 && (
                <Card>
                    <CardContent className="py-12 text-center">
                        <Loader2 className="h-12 w-12 animate-spin text-primary mx-auto mb-4" />
                        <p className="text-lg font-medium">Generating contract...</p>
                        <p className="text-sm text-muted-foreground">
                            This may take a moment
                        </p>
                    </CardContent>
                </Card>
            )}

            {/* Step 4: Complete */}
            {step === 4 && generatedContractId && (
                <div>
                    <h2 className="mb-4 text-xl font-semibold">Step 4: Complete!</h2>
                    <Card>
                        <CardContent className="py-12 text-center">
                            <div className="h-12 w-12 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center mx-auto mb-4">
                                <Check className="h-6 w-6 text-green-600 dark:text-green-400" />
                            </div>
                            <h3 className="text-lg font-medium">Contract Generated Successfully!</h3>
                            <p className="text-sm text-muted-foreground mt-1 mb-6">
                                Your contract "{contractTitle}" has been created and is ready for review.
                            </p>
                            <div className="flex gap-3 justify-center">
                                <Button variant="outline" onClick={() => {
                                    setStep(1)
                                    setSelectedTemplateId(null)
                                    setSelectedTemplate(null)
                                    setFormData({})
                                    setContractTitle('')
                                    setContractDescription('')
                                    setGeneratedContractId(null)
                                }}>
                                    Create Another
                                </Button>
                                <Button onClick={() => navigate(`/contracts/${generatedContractId}`)}>
                                    View Contract
                                </Button>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            )}
        </div>
    )
}
