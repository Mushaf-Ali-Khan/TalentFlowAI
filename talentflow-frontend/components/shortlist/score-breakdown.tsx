'use client'

export interface ScoreData {
  skills_match: number
  experience_relevance: number
  education_fit: number
  growth_trajectory: number
}

export function ScoreBreakdown({ scores }: { scores: ScoreData }) {
  const metrics = [
    { label: 'Skills Match', score: scores.skills_match, color: 'from-emerald-500 to-teal-500', bg: 'bg-emerald-50' },
    { label: 'Experience Relevance', score: scores.experience_relevance, color: 'from-sky-500 to-cyan-500', bg: 'bg-sky-50' },
    { label: 'Education Fit', score: scores.education_fit, color: 'from-amber-500 to-orange-500', bg: 'bg-amber-50' },
    { label: 'Growth Trajectory', score: scores.growth_trajectory, color: 'from-slate-500 to-slate-600', bg: 'bg-slate-50' },
  ]

  return (
    <div className="w-full bg-white rounded-2xl border border-[var(--tf-border)] p-6 shadow-sm">
      <h3 className="text-base font-bold text-[var(--tf-ink)] mb-6 flex items-center gap-2">
        <span className="h-3.5 w-3.5 rounded-full bg-[var(--tf-accent)] animate-pulse"></span>
        Explainable Metric Scores
      </h3>
      <div className="space-y-5">
        {metrics.map((m, idx) => (
          <div key={idx} className="space-y-2">
            <div className="flex items-center justify-between text-sm font-medium">
              <span className="text-[var(--tf-ink)]">{m.label}</span>
              <span className="text-[var(--tf-ink)] font-bold">{m.score.toFixed(0)} / 100</span>
            </div>
            <div className="w-full bg-[var(--tf-surface-2)] rounded-full h-3 overflow-hidden">
              <div 
                className={`bg-gradient-to-r ${m.color} h-3 rounded-full transition-all duration-1000 ease-out`} 
                style={{ width: `${m.score}%` }}
              ></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

