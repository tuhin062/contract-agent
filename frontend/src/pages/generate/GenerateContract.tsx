import { useState } from 'react'
import { useTemplates } from '@/hooks/useTemplates'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Editor } from '@/components/ui/editor'
import { FileText, ArrowRight } from 'lucide-react'

export function GenerateContract() {
    const { data: templates } = useTemplates()
    const [step, setStep] = useState(1)
    const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null)
    const [formData, setFormData] = useState<Record<string, string>>({})
    const [editorContent, setEditorContent] = useState('')

    const currentTemplate = templates?.find((t) => t.id === selectedTemplate)

    const handleSelectTemplate = (templateId: string) => {
        setSelectedTemplate(templateId)
        setStep(2)
    }

    const handleGenerate = () => {
        setStep(3)
        // Simulate generation
        setTimeout(() => {
            setEditorContent(`
                <h1>${currentTemplate?.name}</h1>
                <p><strong>Date:</strong> ${new Date().toLocaleDateString()}</p>
                <p>This contract is made between <strong>${formData['partyA'] || '[Party A]'}</strong> and <strong>${formData['partyB'] || '[Party B]'}</strong>.</p>
                <h2>1. Terms</h2>
                <p>The total value of this agreement is <strong>${formData['value'] || '[Value]'}</strong>.</p>
                <p>Start Date: ${formData['startDate'] || '[Start Date]'}</p>
                <p>End Date: ${formData['endDate'] || '[End Date]'}</p>
                <h2>2. Scope</h2>
                <p>${formData['scope'] || 'The scope of work includes...'}</p>
            `)
            setStep(4)
        }, 2000)
    }

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold">Generate Contract</h1>
                <p className="text-muted-foreground">Create a new contract from templates</p>
            </div>

            {/* Step Indicator */}
            <div className="flex items-center gap-2">
                {[1, 2, 3, 4].map((s) => (
                    <div key={s} className="flex items-center gap-2">
                        <div
                            className={`flex h-8 w-8 items-center justify-center rounded-full text-sm font-medium ${step >= s
                                ? 'bg-primary text-primary-foreground'
                                : 'bg-muted text-muted-foreground'
                                }`}
                        >
                            {s}
                        </div>
                        {s < 4 && <div className="h-0.5 w-12 bg-muted" />}
                    </div>
                ))}
            </div>

            {/* Step Content */}
            {step === 1 && (
                <div>
                    <h2 className="mb-4 text-xl font-semibold">Step 1: Select Template</h2>
                    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                        {templates?.map((template) => (
                            <Card
                                key={template.id}
                                className="cursor-pointer transition-shadow hover:shadow-md"
                                onClick={() => handleSelectTemplate(template.id)}
                            >
                                <CardHeader>
                                    <div className="flex items-center justify-between">
                                        <FileText className="h-5 w-5" />
                                        <Badge variant="secondary">{template.category}</Badge>
                                    </div>
                                    <CardTitle className="text-lg">{template.name}</CardTitle>
                                    <CardDescription>{template.description}</CardDescription>
                                </CardHeader>
                                <CardContent>
                                    <p className="text-sm text-muted-foreground">
                                        Version {template.version}
                                    </p>
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                </div>
            )}

            {step === 2 && currentTemplate && (
                <div>
                    <h2 className="mb-4 text-xl font-semibold">Step 2: Fill Template Fields</h2>
                    <Card>
                        <CardHeader>
                            <CardTitle>{currentTemplate.name}</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            {currentTemplate.fields.map((field) => (
                                <div key={field.id} className="space-y-2">
                                    <label className="text-sm font-medium">
                                        {field.label}
                                        {field.required && <span className="text-destructive">*</span>}
                                    </label>
                                    {field.type === 'textarea' ? (
                                        <textarea
                                            className="w-full rounded-md border border-input bg-background px-3 py-2"
                                            placeholder={field.placeholder}
                                            rows={4}
                                            value={formData[field.name] || ''}
                                            onChange={(e) =>
                                                setFormData({ ...formData, [field.name]: e.target.value })
                                            }
                                        />
                                    ) : field.type === 'select' ? (
                                        <select
                                            className="w-full rounded-md border border-input bg-background px-3 py-2"
                                            value={formData[field.name] || ''}
                                            onChange={(e) =>
                                                setFormData({ ...formData, [field.name]: e.target.value })
                                            }
                                        >
                                            <option value="">Select...</option>
                                            {field.options?.map((option) => (
                                                <option key={option} value={option}>
                                                    {option}
                                                </option>
                                            ))}
                                        </select>
                                    ) : (
                                        <Input
                                            type={field.type}
                                            placeholder={field.placeholder}
                                            value={formData[field.name] || ''}
                                            onChange={(e) =>
                                                setFormData({ ...formData, [field.name]: e.target.value })
                                            }
                                        />
                                    )}
                                </div>
                            ))}
                            <div className="flex gap-2 pt-4">
                                <Button variant="outline" onClick={() => setStep(1)}>
                                    Back
                                </Button>
                                <Button onClick={handleGenerate}>
                                    Generate <ArrowRight className="ml-2 h-4 w-4" />
                                </Button>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            )}

            {step === 3 && (
                <Card>
                    <CardContent className="py-12 text-center">
                        <p className="text-lg font-medium">Generating contract...</p>
                        <p className="text-sm text-muted-foreground">Please wait</p>
                    </CardContent>
                </Card>
            )}

            {step === 4 && (
                <div>
                    <h2 className="mb-4 text-xl font-semibold">Step 4: Review & Edit</h2>
                    <Card>
                        <CardHeader>
                            <CardTitle>Generated Contract</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <Editor
                                value={editorContent}
                                onChange={setEditorContent}
                                className="min-h-[400px]"
                            />
                            <div className="flex gap-2">
                                <Button variant="outline" onClick={() => setStep(1)}>
                                    Start Over
                                </Button>
                                <Button>Save to Repository</Button>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            )}
        </div>
    )
}
