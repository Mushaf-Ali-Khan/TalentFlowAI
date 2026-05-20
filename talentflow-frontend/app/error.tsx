'use client'

import { useEffect } from 'react'

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    console.error(error)
  }, [error])

  return (
    <div className="min-h-screen flex items-center justify-center bg-[var(--tf-bg)] text-[var(--tf-ink)] px-4">
      <div className="max-w-md w-full text-center bg-white border border-[var(--tf-border)] rounded-2xl p-8 shadow-lg">
        <h2 className="text-2xl font-bold">Something went wrong</h2>
        <p className="text-sm text-[var(--tf-muted)] mt-2">
          {error?.message || 'We hit an unexpected error. Please try again.'}
        </p>
        <button
          onClick={reset}
          className="mt-6 px-5 py-2.5 bg-[var(--tf-accent)] text-white rounded-lg font-semibold hover:bg-emerald-700 transition-colors cursor-pointer"
        >
          Try again
        </button>
      </div>
    </div>
  )
}

