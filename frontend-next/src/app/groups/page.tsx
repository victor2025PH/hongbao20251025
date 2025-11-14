'use client'

import { useState, useCallback, Suspense } from 'react'
import Link from 'next/link'
import { useQuery } from '@tanstack/react-query'
import { useSearchParams, useRouter } from 'next/navigation'

import { getGroupList, type GroupListParams } from '@/lib/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import LoadingSkeleton from '@/components/shared/LoadingSkeleton'
import ErrorNotice from '@/components/shared/ErrorNotice'
import { ArrowLeft, Search, ChevronLeft, ChevronRight, ExternalLink } from 'lucide-react'

function GroupsPageContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  
  const [page, setPage] = useState(() => parseInt(searchParams.get('page') || '1', 10))
  const [perPage] = useState(20)
  const [searchQuery, setSearchQuery] = useState(searchParams.get('q') || '')
  const [statusFilter, setStatusFilter] = useState(searchParams.get('status') || '')

  const params: GroupListParams = {
    page,
    per_page: perPage,
    q: searchQuery || undefined,
    status: statusFilter || undefined,
  }

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['group-list', params],
    queryFn: () => getGroupList(params),
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
    router.push(`/groups?${current.toString()}`)
  }, [router, searchParams])

  const handleSearch = useCallback(() => {
    updateURL({ q: searchQuery, page: 1 })
    setPage(1)
  }, [searchQuery, updateURL])

  const handlePageChange = useCallback((newPage: number) => {
    setPage(newPage)
    updateURL({ page: newPage })
  }, [updateURL])

  const handleStatusFilter = useCallback((status: string) => {
    setStatusFilter(status)
    updateURL({ status, page: 1 })
    setPage(1)
  }, [updateURL])

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
          群组列表
        </h1>
        <p className="text-muted-foreground sm:max-w-2xl">
          浏览和管理所有公开群组，支持搜索、筛选和分页
        </p>
      </header>

      {/* 搜索和筛选 */}
      <Card>
        <CardHeader>
          <CardTitle>搜索与筛选</CardTitle>
          <CardDescription>使用关键词搜索或状态筛选群组</CardDescription>
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
                placeholder="搜索群组名称或描述..."
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
              onClick={() => handleStatusFilter('')}
              className={`rounded-full px-3 py-1 text-xs font-medium transition ${
                !statusFilter
                  ? 'bg-primary text-primary-foreground'
                  : 'border border-border bg-background hover:bg-accent'
              }`}
            >
              全部
            </button>
            {['active', 'paused', 'review', 'removed'].map((status) => (
              <button
                key={status}
                type="button"
                onClick={() => handleStatusFilter(status)}
                className={`rounded-full px-3 py-1 text-xs font-medium transition ${
                  statusFilter === status
                    ? 'bg-primary text-primary-foreground'
                    : 'border border-border bg-background hover:bg-accent'
                }`}
              >
                {status === 'active' ? '活跃' : status === 'paused' ? '暂停' : status === 'review' ? '审核中' : '已移除'}
              </button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* 群组列表 */}
      {isLoading && <LoadingSkeleton lines={10} />}
      {error && (
        <ErrorNotice
          message="無法載入群組列表"
          onRetry={() => refetch()}
        />
      )}

      {!isLoading && !error && data && (
        <>
          {data.items.length === 0 ? (
            <Card>
              <CardContent className="py-12 text-center text-sm text-muted-foreground">
                没有找到符合条件的群组
              </CardContent>
            </Card>
          ) : (
            <>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {data.items.map((group) => (
                  <Card key={group.id} className="transition-all duration-200 hover:shadow-lg">
                    <CardHeader>
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex-1">
                          <CardTitle className="text-lg">{group.name}</CardTitle>
                          {group.language && (
                            <p className="mt-1 text-xs uppercase tracking-wide text-muted-foreground">
                              {group.language}
                            </p>
                          )}
                        </div>
                        <Badge
                          variant={
                            group.status === 'active'
                              ? 'default'
                              : group.status === 'paused'
                                ? 'secondary'
                                : group.status === 'review'
                                  ? 'outline'
                                  : 'destructive'
                          }
                          className="text-xs"
                        >
                          {group.status === 'active'
                            ? '活跃'
                            : group.status === 'paused'
                              ? '暂停'
                              : group.status === 'review'
                                ? '审核中'
                                : '已移除'}
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      {group.description && (
                        <p className="text-sm text-muted-foreground line-clamp-2">{group.description}</p>
                      )}

                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          {group.entry_reward_enabled && (
                            <Badge variant="outline" className="border-red-300 text-red-700 dark:text-red-400">
                              +{group.entry_reward_points} 星
                            </Badge>
                          )}
                          <span className="text-xs text-muted-foreground">
                            成員 {group.members_count.toLocaleString()}
                          </span>
                        </div>
                        <a
                          href={group.invite_link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1 rounded-lg border border-border bg-background px-3 py-1.5 text-xs font-medium transition-colors hover:bg-accent"
                        >
                          <ExternalLink className="h-3 w-3" />
                          加入
                        </a>
                      </div>

                      {group.tags.length > 0 && (
                        <div className="flex flex-wrap gap-2">
                          {group.tags.slice(0, 4).map((tag) => (
                            <Badge key={tag} variant="secondary" className="text-xs">
                              #{tag}
                            </Badge>
                          ))}
                        </div>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </div>

              {/* 分页 */}
              {data.pagination.total_pages > 1 && (
                <Card>
                  <CardContent className="pt-6">
                    <div className="flex items-center justify-between">
                      <div className="text-sm text-muted-foreground">
                        共 {data.pagination.total.toLocaleString()} 个群组 · 第 {data.pagination.page} / {data.pagination.total_pages} 页
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
                  </CardContent>
                </Card>
              )}
            </>
          )}
        </>
      )}
    </div>
  )
}

export default function GroupsPage() {
  return (
    <Suspense fallback={<LoadingSkeleton lines={10} />}>
      <GroupsPageContent />
    </Suspense>
  )
}
