import { useMemo, type ReactElement } from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'

import { fetchHealth } from '../api/health'
import { useAuth } from '../providers/AuthProvider'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Badge } from '../components/ui/badge'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs'
import LoadingSkeleton from '../components/LoadingSkeleton'
import ErrorNotice from '../components/ErrorNotice'
import {
  TrendingUp,
  TrendingDown,
  Users,
  MessageSquare,
  AlertCircle,
  CheckCircle2,
  Clock,
  Activity,
  Settings,
  List,
} from 'lucide-react'

// 今日数据统计
const todayStats = [
  {
    label: '今日新增群',
    value: '12',
    change: '+8.3%',
    trend: 'up',
    icon: Users,
    color: 'text-blue-600 dark:text-blue-400',
  },
  {
    label: '今日群聊次数',
    value: '1,234',
    change: '+15.2%',
    trend: 'up',
    icon: MessageSquare,
    color: 'text-green-600 dark:text-green-400',
  },
  {
    label: '活跃用户',
    value: '8,542',
    change: '+12.5%',
    trend: 'up',
    icon: Activity,
    color: 'text-purple-600 dark:text-purple-400',
  },
  {
    label: '失败次数',
    value: '45',
    change: '-5.1%',
    trend: 'down',
    icon: AlertCircle,
    color: 'text-red-600 dark:text-red-400',
  },
]

// 任务执行日志（虚拟数据）
const taskLogs = [
  {
    id: 'T001',
    task: '群发红包',
    status: 'success',
    group: '测试群组 A',
    amount: '¥500',
    time: '14:32:15',
  },
  {
    id: 'T002',
    task: '定时红包',
    status: 'pending',
    group: '测试群组 B',
    amount: '¥200',
    time: '14:28:42',
  },
  {
    id: 'T003',
    task: '个人红包',
    status: 'success',
    group: '测试群组 C',
    amount: '¥100',
    time: '14:25:10',
  },
  {
    id: 'T004',
    task: '群发红包',
    status: 'failed',
    group: '测试群组 D',
    amount: '¥300',
    time: '14:20:33',
  },
  {
    id: 'T005',
    task: '定时红包',
    status: 'success',
    group: '测试群组 E',
    amount: '¥150',
    time: '14:15:08',
  },
]

// 群动态时间线（虚拟数据）
const groupTimeline = [
  {
    id: '1',
    group: '测试群组 A',
    action: '新成员加入',
    user: '用户123',
    time: '2 分钟前',
    type: 'join',
  },
  {
    id: '2',
    group: '测试群组 B',
    action: '发送红包',
    user: '用户456',
    time: '5 分钟前',
    type: 'redpack',
  },
  {
    id: '3',
    group: '测试群组 C',
    action: '消息发送',
    user: '用户789',
    time: '10 分钟前',
    type: 'message',
  },
  {
    id: '4',
    group: '测试群组 D',
    action: '成员离开',
    user: '用户012',
    time: '15 分钟前',
    type: 'leave',
  },
  {
    id: '5',
    group: '测试群组 E',
    action: '红包领取',
    user: '用户345',
    time: '20 分钟前',
    type: 'claim',
  },
]

