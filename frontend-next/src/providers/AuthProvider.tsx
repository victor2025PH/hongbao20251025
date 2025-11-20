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

import { loginWithPassword, loginWithTelegram, type LoginResponse } from '@/api/auth'
import { setAccessToken } from '@/api/http'
import { setAdminAccessToken } from '@/api/admin'
import { type AuthState, type AuthUser } from '@/types/auth'
import { getTelegramInitData } from '@/utils/telegram'

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

// Web Admin 登录凭据（与 web_admin 的 ADMIN_WEB_USER 和 ADMIN_WEB_PASSWORD 对应）
// 默认使用 "admin" 用户名和密码（开发环境）
const DEV_USERNAME = process.env.NEXT_PUBLIC_DEV_USERNAME || process.env.NEXT_PUBLIC_ADMIN_WEB_USER || 'admin'
const DEV_PASSWORD = process.env.NEXT_PUBLIC_DEV_PASSWORD || process.env.NEXT_PUBLIC_ADMIN_WEB_PASSWORD || 'admin'
const DEV_TG_ID = process.env.NEXT_PUBLIC_DEV_TG_ID || process.env.NEXT_PUBLIC_ADMIN_TG_ID ? Number(process.env.NEXT_PUBLIC_DEV_TG_ID || process.env.NEXT_PUBLIC_ADMIN_TG_ID) : undefined
const DEFAULT_LANG = process.env.NEXT_PUBLIC_DEFAULT_LANG || 'zh'
const ADMIN_API_BASE = process.env.NEXT_PUBLIC_ADMIN_API_BASE_URL || 'http://localhost:8001'

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
      
      // 优先尝试使用 Telegram 信息登录到 Web Admin（用于访问红包功能）
      if (initData?.code) {
        try {
          const formData = new FormData()
          formData.append('telegram_code', initData.code)
          
          const response = await fetch(`${ADMIN_API_BASE}/admin/api/v1/auth/login`, {
            method: 'POST',
            credentials: 'include', // 重要：包含 cookies
            body: formData,
          })
          
          if (response.ok) {
            const data = await response.json()
            // Web Admin Telegram 登录成功，设置一个假的 token（实际使用 session）
            setAccessToken('session-auth')
            setAdminAccessToken('session-auth')
            setState({
              status: 'authenticated',
              token: 'session-auth',
              user: {
                id: data.user?.tg_id || 0,
                tgId: data.user?.tg_id || 0,
                username: data.user?.username || null,
                roles: ['admin'],
                isAdmin: true,
              },
              error: null,
            })
            console.log('[AuthProvider] ✅ Web Admin Telegram login successful', data.user)
            return
          } else {
            const errorData = await response.json().catch(() => ({ message: 'Login failed' }))
            console.warn('[AuthProvider] ⚠️ Web Admin Telegram login failed:', errorData)
            // 如果 Telegram 登录失败，继续尝试其他方式
          }
        } catch (error) {
          console.error('[AuthProvider] Web Admin Telegram login error:', error)
          // 如果出错，继续尝试其他登录方式
        }
      }

      // 回退到用户名密码登录（用于访问 web_admin 的 API）
      if (DEV_USERNAME && DEV_PASSWORD) {
        try {
          // 使用 web_admin 的登录接口（使用 session 认证）
          const formData = new FormData()
          formData.append('username', DEV_USERNAME)
          formData.append('password', DEV_PASSWORD)
          
          const response = await fetch(`${ADMIN_API_BASE}/admin/api/v1/auth/login`, {
            method: 'POST',
            credentials: 'include', // 重要：包含 cookies
            body: formData,
          })
          
          if (response.ok) {
            const data = await response.json()
            // Web Admin 登录成功，设置一个假的 token（实际使用 session）
            setAccessToken('session-auth')
            setAdminAccessToken('session-auth')
            setState({
              status: 'authenticated',
              token: 'session-auth',
              user: {
                id: data.user?.tg_id || DEV_TG_ID || 0,
                tgId: data.user?.tg_id || DEV_TG_ID || 0,
                username: data.user?.username || DEV_USERNAME || null,
                roles: ['admin'],
                isAdmin: true,
              },
              error: null,
            })
            console.log('[AuthProvider] ✅ Web Admin password login successful', data.user)
            return
          } else {
            // 登录失败，获取错误信息
            const errorData = await response.json().catch(() => ({ message: 'Login failed' }))
            console.warn('[AuthProvider] ⚠️ Web Admin password login failed:', response.status, errorData)
            // 如果密码错误，提示用户检查配置
            if (response.status === 401) {
              console.error('[AuthProvider] ❌ 登录失败：', errorData.message || 'Invalid credentials')
              // 不在这里设置错误，继续尝试其他方式
            }
          }
        } catch (error) {
          console.error('[AuthProvider] Web Admin password login error:', error)
          // 如果出错，继续尝试其他登录方式
        }
      }
      
      // 如果配置了 JWT 登录凭据，尝试使用 miniapp 的 JWT 登录（作为备选）
      if (initData?.code) {
        try {
          const res = await loginWithTelegram(initData.code, DEFAULT_LANG)
          handleSuccess(res)
          return
        } catch (error) {
          console.error('[AuthProvider] Miniapp Telegram login failed:', error)
        }
      }
      
      if (DEV_USERNAME && DEV_PASSWORD && typeof DEV_TG_ID === 'number' && Number.isFinite(DEV_TG_ID)) {
        try {
          const res = await loginWithPassword(DEV_USERNAME, DEV_PASSWORD, DEV_TG_ID, DEFAULT_LANG)
          handleSuccess(res)
          return
        } catch (error) {
          console.error('[AuthProvider] Miniapp password login failed:', error)
        }
      }

      handleError('無法自動登入：缺少 Telegram 資訊或 DEV 帳密，請確認配置')
    } catch (error: unknown) {
      console.error('[AuthProvider] login failed', error)
      handleError('登入失敗，請稍後再試')
    }
  }, [handleSuccess, handleError])

  // 初始化时执行登录
  useEffect(() => {
    // eslint-disable-next-line react-hooks/exhaustive-deps
    void runLogin()
    // runLogin 是 useCallback，依赖项已正确处理
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
