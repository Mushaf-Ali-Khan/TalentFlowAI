import { apiClient } from './client'

export type BatchFileItem = {
  r2_key: string
  filename: string
  size_bytes: number
  content_type: string
}

export const getUploadUrls = async (files: Array<{filename: string, content_type: string, size_bytes: number}>) => {
  return apiClient.post('/pipeline/upload-urls', files) as any
}

export const submitBatch = async (jobId: string, files: BatchFileItem[], idempotencyKey?: string) => {
  return apiClient.post('/pipeline/submit', {
    job_id: jobId,
    files,
    idempotency_key: idempotencyKey
  }) as any
}

export const getBatchStatus = async (batchId: string) => {
  return apiClient.get(`/pipeline/${batchId}`) as any
}

// In a real implementation this would use R2 presigned URLs
export const uploadFileDirectly = async (url: string, file: File) => {
  // We use standard fetch or axios for the actual PUT to the presigned URL
  const response = await fetch(url, {
    method: 'PUT',
    body: file,
    headers: {
      'Content-Type': file.type,
    },
  })
  if (!response.ok) {
    throw new Error('Upload failed')
  }
  return true
}
