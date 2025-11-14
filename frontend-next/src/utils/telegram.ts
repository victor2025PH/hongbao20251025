interface TelegramInitData {
  code: string
  raw: string
}

interface TelegramThemeParams {
  bg_color?: string
  text_color?: string
  hint_color?: string
  link_color?: string
  button_color?: string
  button_text_color?: string
  secondary_bg_color?: string
}

interface TelegramWebApp {
  initData?: string
  initDataUnsafe?: {
    user?: {
      id: number
      username?: string
    }
    auth_date?: number
    hash?: string
  }
  colorScheme?: 'light' | 'dark'
  themeParams?: TelegramThemeParams
  isExpanded?: boolean
  ready?: () => void
  expand?: () => void
  onEvent?: (event: string, handler: () => void) => void
  offEvent?: (event: string, handler: () => void) => void
  openLink?: (url: string, options?: { try_instant_view?: boolean }) => void
  openTelegramLink?: (url: string) => void
  enableClosingConfirmation?: () => void
}

interface TelegramWindow extends Window {
  Telegram?: {
    WebApp?: TelegramWebApp
  }
}

function getWindow(): TelegramWindow | null {
  if (typeof window === 'undefined') return null
  return window as TelegramWindow
}

function buildCode(): string | null {
  const win = getWindow()
  if (!win) return null
  const unsafe = win.Telegram?.WebApp?.initDataUnsafe
  if (!unsafe?.user || !unsafe.auth_date || !unsafe.hash) {
    return null
  }
  const username = unsafe.user.username ?? ''
  return `${unsafe.user.id}.${username}.${unsafe.auth_date}.${unsafe.hash}`
}

export function getTelegramInitData(): TelegramInitData | null {
  const code = buildCode()
  if (!code) {
    return null
  }
  const win = getWindow()
  const raw = win?.Telegram?.WebApp?.initData ?? ''
  return { code, raw }
}

export function isTelegramWebApp(): boolean {
  const win = getWindow()
  return Boolean(win?.Telegram?.WebApp)
}

export function getTelegramTheme(): {
  colorScheme?: 'light' | 'dark'
  params?: TelegramThemeParams
} {
  const win = getWindow()
  const webApp = win?.Telegram?.WebApp
  return {
    colorScheme: webApp?.colorScheme,
    params: webApp?.themeParams,
  }
}

export function onTelegramThemeChanged(handler: () => void): () => void {
  const win = getWindow()
  const webApp = win?.Telegram?.WebApp
  if (!webApp?.onEvent) {
    return () => {}
  }
  webApp.onEvent('themeChanged', handler)
  return () => {
    try {
      webApp.offEvent?.('themeChanged', handler)
    } catch (error) {
      // swallow
    }
  }
}

export function ensureTelegramReady(): void {
  const win = getWindow()
  const webApp = win?.Telegram?.WebApp
  if (!webApp) {
    return
  }
  try {
    webApp.ready?.()
    if (!webApp.isExpanded) {
      webApp.expand?.()
    }
    webApp.enableClosingConfirmation?.()
  } catch (error) {
    // ignore
  }
}

export function openTelegramLink(url: string, options?: { tryInstantView?: boolean }): void {
  if (typeof window === 'undefined') return
  const win = getWindow()
  const webApp = win?.Telegram?.WebApp
  if (!webApp) {
    window.open(url, '_blank', 'noopener')
    return
  }
  try {
    if (options?.tryInstantView) {
      webApp.openLink?.(url, { try_instant_view: true })
      return
    }
    webApp.openTelegramLink?.(url)
  } catch (error) {
    window.open(url, '_blank', 'noopener')
  }
}

export type { TelegramThemeParams }
