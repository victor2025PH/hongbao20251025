'use client'

import { useMemo } from 'react'
import Link from 'next/link'
import { useQuery } from '@tanstack/react-query'

import { fetchHealth } from '@/api/health'
import { useAuth } from '@/providers/AuthProvider'
import { getDashboard, type DashboardData } from '@/lib/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import LoadingSkeleton from '@/components/shared/LoadingSkeleton'
import ErrorNotice from '@/components/shared/ErrorNotice'
import {
  Users,
  Package,
  DollarSign,
  FileText,
  CreditCard,
  CheckCircle2,
  Settings,
  List,
  FileSearch,
} from 'lucide-react'

export default function Home() {
  const auth = useAuth()

  const { data: healthData, isLoading: healthLoading, error: healthError, refetch: refetchHealth } = useQuery({
    queryKey: ['healthz'],
    queryFn: fetchHealth,
    enabled: true, // 健康检查不需要认证
    retry: 1,
  })

  const { data: dashboardData, isLoading: dashboardLoading, error: dashboardError, refetch: refetchDashboard } = useQuery<DashboardData>({
    queryKey: ['dashboard'],
    queryFn: getDashboard,
    refetchInterval: 30000, // 每30秒自动刷新
    retry: 1, // 只重试一次
  })

  const statsData = dashboardData?.stats

  const status = useMemo(() => {
    if (auth.status === 'loading') return '登入中，請稍候...'
    if (auth.status === 'error') return auth.error ?? '登入失敗'
    if (healthLoading) return '檢查服務狀態中...'
    if (healthError) return '服務異常，請稍後再試'
    if (healthData?.ok) return '後端服務運行正常'
    return '無法取得健康檢查結果'
  }, [auth.status, auth.error, healthLoading, healthError, healthData])

  // 统计卡片配置
  const statsCards = useMemo(() => {
    if (!statsData) return []
    
    return [
      {
        label: '用户总数',
        value: statsData.user_count.toLocaleString(),
        icon: Users,
        color: 'text-blue-600 dark:text-blue-400',
        description: '系统注册用户总数',
      },
      {
        label: '活跃红包数',
        value: statsData.active_envelopes.toLocaleString(),
        icon: Package,
        color: 'text-green-600 dark:text-green-400',
        description: '当前进行中的红包',
      },
      {
        label: '近7天账本金额',
        value: `¥${statsData.last_7d_amount}`,
        icon: DollarSign,
        color: 'text-purple-600 dark:text-purple-400',
        description: '近7天账本流水总额',
      },
      {
        label: '近7天账本条数',
        value: statsData.last_7d_orders.toLocaleString(),
        icon: FileText,
        color: 'text-orange-600 dark:text-orange-400',
        description: '近7天账本记录数',
      },
      {
        label: '充值待处理',
        value: statsData.pending_recharges.toLocaleString(),
        icon: CreditCard,
        color: 'text-amber-600 dark:text-amber-400',
        description: '待处理的充值订单',
      },
      {
        label: '充值成功',
        value: statsData.success_recharges.toLocaleString(),
        icon: CheckCircle2,
        color: 'text-green-600 dark:text-green-400',
        description: '已成功完成的充值',
      },
    ]
  }, [statsData])

  return (
    <div className="container mx-auto space-y-8 p-6 lg:p-8">
      {/* 顶部标题栏 */}
      <header className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="space-y-2">
          <h1 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
            红包系统控制台
          </h1>
          <p className="text-muted-foreground sm:max-w-2xl">
            实时监控红包发送状态、用户活跃度与系统运行情况
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            href="/groups"
            className="inline-flex items-center gap-2 rounded-lg border border-border bg-background px-4 py-2 text-sm font-medium transition-colors hover:bg-accent"
          >
            <List className="h-4 w-4" />
            群组列表
          </Link>
          <Link
            href="/logs/audit"
            className="inline-flex items-center gap-2 rounded-lg border border-border bg-background px-4 py-2 text-sm font-medium transition-colors hover:bg-accent"
          >
            <FileSearch className="h-4 w-4" />
            审计日志
          </Link>
          <Link
            href="/settings"
            className="inline-flex items-center gap-2 rounded-lg border border-border bg-background px-4 py-2 text-sm font-medium transition-colors hover:bg-accent"
          >
            <Settings className="h-4 w-4" />
            设置
          </Link>
          <button
            type="button"
            onClick={() => {
              if (auth.status === 'error') {
                void auth.refresh()
              } else {
                void refetchHealth()
                void refetchDashboard()
              }
            }}
            className="rounded-lg border border-border bg-background px-4 py-2 text-sm font-medium transition-colors hover:bg-accent"
          >
            {auth.status === 'error' ? '重新登入' : '刷新数据'}
          </button>
        </div>
      </header>

      {/* 服务健康状态 */}
      <Card>
        <CardHeader>
          <CardTitle>服務健康狀態</CardTitle>
          <CardDescription>與 FastAPI 後端的基礎連線檢查</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="rounded-lg border bg-muted/50 p-4 text-lg font-medium">
            {status}
          </div>
        </CardContent>
      </Card>

      {/* 统计数据卡片 */}
      {dashboardLoading && (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Card key={i}>
              <CardHeader>
                <LoadingSkeleton lines={2} />
              </CardHeader>
            </Card>
          ))}
        </div>
      )}

      {/* 注意：由于 getDashboard 已经实现了 fallback 到 mock 数据，这里通常不会显示错误 */}
      {dashboardError && !statsData && (
        <Card className="border-destructive">
          <CardContent className="pt-6">
            <ErrorNotice
              message={
                dashboardError instanceof Error
                  ? `無法載入統計數據: ${dashboardError.message}`
                  : '無法載入統計數據，請檢查后端服务是否正常运行'
              }
              onRetry={() => refetchDashboard()}
            />
            <p className="mt-4 text-xs text-muted-foreground">
              提示：如果后端需要认证，请先访问{' '}
              <a
                href="http://localhost:8000/admin/login"
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:underline"
              >
                http://localhost:8000/admin/login
              </a>{' '}
              登录后再刷新此页面
            </p>
            <p className="mt-2 text-xs text-muted-foreground">
              当前显示的是模拟数据，实际数据将在后端服务正常后自动更新
            </p>
          </CardContent>
        </Card>
      )}

      {!dashboardLoading && !dashboardError && statsCards.length > 0 && (
        <>
            {dashboardData?.isMock && (
            <Card className="border-amber-300 bg-amber-50 dark:border-amber-700 dark:bg-amber-950/20">
              <CardContent className="pt-6">
                <p className="text-sm text-amber-800 dark:text-amber-200">
                  ⚠️ 当前展示的是模拟统计数据。请确保后端服务正常运行并已登录。
                </p>
              </CardContent>
            </Card>
          )}
          <section className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {statsCards.map((stat) => {
              const Icon = stat.icon
              return (
                <Card key={stat.label} className="transition-all duration-200 hover:shadow-lg">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">
                      {stat.label}
                    </CardTitle>
                    <Icon className={`h-5 w-5 ${stat.color}`} />
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold">{stat.value}</p>
                    <p className="text-xs text-muted-foreground mt-1">{stat.description}</p>
                  </CardContent>
                </Card>
              )
            })}
          </section>
        </>
      )}

      {/* 趋势图 */}
      {dashboardData?.trends && dashboardData.trends.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>数据趋势</CardTitle>
            <CardDescription>近7天数据变化趋势</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64 flex items-end justify-between gap-2">
              {dashboardData.trends.map((trend, index) => {
                const maxAmount = Math.max(...dashboardData.trends!.map(t => t.amount))
                const height = (trend.amount / maxAmount) * 100
                return (
                  <div key={trend.date} className="flex-1 flex flex-col items-center gap-2">
                    <div className="w-full flex flex-col items-center gap-1">
                      <div
                        className="w-full bg-primary rounded-t transition-all hover:opacity-80"
                        style={{ height: `${height}%`, minHeight: '4px' }}
                        title={`金额: ¥${trend.amount.toLocaleString()}`}
                      />
                    </div>
                    <div className="text-xs text-muted-foreground text-center">
                      {new Date(trend.date).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })}
                    </div>
                    <div className="text-xs font-medium">{trend.amount.toLocaleString()}</div>
                  </div>
                )
              })}
            </div>
            <div className="mt-4 grid grid-cols-3 gap-4 text-sm">
              <div>
                <p className="text-muted-foreground">平均用户数</p>
                <p className="text-lg font-semibold">
                  {Math.round(dashboardData.trends.reduce((sum, t) => sum + t.users, 0) / dashboardData.trends.length).toLocaleString()}
                </p>
              </div>
              <div>
                <p className="text-muted-foreground">平均红包数</p>
                <p className="text-lg font-semibold">
                  {Math.round(dashboardData.trends.reduce((sum, t) => sum + t.envelopes, 0) / dashboardData.trends.length).toLocaleString()}
                </p>
              </div>
              <div>
                <p className="text-muted-foreground">平均金额</p>
                <p className="text-lg font-semibold">
                  ¥{Math.round(dashboardData.trends.reduce((sum, t) => sum + t.amount, 0) / dashboardData.trends.length).toLocaleString()}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* 最近任务列表 */}
      {dashboardData?.recent_tasks && dashboardData.recent_tasks.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>最近任务</CardTitle>
            <CardDescription>最近的红包发送与系统任务记录</CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>任务 ID</TableHead>
                  <TableHead>任务类型</TableHead>
                  <TableHead>群组</TableHead>
                  <TableHead>金额</TableHead>
                  <TableHead>状态</TableHead>
                  <TableHead>时间</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {dashboardData.recent_tasks.map((task) => (
                  <TableRow key={task.id}>
                    <TableCell className="font-medium">{task.id}</TableCell>
                    <TableCell>{task.task}</TableCell>
                    <TableCell>{task.group}</TableCell>
                    <TableCell>{task.amount}</TableCell>
                    <TableCell>
                      <Badge
                        variant={
                          task.status === 'success'
                            ? 'default'
                            : task.status === 'pending'
                              ? 'secondary'
                              : 'destructive'
                        }
                      >
                        {task.status === 'success'
                          ? '成功'
                          : task.status === 'pending'
                            ? '进行中'
                            : '失败'}
                      </Badge>
                    </TableCell>
                    <TableCell>{task.time}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}

      {/* 快速链接 */}
      <Card>
        <CardHeader>
          <CardTitle>快速操作</CardTitle>
          <CardDescription>常用功能入口</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <Link
              href="/groups"
              className="flex items-center gap-3 rounded-lg border border-border bg-background p-4 transition-colors hover:bg-accent"
            >
              <List className="h-5 w-5 text-primary" />
              <div>
                <p className="font-medium">群组管理</p>
                <p className="text-xs text-muted-foreground">查看和管理公开群组</p>
              </div>
            </Link>
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
            <Link
              href="/settings"
              className="flex items-center gap-3 rounded-lg border border-border bg-background p-4 transition-colors hover:bg-accent"
            >
              <Settings className="h-5 w-5 text-primary" />
              <div>
                <p className="font-medium">系统设置</p>
                <p className="text-xs text-muted-foreground">配置系统参数</p>
              </div>
            </Link>
            <a
              href="http://localhost:8000/admin/dashboard"
            target="_blank"
            rel="noopener noreferrer"
              className="flex items-center gap-3 rounded-lg border border-border bg-background p-4 transition-colors hover:bg-accent"
            >
              <FileText className="h-5 w-5 text-primary" />
              <div>
                <p className="font-medium">旧版后台</p>
                <p className="text-xs text-muted-foreground">访问传统管理界面</p>
              </div>
            </a>
            <Link
              href="/tasks"
              className="flex items-center gap-3 rounded-lg border border-border bg-background p-4 transition-colors hover:bg-accent"
            >
              <List className="h-5 w-5 text-primary" />
              <div>
                <p className="font-medium">任务列表</p>
                <p className="text-xs text-muted-foreground">查看红包发送任务</p>
              </div>
            </Link>
        </div>
        </CardContent>
      </Card>
    </div>
  )
}