export default function Dashboard(): ReactElement {
  const auth = useAuth()

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['healthz'],
    queryFn: fetchHealth,
    enabled: auth.status === 'authenticated',
  })

  const status = useMemo(() => {
    if (auth.status === 'loading') return '登入中，請稍候...'
    if (auth.status === 'error') return auth.error ?? '登入失敗'
    if (isLoading) return '檢查服務狀態中...'
    if (error) return '服務異常，請稍後再試'
    if (data?.ok) return '後端服務運行正常'
    return '無法取得健康檢查結果'
  }, [auth.status, auth.error, isLoading, error, data])

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
            to="/groups"
            className="inline-flex items-center gap-2 rounded-lg border border-border bg-background px-4 py-2 text-sm font-medium transition-colors hover:bg-accent"
          >
            <List className="h-4 w-4" />
            群组列表
          </Link>
          <Link
            to="/settings"
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
                void refetch()
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

      {/* 今日数据统计卡片 */}
      <section className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {todayStats.map((stat) => {
          const Icon = stat.icon
          const isPositive = stat.trend === 'up'
          return (
            <Card key={stat.label} className="transition-all duration-200 hover:shadow-lg">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {stat.label}
                </CardTitle>
                <Icon className={`h-5 w-5 ${stat.color}`} />
              </CardHeader>
              <CardContent>
                <div className="flex items-baseline justify-between">
                  <p className="text-2xl font-bold">{stat.value}</p>
                  <Badge
                    variant={isPositive ? 'default' : 'secondary'}
                    className={`gap-1 text-xs font-medium ${
                      isPositive
                        ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                        : 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400'
                    }`}
                  >
                    {isPositive ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                    {stat.change}
                  </Badge>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </section>

      {/* 主要内容区：任务日志和群动态 */}
      <section className="grid gap-6 lg:grid-cols-[2fr_1fr]">
        {/* 任务执行日志 */}
        <Card>
          <CardHeader>
            <CardTitle>任务执行日志</CardTitle>
            <CardDescription>查看最近的红包发送任务执行情况</CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="all" className="space-y-4">
              <TabsList className="w-full justify-start bg-muted/60">
                <TabsTrigger value="all">全部</TabsTrigger>
                <TabsTrigger value="success">成功</TabsTrigger>
                <TabsTrigger value="pending">进行中</TabsTrigger>
                <TabsTrigger value="failed">失败</TabsTrigger>
              </TabsList>
              <TabsContent value="all" className="space-y-0">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>任务ID</TableHead>
                      <TableHead>任务类型</TableHead>
                      <TableHead>群组</TableHead>
                      <TableHead>金额</TableHead>
                      <TableHead>状态</TableHead>
                      <TableHead className="text-right">时间</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {taskLogs.map((log) => (
                      <TableRow key={log.id}>
                        <TableCell className="font-mono text-sm">{log.id}</TableCell>
                        <TableCell>{log.task}</TableCell>
                        <TableCell>{log.group}</TableCell>
                        <TableCell className="font-semibold text-red-600 dark:text-red-400">
                          {log.amount}
                        </TableCell>
                        <TableCell>
                          <Badge
                            variant={
                              log.status === 'success'
                                ? 'default'
                                : log.status === 'pending'
                                  ? 'secondary'
                                  : 'destructive'
                            }
                            className={
                              log.status === 'success'
                                ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                                : log.status === 'pending'
                                  ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400'
                                  : ''
                            }
                          >
                            {log.status === 'success' ? (
                              <CheckCircle2 className="mr-1 h-3 w-3" />
                            ) : log.status === 'pending' ? (
                              <Clock className="mr-1 h-3 w-3" />
                            ) : (
                              <AlertCircle className="mr-1 h-3 w-3" />
                            )}
                            {log.status === 'success' ? '成功' : log.status === 'pending' ? '进行中' : '失败'}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-right text-sm text-muted-foreground">
                          {log.time}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TabsContent>
              <TabsContent value="success">
                <div className="py-8 text-center text-sm text-muted-foreground">
                  显示成功的任务...
                </div>
              </TabsContent>
              <TabsContent value="pending">
                <div className="py-8 text-center text-sm text-muted-foreground">
                  显示进行中的任务...
                </div>
              </TabsContent>
              <TabsContent value="failed">
                <div className="py-8 text-center text-sm text-muted-foreground">
                  显示失败的任务...
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>

        {/* 群动态时间线 */}
        <Card>
          <CardHeader>
            <CardTitle>群动态时间线</CardTitle>
            <CardDescription>实时查看群组最新动态</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {groupTimeline.map((item) => (
              <div
                key={item.id}
                className="flex items-start gap-3 rounded-lg border border-border/60 bg-card p-3 text-sm transition hover:border-primary/40 hover:shadow-sm"
              >
                <div
                  className={`mt-0.5 flex h-8 w-8 items-center justify-center rounded-full ${
                    item.type === 'join'
                      ? 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400'
                      : item.type === 'redpack'
                        ? 'bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400'
                        : item.type === 'claim'
                          ? 'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400'
                          : 'bg-gray-100 text-gray-600 dark:bg-gray-900/30 dark:text-gray-400'
                  }`}
                >
                  {item.type === 'join' ? (
                    <Users className="h-4 w-4" />
                  ) : item.type === 'redpack' ? (
                    <Activity className="h-4 w-4" />
                  ) : item.type === 'claim' ? (
                    <CheckCircle2 className="h-4 w-4" />
                  ) : (
                    <MessageSquare className="h-4 w-4" />
                  )}
                </div>
                <div className="flex-1 space-y-1">
                  <p className="font-medium text-foreground">{item.group}</p>
                  <p className="text-muted-foreground">
                    {item.action} · {item.user}
                  </p>
                  <p className="text-xs text-muted-foreground">{item.time}</p>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </section>
    </div>
  )
}

