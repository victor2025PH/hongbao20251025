'use client'

import { useState, useCallback } from 'react'
import Link from 'next/link'
import { useQuery } from '@tanstack/react-query'
import { useSearchParams, useRouter } from 'next/navigation'

import { getLogs, type LogListParams } from '@/lib/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import LoadingSkeleton from '@/components/shared/LoadingSkeleton'
import ErrorNotice from '@/components/shared/ErrorNotice'
import { ArrowLeft, Search, ChevronLeft, ChevronRight, FileSearch } from 'lucide-react'

export default function LogsPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  
  const [page, setPage] = useState(() => parseInt(searchParams.get('page') || '1', 10))
  const [perPage] = useState(50)
  const [searchQuery, setSearchQuery] = useState(searchParams.get('q') || '')
  const [levelFilter, setLevelFilter] = useState<'info' | 'warn' | 'error' | ''>(() => {
    const level = searchParams.get('level')
    return (level === 'info' || level === 'warn' || level === 'error') ? level : ''
  })

  const params: LogListParams = {
    page,
    per_page: perPage,
    q: searchQuery || undefined,
    level: levelFilter || undefined,
  }

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['logs', params],
    queryFn: () => getLogs(params),
    refetchInterval: 30000, // 每30秒自动刷新
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
    router.push(`/logs?${current.toString()}`)
  }, [router, searchParams])

  const handleSearch = useCallback(() => {
    updateURL({ q: searchQuery, page: 1 })
    setPage(1)
  }, [searchQuery, updateURL])

  const handlePageChange = useCallback((newPage: number) => {
    setPage(newPage)
    updateURL({ page: newPage })
  }, [updateURL])

  const handleLevelFilter = useCallback((level: 'info' | 'warn' | 'error' | '') => {
    setLevelFilter(level)
    updateURL({ level: level || '', page: 1 })
    setPage(1)
  }, [updateURL])

  const formatDate = useCallback((dateStr: string) => {
    try {
      return new Date(dateStr).toLocaleString('zh-CN')
    } catch {
      return dateStr
    }
  }, [])

  return (
    <div className="container mx-auto space-y-8 p-6 lg:p-8">
      <Link
        href="/"
        className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground"
      >
        <ArrowLeft className="h-4 w-4" />
        返回首页
      </Link>

      <header className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
          日志中心
        </h1>
        <p className="text-muted-foreground sm:max-w-2xl">
          查看系统各类日志记录，包括信息、警告和错误日志
        </p>
      </header>

      {/* 筛选区域 */}
      <Card>
        <CardHeader>
          <CardTitle>筛选条件</CardTitle>
          <CardDescription>按级别、关键词等条件筛选日志</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                placeholder="搜索日志消息..."
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

          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => handleLevelFilter('')}
              className={`rounded-full px-3 py-1 text-xs font-medium transition ${
                !levelFilter
                  ? 'bg-primary text-primary-foreground'
                  : 'border border-border bg-background hover:bg-accent'
              }`}
            >
              全部
            </button>
            {(['info', 'warn', 'error'] as const).map((level) => (
              <button
                key={level}
                type="button"
                onClick={() => handleLevelFilter(level)}
                className={`rounded-full px-3 py-1 text-xs font-medium transition ${
                  levelFilter === level
                    ? 'bg-primary text-primary-foreground'
                    : 'border border-border bg-background hover:bg-accent'
                }`}
              >
                {level === 'info' ? '信息' : level === 'warn' ? '警告' : '错误'}
              </button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* 日志列表 */}
      {isLoading && <LoadingSkeleton lines={10} />}
      {error && (
        <ErrorNotice
          message="無法載入日誌"
          onRetry={() => refetch()}
        />
      )}

      {!isLoading && !error && data && (
        <>
          {data.items.length === 0 ? (
            <Card>
              <CardContent className="py-12 text-center text-sm text-muted-foreground">
                没有找到符合条件的日志
              </CardContent>
            </Card>
          ) : (
            <>
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle>日志列表</CardTitle>
                      <CardDescription>
                        共 {data.pagination.total.toLocaleString()} 条记录
                      </CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>时间</TableHead>
                        <TableHead>级别</TableHead>
                        <TableHead>模块</TableHead>
                        <TableHead>消息</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {data.items.map((log) => (
                        <TableRow key={log.id}>
                          <TableCell className="text-sm">
                            {formatDate(log.timestamp)}
                          </TableCell>
                          <TableCell>
                            <Badge
                              variant={
                                log.level === 'error'
                                  ? 'destructive'
                                  : log.level === 'warn'
                                    ? 'secondary'
                                    : 'default'
                              }
                              className="text-xs"
                            >
                              {log.level === 'info' ? '信息' : log.level === 'warn' ? '警告' : '错误'}
                            </Badge>
                          </TableCell>
                          <TableCell className="font-mono text-sm">
                            {log.module}
                          </TableCell>
                          <TableCell className="max-w-md">
                            <p className="text-sm">{log.message}</p>
                            {log.extra && Object.keys(log.extra).length > 0 && (
                              <p className="text-xs text-muted-foreground mt-1">
                                {JSON.stringify(log.extra)}
                              </p>
                            )}
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
                </CardContent>
              </Card>
            </>
          )}
        </>
      )}

      {/* 快速链接 */}
      <Card>
        <CardHeader>
          <CardTitle>相关功能</CardTitle>
          <CardDescription>其他日志和审计功能</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 sm:grid-cols-2">
            <Link
              href="/logs/audit"
              className="flex items-center gap-3 rounded-lg border border-border bg-background p-4 transition-colors hover:bg-accent"
            >
              <FileSearch className="h-5 w-5 text-primary" />
              <div>
                <p className="font-medium">审计日志</p>
                <p className="text-xs text-muted-foreground">查看系统操作记录</p>
              </div>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
