import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { X } from 'lucide-react'
import { useState } from 'react'

interface ContractMetadataFormProps {
    contract: {
        title: string
        parties: string[]
        startDate: string
        endDate: string
        value: number
        tags: string[]
    }
    onSave: (data: any) => void
    onCancel: () => void
}

export function ContractMetadataForm({ contract, onSave, onCancel }: ContractMetadataFormProps) {
    const [formData, setFormData] = useState({
        title: contract.title,
        parties: contract.parties,
        startDate: contract.startDate,
        endDate: contract.endDate,
        value: contract.value,
        tags: contract.tags
    })
    const [newTag, setNewTag] = useState('')

    const addTag = () => {
        if (newTag && !formData.tags.includes(newTag)) {
            setFormData({ ...formData, tags: [...formData.tags, newTag] })
            setNewTag('')
        }
    }

    const removeTag = (tag: string) => {
        setFormData({ ...formData, tags: formData.tags.filter(t => t !== tag) })
    }

    return (
        <Card>
            <CardHeader>
                <CardTitle>Edit Contract Metadata</CardTitle>
            </CardHeader>
            <CardContent>
                <form onSubmit={(e) => { e.preventDefault(); onSave(formData) }} className="space-y-4">
                    <div>
                        <Label htmlFor="title">Contract Title</Label>
                        <Input
                            id="title"
                            value={formData.title}
                            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                            required
                        />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <Label htmlFor="startDate">Start Date</Label>
                            <Input
                                id="startDate"
                                type="date"
                                value={formData.startDate}
                                onChange={(e) => setFormData({ ...formData, startDate: e.target.value })}
                            />
                        </div>
                        <div>
                            <Label htmlFor="endDate">End Date</Label>
                            <Input
                                id="endDate"
                                type="date"
                                value={formData.endDate}
                                onChange={(e) => setFormData({ ...formData, endDate: e.target.value })}
                            />
                        </div>
                    </div>

                    <div>
                        <Label htmlFor="value">Contract Value ($)</Label>
                        <Input
                            id="value"
                            type="number"
                            value={formData.value}
                            onChange={(e) => setFormData({ ...formData, value: Number(e.target.value) })}
                        />
                    </div>

                    <div>
                        <Label htmlFor="tags">Tags</Label>
                        <div className="flex gap-2 mb-2">
                            <Input
                                id="tags"
                                value={newTag}
                                onChange={(e) => setNewTag(e.target.value)}
                                placeholder="Add a tag..."
                                onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
                            />
                            <Button type="button" variant="outline" onClick={addTag}>Add</Button>
                        </div>
                        <div className="flex flex-wrap gap-2">
                            {formData.tags.map(tag => (
                                <Badge key={tag} variant="secondary" className="gap-1">
                                    {tag}
                                    <X className="h-3 w-3 cursor-pointer" onClick={() => removeTag(tag)} />
                                </Badge>
                            ))}
                        </div>
                    </div>

                    <div className="flex gap-3 pt-4">
                        <Button type="button" variant="outline" onClick={onCancel} className="flex-1">
                            Cancel
                        </Button>
                        <Button type="submit" className="flex-1">
                            Save Changes
                        </Button>
                    </div>
                </form>
            </CardContent>
        </Card>
    )
}
