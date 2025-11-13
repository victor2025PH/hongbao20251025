import { adminApiClient } from './admin'

export interface HealthzResponse {
  ok: boolean
  ts?: string  // ISO 时间戳（可选）
}

export async function fetchHealth(): Promise<HealthzResponse> {
  const res = await adminApiClient.get<HealthzResponse>('/healthz')
  return res.data
}
