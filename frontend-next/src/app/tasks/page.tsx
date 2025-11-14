'use client'

import { useState, useCallback, Suspense } from 'react'
import Link from 'next/link'
import { useQuery } from '@tanstack/react-query'
import { useSearchParams, useRouter } from 'next/navigation'

import { getTasks, getTaskDetail, type TaskListParams, type TaskDetail as TaskDetailType } from '@/lib/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import LoadingSkeleton from '@/components/shared/LoadingSkeleton'
import ErrorNotice from '@/components/shared/ErrorNotice'
import { ArrowLeft, Search, ChevronLeft, ChevronRight, Eye, X } from 'lucide-react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'

function TasksPageContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  
  const [page, setPage] = useState(() => parseInt(searchParams.get('page') || '1', 10))
  const [perPage] = useState(20)
  const [searchQuery, setSearchQuery] = useState(searchParams.get('q') || '')
  const [statusFilter, setStatusFilter] = useState<'active' | 'closed' | 'failed' | ''>(() => {
    const status = searchParams.get('status')
    return (status === 'active' || status === 'closed' || status === 'failed') ? status : ''
  })
  const [selectedTaskId, setSelectedTaskId] = useState<number | null>(null)

  const params: TaskListParams = {
    page,
    per_page: perPage,
    q: searchQuery || undefined,
    status: statusFilter || undefined,
  }

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['tasks', params],
    queryFn: () => getTasks(params),
    refetchInterval: 30000, // 每30秒自动刷新
  })

  const { data: taskDetail, isLoading: detailLoading } = useQuery({
    queryKey: ['task-detail', selectedTaskId],
    queryFn: () => getTaskDetail(selectedTaskId!),
    enabled: selectedTaskId !== null,
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
    router.push(`/tasks?${current.toString()}`)
  }, [router, searchParams])

  const handleSearch = useCallback(() => {
    updateURL({ q: searchQuery, page: 1 })
    setPage(1)
  }, [searchQuery, updateURL])

  const handlePageChange = useCallback((newPage: number) => {
    setPage(newPage)
    updateURL({ page: newPage })
  }, [updateURL])

  const handleStatusFilter = useCallback((status: 'active' | 'closed' | 'failed' | '') => {
    setStatusFilter(status)
    updateURL({ status: status || '', page: 1 })
    setPage(1)
  }, [updateURL])

  const formatDate = useCallback((dateStr: string | null) => {
    if (!dateStr) return '-'
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
          红包任务列表
        </h1>
        <p className="text-muted-foreground sm:max-w-2xl">
          查看和管理所有红包发送任务，支持搜索、筛选和查看详情
        </p>
      </header>

      {/* 搜索和筛选 */}
      <Card>
        <CardHeader>
          <CardTitle>搜索与筛选</CardTitle>
          <CardDescription>按任务ID、群组名称或状态筛选任务</CardDescription>
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
                placeholder="搜索任务ID或群组名称..."
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
            {(['active', 'closed', 'failed'] as const).map((status) => (
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
                {status === 'active' ? '进行中' : status === 'closed' ? '成功' : '失败'}
              </button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* 任务列表 */}
      {isLoading && <LoadingSkeleton lines={10} />}
      {error && (
        <ErrorNotice
          message="無法載入任務列表"
          onRetry={() => refetch()}
        />
      )}

      {!isLoading && !error && data && (
        <>
          {data.items.length === 0 ? (
            <Card>
              <CardContent className="py-12 text-center text-sm text-muted-foreground">
                没有找到符合条件的任务
              </CardContent>
            </Card>
          ) : (
            <>
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle>任务列表</CardTitle>
                      <CardDescription>
                        共 {data.pagination.total.toLocaleString()} 个任务
                      </CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>任务 ID</TableHead>
                        <TableHead>类型</TableHead>
                        <TableHead>群组名称</TableHead>
                        <TableHead>金额</TableHead>
                        <TableHead>数量</TableHead>
                        <TableHead>状态</TableHead>
                        <TableHead>创建时间</TableHead>
                        <TableHead>操作</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {data.items.map((task) => (
                        <TableRow key={task.id}>
                          <TableCell className="font-medium">{task.id}</TableCell>
                          <TableCell>{task.type}</TableCell>
                          <TableCell>{task.group_name}</TableCell>
                          <TableCell>¥{task.amount.toFixed(2)}</TableCell>
                          <TableCell>{task.count}</TableCell>
                          <TableCell>
                            <Badge
                              variant={
                                task.status === '成功'
                                  ? 'default'
                                  : task.status === '进行中'
                                    ? 'secondary'
                                    : 'destructive'
                              }
                              className="text-xs"
                            >
                              {task.status}
                            </Badge>
                          </TableCell>
                          <TableCell className="text-sm">
                            {formatDate(task.created_at)}
                          </TableCell>
                          <TableCell>
                            <button
                              onClick={() => setSelectedTaskId(task.id)}
                              className="inline-flex items-center gap-1 rounded-lg border border-border bg-background px-2 py-1 text-xs font-medium transition-colors hover:bg-accent"
                            >
                              <Eye className="h-3 w-3" />
                              详情
                            </button>
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

      {/* 任务详情对话框 */}
      <Dialog open={selectedTaskId !== null} onOpenChange={(open) => !open && setSelectedTaskId(null)}>
        <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>任务详情 #{selectedTaskId}</DialogTitle>
            <DialogDescription>查看任务的完整信息和领取明细</DialogDescription>
          </DialogHeader>
          {detailLoading ? (
            <LoadingSkeleton lines={5} />
          ) : taskDetail ? (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">总金额</p>
                  <p className="text-lg font-semibold">¥{taskDetail.total_amount.toFixed(2)}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">总数量</p>
                  <p className="text-lg font-semibold">{taskDetail.total_count}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">已领取金额</p>
                  <p className="text-lg font-semibold">¥{taskDetail.claimed_amount.toFixed(2)}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">已领取数量</p>
                  <p className="text-lg font-semibold">{taskDetail.claimed_count}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">剩余金额</p>
                  <p className="text-lg font-semibold">¥{taskDetail.remain_amount.toFixed(2)}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">剩余数量</p>
                  <p className="text-lg font-semibold">{taskDetail.remain_count}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">创建时间</p>
                  <p className="text-sm">{formatDate(taskDetail.created_at)}</p>
                </div>
                {taskDetail.closed_at && (
                  <div>
                    <p className="text-sm text-muted-foreground">关闭时间</p>
                    <p className="text-sm">{formatDate(taskDetail.closed_at)}</p>
                  </div>
                )}
              </div>

              {taskDetail.creator && (
                <div>
                  <p className="text-sm text-muted-foreground">创建者</p>
                  <p className="text-sm">
                    {taskDetail.creator.username || `TG ID: ${taskDetail.creator.tg_id}`}
                  </p>
                </div>
              )}

              {taskDetail.lucky && (
                <div className="rounded-lg border bg-muted/50 p-4">
                  <p className="text-sm text-muted-foreground mb-1">幸运王</p>
                  <p className="text-lg font-semibold">
                    {taskDetail.lucky.username || `TG ID: ${taskDetail.lucky.tg_id}`}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    领取金额: ¥{taskDetail.lucky.amount.toFixed(2)}
                  </p>
                </div>
              )}

              {taskDetail.claims.length > 0 && (
                <div>
                  <p className="text-sm font-medium mb-2">领取明细（共 {taskDetail.total_claims} 条）</p>
                  <div className="max-h-64 overflow-y-auto">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>用户</TableHead>
                          <TableHead>金额</TableHead>
                          <TableHead>时间</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {taskDetail.claims.map((claim, idx) => (
                          <TableRow key={idx}>
                            <TableCell>
                              {claim.username || `TG ID: ${claim.user_id}`}
                            </TableCell>
                            <TableCell>¥{claim.amount.toFixed(2)}</TableCell>
                            <TableCell className="text-sm">
                              {formatDate(claim.created_at)}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <ErrorNotice message="無法載入任務詳情" />
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}

export default function TasksPage() {
  return (
    <Suspense fallback={<LoadingSkeleton lines={10} />}>
      <TasksPageContent />
    </Suspense>
  )
}

