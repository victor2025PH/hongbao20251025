import { apiClient } from './http'

export interface LoginRequestTelegram {
  provider: 'telegram'
  telegram_code: string
  language?: string
}

export interface LoginRequestPassword {
  provider: 'password'
  username: string
  password: string
  tg_id: number
  language?: string
}

export interface LoginUserPayload {
  id: number
  tg_id: number
  username?: string | null
  roles: string[]
}

export interface LoginResponse {
  access_token: string
  token_type: string
  expires_in: number
  user: LoginUserPayload
}

export type LoginRequest = LoginRequestTelegram | LoginRequestPassword

export async function login(request: LoginRequest): Promise<LoginResponse> {
  const { data } = await apiClient.post<LoginResponse>('/auth/login', request)
  return data
}

export async function loginWithPassword(
  username: string,
  password: string,
  tgId: number,
  language?: string,
): Promise<LoginResponse> {
  return login({ provider: 'password', username, password, tg_id: tgId, language })
}

export async function loginWithTelegram(code: string, language?: string): Promise<LoginResponse> {
  return login({ provider: 'telegram', telegram_code: code, language })
}
