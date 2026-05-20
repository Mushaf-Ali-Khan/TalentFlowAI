import { apiClient } from './client'

export interface InterviewInput {
  candidate_id: string
  job_id: string
  scheduled_at: string
  duration_minutes?: number
  format?: 'video' | 'phone' | 'in_person'
  meeting_link?: string
  notes?: string
}

export interface InterviewUpdateInput {
  scheduled_at?: string
  duration_minutes?: number
  format?: 'video' | 'phone' | 'in_person'
  meeting_link?: string
  notes?: string
  status?: 'scheduled' | 'completed' | 'cancelled'
}

export interface InterviewDetails {
  id: string
  candidate_id: string
  candidate_name: string
  candidate_email: string
  job_id: string
  job_title: string
  scheduled_at: string
  duration_minutes: number
  format: 'video' | 'phone' | 'in_person'
  meeting_link?: string
  notes?: string
  status: 'scheduled' | 'completed' | 'cancelled'
  created_at: string
}

export const getInterviews = async (): Promise<InterviewDetails[]> => {
  return apiClient.get('/interviews') as any
}

export const scheduleInterview = async (data: InterviewInput): Promise<InterviewDetails> => {
  return apiClient.post('/interviews', data) as any
}

export const updateInterview = async (id: string, data: InterviewUpdateInput): Promise<InterviewDetails> => {
  return apiClient.patch(`/interviews/${id}`, data) as any
}

export const cancelInterview = async (id: string): Promise<{ message: string }> => {
  return apiClient.delete(`/interviews/${id}`) as any
}
