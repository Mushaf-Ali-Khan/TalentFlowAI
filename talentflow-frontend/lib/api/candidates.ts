import { apiClient } from './client'

export const getCandidate = async (id: string) => {
  return apiClient.get(`/candidates/${id}`)
}

export const updateCandidateStatus = async (id: string, status: string, note?: string) => {
  return apiClient.patch(`/candidates/${id}/status`, { status, note })
}
