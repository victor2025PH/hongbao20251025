/// <reference types="vite/client" />

declare namespace NodeJS {
  interface ProcessEnv {
    readonly VITE_API_BASE_URL?: string
    readonly VITE_DEV_USERNAME?: string
    readonly VITE_DEV_PASSWORD?: string
    readonly VITE_DEV_TG_ID?: string
    readonly VITE_DEFAULT_LANG?: string
  }
}
