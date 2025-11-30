import { sleep } from './utils'

// Simulate API calls with delays
export async function mockFetch<T>(data: T, delay = 800): Promise<T> {
    await sleep(delay)
    return data
}

export async function mockMutation<T>(data: T, delay = 1000): Promise<T> {
    await sleep(delay)
    return data
}

// Storage helpers
export const storage = {
    get: <T>(key: string): T | null => {
        const item = localStorage.getItem(key)
        return item ? JSON.parse(item) : null
    },
    set: <T>(key: string, value: T): void => {
        localStorage.setItem(key, JSON.stringify(value))
    },
    remove: (key: string): void => {
        localStorage.removeItem(key)
    },
}
