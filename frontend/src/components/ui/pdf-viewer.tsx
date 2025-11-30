import { useState } from 'react'
import { Document, Page, pdfjs } from 'react-pdf'
import { ChevronLeft, ChevronRight, Loader2, ZoomIn, ZoomOut } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

import 'react-pdf/dist/Page/AnnotationLayer.css'
import 'react-pdf/dist/Page/TextLayer.css'

// Configure worker
pdfjs.GlobalWorkerOptions.workerSrc = `https://unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

interface PDFViewerProps {
    url: string
    className?: string
}

export function PDFViewer({ url, className }: PDFViewerProps) {
    const [numPages, setNumPages] = useState<number>(0)
    const [pageNumber, setPageNumber] = useState<number>(1)
    const [scale, setScale] = useState<number>(1.0)
    const [loading, setLoading] = useState<boolean>(true)

    function onDocumentLoadSuccess({ numPages }: { numPages: number }) {
        setNumPages(numPages)
        setLoading(false)
    }

    return (
        <div className={cn("flex flex-col items-center gap-4", className)}>
            <div className="flex items-center gap-2 rounded-md border bg-background p-2 shadow-sm">
                <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => setPageNumber((prev) => Math.max(prev - 1, 1))}
                    disabled={pageNumber <= 1}
                >
                    <ChevronLeft className="h-4 w-4" />
                </Button>
                <span className="text-sm font-medium">
                    Page {pageNumber} of {numPages || '--'}
                </span>
                <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => setPageNumber((prev) => Math.min(prev + 1, numPages))}
                    disabled={pageNumber >= numPages}
                >
                    <ChevronRight className="h-4 w-4" />
                </Button>
                <div className="mx-2 h-4 w-px bg-border" />
                <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => setScale((prev) => Math.max(prev - 0.2, 0.5))}
                >
                    <ZoomOut className="h-4 w-4" />
                </Button>
                <span className="text-sm font-medium w-12 text-center">
                    {Math.round(scale * 100)}%
                </span>
                <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => setScale((prev) => Math.min(prev + 0.2, 2.0))}
                >
                    <ZoomIn className="h-4 w-4" />
                </Button>
            </div>

            <div className="relative min-h-[500px] w-full max-w-3xl overflow-auto rounded-md border bg-muted/20 p-4 flex justify-center">
                {loading && (
                    <div className="absolute inset-0 flex items-center justify-center">
                        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
                    </div>
                )}
                <Document
                    file={url}
                    onLoadSuccess={onDocumentLoadSuccess}
                    loading={null}
                    className="shadow-lg"
                >
                    <Page
                        pageNumber={pageNumber}
                        scale={scale}
                        renderTextLayer={true}
                        renderAnnotationLayer={true}
                        className="bg-white"
                    />
                </Document>
            </div>
        </div>
    )
}
