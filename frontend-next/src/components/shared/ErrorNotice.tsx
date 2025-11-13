import type { ReactElement } from 'react'

interface Props {
  message: string
  onRetry?: () => void
}

export function ErrorNotice({ message, onRetry }: Props): ReactElement {
  return (
    <div className="flex items-center justify-between gap-4 rounded-xl border border-red-500/40 bg-red-500/10 px-4 py-3 text-sm text-red-200">
      <span>{message}</span>
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="rounded-lg border border-red-400/40 px-3 py-1 text-xs font-medium text-red-100 transition hover:border-red-300 hover:bg-red-500/20"
        >
          重試
        </button>
      )}
    </div>
  )
}

export default ErrorNotice
