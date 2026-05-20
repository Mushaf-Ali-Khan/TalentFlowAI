'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Sparkles, Briefcase, BarChart3, Calendar, FileText, User } from 'lucide-react'
import { UserButton, useUser, SignInButton } from '@clerk/nextjs'

export function GlobalHeader() {
  const pathname = usePathname()
  const { isSignedIn, isLoaded } = useUser()

  const tabs = [
    { name: 'Dashboard', href: '/', icon: Briefcase },
    { name: 'Analytics Sentinel', href: '/analytics', icon: BarChart3 },
    { name: 'Interview Scheduler', href: '/interviews', icon: Calendar },
    { name: 'Reports Builder', href: '/reports', icon: FileText },
  ]

  const isActive = (href: string) => {
    if (href === '/') {
      return pathname === '/'
    }
    return pathname?.startsWith(href)
  }

  return (
    <header className="border-b border-[var(--tf-border)] bg-white/80 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo Brand Section */}
          <div className="flex items-center gap-8">
            <Link href="/" className="flex items-center gap-3 group">
              <div className="h-10 w-10 rounded-2xl bg-gradient-to-br from-[var(--tf-accent)] to-[var(--tf-accent-3)] flex items-center justify-center text-white shadow-lg shadow-emerald-500/10 group-hover:scale-105 transition-transform duration-200">
                <Sparkles className="w-5 h-5" />
              </div>
              <div>
                <span className="text-lg font-bold tracking-tight text-[var(--tf-ink)] group-hover:text-emerald-800 transition-colors">
                  TalentFlow AI
                </span>
                <span className="block text-[10px] uppercase tracking-wider text-[var(--tf-muted)]">
                  Hiring Intelligence Studio
                </span>
              </div>
            </Link>

            {/* Navigation Tabs */}
            <nav className="hidden md:flex items-center gap-1">
              {tabs.map((tab) => {
                const active = isActive(tab.href)
                const Icon = tab.icon
                return (
                  <Link
                    key={tab.name}
                    href={tab.href}
                    className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold transition-all duration-200 ${
                      active
                        ? 'bg-emerald-50 text-[var(--tf-accent)] border border-emerald-100 shadow-sm shadow-emerald-500/5'
                        : 'text-[var(--tf-muted)] hover:text-[var(--tf-ink)] hover:bg-[var(--tf-surface-2)] border border-transparent'
                    }`}
                  >
                    <Icon className={`w-4 h-4 ${active ? 'text-[var(--tf-accent)]' : 'text-slate-400'}`} />
                    {tab.name}
                  </Link>
                )
              })}
            </nav>
          </div>

          {/* User Auth Widgets */}
          <div className="flex items-center gap-4">
            <span className="hidden sm:inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-slate-50 text-[var(--tf-muted)] border border-[var(--tf-border)]">
              Sandbox Mode
            </span>
            
            <div className="h-9 w-[1px] bg-slate-200 hidden sm:block"></div>

            {isLoaded && isSignedIn ? (
              <div className="flex items-center gap-2 border border-[var(--tf-border)] bg-white p-1 rounded-2xl animate-fadeIn">
                <UserButton />
              </div>
            ) : isLoaded ? (
              <SignInButton mode="modal">
                <button className="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold bg-[var(--tf-accent)] text-white hover:bg-emerald-700 transition-colors cursor-pointer shadow-lg shadow-emerald-500/10">
                  <User className="w-3.5 h-3.5" /> Sign In
                </button>
              </SignInButton>
            ) : (
              <div className="h-8 w-8 rounded-full bg-slate-100 animate-pulse"></div>
            )}
          </div>
        </div>
      </div>

      {/* Mobile Sub-Header Navigation */}
      <div className="md:hidden border-t border-[var(--tf-border)] bg-white/90">
        <div className="max-w-7xl mx-auto px-4 flex overflow-x-auto py-2 gap-1.5 scrollbar-none">
          {tabs.map((tab) => {
            const active = isActive(tab.href)
            const Icon = tab.icon
            return (
              <Link
                key={tab.name}
                href={tab.href}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold whitespace-nowrap border ${
                  active
                    ? 'bg-emerald-50 text-[var(--tf-accent)] border-emerald-200'
                    : 'text-[var(--tf-muted)] border-transparent hover:bg-slate-100'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                {tab.name}
              </Link>
            )
          })}
        </div>
      </div>
    </header>
  )
}

