import axios from 'axios'

// Web Admin API 基础地址（端口 8001）
const ADMIN_API_BASE_URL = process.env.NEXT_PUBLIC_ADMIN_API_BASE_URL || 'http://localhost:8001'

let adminAccessToken: string | null = null

export function setAdminAccessToken(token: string | null) {
  adminAccessToken = token
}

export const adminApiClient = axios.create({
  baseURL: ADMIN_API_BASE_URL,
  withCredentials: true, // 支持 cookie 认证
})

adminApiClient.interceptors.request.use((config) => {
  // 确保 API 请求包含 Accept: application/json 头
  config.headers = config.headers ?? {}
  config.headers['Accept'] = 'application/json'
  
  if (adminAccessToken) {
    config.headers.Authorization = `Bearer ${adminAccessToken}`
  }
  return config
})

export default adminApiClient

