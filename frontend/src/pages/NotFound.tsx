import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { FileQuestion } from 'lucide-react'

export function NotFound() {
    return (
        <div className="flex flex-col items-center justify-center min-h-[60vh] page-enter">
            <FileQuestion className="h-24 w-24 text-muted-foreground mb-6" />
            <h1 className="text-6xl font-bold text-muted-foreground mb-4">404</h1>
            <h2 className="text-2xl font-semibold mb-2">Page Not Found</h2>
            <p className="text-muted-foreground mb-8 text-center max-w-md">
                The page you're looking for doesn't exist or has been moved.
            </p>
            <div className="flex gap-3">
                <Button asChild>
                    <Link to="/dashboard">
                        Go to Dashboard
                    </Link>
                </Button>
                <Button variant="outline" asChild>
                    <Link to="/contracts">
                        View Contracts
                    </Link>
                </Button>
            </div>
        </div>
    )
}
