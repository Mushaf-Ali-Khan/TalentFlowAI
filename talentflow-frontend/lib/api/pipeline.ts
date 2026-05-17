import { apiClient } from './client'

export const getUploadUrls = async (files: Array<{filename: string, content_type: string, size_bytes: number}>) => {
  return apiClient.post('/pipeline/upload-urls', files)
}

export const submitBatch = async (jobId: string, r2Keys: string[], idempotencyKey?: string) => {
  return apiClient.post('/pipeline/submit', {
    job_id: jobId,
    r2_keys: r2Keys,
    idempotency_key: idempotencyKey
  })
}

export const getBatchStatus = async (batchId: string) => {
  return apiClient.get(`/pipeline/${batchId}`)
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
