'use client'

import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'
import { CVDropzone } from '@/components/pipeline/cv-dropzone'
import { usePipelineStore } from '@/lib/stores/pipeline-store'
import { getUploadUrls, uploadFileDirectly, submitBatch, getBatchStatus, type BatchFileItem } from '@/lib/api/pipeline'
import { AgentStatusTimeline, StepStatus } from '@/components/pipeline/agent-status-timeline'
import { Play, CheckCircle2, AlertTriangle, Loader2 } from 'lucide-react'
import { useToast } from '@/lib/providers/toast-provider'

export default function PipelinePage() {
  const { jobId } = useParams()
  const [isProcessing, setIsProcessing] = useState(false)
  const [batchStatus, setBatchStatus] = useState<any>(null)
  const { pushToast } = useToast()
  
  const stagedFiles = usePipelineStore(state => state.stagedFiles)
  const updateFileStatus = usePipelineStore(state => state.updateFileStatus)
  const updateFileProgress = usePipelineStore(state => state.updateFileProgress)
  const batchId = usePipelineStore(state => state.batchId)
  const setBatchId = usePipelineStore(state => state.setBatchId)

  // Polling logic
  useEffect(() => {
    let interval: NodeJS.Timeout
    if (batchId && batchStatus?.status !== 'completed' && batchStatus?.status !== 'failed') {
      interval = setInterval(async () => {
        try {
          const res = await getBatchStatus(batchId)
          setBatchStatus(res)
          if (res.status === 'completed' || res.status === 'failed') {
            setIsProcessing(false)
          }
        } catch (error) {
          console.error("Failed to poll batch status", error)
          pushToast('Failed to refresh batch status.', 'error')
        }
      }, 3000)
    }
    return () => clearInterval(interval)
  }, [batchId, batchStatus, pushToast])

  const handleProcessBatch = async () => {
    if (stagedFiles.length === 0) return
    setIsProcessing(true)

    try {
      // 1. Get Presigned URLs
      const filesToUpload = stagedFiles.map(f => ({
        filename: f.file.name,
        content_type: f.file.type,
        size_bytes: f.file.size
      }))
      
      const uploadUrlsRes = await getUploadUrls(filesToUpload)
      const uploadData = uploadUrlsRes // assuming array of {upload_url, r2_key}

      // 2. Upload Files to R2
      const uploadPromises = stagedFiles.map(async (f, index) => {
        const data = uploadData[index]
        updateFileStatus(f.id, 'uploading')
        try {
          // Simulate progress
          const interval = setInterval(() => {
            const current = usePipelineStore.getState().stagedFiles.find(sf => sf.id === f.id)?.progress ?? 0
            usePipelineStore.getState().updateFileProgress(f.id, Math.min(90, current + 10))
          }, 200)
          
          await uploadFileDirectly(data.upload_url, f.file)
          clearInterval(interval)
          
          updateFileProgress(f.id, 100)
          updateFileStatus(f.id, 'done', undefined, data.r2_key)
          return data.r2_key
        } catch (error) {
          updateFileStatus(f.id, 'error', 'Upload failed')
          throw error
        }
      })

      await Promise.all(uploadPromises)

      const filesForSubmit: BatchFileItem[] = stagedFiles.map((f, index) => ({
        r2_key: uploadData[index].r2_key,
        filename: f.file.name,
        size_bytes: f.file.size,
        content_type: f.file.type || 'application/octet-stream'
      }))

      // 3. Submit Batch to Backend
      const idempotencyKey = crypto.randomUUID()
      const batchRes = await submitBatch(jobId as string, filesForSubmit, idempotencyKey)
      
      setBatchId(batchRes.id)
      setBatchStatus(batchRes)

    } catch (error) {
      console.error("Batch processing failed", error)
      pushToast('Batch processing failed. Please try again.', 'error')
      setIsProcessing(false)
    }
  }

  const getTimelineSteps = () => {
    const steps = [
      { id: 'upload', title: 'Document Upload', description: 'Securely upload CVs to R2 storage', status: 'pending' as StepStatus },
      { id: 'extract', title: 'Data Extraction', description: 'Parse text and extract structured profile via LLM', status: 'pending' as StepStatus },
      { id: 'embed', title: 'Semantic Indexing', description: 'Generate bge-m3 embeddings', status: 'pending' as StepStatus },
      { id: 'score', title: 'Explainable Scoring', description: 'Hybrid scoring against job requirements', status: 'pending' as StepStatus },
      { id: 'bias', title: 'Bias Audit', description: 'Check for protected attributes', status: 'pending' as StepStatus }
    ]

    if (isProcessing || batchStatus) {
      steps[0].status = 'completed' // Upload done if we got here
      
      if (batchStatus) {
        if (batchStatus.status === 'completed') {
          steps.forEach(s => s.status = 'completed')
        } else if (batchStatus.status === 'processing') {
          // Simulate progression based on processed_cvs
          const progress = batchStatus.total_cvs > 0 ? batchStatus.processed_cvs / batchStatus.total_cvs : 0
          steps[1].status = progress > 0.2 ? 'completed' : 'active'
          steps[2].status = progress > 0.4 ? 'completed' : (progress > 0.2 ? 'active' : 'pending')
          steps[3].status = progress > 0.7 ? 'completed' : (progress > 0.4 ? 'active' : 'pending')
          steps[4].status = progress > 0.9 ? 'completed' : (progress > 0.7 ? 'active' : 'pending')
        } else if (batchStatus.status === 'failed') {
          steps[1].status = 'error'
        }
      } else {
        steps[1].status = 'active'
      }
    }

    return steps
  }

  const progressPercent = batchStatus?.total_cvs
    ? Math.round((batchStatus.processed_cvs / batchStatus.total_cvs) * 100)
    : 0

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold text-[var(--tf-ink)]">Add candidates</h1>
          <p className="text-sm text-[var(--tf-muted)] mt-1">Upload CVs and run the full TalentFlow pipeline.</p>
        </div>
        {batchStatus?.status === 'completed' && (
          <div className="flex flex-wrap gap-3">
            <a href={`/jobs/${jobId}/shortlist`} className="px-4 py-2 bg-[var(--tf-accent)] text-white rounded-lg font-medium hover:bg-emerald-700 transition-colors">
              View Shortlist
            </a>
            {batchId && (
              <>
                <a
                  href={`/api/v1/reports/batch/${batchId}?format=csv`}
                  className="px-4 py-2 border border-[var(--tf-border)] bg-white text-[var(--tf-ink)] rounded-lg font-medium hover:bg-[var(--tf-surface-2)] transition-colors"
                >
                  Download CSV
                </a>
                <a
                  href={`/api/v1/reports/batch/${batchId}?format=pdf`}
                  className="px-4 py-2 border border-[var(--tf-border)] bg-white text-[var(--tf-ink)] rounded-lg font-medium hover:bg-[var(--tf-surface-2)] transition-colors"
                >
                  Download PDF
                </a>
              </>
            )}
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-6">
          <CVDropzone />
          
          <div className="flex justify-end">
            <button
              onClick={handleProcessBatch}
              disabled={stagedFiles.length === 0 || isProcessing || batchStatus?.status === 'completed'}
              className="flex items-center px-6 py-3 bg-[var(--tf-accent)] text-white rounded-lg font-medium hover:bg-emerald-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isProcessing ? (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" /> Processing...
                </>
              ) : (
                <>
                  <Play className="w-5 h-5 mr-2" /> Process Batch ({stagedFiles.length})
                </>
              )}
            </button>
          </div>

          {batchStatus && (
            <div className="bg-white/90 p-6 border border-[var(--tf-border)] rounded-2xl shadow-sm">
              <h3 className="text-lg font-semibold text-[var(--tf-ink)] mb-4">Batch progress</h3>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-[var(--tf-muted)]">
                  {batchStatus.processed_cvs} / {batchStatus.total_cvs} Processed
                </span>
                <span className="text-sm font-medium text-[var(--tf-muted)]">
                  {progressPercent}%
                </span>
              </div>
              <div className="w-full bg-[var(--tf-surface-2)] rounded-full h-2.5">
                <div 
                  className="bg-[var(--tf-accent)] h-2.5 rounded-full transition-all duration-500" 
                  style={{ width: `${progressPercent}%` }}
                ></div>
              </div>
            </div>
          )}
        </div>

        <div className="lg:col-span-1">
          <div className="bg-white/90 p-6 border border-[var(--tf-border)] rounded-2xl shadow-sm sticky top-8">
            <h3 className="text-lg font-semibold text-[var(--tf-ink)] mb-6">Agent pipeline status</h3>
            <AgentStatusTimeline steps={getTimelineSteps()} />
          </div>
        </div>
      </div>
    </div>
  )
}
