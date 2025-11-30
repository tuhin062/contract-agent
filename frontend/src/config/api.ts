export const API_CONFIG = {
    baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
    useMock: import.meta.env.VITE_USE_MOCK_DATA !== 'false',
    timeout: 30000,
}

export const APP_CONFIG = {
    name: import.meta.env.VITE_APP_NAME || 'Contract Agent',
    version: import.meta.env.VITE_APP_VERSION || '1.0.0',
}
