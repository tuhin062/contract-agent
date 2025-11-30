import { toast as sonnerToast, Toaster } from 'sonner'

// Re-export Toaster for use in App.tsx
export { Toaster }

// Toast utility functions
export const toast = {
    success: (message: string, description?: string) => {
        sonnerToast.success(message, { description })
    },
    error: (message: string, description?: string) => {
        sonnerToast.error(message, { description })
    },
    info: (message: string, description?: string) => {
        sonnerToast.info(message, { description })
    },
    warning: (message: string, description?: string) => {
        sonnerToast.warning(message, { description })
    },
    promise: sonnerToast.promise,
}
