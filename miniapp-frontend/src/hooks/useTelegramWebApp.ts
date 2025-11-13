import { useEffect, useMemo, useState } from 'react'

import {
  ensureTelegramReady,
  getTelegramTheme,
  isTelegramWebApp,
  onTelegramThemeChanged,
  type TelegramThemeParams,
} from '../utils/telegram'

interface TelegramIntegration {
  isTelegram: boolean
  colorScheme: 'light' | 'dark' | undefined
  themeParams: TelegramThemeParams | undefined
}

function applyTheme(params?: TelegramThemeParams): void {
  const root = document.documentElement
  if (!root) return

  const fallback: Record<string, string> = {
    '--tg-bg-color': params?.bg_color ?? '#0e1117',
    '--tg-text-color': params?.text_color ?? '#e6edf3',
    '--tg-hint-color': params?.hint_color ?? '#9da5b4',
    '--tg-link-color': params?.link_color ?? '#409cff',
    '--tg-button-color': params?.button_color ?? '#2ea6ff',
    '--tg-button-text': params?.button_text_color ?? '#ffffff',
    '--tg-secondary-bg': params?.secondary_bg_color ?? '#161b22',
  }

  Object.entries(fallback).forEach(([key, value]) => {
    root.style.setProperty(key, value)
  })
}

export function useTelegramWebApp(): TelegramIntegration {
  const [state, setState] = useState(() => {
    const theme = getTelegramTheme()
    return {
      isTelegram: isTelegramWebApp(),
      colorScheme: theme.colorScheme,
      themeParams: theme.params,
    }
  })

  useEffect(() => {
    if (!state.isTelegram) {
      return
    }
    ensureTelegramReady()
  }, [state.isTelegram])

  useEffect(() => {
    applyTheme(state.themeParams)
  }, [state.themeParams])

  useEffect(() => {
    if (!state.isTelegram) {
      return
    }

    const handler = () => {
      const theme = getTelegramTheme()
      setState({
        isTelegram: true,
        colorScheme: theme.colorScheme,
        themeParams: theme.params,
      })
    }

    const unsubscribe = onTelegramThemeChanged(handler)
    return () => {
      unsubscribe()
    }
  }, [state.isTelegram])

  return useMemo(() => state, [state])
}

export default useTelegramWebApp
