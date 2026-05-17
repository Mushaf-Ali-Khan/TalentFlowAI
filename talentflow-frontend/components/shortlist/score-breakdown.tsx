'use client'

export interface ScoreData {
  skills_match: number
  experience_relevance: number
  education_fit: number
  growth_trajectory: number
}

export function ScoreBreakdown({ scores }: { scores: ScoreData }) {
  const metrics = [
    { label: 'Skills Match', score: scores.skills_match, color: 'from-blue-500 to-indigo-500', bg: 'bg-blue-50' },
    { label: 'Experience Relevance', score: scores.experience_relevance, color: 'from-emerald-500 to-teal-500', bg: 'bg-emerald-50' },
    { label: 'Education Fit', score: scores.education_fit, color: 'from-purple-500 to-fuchsia-500', bg: 'bg-purple-50' },
    { label: 'Growth Trajectory', score: scores.growth_trajectory, color: 'from-amber-500 to-orange-500', bg: 'bg-amber-50' },
  ]

  return (
    <div className="w-full bg-white rounded-2xl border border-gray-100 p-6 shadow-sm">
      <h3 className="text-base font-bold text-gray-800 mb-6 flex items-center gap-2">
        <span className="h-3.5 w-3.5 rounded-full bg-blue-600 animate-pulse"></span>
        Explainable Metric Scores
      </h3>
      <div className="space-y-5">
        {metrics.map((m, idx) => (
          <div key={idx} className="space-y-2">
            <div className="flex items-center justify-between text-sm font-medium">
              <span className="text-gray-700">{m.label}</span>
              <span className="text-gray-900 font-bold">{m.score.toFixed(0)} / 100</span>
            </div>
            <div className="w-full bg-gray-100 rounded-full h-3 overflow-hidden">
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

