import {
  createContext,
  type PropsWithChildren,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react'
import type { ReactElement } from 'react'

import { loginWithPassword, loginWithTelegram, type LoginResponse } from '../api/auth'
import { setAccessToken } from '../api/http'
import { type AuthState, type AuthUser } from '../types/auth'
import { getTelegramInitData } from '../utils/telegram'

interface AuthContextValue extends AuthState {
  refresh: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

const initialState: AuthState = {
  status: 'idle',
  token: null,
  user: null,
  error: null,
}

const DEV_USERNAME = import.meta.env.VITE_DEV_USERNAME as string | undefined
const DEV_PASSWORD = import.meta.env.VITE_DEV_PASSWORD as string | undefined
const DEV_TG_ID = import.meta.env.VITE_DEV_TG_ID ? Number(import.meta.env.VITE_DEV_TG_ID) : undefined
const DEFAULT_LANG = import.meta.env.VITE_DEFAULT_LANG as string | undefined

function toAuthUser(res: LoginResponse): AuthUser {
  const { user } = res
  return {
    id: user.id,
    tgId: user.tg_id,
    username: user.username ?? null,
    roles: user.roles,
    isAdmin: user.roles.includes('admin') || user.roles.includes('miniapp:admin'),
  }
}

export function AuthProvider({ children }: PropsWithChildren): ReactElement {
  const [state, setState] = useState<AuthState>(initialState)

  const handleSuccess = useCallback((res: LoginResponse) => {
    setAccessToken(res.access_token)
    setState({
      status: 'authenticated',
      token: res.access_token,
      user: toAuthUser(res),
      error: null,
    })
  }, [])

  const handleError = useCallback((message: string) => {
    setAccessToken(null)
    setState({ status: 'error', token: null, user: null, error: message })
  }, [])

  const runLogin = useCallback(async () => {
    setState((prev): AuthState => ({ ...prev, status: 'loading', error: null }))

    try {
      const initData = getTelegramInitData()
      if (initData?.code) {
        const res = await loginWithTelegram(initData.code, DEFAULT_LANG)
        handleSuccess(res)
        return
      }

      if (DEV_USERNAME && DEV_PASSWORD && typeof DEV_TG_ID === 'number' && Number.isFinite(DEV_TG_ID)) {
        const res = await loginWithPassword(DEV_USERNAME, DEV_PASSWORD, DEV_TG_ID, DEFAULT_LANG)
        handleSuccess(res)
        return
      }

      handleError('無法自動登入：缺少 Telegram 資訊或 DEV 帳密，請確認配置')
    } catch (error: unknown) {
      console.error('[AuthProvider] login failed', error)
      handleError('登入失敗，請稍後再試')
    }
  }, [handleSuccess, handleError])

  useEffect(() => {
    void runLogin()
  }, [runLogin])

  const value = useMemo<AuthContextValue>(() => ({
    ...state,
    refresh: runLogin,
  }), [state, runLogin])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return ctx
}
