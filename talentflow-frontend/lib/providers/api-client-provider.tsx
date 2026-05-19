'use client'

import { useEffect } from 'react'
import { useAuth } from '@clerk/nextjs'
import { setupApiClient } from '@/lib/api/client'

let initialized = false

export function ApiClientProvider({ children }: { children: React.ReactNode }) {
  const { getToken } = useAuth()

  useEffect(() => {
    if (initialized) return
    setupApiClient(() => getToken())
    initialized = true
  }, [getToken])

  return <>{children}</>
}
