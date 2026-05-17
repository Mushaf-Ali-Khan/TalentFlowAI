'use client'

import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'
import { CVDropzone } from '@/components/pipeline/cv-dropzone'
import { usePipelineStore } from '@/lib/stores/pipeline-store'
import { getUploadUrls, uploadFileDirectly, submitBatch, getBatchStatus } from '@/lib/api/pipeline'
import { AgentStatusTimeline, StepStatus } from '@/components/pipeline/agent-status-timeline'
import { Play, CheckCircle2, AlertTriangle, Loader2 } from 'lucide-react'

export default function PipelinePage() {
  const { jobId } = useParams()
  const [isProcessing, setIsProcessing] = useState(false)
  const [batchStatus, setBatchStatus] = useState<any>(null)
  
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
        }
      }, 3000)
    }
    return () => clearInterval(interval)
  }, [batchId, batchStatus])

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
            usePipelineStore.getState().updateFileProgress(f.id, Math.min(90, f.progress + 10))
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

      const r2Keys = await Promise.all(uploadPromises)

      // 3. Submit Batch to Backend
      const idempotencyKey = crypto.randomUUID()
      const batchRes = await submitBatch(jobId as string, r2Keys, idempotencyKey)
      
      setBatchId(batchRes.id)
      setBatchStatus(batchRes)

    } catch (error) {
      console.error("Batch processing failed", error)
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

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Add Candidates</h1>
          <p className="text-sm text-gray-500 mt-1">Upload CVs to process them through the AI pipeline.</p>
        </div>
        {batchStatus?.status === 'completed' && (
          <a href={`/jobs/${jobId}/shortlist`} className="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors">
            View Shortlist
          </a>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-6">
          <CVDropzone />
          
          <div className="flex justify-end">
            <button
              onClick={handleProcessBatch}
              disabled={stagedFiles.length === 0 || isProcessing || batchStatus?.status === 'completed'}
              className="flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
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
            <div className="bg-white p-6 border rounded-xl shadow-sm">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Batch Progress</h3>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">
                  {batchStatus.processed_cvs} / {batchStatus.total_cvs} Processed
                </span>
                <span className="text-sm font-medium text-gray-500">
                  {Math.round((batchStatus.processed_cvs / batchStatus.total_cvs) * 100)}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2.5">
                <div 
                  className="bg-blue-600 h-2.5 rounded-full transition-all duration-500" 
                  style={{ width: `${(batchStatus.processed_cvs / batchStatus.total_cvs) * 100}%` }}
                ></div>
              </div>
            </div>
          )}
        </div>

        <div className="lg:col-span-1">
          <div className="bg-white p-6 border rounded-xl shadow-sm sticky top-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-6">Agent Pipeline Status</h3>
            <AgentStatusTimeline steps={getTimelineSteps()} />
          </div>
        </div>
      </div>
    </div>
  )
}
