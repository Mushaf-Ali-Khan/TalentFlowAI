'use client'

import { useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getJob, getCandidatesForJob } from '@/lib/api/jobs'
import { getCandidate, updateCandidateStatus } from '@/lib/api/candidates'
import { CandidateTable, type CandidateRow } from '@/components/shortlist/candidate-table'
import { CandidateDrawer, type CandidateDetail } from '@/components/shortlist/candidate-drawer'
import { ArrowLeft, Sparkles, AlertCircle, RefreshCw, UploadCloud, CheckCircle2, XCircle, Search, HelpCircle, Loader2 } from 'lucide-react'

export default function ShortlistPage() {
  const { jobId } = useParams()
  const router = useRouter()
  const queryClient = useQueryClient()
  
  const [selectedCandidateId, setSelectedCandidateId] = useState<string | null>(null)
  const [isDrawerOpen, setIsDrawerOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')

  // 1. Fetch Job Info
  const { data: job, isLoading: isJobLoading } = useQuery<any>({
    queryKey: ['job', jobId],
    queryFn: () => getJob(jobId as string),
  })

  // 2. Fetch Screened Candidates
  const { data: rawCandidates, isLoading: isCandidatesLoading, refetch } = useQuery<any[]>({
    queryKey: ['candidates', jobId],
    queryFn: () => getCandidatesForJob(jobId as string),
  })

  // 3. Fetch Specific Selected Candidate Detail (for Drawer)
  const { data: candidateDetail, isLoading: isDetailLoading } = useQuery<any>({
    queryKey: ['candidate-detail', selectedCandidateId],
    queryFn: () => getCandidate(selectedCandidateId as string),
    enabled: !!selectedCandidateId,
  })

  // 4. Update Candidate Recruiter Status
  const updateStatusMutation = useMutation({
    mutationFn: ({ id, status, note }: { id: string; status: string; note?: string }) => 
      updateCandidateStatus(id, status, note),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['candidates', jobId] })
      queryClient.invalidateQueries({ queryKey: ['candidate-detail', selectedCandidateId] })
      setIsDrawerOpen(false)
    }
  })

  const handleRowClick = (id: string) => {
    setSelectedCandidateId(id)
    setIsDrawerOpen(true)
  }

  const handleStatusChange = (status: string, note?: string) => {
    if (!selectedCandidateId) return
    updateStatusMutation.mutate({ id: selectedCandidateId, status, note })
  }

  // Filter and map raw candidates into table schema
  const filteredCandidates = (rawCandidates || [])
    .filter(c => c.name.toLowerCase().includes(searchQuery.toLowerCase()))
    .map(c => {
      // Safely fetch metrics
      const scoreData = c.score_breakdown || {}
      return {
        id: c.id,
        name: c.name || c.profile?.name || 'Candidate',
        role: job?.title || 'Senior Backend Engineer',
        total_score: c.total_score || 0,
        skills_match: scoreData.skills_match || 0,
        experience: c.profile?.total_years_experience || 0,
        auto_rejected: c.auto_rejected || false,
        needs_manual_review: c.needs_manual_review || false,
        status: c.recruiter_status || 'new'
      } as CandidateRow
    })

  // Format candidate details for drawer
  const formattedCandidateDetail = candidateDetail ? {
    id: candidateDetail.id,
    name: candidateDetail.name || candidateDetail.profile?.name || 'Candidate',
    email: candidateDetail.email || candidateDetail.profile?.email || 'N/A',
    phone: candidateDetail.phone || candidateDetail.profile?.phone || 'N/A',
    location: candidateDetail.location || candidateDetail.profile?.location || 'Remote',
    total_score: candidateDetail.total_score || 0,
    llm_score: candidateDetail.llm_score || 0,
    semantic_score: candidateDetail.semantic_score || 0,
    score_data: {
      skills_match: candidateDetail.score_breakdown?.skills_match || 0,
      experience_relevance: candidateDetail.score_breakdown?.experience_relevance || 0,
      education_fit: candidateDetail.score_breakdown?.education_fit || 0,
      growth_trajectory: candidateDetail.score_breakdown?.growth_trajectory || 0,
    },
    justifications: {
      skills_match: candidateDetail.profile?.skills?.map((s: any) => `${s.name} (${s.proficiency || 'proficient'})`).join(', ') || 'No skill match parsed.',
      experience_relevance: candidateDetail.profile?.experience?.map((e: any) => `${e.title} at ${e.company}`).join(', ') || 'No explicit experience parsed.',
      education_fit: candidateDetail.profile?.education?.map((ed: any) => `${ed.degree} in ${ed.field}`).join(', ') || 'No university degree details.',
      growth_trajectory: `Seniority level ranked at: ${candidateDetail.profile?.seniority_level || 'mid-level'}. Confidence rating: ${Math.round(candidateDetail.extraction_confidence * 100)}%`
    },
    raw_profile: candidateDetail.profile || {}
  } as CandidateDetail : null

  const shortlistedCount = filteredCandidates.filter(c => c.status === 'shortlisted').length
  const flaggedCount = filteredCandidates.filter(c => c.needs_manual_review).length
  const avgScore = filteredCandidates.length > 0 
    ? filteredCandidates.reduce((acc, curr) => acc + curr.total_score, 0) / filteredCandidates.length
    : 0

  return (
    <div className="min-h-screen bg-[#070913] text-[#f1f3f9] font-sans pb-16">
      
      {/* Background radial highlight */}
      <div className="absolute top-[5%] right-[10%] w-[500px] h-[500px] rounded-full bg-indigo-900/10 blur-[100px] pointer-events-none"></div>

      <header className="border-b border-gray-800/60 bg-gray-950/40 backdrop-blur-md sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <button 
            onClick={() => router.push('/')}
            className="flex items-center gap-2 text-sm font-semibold text-gray-400 hover:text-white transition-colors group"
          >
            <ArrowLeft className="w-4 h-4 transition-transform group-hover:-translate-x-1" /> Back to Jobs
          </button>
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-emerald-500 animate-ping"></span>
            <span className="text-xs font-bold text-gray-400">Database Synced</span>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        
        {/* Job Details Card Header */}
        <div className="bg-gray-900/30 border border-gray-800/80 rounded-3xl p-8 backdrop-blur-sm mb-8 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500/5 rounded-bl-full pointer-events-none"></div>
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
            <div>
              <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-indigo-950 text-indigo-300 border border-indigo-800/40 mb-3">
                Screening Pipeline Active
              </span>
              <h1 className="text-3xl font-extrabold text-white">
                {isJobLoading ? 'Loading Job Role...' : job?.title || 'Senior Backend Engineer'}
              </h1>
              <p className="text-sm text-gray-400 mt-2 line-clamp-2 max-w-3xl">
                {job?.description || 'Loading requirements...'}
              </p>
            </div>
            
            <a 
              href={`/jobs/${jobId}/pipeline`}
              className="flex items-center gap-2 px-5 py-3 bg-indigo-600 text-white rounded-xl font-bold text-sm hover:bg-indigo-500 transition-colors shadow-lg shadow-indigo-600/10 shrink-0"
            >
              <UploadCloud className="w-4.5 h-4.5" /> Parse New Candidates
            </a>
          </div>
        </div>

        {/* Shortlist Metric Highlights */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 mb-8">
          <div className="bg-gray-900/30 border border-gray-800/80 rounded-2xl p-6 backdrop-blur-sm">
            <div className="flex justify-between items-center">
              <p className="text-xs font-bold text-gray-400 uppercase tracking-wider">Shortlisted Candidates</p>
              <CheckCircle2 className="w-5 h-5 text-emerald-400" />
            </div>
            <p className="text-3xl font-extrabold text-white mt-3">{shortlistedCount} Candidates</p>
          </div>

          <div className="bg-gray-900/30 border border-gray-800/80 rounded-2xl p-6 backdrop-blur-sm">
            <div className="flex justify-between items-center">
              <p className="text-xs font-bold text-gray-400 uppercase tracking-wider">Average Evaluation Score</p>
              <Sparkles className="w-5 h-5 text-indigo-400" />
            </div>
            <p className="text-3xl font-extrabold text-white mt-3">{avgScore > 0 ? `${avgScore.toFixed(1)} / 100` : 'N/A'}</p>
          </div>

          <div className="bg-gray-900/30 border border-gray-800/80 rounded-2xl p-6 backdrop-blur-sm">
            <div className="flex justify-between items-center">
              <p className="text-xs font-bold text-gray-400 uppercase tracking-wider">Needs Manual Review</p>
              <AlertCircle className="w-5 h-5 text-orange-400" />
            </div>
            <p className="text-3xl font-extrabold text-white mt-3">{flaggedCount} Flagged</p>
          </div>
        </div>

        {/* Search & Listing */}
        <div className="bg-gray-900/30 border border-gray-800/80 rounded-3xl p-6 backdrop-blur-sm">
          
          <div className="flex flex-col sm:flex-row justify-between items-center gap-4 mb-6">
            <div className="relative w-full sm:max-w-md">
              <Search className="w-4 h-4 text-gray-500 absolute left-3.5 top-3.5" />
              <input
                type="text"
                placeholder="Search candidates by name..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-[#0a0d1d] border border-gray-800/80 rounded-xl pl-10 pr-4 py-2.5 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-indigo-500 transition-colors"
              />
            </div>
            
            <button 
              onClick={() => refetch()}
              className="flex items-center gap-2 text-xs font-bold text-gray-400 hover:text-white transition-colors px-3 py-2 border border-gray-800 rounded-xl bg-gray-900/20 shrink-0"
            >
              <RefreshCw className="w-3.5 h-3.5" /> Sync candidates
            </button>
          </div>

          {isCandidatesLoading ? (
            <div className="flex flex-col items-center justify-center p-16">
              <Loader2 className="w-12 h-12 text-indigo-500 animate-spin mb-4" />
              <p className="text-gray-400 text-sm">Fetching and comparing screened candidates...</p>
            </div>
          ) : filteredCandidates.length > 0 ? (
            <div className="overflow-hidden rounded-2xl border border-gray-800/60 bg-[#0a0d1d]/40">
              
              <table className="min-w-full divide-y divide-gray-850">
                <thead className="bg-gray-950/60 text-xs font-bold uppercase tracking-wider text-gray-400">
                  <tr>
                    <th scope="col" className="px-6 py-4 text-left">Candidate Name</th>
                    <th scope="col" className="px-6 py-4 text-center">Screening Score</th>
                    <th scope="col" className="px-6 py-4 text-left">Primary Skillsets</th>
                    <th scope="col" className="px-6 py-4 text-center">Exp</th>
                    <th scope="col" className="px-6 py-4 text-center">Review Action</th>
                  </tr>
                </thead>
                
                <tbody className="divide-y divide-gray-850 bg-transparent text-sm">
                  {filteredCandidates.map((candidate) => (
                    <tr 
                      key={candidate.id}
                      onClick={() => handleRowClick(candidate.id)}
                      className="hover:bg-indigo-900/10 cursor-pointer transition-all border-l-2 border-l-transparent hover:border-l-indigo-500"
                    >
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-indigo-500/20 to-purple-600/30 border border-indigo-500/30 flex items-center justify-center text-indigo-300 font-bold">
                            {candidate.name.charAt(0)}
                          </div>
                          <div>
                            <p className="font-bold text-white flex items-center gap-2">
                              {candidate.name}
                              {candidate.needs_manual_review && (
                                <span className="inline-flex items-center px-1.5 py-0.5 rounded bg-orange-950 text-orange-400 border border-orange-800/40 text-[10px]">
                                  Flagged
                                </span>
                              )}
                            </p>
                            <p className="text-xs text-gray-500 mt-0.5">{candidate.role}</p>
                          </div>
                        </div>
                      </td>

                      <td className="px-6 py-4 text-center whitespace-nowrap">
                        <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-extrabold ${
                          candidate.total_score >= 70 ? 'bg-emerald-950 text-emerald-300 border border-emerald-800/30' :
                          candidate.total_score >= 50 ? 'bg-indigo-950 text-indigo-300 border border-indigo-800/30' :
                          'bg-red-950 text-red-300 border border-red-800/30'
                        }`}>
                          {candidate.total_score.toFixed(1)} / 100
                        </span>
                      </td>

                      <td className="px-6 py-4 max-w-xs truncate text-gray-300 font-medium">
                        {rawCandidates?.find(rc => rc.id === candidate.id)?.profile?.skills?.map((s: any) => s.name).slice(0, 4).join(', ') || 'General Technical skills'}
                      </td>

                      <td className="px-6 py-4 text-center font-bold text-gray-400">
                        {candidate.experience.toFixed(0)} yrs
                      </td>

                      <td className="px-6 py-4 text-center whitespace-nowrap">
                        {candidate.status === 'shortlisted' ? (
                          <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-950 text-emerald-400 border border-emerald-900">
                            Shortlisted
                          </span>
                        ) : candidate.status === 'rejected' ? (
                          <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-red-950 text-red-400 border border-red-900">
                            Rejected
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-indigo-950 text-indigo-300 border border-indigo-900">
                            Assessed
                          </span>
                        )}
                      </td>

                    </tr>
                  ))}
                </tbody>
              </table>

            </div>
          ) : (
            <div className="bg-[#0a0d1d]/20 border border-dashed border-gray-800 rounded-2xl p-16 text-center">
              <UploadCloud className="w-12 h-12 text-gray-600 mx-auto mb-4 animate-pulse" />
              <h3 className="text-lg font-bold text-white">No screening history found</h3>
              <p className="text-gray-400 text-sm max-w-sm mx-auto mt-2 mb-6">
                Parse candidate docx/pdf resumes inside this role's sandbox to let the AI comparative screening begin.
              </p>
              <a 
                href={`/jobs/${jobId}/pipeline`}
                className="inline-flex items-center gap-2 px-5 py-2.5 bg-indigo-600 text-white rounded-xl font-bold text-xs hover:bg-indigo-500 transition-colors"
              >
                Go to Upload Pipeline <ArrowRight className="w-3.5 h-3.5" />
              </a>
            </div>
          )}
        </div>

        {/* Candidates Drawer Modal */}
        <div className="text-gray-900">
          <CandidateDrawer
            isOpen={isDrawerOpen}
            onClose={() => setIsDrawerOpen(false)}
            candidate={formattedCandidateDetail}
          />
        </div>

        {/* Render status modifiers if detail is loaded */}
        {isDrawerOpen && formattedCandidateDetail && (
          <div className="fixed bottom-6 right-6 z-[100] flex gap-3.5 bg-gray-950 border border-gray-800 p-4 rounded-2xl shadow-2xl backdrop-blur-md animate-slideIn">
            <button 
              onClick={() => handleStatusChange('rejected', 'Does not meet core requirements.')}
              className="flex items-center gap-2 px-4 py-2.5 bg-red-950/40 text-red-400 hover:bg-red-900/30 border border-red-800/40 rounded-xl text-xs font-extrabold transition-all"
            >
              <XCircle className="w-4 h-4" /> Reject candidate
            </button>
            <button 
              onClick={() => handleStatusChange('shortlisted', 'Excellent profile matched.')}
              className="flex items-center gap-2 px-5 py-2.5 bg-emerald-600 text-white hover:bg-emerald-500 rounded-xl text-xs font-extrabold transition-all shadow-lg shadow-emerald-600/10"
            >
              <CheckCircle2 className="w-4 h-4" /> Shortlist Profile
            </button>
          </div>
        )}

      </main>
    </div>
  )
}
