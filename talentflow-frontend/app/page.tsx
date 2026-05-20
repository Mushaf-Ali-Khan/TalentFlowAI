'use client'

import { useEffect, useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getJobs, createJob } from '@/lib/api/jobs'
import { getAnalyticsOverview } from '@/lib/api/analytics'
import { Briefcase, Users, CheckCircle, BarChart3, Plus, ArrowRight, UploadCloud, Sparkles, Loader2 } from 'lucide-react'
import { useToast } from '@/lib/providers/toast-provider'

import { GlobalHeader } from '@/components/global-header'

export default function DashboardPage() {
  const queryClient = useQueryClient()
  const [newTitle, setNewTitle] = useState('')
  const [newDescription, setNewDescription] = useState('')
  const [isSuccessMessageVisible, setIsSuccessMessageVisible] = useState(false)
  const { pushToast } = useToast()

  // 1. Fetch active jobs from backend
  const { data: jobs, isLoading, error } = useQuery<any>({
    queryKey: ['jobs'],
    queryFn: getJobs,
  })

  const { data: analytics } = useQuery({
    queryKey: ['analytics', 'overview'],
    queryFn: getAnalyticsOverview,
  })

  useEffect(() => {
    if (error) {
      pushToast('Failed to load jobs. Please refresh.', 'error')
    }
  }, [error, pushToast])

  // 2. Create Job Mutation
  const createJobMutation = useMutation({
    mutationFn: (jobData: { title: string; description: string; scoring_rubric: any }) => createJob(jobData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] })
      setNewTitle('')
      setNewDescription('')
      setIsSuccessMessageVisible(true)
      setTimeout(() => setIsSuccessMessageVisible(false), 5000)
    },
  })

  const handleCreateJob = (e: React.FormEvent) => {
    e.preventDefault()
    if (!newTitle.trim() || !newDescription.trim()) return

    createJobMutation.mutate({
      title: newTitle,
      description: newDescription,
      scoring_rubric: {}, // backend populates rubrics
    })
  }

  // Pre-fill a sample description for the developer user
  const handlePreFillSample = () => {
    setNewTitle('Senior Backend Engineer')
    setNewDescription(
      `We are looking for a Senior Backend Engineer to join our team. \n\n` +
      `Key Requirements:\n` +
      `- 5+ years of experience with Python, Django, or FastAPI\n` +
      `- Deep experience with PostgreSQL, pgvector, or relational DBs\n` +
      `- Hands-on experience with Redis, Celery, and Docker containerization\n` +
      `- Knowledge of microservices and LLM vector embeddings search is a plus.`
    )
  }

  const activeRoles = jobs ? jobs.length : (analytics?.active_jobs ?? 0)
  const totalCandidates = analytics?.total_candidates ?? 0
  const passRate = analytics ? `${Math.round(analytics.pass_rate * 100)}%` : '—'
  const avgSemantic = analytics ? `${(analytics.avg_semantic_score * 100).toFixed(1)}%` : '—'

  return (
    <div className="min-h-screen relative overflow-hidden">
      <div className="absolute -top-32 -left-40 h-[520px] w-[520px] rounded-full bg-[var(--tf-accent-3)]/10 blur-[120px]" />
      <div className="absolute -top-24 right-[-10%] h-[420px] w-[420px] rounded-full bg-[var(--tf-accent)]/10 blur-[120px]" />

      <GlobalHeader />


      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 relative z-10">
        <section className="grid grid-cols-1 lg:grid-cols-[1.2fr,0.8fr] gap-10 items-end">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-[var(--tf-muted)]">AI recruitment intelligence</p>
            <h1 className="text-4xl sm:text-5xl font-bold tracking-tight text-[var(--tf-ink)] mt-3">
              Curate shortlists with explainable, bias-aware scoring.
            </h1>
            <p className="mt-4 text-base sm:text-lg text-[var(--tf-muted)] max-w-2xl">
              Upload CVs, extract structured profiles, generate semantic embeddings, and score candidates with transparent rationale at every step.
            </p>
            <div className="mt-6 flex flex-wrap gap-3">
              {["Semantic matching", "LLM evaluation", "Bias audit", "Pipeline automation"].map((pill) => (
                <span key={pill} className="px-3 py-1 rounded-full text-xs font-semibold border border-[var(--tf-border)] bg-white/70 text-[var(--tf-muted)]">
                  {pill}
                </span>
              ))}
            </div>
          </div>

          <div className="bg-white/80 border border-[var(--tf-border)] rounded-3xl p-6 shadow-sm">
            <p className="text-xs font-semibold text-[var(--tf-muted)] uppercase tracking-wider">Recruiting pulse</p>
            <div className="mt-4 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-[var(--tf-ink)]">Active roles</span>
                <span className="text-lg font-semibold text-[var(--tf-accent)]">{activeRoles}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-[var(--tf-ink)]">Total CVs processed</span>
                <span className="text-lg font-semibold text-[var(--tf-accent-3)]">{totalCandidates}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-[var(--tf-ink)]">Avg semantic similarity</span>
                <span className="text-lg font-semibold text-[var(--tf-accent-2)]">{avgSemantic}</span>
              </div>
            </div>
            <div className="mt-6 bg-[var(--tf-surface-2)] rounded-2xl p-4 text-sm text-[var(--tf-muted)]">
              TalentFlow prioritizes explainability first. Every score is linked to evidence in the extracted profile.
            </div>
          </div>
        </section>

        <section className="grid grid-cols-1 md:grid-cols-4 gap-6 mt-10">
          {[
            { label: 'Active Recruitment Roles', value: activeRoles, icon: Briefcase, accent: 'text-[var(--tf-accent)]' },
            { label: 'Total CVs Processed', value: totalCandidates, icon: Users, accent: 'text-[var(--tf-accent-3)]' },
            { label: 'Passed Screening Threshold', value: passRate, icon: CheckCircle, accent: 'text-emerald-600' },
            { label: 'Avg Match Similarity', value: avgSemantic, icon: BarChart3, accent: 'text-[var(--tf-accent-2)]' },
          ].map((stat, idx) => (
            <div key={idx} className="bg-white/80 border border-[var(--tf-border)] rounded-2xl p-5 shadow-sm">
              <div className="flex items-center justify-between">
                <p className="text-xs font-semibold text-[var(--tf-muted)] uppercase tracking-wider">{stat.label}</p>
                <stat.icon className={`w-5 h-5 ${stat.accent}`} />
              </div>
              <p className="text-2xl font-bold text-[var(--tf-ink)] mt-3">{stat.value}</p>
            </div>
          ))}
        </section>

        <section className="grid grid-cols-1 lg:grid-cols-3 gap-8 mt-12">
          <div className="lg:col-span-2 space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-[var(--tf-ink)] flex items-center gap-2">
                <Briefcase className="w-5 h-5 text-[var(--tf-accent)]" /> Active job pipelines
              </h2>
            </div>

            {isLoading ? (
              <div className="flex flex-col items-center justify-center p-12 bg-white/70 border border-[var(--tf-border)] rounded-2xl">
                <Loader2 className="w-10 h-10 text-[var(--tf-accent)] animate-spin mb-4" />
                <p className="text-[var(--tf-muted)] text-sm">Loading active recruitment jobs...</p>
              </div>
            ) : jobs && jobs.length > 0 ? (
              <div className="grid grid-cols-1 gap-6">
                {jobs.map((job: any) => (
                  <div key={job.id} className="bg-white/80 border border-[var(--tf-border)] rounded-2xl p-6 transition-all hover:shadow-md">
                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                      <div>
                        <h3 className="text-lg font-bold text-[var(--tf-ink)]">
                          {job.title}
                        </h3>
                        <p className="text-xs text-[var(--tf-muted)] mt-1">Job ID: {job.id}</p>
                        <p className="text-sm text-[var(--tf-muted)] mt-3 line-clamp-2 max-w-xl">
                          {job.description}
                        </p>
                      </div>
                      <div className="flex sm:flex-col gap-2.5 shrink-0 justify-end">
                        <a
                          href={`/jobs/${job.id}/pipeline`}
                          className="inline-flex items-center justify-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold border border-[var(--tf-border)] bg-white text-[var(--tf-ink)] hover:bg-[var(--tf-surface-2)] transition-colors"
                        >
                          <UploadCloud className="w-3.5 h-3.5" /> Upload CVs
                        </a>
                        <a
                          href={`/jobs/${job.id}/shortlist`}
                          className="inline-flex items-center justify-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold bg-[var(--tf-accent)] text-white hover:bg-emerald-700 transition-colors"
                        >
                          View Shortlist <ArrowRight className="w-3.5 h-3.5" />
                        </a>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="bg-white/70 border border-dashed border-[var(--tf-border)] rounded-2xl p-12 text-center">
                <Briefcase className="w-12 h-12 text-[var(--tf-muted)] mx-auto mb-4" />
                <h3 className="text-lg font-bold text-[var(--tf-ink)]">No active jobs found</h3>
                <p className="text-[var(--tf-muted)] text-sm max-w-sm mx-auto mt-2">
                  Create your first role brief to launch the recruitment flow and start screening candidates.
                </p>
              </div>
            )}
          </div>

          <div className="lg:col-span-1">
            <div className="bg-white/90 border border-[var(--tf-border)] rounded-3xl p-6 shadow-sm sticky top-24">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-bold text-[var(--tf-ink)] flex items-center gap-2">
                  <Plus className="w-5 h-5 text-[var(--tf-accent)]" /> Create role brief
                </h2>
                <button
                  type="button"
                  onClick={handlePreFillSample}
                  className="text-xs font-semibold text-[var(--tf-accent)] hover:text-emerald-700 border border-[var(--tf-border)] px-2.5 py-1.5 rounded-lg transition-colors bg-white"
                >
                  Fill Sample
                </button>
              </div>

              {isSuccessMessageVisible && (
                <div className="mb-6 p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-700 text-sm font-medium">
                  Job description registered successfully. Check the active job list.
                </div>
              )}

              <form onSubmit={handleCreateJob} className="space-y-5">
                <div>
                  <label htmlFor="title" className="block text-xs font-semibold uppercase tracking-wider text-[var(--tf-muted)] mb-2">
                    Job title
                  </label>
                  <input
                    type="text"
                    id="title"
                    value={newTitle}
                    onChange={(e) => setNewTitle(e.target.value)}
                    placeholder="e.g. Senior Backend Engineer"
                    required
                    className="w-full bg-white border border-[var(--tf-border)] rounded-xl px-4 py-3 text-sm text-[var(--tf-ink)] placeholder:text-[var(--tf-muted)] focus:outline-none focus:border-[var(--tf-accent)] focus:ring-1 focus:ring-[var(--tf-accent)] transition-all"
                  />
                </div>

                <div>
                  <label htmlFor="desc" className="block text-xs font-semibold uppercase tracking-wider text-[var(--tf-muted)] mb-2">
                    Role overview & requirements
                  </label>
                  <textarea
                    id="desc"
                    value={newDescription}
                    onChange={(e) => setNewDescription(e.target.value)}
                    placeholder="Paste job details, stack, responsibilities..."
                    required
                    rows={8}
                    className="w-full bg-white border border-[var(--tf-border)] rounded-xl px-4 py-3 text-sm text-[var(--tf-ink)] placeholder:text-[var(--tf-muted)] focus:outline-none focus:border-[var(--tf-accent)] focus:ring-1 focus:ring-[var(--tf-accent)] transition-all resize-none font-mono"
                  />
                </div>

                <button
                  type="submit"
                  disabled={createJobMutation.isPending}
                  className="w-full flex items-center justify-center gap-2 px-6 py-3.5 bg-[var(--tf-accent)] text-white rounded-xl font-semibold text-sm hover:bg-emerald-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
                >
                  {createJobMutation.isPending ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" /> Registering role...
                    </>
                  ) : (
                    <>
                      Register Job Description <Sparkles className="w-4 h-4" />
                    </>
                  )}
                </button>
              </form>
            </div>
          </div>
        </section>
      </main>
    </div>
  )
}
