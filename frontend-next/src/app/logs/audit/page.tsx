'use client'

import { useState, useCallback, useMemo, Suspense } from 'react'
import Link from 'next/link'
import { useQuery } from '@tanstack/react-query'
import { useSearchParams, useRouter } from 'next/navigation'

import { getAuditLogs, type AuditLogsParams } from '@/lib/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import LoadingSkeleton from '@/components/shared/LoadingSkeleton'
import ErrorNotice from '@/components/shared/ErrorNotice'
import { ArrowLeft, Search, Filter, ChevronLeft, ChevronRight } from 'lucide-react'

const TYPE_OPTIONS = ['RESET', 'ADJUST', 'RECHARGE', 'CLAIM', 'ENVELOPE_CLAIM', 'HONGBAO_SEND', 'HONGBAO_GRAB']

function AuditLogsPageContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  
  const [page, setPage] = useState(() => parseInt(searchParams.get('page') || '1', 10))
  const [perPage] = useState(50)
  const [searchQuery, setSearchQuery] = useState(searchParams.get('q') || '')
  const [selectedTypes, setSelectedTypes] = useState<string[]>(() => {
    const types = searchParams.get('types')
    return types ? types.split(',') : []
  })
  const [tokenFilter, setTokenFilter] = useState(searchParams.get('token') || '')
  const [userFilter, setUserFilter] = useState(searchParams.get('user') || '')

  const params: AuditLogsParams = useMemo(() => {
    const p: AuditLogsParams = {
      page,
      per_page: perPage,
    }
    if (searchQuery) p.q = searchQuery
    if (selectedTypes.length > 0) p.types = selectedTypes
    if (tokenFilter) p.token = tokenFilter
    if (userFilter) p.user = userFilter
    return p
  }, [page, perPage, searchQuery, selectedTypes, tokenFilter, userFilter])

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['audit-logs', params],
    queryFn: () => getAuditLogs(params),
  })

  const updateURL = useCallback((newParams: Record<string, string | number>) => {
    const current = new URLSearchParams(searchParams.toString())
    Object.entries(newParams).forEach(([key, value]) => {
      if (value) {
        current.set(key, String(value))
      } else {
        current.delete(key)
      }
    })
    router.push(`/logs/audit?${current.toString()}`)
  }, [router, searchParams])

  const handleSearch = useCallback(() => {
    updateURL({ q: searchQuery, page: 1 })
    setPage(1)
  }, [searchQuery, updateURL])

  const handleTypeToggle = useCallback((type: string) => {
    const newTypes = selectedTypes.includes(type)
      ? selectedTypes.filter(t => t !== type)
      : [...selectedTypes, type]
    setSelectedTypes(newTypes)
    updateURL({ types: newTypes.join(','), page: 1 })
    setPage(1)
  }, [selectedTypes, updateURL])

  const handlePageChange = useCallback((newPage: number) => {
    setPage(newPage)
    updateURL({ page: newPage })
  }, [updateURL])

  const formatDate = useCallback((dateStr: string) => {
    try {
      return new Date(dateStr).toLocaleString('zh-TW')
    } catch {
      return dateStr
    }
  }, [])

  const formatAmount = useCallback((amount: number, token: string) => {
    if (amount >= 0) {
      return `+${amount.toLocaleString()} ${token}`
    }
    return `${amount.toLocaleString()} ${token}`
  }, [])

  return (
    <div className="container mx-auto space-y-8 p-6 lg:p-8">
      {/* 返回按钮 */}
      <Link
        href="/"
        className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground"
      >
        <ArrowLeft className="h-4 w-4" />
        返回首页
      </Link>

      <header className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
          审计日志
        </h1>
        <p className="text-muted-foreground sm:max-w-2xl">
          查看系统操作记录，包括余额调整、充值、红包等关键操作
        </p>
      </header>

      {/* 筛选区域 */}
      <Card>
        <CardHeader>
          <CardTitle>筛选条件</CardTitle>
          <CardDescription>按类型、用户、币种等条件筛选日志</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* 搜索框 */}
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                placeholder="搜索备注、订单ID、红包ID..."
                className="w-full rounded-lg border border-input bg-background pl-10 pr-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              />
            </div>
            <button
              onClick={handleSearch}
              className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
            >
              搜索
            </button>
          </div>

          {/* 类型筛选 */}
          <div className="space-y-2">
            <label className="text-sm font-medium">操作类型</label>
            <div className="flex flex-wrap gap-2">
              {TYPE_OPTIONS.map((type) => (
                <button
                  key={type}
                  type="button"
                  onClick={() => handleTypeToggle(type)}
                  className={`rounded-full px-3 py-1 text-xs font-medium transition ${
                    selectedTypes.includes(type)
                      ? 'bg-primary text-primary-foreground'
                      : 'border border-border bg-background hover:bg-accent'
                  }`}
                >
                  {type}
                </button>
              ))}
            </div>
          </div>

          {/* 其他筛选 */}
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <label htmlFor="token" className="text-sm font-medium">
                币种
              </label>
              <input
                id="token"
                type="text"
                value={tokenFilter}
                onChange={(e) => setTokenFilter(e.target.value)}
                placeholder="USDT, TON, POINT..."
                className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              />
            </div>
            <div className="space-y-2">
              <label htmlFor="user" className="text-sm font-medium">
                用户 (ID 或 @username)
              </label>
              <input
                id="user"
                type="text"
                value={userFilter}
                onChange={(e) => setUserFilter(e.target.value)}
                placeholder="123456 或 @username"
                className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 日志列表 */}
      {isLoading && <LoadingSkeleton lines={10} />}
      {error && (
        <ErrorNotice
          message="無法載入審計日誌"
          onRetry={() => refetch()}
        />
      )}

      {!isLoading && !error && data && (
        <>
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>日志列表</CardTitle>
                  <CardDescription>
                    共 {data.pagination.total.toLocaleString()} 条记录
                    {data.sum_amount !== 0 && (
                      <span className="ml-2">
                        · 总金额: {data.sum_amount.toLocaleString()}
                      </span>
                    )}
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {data.items.length === 0 ? (
                <div className="py-12 text-center text-sm text-muted-foreground">
                  没有找到符合条件的日志记录
                </div>
              ) : (
                <>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>时间</TableHead>
                        <TableHead>类型</TableHead>
                        <TableHead>用户</TableHead>
                        <TableHead>币种</TableHead>
                        <TableHead className="text-right">金额</TableHead>
                        <TableHead>备注</TableHead>
                        <TableHead>操作人</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {data.items.map((item) => (
                        <TableRow key={item.id}>
                          <TableCell className="text-sm">
                            {formatDate(item.created_at)}
                          </TableCell>
                          <TableCell>
                            <Badge variant="secondary" className="text-xs">
                              {item.type}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <div className="text-sm">
                              {item.username ? (
                                <span>@{item.username}</span>
                              ) : (
                                <span className="text-muted-foreground">
                                  {item.tg_id || item.user_id || '-'}
                                </span>
                              )}
                            </div>
                          </TableCell>
                          <TableCell className="font-mono text-sm">
                            {item.token || '-'}
                          </TableCell>
                          <TableCell className={`text-right font-medium ${
                            item.amount >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
                          }`}>
                            {formatAmount(item.amount, item.token || '')}
                          </TableCell>
                          <TableCell className="max-w-xs truncate text-sm text-muted-foreground">
                            {item.note || '-'}
                          </TableCell>
                          <TableCell className="text-sm text-muted-foreground">
                            {item.operator_id ? `#${item.operator_id}` : '-'}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>

                  {/* 分页 */}
                  {data.pagination.total_pages > 1 && (
                    <div className="mt-4 flex items-center justify-between">
                      <div className="text-sm text-muted-foreground">
                        第 {data.pagination.page} / {data.pagination.total_pages} 页
                      </div>
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => handlePageChange(page - 1)}
                          disabled={page <= 1}
                          className="inline-flex items-center gap-1 rounded-lg border border-border bg-background px-3 py-2 text-sm font-medium transition-colors hover:bg-accent disabled:opacity-50"
                        >
                          <ChevronLeft className="h-4 w-4" />
                          上一页
                        </button>
                        <button
                          onClick={() => handlePageChange(page + 1)}
                          disabled={page >= data.pagination.total_pages}
                          className="inline-flex items-center gap-1 rounded-lg border border-border bg-background px-3 py-2 text-sm font-medium transition-colors hover:bg-accent disabled:opacity-50"
                        >
                          下一页
                          <ChevronRight className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                  )}
                </>
              )}
            </CardContent>
          </Card>
        </>
      )}
    </div>
  )
}

export default function AuditLogsPage() {
  return (
    <Suspense fallback={<LoadingSkeleton lines={10} />}>
      <AuditLogsPageContent />
    </Suspense>
  )
}

