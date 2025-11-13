export interface AuthUser {
  id: number
  tgId: number
  username?: string | null
  roles: string[]
  isAdmin: boolean
}

export type AuthStatus = 'idle' | 'loading' | 'authenticated' | 'error'

export interface AuthState {
  status: AuthStatus
  token: string | null
  user: AuthUser | null
  error?: string | null
}
