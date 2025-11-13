import { apiClient } from './http'

export interface HealthzResponse {
  ok: boolean
}

export async function fetchHealth(): Promise<HealthzResponse> {
  const res = await apiClient.get<HealthzResponse>('/healthz')
  return res.data
}
