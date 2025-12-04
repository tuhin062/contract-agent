/**
 * Upload Service
 * Handles file upload, listing, and management
 */
import apiClient from './api'

export interface UploadResponse {
    id: string
    filename: string
    file_type: string
    size: number
    path: string
    text_extraction_status: string
    pages_count?: number
    uploaded_by: string
    uploaded_at: string
}

export interface ExtractedTextResponse {
    file_id: string
    status: string
    pages_count?: number
    text?: string
    chunks?: any[]
}

export const uploadService = {
    async uploadFile(file: File): Promise<UploadResponse> {
        const formData = new FormData()
        formData.append('file', file)

        // Don't set Content-Type header - let browser set it with boundary
        const response = await apiClient.post<UploadResponse>('/uploads', formData, {
            timeout: 120000, // 2 minute timeout for large files
        })

        return response.data
    },

    async listUploads(params?: {
        file_type?: string
        status?: string
        skip?: number
        limit?: number
    }): Promise<UploadResponse[]> {
        const response = await apiClient.get<UploadResponse[]>('/uploads', { params })
        return response.data
    },

    async getUpload(id: string): Promise<UploadResponse> {
        const response = await apiClient.get<UploadResponse>(`/uploads/${id}`)
        return response.data
    },

    async getExtractedText(id: string): Promise<ExtractedTextResponse> {
        const response = await apiClient.get<ExtractedTextResponse>(`/uploads/${id}/text`)
        return response.data
    },

    async deleteUpload(id: string): Promise<void> {
        await apiClient.delete(`/uploads/${id}`)
    },

    getDownloadUrl(id: string): string {
        const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
        const token = localStorage.getItem('access_token')
        return `${baseUrl}/api/v1/uploads/${id}/download?token=${token}`
    },
}

export default uploadService
