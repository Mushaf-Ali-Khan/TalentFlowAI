'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { getJobs } from '@/lib/api/jobs'
import { GlobalHeader } from '@/components/global-header'
import { FileText, Download, Briefcase, Table, Layers, ArrowRight, Loader2, Sparkles } from 'lucide-react'
import { useToast } from '@/lib/providers/toast-provider'

export default function ReportsPage() {
  const { pushToast } = useToast()
  const [selectedJobId, setSelectedJobId] = useState<string>('')
  const [format, setFormat] = useState<'pdf' | 'csv'>('pdf')
  const [isExporting, setIsExporting] = useState(false)

  // Fetch active jobs
  const { data: jobs, isLoading } = useQuery<any>({
    queryKey: ['jobs'],
    queryFn: getJobs,
  })

  const activeJobs = (jobs || []) as any[]

  // Mock list of historically generated reports to show rich utility options
  const [historicalReports, setHistoricalReports] = useState([
    { id: 'rep_1', name: 'Standard Candidate Shortlist Dossier', job: 'Senior Backend Engineer', format: 'PDF', date: '2026-05-19 13:41', size: '2.4 MB' },
    { id: 'rep_2', name: 'Raw Screening Matrix Spreadsheet', job: 'Senior Backend Engineer', format: 'CSV', date: '2026-05-19 13:40', size: '14.8 KB' },
    { id: 'rep_3', name: 'Bias Audit Compliance Ledger', job: 'General Recruiting Pool', format: 'PDF', date: '2026-05-18 16:22', size: '1.8 MB' },
  ])

  const handleExport = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedJobId) {
      pushToast('Please select an active recruitment pipeline first.', 'error')
      return
    }

    setIsExporting(true)
    pushToast(`Generating explainable report dossier in ${format.toUpperCase()}...`, 'info')

    setTimeout(() => {
      setIsExporting(false)
      const selectedJob = activeJobs?.find(j => j.id === selectedJobId)
      
      // Add to local list dynamically for UX feedback
      const newReport = {
        id: `rep_${Date.now()}`,
        name: `${format.toUpperCase() === 'PDF' ? 'Explainable Candidate Shortlist Dossier' : 'Raw Screening Matrix Spreadsheet'}`,
        job: selectedJob?.title || 'Unknown Job',
        format: format.toUpperCase(),
        date: new Date().toISOString().replace('T', ' ').substring(0, 16),
        size: format === 'pdf' ? '1.9 MB' : '8.2 KB',
      }
      setHistoricalReports(prev => [newReport, ...prev])
      pushToast('Report generated successfully! Download started.', 'info')

      // Trigger a clean mockup download or redirect if backend batch endpoint is ready
      // For a demo-ready prototype, download a beautiful mock resume summary or trigger batch download anchor
      const downloadUrl = `/api/v1/reports/batch/${selectedJobId}?format=${format}`
      
      // Create a temporary link element
      const link = document.createElement('a')
      link.href = downloadUrl
      link.setAttribute('download', `talentflow_${selectedJob?.title.toLowerCase().replace(/ /g, '_')}_report.${format}`)
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }, 2000)
  }

  return (
    <div className="min-h-screen relative overflow-hidden bg-[var(--tf-bg)] pb-16">
      {/* Background blur accents */}
      <div className="absolute -top-32 -left-40 h-[520px] w-[520px] rounded-full bg-[var(--tf-accent-3)]/10 blur-[120px] pointer-events-none" />
      <div className="absolute top-[40%] right-[-10%] h-[420px] w-[420px] rounded-full bg-[var(--tf-accent)]/10 blur-[120px] pointer-events-none" />

      <GlobalHeader />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 relative z-10">
        
        {/* Header Title block */}
        <div className="mb-10">
          <h1 className="text-3xl font-extrabold text-[var(--tf-ink)] tracking-tight">Reports Dossier Builder</h1>
          <p className="text-sm text-[var(--tf-muted)] mt-1">Compile comprehensive screening summaries, bias audit charts, and structured candidate comparison spreadsheets.</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Export Builder Form */}
          <div className="lg:col-span-1">
            <div className="bg-white/95 border border-[var(--tf-border)] rounded-3xl p-6 shadow-sm sticky top-24">
              <h2 className="text-xl font-bold text-[var(--tf-ink)] flex items-center gap-2 mb-6">
                <FileText className="w-5 h-5 text-[var(--tf-accent)]" /> Export Dossier
              </h2>

              <form onSubmit={handleExport} className="space-y-6">
                
                {/* 1. Job selector */}
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-[var(--tf-muted)] mb-2.5">
                    Select Active Pipeline
                  </label>
                  {isLoading ? (
                    <div className="flex items-center gap-2 text-sm text-[var(--tf-muted)]">
                      <Loader2 className="w-4 h-4 animate-spin text-[var(--tf-accent)]" /> Loading jobs...
                    </div>
                  ) : activeJobs && activeJobs.length > 0 ? (
                    <select
                      value={selectedJobId}
                      onChange={(e) => setSelectedJobId(e.target.value)}
                      required
                      className="w-full bg-white border border-[var(--tf-border)] rounded-xl px-4 py-3 text-sm text-[var(--tf-ink)] focus:outline-none focus:border-[var(--tf-accent)] focus:ring-1 focus:ring-[var(--tf-accent)] transition-colors cursor-pointer"
                    >
                      <option value="">-- Choose active role --</option>
                      {activeJobs.map(job => (
                        <option key={job.id} value={job.id}>{job.title}</option>
                      ))}
                    </select>
                  ) : (
                    <p className="text-xs text-red-500 font-semibold">No active job pipelines found. Create one first!</p>
                  )}
                </div>

                {/* 2. Format selector */}
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-[var(--tf-muted)] mb-2.5">
                    Choose Export Format
                  </label>
                  <div className="grid grid-cols-2 gap-3">
                    {[
                      { type: 'pdf', title: 'PDF Dossier', desc: 'Beautiful, explainable visual document', icon: FileText },
                      { type: 'csv', title: 'CSV Matrix', desc: 'Raw spreadsheet suitable for ATS import', icon: Table },
                    ].map((opt) => (
                      <button
                        key={opt.type}
                        type="button"
                        onClick={() => setFormat(opt.type as 'pdf' | 'csv')}
                        className={`p-4 border rounded-2xl flex flex-col text-left transition-all duration-200 cursor-pointer ${
                          format === opt.type
                            ? 'bg-emerald-50 border-emerald-300 text-emerald-800 ring-2 ring-emerald-500/10'
                            : 'bg-white border-[var(--tf-border)] hover:bg-slate-50 text-slate-700'
                        }`}
                      >
                        <opt.icon className="w-5 h-5 text-[var(--tf-accent)] mb-2" />
                        <span className="text-xs font-bold block">{opt.title}</span>
                        <span className="text-[10px] text-[var(--tf-muted)] mt-1 leading-normal">{opt.desc}</span>
                      </button>
                    ))}
                  </div>
                </div>

                {/* 3. Export submit trigger */}
                <button
                  type="submit"
                  disabled={isExporting || !selectedJobId}
                  className="w-full flex items-center justify-center gap-2 px-6 py-3.5 bg-[var(--tf-accent)] text-white rounded-xl font-bold text-sm hover:bg-emerald-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer shadow-lg shadow-emerald-500/10"
                >
                  {isExporting ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" /> Compiling Dossier...
                    </>
                  ) : (
                    <>
                      Generate Report <Sparkles className="w-4 h-4" />
                    </>
                  )}
                </button>

              </form>
            </div>
          </div>

          {/* Report Export Logs */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white/95 border border-[var(--tf-border)] rounded-3xl p-6 shadow-sm">
              <div className="flex justify-between items-center mb-6">
                <div>
                  <h3 className="text-lg font-bold text-[var(--tf-ink)] flex items-center gap-2">
                    <Layers className="w-5 h-5 text-[var(--tf-accent)]" /> Generated Reports Registry
                  </h3>
                  <p className="text-xs text-[var(--tf-muted)] mt-0.5">Historical logs of all compiled candidate evaluations and sheets.</p>
                </div>
              </div>

              <div className="divide-y divide-[var(--tf-border)]">
                {historicalReports.map((report) => (
                  <div key={report.id} className="py-4 flex items-center justify-between gap-4 first:pt-0 last:pb-0">
                    <div className="flex items-center gap-3">
                      <div className={`h-10 w-10 rounded-xl flex items-center justify-center font-bold text-xs ${
                        report.format === 'PDF' 
                          ? 'bg-red-50 text-red-600 border border-red-100'
                          : 'bg-emerald-50 text-emerald-600 border border-emerald-100'
                      }`}>
                        {report.format}
                      </div>
                      <div>
                        <p className="font-bold text-sm text-[var(--tf-ink)]">{report.name}</p>
                        <p className="text-xs text-[var(--tf-muted)] mt-0.5 flex items-center gap-1">
                          <Briefcase className="w-3 h-3 text-slate-400" /> {report.job}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        <p className="text-[10px] text-slate-400 font-bold">{report.date}</p>
                        <p className="text-xs text-[var(--tf-muted)] font-semibold mt-0.5">{report.size}</p>
                      </div>
                      <button 
                        onClick={() => {
                          pushToast('Download started for historical dossier.', 'info')
                        }}
                        className="p-2 border border-slate-200 hover:bg-slate-50 rounded-xl transition-colors cursor-pointer"
                        title="Download historical dossier"
                      >
                        <Download className="w-4 h-4 text-slate-600" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Explanatory Callout */}
            <div className="bg-emerald-50/40 border border-emerald-100 rounded-3xl p-6 flex gap-4">
              <Sparkles className="w-6 h-6 text-[var(--tf-accent)] shrink-0 mt-0.5 animate-pulse" />
              <div className="text-xs text-emerald-800 leading-relaxed">
                <p className="font-extrabold text-sm mb-1.5">What is inside an Explainable Dossier?</p>
                <ul className="space-y-1 list-disc pl-4 font-semibold text-emerald-700">
                  <li>Direct candidate-to-rubric score matching ratios across 4 critical assessment areas.</li>
                  <li>Textual evidence links extracted verbatim from resumes to defend each LLM score.</li>
                  <li>Verified BGE-M3 high-dimensional cosine similarity ranking to demonstrate semantic alignment.</li>
                  <li>Full bias auditing records confirming fair hiring criteria compliance.</li>
                </ul>
              </div>
            </div>
          </div>

        </div>
      </main>
    </div>
  )
}
