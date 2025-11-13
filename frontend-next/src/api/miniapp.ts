import axios from 'axios'

// Miniapp API 基础地址（端口 8080）
const MINIAPP_API_BASE_URL = process.env.NEXT_PUBLIC_MINIAPP_API_BASE_URL || 'http://localhost:8080'

let miniappAccessToken: string | null = null

export function setMiniappAccessToken(token: string | null) {
  miniappAccessToken = token
}

export const miniappApiClient = axios.create({
  baseURL: MINIAPP_API_BASE_URL,
})

miniappApiClient.interceptors.request.use((config) => {
  if (miniappAccessToken) {
    config.headers = config.headers ?? {}
    config.headers.Authorization = `Bearer ${miniappAccessToken}`
  }
  return config
})

export default miniappApiClient

