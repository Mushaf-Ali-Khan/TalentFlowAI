import { apiClient } from './client'

export const getJobs = async () => {
  return apiClient.get('/jobs')
}

export const getJob = async (id: string) => {
  return apiClient.get(`/jobs/${id}`)
}

export const createJob = async (jobData: any) => {
  return apiClient.post('/jobs', jobData)
}

export const getCandidatesForJob = async (id: string) => {
  return apiClient.get(`/jobs/${id}/candidates`)
}

