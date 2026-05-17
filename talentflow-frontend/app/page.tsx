'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getJobs, createJob } from '@/lib/api/jobs'
import { Briefcase, Users, CheckCircle, BarChart3, Plus, ArrowRight, UploadCloud, Sparkles, Loader2 } from 'lucide-react'

export default function DashboardPage() {
  const queryClient = useQueryClient()
  const [newTitle, setNewTitle] = useState('')
  const [newDescription, setNewDescription] = useState('')
  const [isSuccessMessageVisible, setIsSuccessMessageVisible] = useState(false)

  // 1. Fetch active jobs from backend
  const { data: jobs, isLoading, error } = useQuery<any>({
    queryKey: ['jobs'],
    queryFn: getJobs,
  })

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

  return (
    <div className="min-h-screen bg-[#070913] text-[#f1f3f9] font-sans overflow-x-hidden selection:bg-indigo-500 selection:text-white relative">
      
      {/* Sleek Neon Background Gradients */}
      <div className="absolute top-[-10%] left-[-10%] w-[600px] h-[600px] rounded-full bg-indigo-900/20 blur-[120px] pointer-events-none"></div>
      <div className="absolute bottom-[-10%] right-[-10%] w-[600px] h-[600px] rounded-full bg-purple-900/10 blur-[150px] pointer-events-none"></div>

      <header className="border-b border-gray-800/60 bg-gray-950/40 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold tracking-tight bg-gradient-to-r from-white via-indigo-200 to-indigo-400 bg-clip-text text-transparent">
              TalentFlow <span className="font-extrabold text-indigo-500">AI</span>
            </span>
          </div>
          <div className="flex items-center gap-4">
            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-indigo-950 text-indigo-300 border border-indigo-800/40">
              Dev Mode Bypass Active
            </span>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 relative z-10">
        
        {/* Banner Hero */}
        <div className="mb-12 text-center sm:text-left">
          <h1 className="text-4xl font-extrabold tracking-tight sm:text-5xl bg-gradient-to-r from-white via-gray-100 to-indigo-200 bg-clip-text text-transparent">
            AI Recruitment Intelligence
          </h1>
          <p className="mt-3 text-lg text-gray-400 max-w-3xl">
            Automate screening, parse CVs directly in the sandbox, extract clean profiles, generate embeddings, and score candidates explainably.
          </p>
        </div>

        {/* Analytics Highlights */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
          {[
            { label: 'Active Recruitment Roles', value: jobs ? jobs.length : 1, icon: Briefcase, color: 'text-indigo-400', bg: 'bg-indigo-950/40' },
            { label: 'Total CVs Processed', value: '2', icon: Users, color: 'text-purple-400', bg: 'bg-purple-950/40' },
            { label: 'Passed Screening Threshold', value: '100%', icon: CheckCircle, color: 'text-emerald-400', bg: 'bg-emerald-950/40' },
            { label: 'Avg Match Similarity', value: '60.1%', icon: BarChart3, color: 'text-amber-400', bg: 'bg-amber-950/40' },
          ].map((stat, idx) => (
            <div key={idx} className="bg-gray-900/40 border border-gray-800/80 rounded-2xl p-6 backdrop-blur-sm flex items-center justify-between transition-all hover:border-gray-700/60">
              <div>
                <p className="text-xs font-bold text-gray-400 uppercase tracking-wider">{stat.label}</p>
                <p className="text-3xl font-extrabold text-white mt-2">{stat.value}</p>
              </div>
              <div className={`p-3.5 rounded-xl ${stat.bg} ${stat.color}`}>
                <stat.icon className="w-6 h-6" />
              </div>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Job Openings Board */}
          <div className="lg:col-span-2 space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                <Briefcase className="w-5 h-5 text-indigo-500" /> Active Job Openings
              </h2>
            </div>

            {isLoading ? (
              <div className="flex flex-col items-center justify-center p-12 bg-gray-900/30 border border-gray-800 rounded-2xl">
                <Loader2 className="w-10 h-10 text-indigo-500 animate-spin mb-4" />
                <p className="text-gray-400 text-sm">Loading active recruitment jobs...</p>
              </div>
            ) : jobs && jobs.length > 0 ? (
              <div className="grid grid-cols-1 gap-6">
                {jobs.map((job: any) => (
                  <div key={job.id} className="bg-gray-900/30 border border-gray-800/80 rounded-2xl p-6 transition-all hover:bg-gray-900/50 hover:border-indigo-500/40 group relative overflow-hidden">
                    <div className="absolute top-0 right-0 w-24 h-24 bg-indigo-500/5 rounded-bl-full pointer-events-none transition-all group-hover:bg-indigo-500/10"></div>
                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                      <div>
                        <h3 className="text-lg font-bold text-white group-hover:text-indigo-400 transition-colors">
                          {job.title}
                        </h3>
                        <p className="text-xs text-gray-500 mt-1">Job ID: {job.id}</p>
                        <p className="text-sm text-gray-400 mt-3 line-clamp-2 max-w-xl">
                          {job.description}
                        </p>
                      </div>
                      <div className="flex sm:flex-col gap-2.5 shrink-0 justify-end">
                        <a 
                          href={`/jobs/${job.id}/pipeline`} 
                          className="inline-flex items-center justify-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold bg-gray-800 text-white hover:bg-indigo-600 transition-colors shadow-md"
                        >
                          <UploadCloud className="w-3.5 h-3.5" /> Upload CVs
                        </a>
                        <a 
                          href={`/jobs/${job.id}/shortlist`} 
                          className="inline-flex items-center justify-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold bg-indigo-600 text-white hover:bg-indigo-500 transition-colors shadow-md shadow-indigo-600/10"
                        >
                          View Shortlist <ArrowRight className="w-3.5 h-3.5" />
                        </a>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="bg-gray-900/20 border border-dashed border-gray-800 rounded-2xl p-12 text-center">
                <Briefcase className="w-12 h-12 text-gray-600 mx-auto mb-4" />
                <h3 className="text-lg font-bold text-white">No active jobs found</h3>
                <p className="text-gray-400 text-sm max-w-sm mx-auto mt-2">
                  Create your first job description in the side panel or pre-fill the sample template to launch the recruitment flow.
                </p>
              </div>
            )}
          </div>

          {/* New Job Form */}
          <div className="lg:col-span-1">
            <div className="bg-gray-900/40 border border-gray-800/80 rounded-3xl p-6 backdrop-blur-sm sticky top-24">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-bold text-white flex items-center gap-2">
                  <Plus className="w-5 h-5 text-indigo-500" /> Create Recruitment Job
                </h2>
                <button
                  type="button"
                  onClick={handlePreFillSample}
                  className="text-xs font-bold text-indigo-400 hover:text-indigo-300 border border-indigo-500/20 px-2.5 py-1.5 rounded-lg transition-colors bg-indigo-950/20"
                >
                  Fill Sample
                </button>
              </div>

              {isSuccessMessageVisible && (
                <div className="mb-6 p-4 rounded-xl bg-emerald-950/60 border border-emerald-800 text-emerald-400 text-sm font-medium animate-fadeIn">
                  🎉 Job description registered successfully! Check the active job openings list.
                </div>
              )}

              <form onSubmit={handleCreateJob} className="space-y-5">
                <div>
                  <label htmlFor="title" className="block text-xs font-bold uppercase tracking-wider text-gray-400 mb-2">
                    Job Title
                  </label>
                  <input
                    type="text"
                    id="title"
                    value={newTitle}
                    onChange={(e) => setNewTitle(e.target.value)}
                    placeholder="e.g. Senior Backend Engineer"
                    required
                    className="w-full bg-[#0a0d1d] border border-gray-800/80 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all"
                  />
                </div>

                <div>
                  <label htmlFor="desc" className="block text-xs font-bold uppercase tracking-wider text-gray-400 mb-2">
                    Job Description & Requirements
                  </label>
                  <textarea
                    id="desc"
                    value={newDescription}
                    onChange={(e) => setNewDescription(e.target.value)}
                    placeholder="Paste job details, stack, guidelines..."
                    required
                    rows={8}
                    className="w-full bg-[#0a0d1d] border border-gray-800/80 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all resize-none font-mono"
                  />
                </div>

                <button
                  type="submit"
                  disabled={createJobMutation.isPending}
                  className="w-full flex items-center justify-center gap-2 px-6 py-3.5 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-xl font-semibold text-sm hover:from-indigo-600 hover:to-purple-700 transition-all shadow-lg shadow-indigo-600/15 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
                >
                  {createJobMutation.isPending ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" /> Registering Job...
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

        </div>

      </main>
    </div>
  )
}
