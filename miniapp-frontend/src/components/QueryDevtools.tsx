import { lazy, Suspense, type ReactElement } from 'react'

const ReactQueryDevtools = lazy(() =>
  import('@tanstack/react-query-devtools').then((mod) => ({ default: mod.ReactQueryDevtools })),
)

export function QueryDevtools(): ReactElement | null {
  const enabled = (import.meta.env.VITE_ENABLE_DEVTOOLS ?? 'false').toLowerCase() === 'true'
  if (!enabled) {
    return null
  }

  return (
    <Suspense fallback={null}>
      <ReactQueryDevtools initialIsOpen={false} buttonPosition="bottom-left" />
    </Suspense>
  )
}

export default QueryDevtools
