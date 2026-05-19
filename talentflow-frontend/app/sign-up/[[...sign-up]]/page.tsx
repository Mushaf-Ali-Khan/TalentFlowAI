import { SignUp } from '@clerk/nextjs'

export default function SignUpPage() {
  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="w-full max-w-md bg-white/90 border border-[var(--tf-border)] rounded-3xl shadow-xl p-6">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-[var(--tf-ink)]">Create your workspace</h1>
          <p className="text-sm text-[var(--tf-muted)] mt-1">Start building your AI hiring pipeline.</p>
        </div>
        <SignUp appearance={{ elements: { card: "shadow-none border-0 bg-transparent p-0" } }} />
      </div>
    </div>
  )
}
