import type { ReactElement } from 'react'

interface Props {
  lines?: number
  className?: string
}

export function LoadingSkeleton({ lines = 3, className = '' }: Props): ReactElement {
  return (
    <div className={`grid gap-2 ${className}`} role="status" aria-live="polite">
      {Array.from({ length: lines }, (_, index) => (
        <div
          key={index}
          className="h-3 animate-pulse rounded-full bg-white/10"
          style={{ animationDelay: `${index * 60}ms` }}
        />
      ))}
    </div>
  )
}

export default LoadingSkeleton
