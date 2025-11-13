'use client'

import { useQuery } from '@tanstack/react-query'
import Link from 'next/link'
import { getRedPacketStats } from '@/lib/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import LoadingSkeleton from '@/components/shared/LoadingSkeleton'
import ErrorNotice from '@/components/shared/ErrorNotice'
import { ArrowLeft, TrendingUp, Package, DollarSign, CheckCircle2, XCircle } from 'lucide-react'

export default function StatsPage() {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['red-packet-stats'],
    queryFn: getRedPacketStats,
    refetchInterval: 30000, // 每30秒自动刷新
  })

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
          红包统计
        </h1>
        <p className="text-muted-foreground sm:max-w-2xl">
          查看红包发送统计、成功率分析和趋势图表
        </p>
      </header>

      {isLoading && <LoadingSkeleton lines={10} />}
      {error && (
        <ErrorNotice
          message="無法載入紅包統計數據"
          onRetry={() => refetch()}
        />
      )}

      {!isLoading && !error && data && (
        <>
          {/* 总体统计卡片 */}
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">总发送数</CardTitle>
                <Package className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{data.total_sent.toLocaleString()}</div>
                <p className="text-xs text-muted-foreground mt-1">累计发送红包数量</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">总金额</CardTitle>
                <DollarSign className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">¥{data.total_amount}</div>
                <p className="text-xs text-muted-foreground mt-1">累计发送红包总金额</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">成功率</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{data.success_rate.toFixed(1)}%</div>
                <p className="text-xs text-muted-foreground mt-1">红包发送成功率</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">平均金额</CardTitle>
                <DollarSign className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">¥{data.avg_amount}</div>
                <p className="text-xs text-muted-foreground mt-1">单个红包平均金额</p>
              </CardContent>
            </Card>
          </div>

          {/* 按类型统计 */}
          <Card>
            <CardHeader>
              <CardTitle>按类型统计</CardTitle>
              <CardDescription>不同红包类型的发送统计</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {data.by_type.map((item) => (
                  <div key={item.type} className="flex items-center justify-between">
                    <div className="flex-1">
                      <p className="font-medium">{item.type}</p>
                      <p className="text-sm text-muted-foreground">
                        发送 {item.count.toLocaleString()} 次 · 总金额 ¥{item.amount}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-semibold">{item.count.toLocaleString()}</p>
                      <p className="text-xs text-muted-foreground">次数</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* 按小时统计 */}
          <Card>
            <CardHeader>
              <CardTitle>24小时发送分布</CardTitle>
              <CardDescription>一天中各时段的红包发送情况</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-64 flex items-end justify-between gap-1">
                {data.by_hour.map((item) => {
                  const maxCount = Math.max(...data.by_hour.map(h => h.count))
                  const height = (item.count / maxCount) * 100
                  return (
                    <div key={item.hour} className="flex-1 flex flex-col items-center gap-1">
                      <div
                        className="w-full bg-primary rounded-t transition-all hover:opacity-80"
                        style={{ height: `${height}%`, minHeight: '4px' }}
                        title={`${item.hour}:00 - ${item.count} 次, ¥${item.amount}`}
                      />
                      <div className="text-xs text-muted-foreground">{item.hour}</div>
                    </div>
                  )
                })}
              </div>
            </CardContent>
          </Card>

          {/* 近7天趋势 */}
          <Card>
            <CardHeader>
              <CardTitle>近7天趋势</CardTitle>
              <CardDescription>最近7天的红包发送趋势</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {data.recent_7_days.map((day) => (
                  <div key={day.date} className="flex items-center justify-between p-4 rounded-lg border bg-muted/50">
                    <div className="flex-1">
                      <p className="font-medium">
                        {new Date(day.date).toLocaleDateString('zh-CN', {
                          month: 'long',
                          day: 'numeric',
                          weekday: 'short',
                        })}
                      </p>
                      <div className="mt-2 flex items-center gap-4 text-sm">
                        <span className="text-muted-foreground">
                          发送: {day.count.toLocaleString()} 次
                        </span>
                        <span className="text-muted-foreground">
                          金额: ¥{day.amount}
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="flex items-center gap-2">
                        <CheckCircle2 className="h-4 w-4 text-green-600" />
                        <span className="text-sm font-medium">{day.success}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <XCircle className="h-4 w-4 text-red-600" />
                        <span className="text-sm font-medium">{day.failed}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  )
}

