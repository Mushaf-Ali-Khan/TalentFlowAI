import { apiClient } from './client'

export type AnalyticsOverview = {
  total_candidates: number
  avg_total_score: number
  avg_semantic_score: number
  pass_rate: number
  active_jobs: number
  score_distribution?: Record<string, number>
}

export const getAnalyticsOverview = async (): Promise<AnalyticsOverview> => {
  return apiClient.get('/analytics/overview')
}
