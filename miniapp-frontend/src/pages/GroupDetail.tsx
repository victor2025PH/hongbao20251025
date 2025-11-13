import { useParams, Link, type ReactElement } from 'react'
import { useQuery } from '@tanstack/react-query'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Badge } from '../components/ui/badge'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table'
import LoadingSkeleton from '../components/LoadingSkeleton'
import ErrorNotice from '../components/ErrorNotice'
import { openTelegramLink } from '../utils/telegram'
import { apiClient } from '../api/http'
import type { PublicGroupSummary } from '../types/publicGroups'
import { Users, MessageSquare, Calendar, Tag, ExternalLink, ArrowLeft } from 'lucide-react'

// 群动态数据（虚拟数据）
const groupActivities = [
  {
    id: '1',
    action: '新成员加入',
    user: '用户123',
    time: '2 分钟前',
    type: 'join',
  },
  {
    id: '2',
    action: '发送红包',
    user: '用户456',
    amount: '¥50',
    time: '5 分钟前',
    type: 'redpack',
  },
  {
    id: '3',
    action: '消息发送',
    user: '用户789',
    time: '10 分钟前',
    type: 'message',
  },
  {
    id: '4',
    action: '红包领取',
    user: '用户012',
    amount: '¥20',
    time: '15 分钟前',
    type: 'claim',
  },
]

export default function GroupDetail(): ReactElement {
  const { id } = useParams<{ id: string }>()

  const groupQuery = useQuery<PublicGroupSummary>({
    queryKey: ['public-group', id],
    queryFn: async () => {
      const { data } = await apiClient.get<PublicGroupSummary>(`/groups/public/${id}`)
      return data
    },
    enabled: !!id,
  })

  const group = groupQuery.data

  if (groupQuery.isLoading) {
    return (
      <div className="container mx-auto space-y-8 p-6 lg:p-8">
        <LoadingSkeleton lines={10} />
      </div>
    )
  }

  if (groupQuery.isError || !group) {
    return (
      <div className="container mx-auto space-y-8 p-6 lg:p-8">
        <ErrorNotice
          message="無法載入群組資料"
          onRetry={() => groupQuery.refetch()}
        />
      </div>
    )
  }

  return (
    <div className="container mx-auto space-y-8 p-6 lg:p-8">
      {/* 返回按钮 */}
      <Link
        to="/groups"
        className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground"
      >
        <ArrowLeft className="h-4 w-4" />
        返回群组列表
      </Link>

      {/* 群组基本信息 */}
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="space-y-2">
              <CardTitle className="text-2xl">{group.name}</CardTitle>
              <CardDescription>{group.description || '暂无描述'}</CardDescription>
            </div>
            <button
              onClick={() => openTelegramLink(group.invite_link)}
              className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
            >
              <ExternalLink className="h-4 w-4" />
              加入群组
            </button>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* 基本信息表格 */}
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Users className="h-4 w-4" />
                <span>成员数量</span>
              </div>
              <p className="text-2xl font-bold">{group.members_count.toLocaleString()}</p>
            </div>
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Tag className="h-4 w-4" />
                <span>语言</span>
              </div>
              <p className="text-2xl font-bold">{group.language?.toUpperCase() || 'N/A'}</p>
            </div>
            {group.entry_reward_enabled && (
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <MessageSquare className="h-4 w-4" />
                  <span>入群奖励</span>
                </div>
                <p className="text-2xl font-bold text-red-600 dark:text-red-400">
                  +{group.entry_reward_points} 星
                </p>
              </div>
            )}
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Calendar className="h-4 w-4" />
                <span>创建时间</span>
              </div>
              <p className="text-sm">
                {group.created_at
                  ? new Date(group.created_at).toLocaleString('zh-TW')
                  : '未知'}
              </p>
            </div>
          </div>

          {/* 标签 */}
          {group.tags.length > 0 && (
            <div className="space-y-2">
              <p className="text-sm font-medium text-muted-foreground">标签</p>
              <div className="flex flex-wrap gap-2">
                {group.tags.map((tag) => (
                  <Badge key={tag} variant="secondary">
                    #{tag}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* 状态信息 */}
          <div className="flex items-center gap-2">
            <Badge
              variant={group.status === 'active' ? 'default' : 'secondary'}
              className={
                group.status === 'active'
                  ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                  : ''
              }
            >
              {group.status === 'active' ? '活跃' : group.status}
            </Badge>
            {group.is_pinned && (
              <Badge variant="outline" className="border-amber-300 text-amber-700 dark:text-amber-400">
                置顶
              </Badge>
            )}
            {group.is_bookmarked && (
              <Badge variant="outline" className="border-yellow-300 text-yellow-700 dark:text-yellow-400">
                已收藏
              </Badge>
            )}
          </div>
        </CardContent>
      </Card>

      {/* 群动态时间线 */}
      <Card>
        <CardHeader>
          <CardTitle>群动态</CardTitle>
          <CardDescription>查看群组最新活动记录</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>动作</TableHead>
                <TableHead>用户</TableHead>
                <TableHead>金额</TableHead>
                <TableHead className="text-right">时间</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {groupActivities.map((activity) => (
                <TableRow key={activity.id}>
                  <TableCell className="font-medium">{activity.action}</TableCell>
                  <TableCell>{activity.user}</TableCell>
                  <TableCell>
                    {activity.amount ? (
                      <span className="font-semibold text-red-600 dark:text-red-400">
                        {activity.amount}
                      </span>
                    ) : (
                      '-'
                    )}
                  </TableCell>
                  <TableCell className="text-right text-sm text-muted-foreground">
                    {activity.time}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}

