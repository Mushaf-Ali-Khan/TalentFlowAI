import axios from 'axios'

const isServer = typeof window === 'undefined'

export const apiClient = axios.create({
  baseURL: isServer ? (process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8001') + '/api/v1' : '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add a request interceptor to attach Clerk token if needed
// Note: In Next.js App Router (client components), we typically use the useAuth hook
// from @clerk/nextjs to get the token.
// We will expose a setup function that components can call or use a custom hook to wrap api calls.
export const setupApiClient = (getToken: () => Promise<string | null>) => {
  apiClient.interceptors.request.use(async (config) => {
    const token = await getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  })
}

apiClient.interceptors.response.use(
  (response) => {
    // Return only the data payload if it matches our envelope
    if (response.data && response.data.success !== undefined) {
        return response.data.data
    }
    return response.data
  },
  (error) => {
    return Promise.reject(error)
  }
)
