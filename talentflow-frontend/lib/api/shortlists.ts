import { apiClient } from './client'

export const getShortlistForBatch = async (batchId: string) => {
  return apiClient.get(`/shortlists/batch/${batchId}`)
}
