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
          "fixed inset-y-0 right-0 w-full max-w-2xl bg-white shadow-xl z-50 transform transition-transform duration-300 ease-in-out flex flex-col",
          isOpen ? "translate-x-0" : "translate-x-full"
        )}
      >
        {candidate && (
          <>
            <div className="px-6 py-4 border-b flex justify-between items-center bg-gray-50">
              <div>
                <h2 className="text-xl font-semibold text-gray-900">{candidate.name}</h2>
                <p className="text-sm text-gray-500">{candidate.location} • {candidate.email}</p>
              </div>
              <button
                onClick={onClose}
                className="p-2 rounded-full text-gray-400 hover:bg-gray-200 hover:text-gray-600 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="flex-1 overflow-y-auto p-6 space-y-8">
              {/* Scores Header */}
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-blue-50 rounded-xl p-4 border border-blue-100 text-center">
                  <p className="text-xs text-blue-600 uppercase font-bold mb-1">Total Score</p>
                  <p className="text-3xl font-bold text-blue-700">{candidate.total_score.toFixed(1)}</p>
                </div>
                <div className="bg-gray-50 rounded-xl p-4 border text-center">
                  <p className="text-xs text-gray-500 uppercase font-bold mb-1">Semantic</p>
                  <p className="text-2xl font-semibold text-gray-700">{(candidate.semantic_score * 100).toFixed(1)}</p>
                </div>
                <div className="bg-gray-50 rounded-xl p-4 border text-center">
                  <p className="text-xs text-gray-500 uppercase font-bold mb-1">LLM Eval</p>
                  <p className="text-2xl font-semibold text-gray-700">{candidate.llm_score.toFixed(1)}</p>
                </div>
              </div>

              {/* Score Breakdown Radar */}
              <ScoreBreakdown scores={candidate.score_data} />

              {/* Justifications */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-900 border-b pb-2">AI Evaluation Justifications</h3>
                <div className="space-y-3">
                  <div>
                    <h4 className="text-sm font-medium text-gray-700">Skills Match</h4>
                    <p className="text-sm text-gray-600 mt-1">{candidate.justifications.skills_match}</p>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-gray-700">Experience Relevance</h4>
                    <p className="text-sm text-gray-600 mt-1">{candidate.justifications.experience_relevance}</p>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-gray-700">Education Fit</h4>
                    <p className="text-sm text-gray-600 mt-1">{candidate.justifications.education_fit}</p>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-gray-700">Growth Trajectory</h4>
                    <p className="text-sm text-gray-600 mt-1">{candidate.justifications.growth_trajectory}</p>
                  </div>
                </div>
              </div>

              {/* Raw JSON */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 border-b pb-2 mb-4">Raw Extracted Profile</h3>
                <pre className="bg-gray-900 text-gray-100 p-4 rounded-xl overflow-x-auto text-xs font-mono">
                  {JSON.stringify(candidate.raw_profile, null, 2)}
                </pre>
              </div>
            </div>
            
            <div className="px-6 py-4 border-t bg-gray-50 flex justify-end gap-3">
              <button onClick={onClose} className="px-4 py-2 border rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-100 transition-colors">
                Close
              </button>
              <button className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors shadow-sm">
                Shortlist Candidate
              </button>
            </div>
          </>
        )}
      </div>
    </>
  )
}
