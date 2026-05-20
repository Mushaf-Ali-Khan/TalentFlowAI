'use client'

import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getJobs, getCandidatesForJob } from '@/lib/api/jobs'
import { getInterviews, scheduleInterview, updateInterview, cancelInterview, type InterviewDetails } from '@/lib/api/interviews'
import { GlobalHeader } from '@/components/global-header'
import { Calendar, Video, Phone, MapPin, Clock, Plus, Trash2, CheckCircle2, XCircle, AlertCircle, Loader2, Sparkles, User, ExternalLink } from 'lucide-react'
import { useToast } from '@/lib/providers/toast-provider'

export default function InterviewsPage() {
  const queryClient = useQueryClient()
  const { pushToast } = useToast()

  // Form states
  const [selectedJobId, setSelectedJobId] = useState<string>('')
  const [selectedCandidateId, setSelectedCandidateId] = useState<string>('')
  const [scheduledAt, setScheduledAt] = useState<string>('')
  const [durationMinutes, setDurationMinutes] = useState<number>(45)
  const [format, setFormat] = useState<'video' | 'phone' | 'in_person'>('video')
  const [meetingLink, setMeetingLink] = useState<string>('')
  const [notes, setNotes] = useState<string>('')
  const [isFormOpen, setIsFormOpen] = useState(false)

  // 1. Fetch all scheduled interviews from database
  const { data: interviews, isLoading: isInterviewsLoading } = useQuery<any>({
    queryKey: ['interviews'],
    queryFn: getInterviews,
  })

  // 2. Fetch active jobs to populate scheduling selector
  const { data: jobs, isLoading: isJobsLoading } = useQuery<any>({
    queryKey: ['jobs'],
    queryFn: getJobs,
  })

  // 3. Fetch candidates dynamically based on selected job in form
  const { data: candidates, isLoading: isCandidatesLoading } = useQuery<any>({
    queryKey: ['candidates-for-job', selectedJobId],
    queryFn: () => getCandidatesForJob(selectedJobId),
    enabled: !!selectedJobId,
  })

  const activeInterviews = (interviews || []) as any[]
  const activeJobs = (jobs || []) as any[]
  const activeCandidates = (candidates || []) as any[]

  // Pre-fill meeting link when format is 'video'
  useEffect(() => {
    if (format === 'video') {
      setMeetingLink(`https://meet.google.com/tfai-${Math.random().toString(36).substring(2, 6)}-${Math.random().toString(36).substring(2, 5)}`)
    } else {
      setMeetingLink('')
    }
  }, [format])

  // 4. Create Interview Mutation
  const createInterviewMutation = useMutation({
    mutationFn: (data: any) => scheduleInterview(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['interviews'] })
      pushToast('Interview scheduled and email invitation dispatched.', 'info')
      // Reset form
      setSelectedJobId('')
      setSelectedCandidateId('')
      setScheduledAt('')
      setNotes('')
      setIsFormOpen(false)
    },
    onError: () => {
      pushToast('Failed to schedule interview. Verify inputs.', 'error')
    }
  })

  // 5. Update Status Mutation (Mark Complete)
  const updateStatusMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: 'completed' | 'cancelled' }) => updateInterview(id, { status }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['interviews'] })
      pushToast('Interview status updated successfully.', 'info')
    }
  })

  // 6. Delete/Cancel Mutation
  const deleteMutation = useMutation({
    mutationFn: (id: string) => cancelInterview(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['interviews'] })
      pushToast('Interview has been cancelled.', 'info')
    }
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedJobId || !selectedCandidateId || !scheduledAt) {
      pushToast('Please complete all required scheduling fields.', 'error')
      return
    }

    createInterviewMutation.mutate({
      candidate_id: selectedCandidateId,
      job_id: selectedJobId,
      scheduled_at: new Date(scheduledAt).toISOString(),
      duration_minutes: durationMinutes,
      format,
      meeting_link: meetingLink || undefined,
      notes: notes || undefined,
    })
  }

  const getFormatIcon = (f: string) => {
    switch (f) {
      case 'video': return <Video className="w-4 h-4 text-indigo-600" />
      case 'phone': return <Phone className="w-4 h-4 text-sky-600" />
      default: return <MapPin className="w-4 h-4 text-emerald-600" />
    }
  }

  return (
    <div className="min-h-screen relative overflow-hidden bg-[var(--tf-bg)] pb-16">
      {/* Background gradients */}
      <div className="absolute -top-32 -left-40 h-[520px] w-[520px] rounded-full bg-[var(--tf-accent-3)]/10 blur-[120px] pointer-events-none" />
      <div className="absolute top-[40%] right-[-10%] h-[420px] w-[420px] rounded-full bg-[var(--tf-accent)]/10 blur-[120px] pointer-events-none" />

      <GlobalHeader />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 relative z-10">
        
        {/* Page title banner */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-6 mb-10">
          <div>
            <h1 className="text-3xl font-extrabold text-[var(--tf-ink)] tracking-tight">Interview Board</h1>
            <p className="text-sm text-[var(--tf-muted)] mt-1">Coordinate, schedule, and review candidate live interview assessments.</p>
          </div>
          
          <button
            onClick={() => setIsFormOpen(!isFormOpen)}
            className="flex items-center gap-2 px-5 py-3 bg-[var(--tf-accent)] text-white rounded-xl font-bold text-sm hover:bg-emerald-700 transition-colors shadow-lg shadow-emerald-500/10 cursor-pointer"
          >
            <Plus className="w-4 h-4" /> Book New Interview
          </button>
        </div>

        {/* Create/Book Form Modal Drawer */}
        {isFormOpen && (
          <div className="bg-white/95 border border-[var(--tf-border)] rounded-3xl p-6 shadow-md mb-10 max-w-3xl animate-slideIn">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-lg font-extrabold text-[var(--tf-ink)] flex items-center gap-2">
                <Calendar className="w-5 h-5 text-[var(--tf-accent)]" /> Configure Interview Slot
              </h2>
              <button 
                onClick={() => setIsFormOpen(false)}
                className="text-xs font-bold text-[var(--tf-muted)] hover:text-red-600 transition-colors cursor-pointer"
              >
                Close Editor
              </button>
            </div>

            <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-5">
              {/* 1. Job selector */}
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-[var(--tf-muted)] mb-2">
                  1. Choose Active Pipeline
                </label>
                <select
                  value={selectedJobId}
                  onChange={(e) => {
                    setSelectedJobId(e.target.value)
                    setSelectedCandidateId('')
                  }}
                  required
                  className="w-full bg-white border border-[var(--tf-border)] rounded-xl px-4 py-2.5 text-sm text-[var(--tf-ink)] focus:outline-none focus:border-[var(--tf-accent)] transition-colors cursor-pointer"
                >
                  <option value="">-- Select role pipeline --</option>
                  {activeJobs?.map(job => (
                    <option key={job.id} value={job.id}>{job.title}</option>
                  ))}
                </select>
              </div>

              {/* 2. Candidate selector */}
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-[var(--tf-muted)] mb-2">
                  2. Choose Screened Candidate
                </label>
                <select
                  value={selectedCandidateId}
                  onChange={(e) => setSelectedCandidateId(e.target.value)}
                  disabled={!selectedJobId || isCandidatesLoading}
                  required
                  className="w-full bg-white border border-[var(--tf-border)] rounded-xl px-4 py-2.5 text-sm text-[var(--tf-ink)] focus:outline-none focus:border-[var(--tf-accent)] disabled:opacity-50 transition-colors cursor-pointer"
                >
                  <option value="">
                    {!selectedJobId 
                      ? 'Select pipeline first...' 
                      : isCandidatesLoading 
                        ? 'Fetching candidates...' 
                        : activeCandidates && activeCandidates.length > 0
                          ? `-- Select candidate --`
                          : 'No candidates matched under this role'}
                  </option>
                  {activeCandidates?.map(cand => {
                    const name = cand.name || cand.profile?.name || 'Screened Candidate'
                    return (
                      <option key={cand.id} value={cand.id}>
                        {name} (Score: {Math.round(cand.total_score || 0)})
                      </option>
                    )
                  })}
                </select>
              </div>

              {/* 3. Time Picker */}
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-[var(--tf-muted)] mb-2">
                  3. Scheduled Date & Time
                </label>
                <input
                  type="datetime-local"
                  value={scheduledAt}
                  onChange={(e) => setScheduledAt(e.target.value)}
                  required
                  className="w-full bg-white border border-[var(--tf-border)] rounded-xl px-4 py-2.5 text-sm text-[var(--tf-ink)] focus:outline-none focus:border-[var(--tf-accent)] transition-colors cursor-pointer"
                />
              </div>

              {/* 4. Format & Duration */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-[var(--tf-muted)] mb-2">
                    4. Format
                  </label>
                  <select
                    value={format}
                    onChange={(e: any) => setFormat(e.target.value)}
                    required
                    className="w-full bg-white border border-[var(--tf-border)] rounded-xl px-3 py-2.5 text-sm text-[var(--tf-ink)] focus:outline-none focus:border-[var(--tf-accent)] transition-colors cursor-pointer"
                  >
                    <option value="video">Google Meet</option>
                    <option value="phone">Phone Call</option>
                    <option value="in_person">In Person</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-[var(--tf-muted)] mb-2">
                    5. Duration
                  </label>
                  <select
                    value={durationMinutes}
                    onChange={(e) => setDurationMinutes(Number(e.target.value))}
                    required
                    className="w-full bg-white border border-[var(--tf-border)] rounded-xl px-3 py-2.5 text-sm text-[var(--tf-ink)] focus:outline-none focus:border-[var(--tf-accent)] transition-colors cursor-pointer"
                  >
                    <option value={30}>30 mins</option>
                    <option value={45}>45 mins</option>
                    <option value={60}>60 mins</option>
                    <option value={90}>90 mins</option>
                  </select>
                </div>
              </div>

              {/* 5. Meeting link */}
              <div className="md:col-span-2">
                <label className="block text-xs font-bold uppercase tracking-wider text-[var(--tf-muted)] mb-2">
                  Google Meet link
                </label>
                <input
                  type="text"
                  value={meetingLink}
                  onChange={(e) => setMeetingLink(e.target.value)}
                  placeholder="e.g. https://meet.google.com/xxx-xxxx-xxx"
                  className="w-full bg-white border border-[var(--tf-border)] rounded-xl px-4 py-2.5 text-sm text-[var(--tf-ink)] focus:outline-none focus:border-[var(--tf-accent)] transition-colors"
                />
              </div>

              {/* 6. Notes */}
              <div className="md:col-span-2">
                <label className="block text-xs font-bold uppercase tracking-wider text-[var(--tf-muted)] mb-2">
                  Recruiter / Assessor Notes
                </label>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Add details, key areas to examine during meeting..."
                  rows={3}
                  className="w-full bg-white border border-[var(--tf-border)] rounded-xl px-4 py-2.5 text-sm text-[var(--tf-ink)] focus:outline-none focus:border-[var(--tf-accent)] resize-none"
                />
              </div>

              {/* Submit btn */}
              <div className="md:col-span-2 flex justify-end gap-3 mt-2">
                <button
                  type="button"
                  onClick={() => setIsFormOpen(false)}
                  className="px-5 py-2.5 border border-slate-200 text-slate-700 font-semibold rounded-xl text-xs hover:bg-slate-50 transition-colors cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={createInterviewMutation.isPending}
                  className="flex items-center gap-2 px-6 py-2.5 bg-[var(--tf-accent)] text-white font-extrabold rounded-xl text-xs hover:bg-emerald-700 transition-colors cursor-pointer"
                >
                  {createInterviewMutation.isPending ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" /> Scheduling...
                    </>
                  ) : (
                    <>
                      Confirm & Schedule <Sparkles className="w-4 h-4" />
                    </>
                  )}
                </button>
              </div>

            </form>
          </div>
        )}

        {/* Interviews List */}
        <div className="bg-white/90 border border-[var(--tf-border)] rounded-3xl p-6 shadow-sm">
          <h2 className="text-xl font-extrabold text-[var(--tf-ink)] mb-6 flex items-center gap-2">
            <Clock className="w-5 h-5 text-[var(--tf-accent)]" /> Active Interview Board
          </h2>

          {isInterviewsLoading ? (
            <div className="flex flex-col items-center justify-center p-20">
              <Loader2 className="w-10 h-10 text-[var(--tf-accent)] animate-spin mb-4" />
              <p className="text-[var(--tf-muted)] text-sm font-semibold">Loading active schedules...</p>
            </div>
          ) : activeInterviews && activeInterviews.length > 0 ? (
            <div className="space-y-4">
              {activeInterviews.map((item) => {
                const date = new Date(item.scheduled_at)
                const formattedDate = date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })
                const formattedTime = date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })

                return (
                  <div 
                    key={item.id} 
                    className={`p-5 border rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-6 transition-all ${
                      item.status === 'completed'
                        ? 'bg-slate-50/70 border-slate-100 opacity-70'
                        : item.status === 'cancelled'
                          ? 'bg-red-50/30 border-red-100 opacity-60'
                          : 'bg-white border-[var(--tf-border)] hover:shadow-sm'
                    }`}
                  >
                    {/* Left: Info */}
                    <div className="flex items-start gap-4">
                      <div className="h-12 w-12 rounded-xl bg-slate-50 border border-slate-100 flex flex-col items-center justify-center text-[var(--tf-muted)] shrink-0">
                        <span className="text-[10px] font-bold uppercase">{date.toLocaleString('en-US', { month: 'short' })}</span>
                        <span className="text-base font-extrabold leading-none text-[var(--tf-ink)] mt-0.5">{date.getDate()}</span>
                      </div>
                      
                      <div>
                        <div className="flex flex-wrap items-center gap-2.5">
                          <h4 className="font-extrabold text-sm text-[var(--tf-ink)]">{item.candidate_name}</h4>
                          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-slate-100 text-slate-700 border border-slate-200">
                            {getFormatIcon(item.format)}
                            {item.format === 'video' ? 'Google Meet' : item.format === 'phone' ? 'Phone' : 'In Person'}
                          </span>
                          
                          {item.status === 'completed' ? (
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-100 text-[10px] font-bold">
                              <CheckCircle2 className="w-3 h-3" /> Completed
                            </span>
                          ) : item.status === 'cancelled' ? (
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-red-50 text-red-700 border border-red-100 text-[10px] font-bold">
                              <XCircle className="w-3 h-3" /> Cancelled
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-100 text-[10px] font-bold">
                              Scheduled
                            </span>
                          )}
                        </div>

                        <p className="text-xs text-[var(--tf-muted)] mt-1.5 font-semibold">
                          Assigned role: <span className="text-slate-800 font-bold">{item.job_title}</span> | Time: <span className="text-slate-800 font-bold">{formattedDate} at {formattedTime}</span> ({item.duration_minutes} min duration)
                        </p>
                        
                        {item.notes && (
                          <p className="text-[11px] text-slate-500 mt-2 italic bg-slate-50/50 p-2 rounded-xl border border-slate-100">
                            Notes: "{item.notes}"
                          </p>
                        )}
                      </div>
                    </div>

                    {/* Right Actions */}
                    <div className="flex items-center gap-3 shrink-0 self-end md:self-center">
                      {item.format === 'video' && item.meeting_link && item.status === 'scheduled' && (
                        <a
                          href={item.meeting_link}
                          target="_blank"
                          rel="noreferrer"
                          className="flex items-center gap-1.5 px-4 py-2 border border-emerald-200 bg-emerald-50 text-[var(--tf-accent)] hover:bg-emerald-100 rounded-xl text-xs font-bold transition-all"
                        >
                          Join Meeting <ExternalLink className="w-3 h-3" />
                        </a>
                      )}

                      {item.status === 'scheduled' && (
                        <button
                          onClick={() => updateStatusMutation.mutate({ id: item.id, status: 'completed' })}
                          className="px-3 py-2 border border-slate-200 hover:bg-slate-100 text-xs font-semibold rounded-xl text-slate-700 transition-all cursor-pointer"
                        >
                          Mark Completed
                        </button>
                      )}

                      <button
                        onClick={() => {
                          if (confirm('Are you sure you want to cancel this interview?')) {
                            deleteMutation.mutate(item.id)
                          }
                        }}
                        className="p-2.5 text-slate-400 hover:text-red-600 hover:bg-red-50 border border-slate-100 hover:border-red-100 rounded-xl transition-all cursor-pointer"
                        title="Cancel interview"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                )
              })}
            </div>
          ) : (
            <div className="bg-white/70 border border-dashed border-[var(--tf-border)] rounded-2xl p-16 text-center">
              <Calendar className="w-12 h-12 text-[var(--tf-muted)] mx-auto mb-4 animate-pulse" />
              <h3 className="text-lg font-bold text-[var(--tf-ink)]">No interviews booked</h3>
              <p className="text-[var(--tf-muted)] text-sm max-w-sm mx-auto mt-2">
                Launch live candidate reviews. Book video or phone assessment slots for any candidate.
              </p>
            </div>
          )}
        </div>

      </main>
    </div>
  )
}
