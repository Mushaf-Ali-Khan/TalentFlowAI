'use client'

import { X } from 'lucide-react'
import { ScoreBreakdown, type ScoreData } from './score-breakdown'
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export interface CandidateDetail {
  id: string
  name: string
  email: string
  phone: string
  location: string
  total_score: number
  llm_score: number
  semantic_score: number
  score_data: ScoreData
  justifications: {
    skills_match: string
    experience_relevance: string
    education_fit: string
    growth_trajectory: string
  }
  raw_profile: any
}

export function CandidateDrawer({
  candidate,
  isOpen,
  onClose,
}: {
  candidate: CandidateDetail | null
  isOpen: boolean
  onClose: () => void
}) {
  return (
    <>
      {/* Backdrop */}
      <div
        className={cn(
          "fixed inset-0 bg-gray-900/50 transition-opacity z-40",
          isOpen ? "opacity-100" : "opacity-0 pointer-events-none"
        )}
        onClick={onClose}
      />
      
      {/* Drawer */}
      <div
        className={cn(
          "fixed inset-y-0 right-0 w-full max-w-2xl bg-white/95 shadow-xl z-50 transform transition-transform duration-300 ease-in-out flex flex-col",
          isOpen ? "translate-x-0" : "translate-x-full"
        )}
      >
        {candidate && (
          <>
            <div className="px-6 py-4 border-b border-[var(--tf-border)] flex justify-between items-center bg-white/80">
              <div>
                <h2 className="text-xl font-semibold text-[var(--tf-ink)]">{candidate.name}</h2>
                <p className="text-sm text-[var(--tf-muted)]">{candidate.location} • {candidate.email}</p>
              </div>
              <button
                onClick={onClose}
                className="p-2 rounded-full text-[var(--tf-muted)] hover:bg-[var(--tf-surface-2)] hover:text-[var(--tf-ink)] transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="flex-1 overflow-y-auto p-6 space-y-8">
              {/* Scores Header */}
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-emerald-50 rounded-xl p-4 border border-emerald-200 text-center">
                  <p className="text-xs text-emerald-700 uppercase font-bold mb-1">Total Score</p>
                  <p className="text-3xl font-bold text-emerald-700">{candidate.total_score.toFixed(1)}</p>
                </div>
                <div className="bg-white rounded-xl p-4 border border-[var(--tf-border)] text-center">
                  <p className="text-xs text-[var(--tf-muted)] uppercase font-bold mb-1">Semantic</p>
                  <p className="text-2xl font-semibold text-[var(--tf-ink)]">{(candidate.semantic_score * 100).toFixed(1)}</p>
                </div>
                <div className="bg-white rounded-xl p-4 border border-[var(--tf-border)] text-center">
                  <p className="text-xs text-[var(--tf-muted)] uppercase font-bold mb-1">LLM Eval</p>
                  <p className="text-2xl font-semibold text-[var(--tf-ink)]">{candidate.llm_score.toFixed(1)}</p>
                </div>
              </div>

              {/* Score Breakdown Radar */}
              <ScoreBreakdown scores={candidate.score_data} />

              {/* Justifications */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-[var(--tf-ink)] border-b border-[var(--tf-border)] pb-2">AI Evaluation Justifications</h3>
                <div className="space-y-3">
                  <div>
                    <h4 className="text-sm font-medium text-[var(--tf-ink)]">Skills Match</h4>
                    <p className="text-sm text-[var(--tf-muted)] mt-1">{candidate.justifications.skills_match}</p>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-[var(--tf-ink)]">Experience Relevance</h4>
                    <p className="text-sm text-[var(--tf-muted)] mt-1">{candidate.justifications.experience_relevance}</p>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-[var(--tf-ink)]">Education Fit</h4>
                    <p className="text-sm text-[var(--tf-muted)] mt-1">{candidate.justifications.education_fit}</p>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-[var(--tf-ink)]">Growth Trajectory</h4>
                    <p className="text-sm text-[var(--tf-muted)] mt-1">{candidate.justifications.growth_trajectory}</p>
                  </div>
                </div>
              </div>

              {/* Raw JSON */}
              <div>
                <h3 className="text-lg font-semibold text-[var(--tf-ink)] border-b border-[var(--tf-border)] pb-2 mb-4">Raw Extracted Profile</h3>
                <pre className="bg-slate-900 text-slate-100 p-4 rounded-xl overflow-x-auto text-xs font-mono">
                  {JSON.stringify(candidate.raw_profile, null, 2)}
                </pre>
              </div>
            </div>
            
            <div className="px-6 py-4 border-t border-[var(--tf-border)] bg-white/80 flex justify-end gap-3">
              <button onClick={onClose} className="px-4 py-2 border border-[var(--tf-border)] rounded-lg text-sm font-medium text-[var(--tf-ink)] hover:bg-[var(--tf-surface-2)] transition-colors">
                Close
              </button>
              <button className="px-4 py-2 bg-[var(--tf-accent)] text-white rounded-lg text-sm font-medium hover:bg-emerald-700 transition-colors shadow-sm">
                Shortlist Candidate
              </button>
            </div>
          </>
        )}
      </div>
    </>
  )
}
