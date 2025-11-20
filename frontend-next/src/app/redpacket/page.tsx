'use client'

import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { Gift, Send, Search, History, Wallet, TrendingUp, Users } from 'lucide-react'
import LoadingSkeleton from '@/components/shared/LoadingSkeleton'
import ErrorNotice from '@/components/shared/ErrorNotice'
import { getGroupList, type GroupItem } from '@/lib/api'

// Toast hook - 如果不存在，使用简单的 alert
const useToast = () => {
  return {
    toast: ({ title, description, variant }: { title?: string; description?: string; variant?: 'default' | 'destructive' }) => {
      if (variant === 'destructive') {
        alert(`${title || '错误'}: ${description || ''}`)
      } else {
        console.log(`${title || '提示'}: ${description || ''}`)
      }
    },
  }
}

// API 客户端
const API_BASE = process.env.NEXT_PUBLIC_ADMIN_API_BASE_URL || 'http://localhost:8001'

interface SendRedPacketRequest {
  chat_id: number
  token: 'USDT' | 'TON' | 'POINT'
  total_amount: number
  shares: number
  note?: string
}

interface RedPacketInfo {
  id: number
  chat_id: number
  sender_tg_id: number
  token: string
  total_amount: string
  shares: number
  remain_shares: number
  note?: string
  status: string
  created_at: string
  activated_at?: string
}

interface UserBalance {
  tg_id: number
  username?: string
  balance_usdt: string
  balance_ton: string
  balance_point: string
}

// API 函数
async function sendRedPacket(data: SendRedPacketRequest) {
  const response = await fetch(`${API_BASE}/admin/api/v1/redpacket/send`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '发送失败' }))
    throw new Error(error.detail || '发送失败')
  }
  return response.json()
}

async function grabRedPacket(envelopeId: number) {
  const response = await fetch(`${API_BASE}/admin/api/v1/redpacket/${envelopeId}/grab`, {
    method: 'POST',
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
    },
    credentials: 'include',
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '抢红包失败' }))
    throw new Error(error.detail || '抢红包失败')
  }
  return response.json()
}

async function getRedPacketInfo(envelopeId: number) {
  const response = await fetch(`${API_BASE}/admin/api/v1/redpacket/${envelopeId}`, {
    credentials: 'include',
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
    },
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '查询失败' }))
    throw new Error(error.detail || '查询失败')
  }
  return response.json()
}

async function getUserBalance() {
  const response = await fetch(`${API_BASE}/admin/api/v1/redpacket/balance`, {
    credentials: 'include',
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
    },
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '查询失败' }))
    throw new Error(error.detail || '查询失败')
  }
  return response.json()
}

async function getRedPacketHistory(page: number = 1, limit: number = 20) {
  const response = await fetch(`${API_BASE}/admin/api/v1/redpacket/history?page=${page}&limit=${limit}`, {
    credentials: 'include',
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
    },
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '查询失败' }))
    throw new Error(error.detail || '查询失败')
  }
  return response.json()
}

export default function RedPacketPage() {
  const { toast } = useToast()
  const queryClient = useQueryClient()

  // 发送红包表单状态
  const [sendForm, setSendForm] = useState<SendRedPacketRequest>({
    chat_id: 0,
    token: 'POINT',
    total_amount: 0,
    shares: 1,
    note: '',
  })

  // 查询红包 ID 状态
  const [queryEnvelopeId, setQueryEnvelopeId] = useState<string>('')

  // 查询用户余额
  const { data: balance, isLoading: balanceLoading, error: balanceError } = useQuery<UserBalance>({
    queryKey: ['redpacket-balance'],
    queryFn: getUserBalance,
    refetchInterval: 30000, // 每30秒刷新余额
    retry: false, // 不自动重试，避免持续失败
  })

  // 查询红包历史
  const [historyPage, setHistoryPage] = useState(1)
  const { data: history, isLoading: historyLoading, error: historyError } = useQuery({
    queryKey: ['redpacket-history', historyPage],
    queryFn: () => getRedPacketHistory(historyPage, 20),
    retry: false, // 不自动重试
  })

  // 查询群组列表（仅显示活跃状态的群组）
  const { data: groupsData, isLoading: groupsLoading, error: groupsError } = useQuery({
    queryKey: ['group-list', 'active'],
    queryFn: () => getGroupList({ status: 'active', per_page: 100 }),
    retry: false, // 不自动重试
  })

  // 错误日志记录（使用 useEffect 处理副作用）
  useEffect(() => {
    if (balanceError) {
      console.error('[余额查询] 失败:', balanceError)
    }
  }, [balanceError])

  useEffect(() => {
    if (historyError) {
      console.error('[历史记录查询] 失败:', historyError)
    }
  }, [historyError])

  useEffect(() => {
    if (groupsError) {
      console.error('[群组列表查询] 失败:', groupsError)
    }
  }, [groupsError])

  // 发送红包
  const sendMutation = useMutation({
    mutationFn: sendRedPacket,
    onSuccess: (data) => {
      toast({
        title: '发送成功',
        description: `红包已发送到群组，红包 ID: ${data.envelope_id}`,
      })
      setSendForm({
        chat_id: 0,
        token: 'POINT',
        total_amount: 0,
        shares: 1,
        note: '',
      })
      queryClient.invalidateQueries({ queryKey: ['redpacket-history'] })
      queryClient.invalidateQueries({ queryKey: ['redpacket-balance'] })
    },
    onError: (error: Error) => {
      toast({
        title: '发送失败',
        description: error.message,
        variant: 'destructive',
      })
    },
  })

  // 抢红包
  const grabMutation = useMutation({
    mutationFn: grabRedPacket,
    onSuccess: (data) => {
      toast({
        title: '抢红包成功',
        description: `恭喜！你抢到了 ${data.amount} ${data.token}`,
      })
      queryClient.invalidateQueries({ queryKey: ['redpacket-history'] })
      queryClient.invalidateQueries({ queryKey: ['redpacket-balance'] })
    },
    onError: (error: Error) => {
      toast({
        title: '抢红包失败',
        description: error.message,
        variant: 'destructive',
      })
    },
  })

  // 查询红包信息
  const { data: redPacketInfo, isLoading: infoLoading, refetch: refetchInfo } = useQuery<RedPacketInfo>({
    queryKey: ['redpacket-info', queryEnvelopeId],
    queryFn: () => getRedPacketInfo(Number(queryEnvelopeId)),
    enabled: !!queryEnvelopeId && !isNaN(Number(queryEnvelopeId)),
  })

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault()
    if (sendForm.chat_id <= 0) {
      toast({
        title: '参数错误',
        description: '请输入有效的群组 ID',
        variant: 'destructive',
      })
      return
    }
    if (sendForm.total_amount <= 0) {
      toast({
        title: '参数错误',
        description: '红包金额必须大于 0',
        variant: 'destructive',
      })
      return
    }
    if (sendForm.shares < 1) {
      toast({
        title: '参数错误',
        description: '红包份数必须大于等于 1',
        variant: 'destructive',
      })
      return
    }
    sendMutation.mutate(sendForm)
  }

  const handleQuery = () => {
    if (!queryEnvelopeId || isNaN(Number(queryEnvelopeId))) {
      toast({
        title: '参数错误',
        description: '请输入有效的红包 ID',
        variant: 'destructive',
      })
      return
    }
    refetchInfo()
  }

  const handleGrab = (envelopeId: number) => {
    grabMutation.mutate(envelopeId)
  }

  const formatBalance = (balance: string, token: string) => {
    const num = parseFloat(balance || '0')
    if (token === 'POINT') {
      return Math.floor(num).toLocaleString()
    }
    return num.toFixed(2)
  }

  return (
    <div className="container mx-auto py-8 px-4 max-w-7xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2 flex items-center gap-2">
          <Gift className="h-8 w-8 text-red-500" />
          红包功能
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          发送红包、查询记录、参与游戏 - 与 Telegram 红包机器人无缝对接
        </p>
      </div>

      {/* 余额卡片 */}
      {balanceLoading ? (
        <LoadingSkeleton />
      ) : balanceError ? (
        <ErrorNotice 
          message={`无法加载余额信息: ${balanceError instanceof Error ? balanceError.message : '未知错误'}`}
          onRetry={() => queryClient.invalidateQueries({ queryKey: ['redpacket-balance'] })}
        />
      ) : balance ? (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Wallet className="h-5 w-5" />
              我的余额
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">USDT</div>
                <div className="text-2xl font-bold">{formatBalance(balance.balance_usdt, 'USDT')}</div>
              </div>
              <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">TON</div>
                <div className="text-2xl font-bold">{formatBalance(balance.balance_ton, 'TON')}</div>
              </div>
              <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">POINT</div>
                <div className="text-2xl font-bold">{formatBalance(balance.balance_point, 'POINT')}</div>
              </div>
            </div>
          </CardContent>
        </Card>
      ) : (
        <ErrorNotice message="无法加载余额信息" />
      )}

      <Tabs defaultValue="send" className="space-y-4">
        <TabsList>
          <TabsTrigger value="send">
            <Send className="h-4 w-4 mr-2" />
            发送红包
          </TabsTrigger>
          <TabsTrigger value="query">
            <Search className="h-4 w-4 mr-2" />
            查询红包
          </TabsTrigger>
          <TabsTrigger value="history">
            <History className="h-4 w-4 mr-2" />
            历史记录
          </TabsTrigger>
        </TabsList>

        {/* 发送红包 */}
        <TabsContent value="send">
          <Card>
            <CardHeader>
              <CardTitle>发送红包</CardTitle>
              <CardDescription>
                填写红包信息，系统会将红包发送到指定的 Telegram 群组
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSend} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="chat_id">选择群组 *</Label>
                    {groupsLoading ? (
                      <div className="p-2 text-sm text-gray-500">加载群组列表...</div>
                    ) : groupsError ? (
                      <div className="p-2 space-y-2">
                        <div className="text-sm text-red-600">
                          无法加载群组列表: {groupsError instanceof Error ? groupsError.message : '未知错误'}
                        </div>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => queryClient.invalidateQueries({ queryKey: ['group-list', 'active'] })}
                        >
                          重试
                        </Button>
                      </div>
                    ) : groupsData && groupsData.items && groupsData.items.length > 0 ? (
                      <>
                        <Select
                          value={sendForm.chat_id > 0 ? String(sendForm.chat_id) : ''}
                          onValueChange={(value) => {
                            // 从群组中提取 chat_id
                            const group = groupsData.items.find((g) => String(g.id) === value)
                            if (group) {
                              // 如果后端返回了 chat_id，使用它；否则提示用户需要手动输入
                              if (group.chat_id) {
                                setSendForm({ ...sendForm, chat_id: group.chat_id })
                              } else {
                                // 如果没有 chat_id，显示提示信息
                                toast({
                                  title: '注意',
                                  description: `群组 "${group.name}" 没有配置 chat_id，请手动输入群组 ID`,
                                  variant: 'default',
                                })
                                // 仍然设置群组 ID 以便用户知道选择了哪个群组
                                setSendForm({ ...sendForm, chat_id: 0 })
                              }
                            }
                          }}
                          required
                        >
                          <SelectTrigger id="chat_id">
                            <SelectValue placeholder="请选择群组" />
                          </SelectTrigger>
                          <SelectContent>
                            {groupsData.items.map((group) => (
                              <SelectItem key={group.id} value={String(group.id)}>
                                <div className="flex flex-col">
                                  <div className="flex items-center gap-2">
                                    <span className="font-medium">{group.name}</span>
                                    {group.chat_id && (
                                      <Badge variant="outline" className="text-xs">
                                        ID: {group.chat_id}
                                      </Badge>
                                    )}
                                  </div>
                                  {group.description && (
                                    <span className="text-xs text-gray-500 truncate max-w-xs">
                                      {group.description}
                                    </span>
                                  )}
                                  <div className="flex items-center gap-2 text-xs text-gray-400">
                                    {group.members_count > 0 && (
                                      <span>{group.members_count} 成员</span>
                                    )}
                                    {group.invite_link && (
                                      <span className="truncate max-w-xs">{group.invite_link}</span>
                                    )}
                                  </div>
                                </div>
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        {sendForm.chat_id <= 0 && (
                          <div className="mt-2 space-y-2">
                            <Label htmlFor="chat_id_manual">或手动输入群组 ID</Label>
                            <Input
                              id="chat_id_manual"
                              type="number"
                              placeholder="例如: -1001234567890"
                              value={sendForm.chat_id || ''}
                              onChange={(e) => setSendForm({ ...sendForm, chat_id: Number(e.target.value) })}
                            />
                            <p className="text-xs text-gray-500">
                              如果选择的群组没有配置 chat_id，请在此手动输入 Telegram 群组的 chat_id
                            </p>
                          </div>
                        )}
                      </>
                    ) : (
                      <div className="space-y-2">
                        <Input
                          id="chat_id"
                          type="number"
                          placeholder="例如: -1001234567890"
                          value={sendForm.chat_id || ''}
                          onChange={(e) => setSendForm({ ...sendForm, chat_id: Number(e.target.value) })}
                          required
                        />
                        <p className="text-xs text-gray-500">
                          没有可用的群组列表，请输入 Telegram 群组的 chat_id（负数表示群组）
                        </p>
                      </div>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="token">币种 *</Label>
                    <Select
                      value={sendForm.token}
                      onValueChange={(value: 'USDT' | 'TON' | 'POINT') =>
                        setSendForm({ ...sendForm, token: value })
                      }
                    >
                      <SelectTrigger id="token">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="USDT">USDT</SelectItem>
                        <SelectItem value="TON">TON</SelectItem>
                        <SelectItem value="POINT">POINT (积分)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="total_amount">红包总金额 *</Label>
                    <Input
                      id="total_amount"
                      type="number"
                      step="0.01"
                      min="0.01"
                      placeholder="例如: 100"
                      value={sendForm.total_amount || ''}
                      onChange={(e) => setSendForm({ ...sendForm, total_amount: Number(e.target.value) })}
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="shares">红包份数 *</Label>
                    <Input
                      id="shares"
                      type="number"
                      min="1"
                      placeholder="例如: 10"
                      value={sendForm.shares || ''}
                      onChange={(e) => setSendForm({ ...sendForm, shares: Number(e.target.value) })}
                      required
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="note">祝福语（可选）</Label>
                  <Textarea
                    id="note"
                    placeholder="例如: 恭喜发财，大吉大利！"
                    value={sendForm.note || ''}
                    onChange={(e) => setSendForm({ ...sendForm, note: e.target.value })}
                    maxLength={120}
                    rows={3}
                  />
                </div>

                {sendMutation.isError && (
                  <Alert variant="destructive">
                    <AlertDescription>
                      {sendMutation.error?.message || '发送失败，请重试'}
                    </AlertDescription>
                  </Alert>
                )}

                <Button
                  type="submit"
                  disabled={sendMutation.isPending}
                  className="w-full"
                  size="lg"
                >
                  {sendMutation.isPending ? (
                    <>发送中...</>
                  ) : (
                    <>
                      <Send className="h-4 w-4 mr-2" />
                      发送红包
                    </>
                  )}
                </Button>
              </form>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 查询红包 */}
        <TabsContent value="query">
          <Card>
            <CardHeader>
              <CardTitle>查询红包信息</CardTitle>
              <CardDescription>输入红包 ID 查询红包详情</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex gap-2">
                  <Input
                    placeholder="请输入红包 ID"
                    value={queryEnvelopeId}
                    onChange={(e) => setQueryEnvelopeId(e.target.value)}
                  />
                  <Button onClick={handleQuery} disabled={infoLoading || !queryEnvelopeId}>
                    {infoLoading ? '查询中...' : '查询'}
                  </Button>
                </div>

                {redPacketInfo && (
                  <div className="space-y-4 mt-4">
                    <Card>
                      <CardHeader>
                        <CardTitle>红包详情</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-2">
                          <div className="flex justify-between">
                            <span className="text-gray-600 dark:text-gray-400">红包 ID:</span>
                            <span className="font-medium">{redPacketInfo.id}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600 dark:text-gray-400">币种:</span>
                            <Badge variant="outline">{redPacketInfo.token}</Badge>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600 dark:text-gray-400">总金额:</span>
                            <span className="font-medium">
                              {parseFloat(redPacketInfo.total_amount).toFixed(2)} {redPacketInfo.token}
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600 dark:text-gray-400">总份数:</span>
                            <span className="font-medium">{redPacketInfo.shares}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600 dark:text-gray-400">剩余份数:</span>
                            <span className="font-medium text-orange-600">{redPacketInfo.remain_shares}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600 dark:text-gray-400">状态:</span>
                            <Badge
                              variant={
                                redPacketInfo.status === 'active' ? 'default' : 'secondary'
                              }
                            >
                              {redPacketInfo.status === 'active' ? '进行中' : '已结束'}
                            </Badge>
                          </div>
                          {redPacketInfo.note && (
                            <div className="flex justify-between">
                              <span className="text-gray-600 dark:text-gray-400">祝福语:</span>
                              <span className="font-medium">{redPacketInfo.note}</span>
                            </div>
                          )}
                        </div>

                        {redPacketInfo.status === 'active' && redPacketInfo.remain_shares > 0 && (
                          <div className="mt-4">
                            <Button
                              onClick={() => handleGrab(redPacketInfo.id)}
                              disabled={grabMutation.isPending}
                              className="w-full"
                              variant="default"
                            >
                              {grabMutation.isPending ? (
                                <>抢红包中...</>
                              ) : (
                                <>
                                  <Gift className="h-4 w-4 mr-2" />
                                  立即抢红包
                                </>
                              )}
                            </Button>
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  </div>
                )}

                {infoLoading && <LoadingSkeleton />}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 历史记录 */}
        <TabsContent value="history">
          <Card>
            <CardHeader>
              <CardTitle>红包历史记录</CardTitle>
              <CardDescription>查看你发送和参与的红包记录</CardDescription>
            </CardHeader>
            <CardContent>
              {historyLoading ? (
                <LoadingSkeleton />
              ) : historyError ? (
                <ErrorNotice 
                  message={`无法加载历史记录: ${historyError instanceof Error ? historyError.message : '未知错误'}`}
                  onRetry={() => queryClient.invalidateQueries({ queryKey: ['redpacket-history', historyPage] })}
                />
              ) : history?.items && history.items.length > 0 ? (
                <div className="space-y-4">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>红包 ID</TableHead>
                        <TableHead>币种</TableHead>
                        <TableHead>总金额</TableHead>
                        <TableHead>份数</TableHead>
                        <TableHead>状态</TableHead>
                        <TableHead>创建时间</TableHead>
                        <TableHead>操作</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {history.items.map((item: RedPacketInfo) => (
                        <TableRow key={item.id}>
                          <TableCell className="font-medium">{item.id}</TableCell>
                          <TableCell>
                            <Badge variant="outline">{item.token}</Badge>
                          </TableCell>
                          <TableCell>
                            {parseFloat(item.total_amount).toFixed(2)} {item.token}
                          </TableCell>
                          <TableCell>
                            {item.remain_shares} / {item.shares}
                          </TableCell>
                          <TableCell>
                            <Badge
                              variant={item.status === 'active' ? 'default' : 'secondary'}
                            >
                              {item.status === 'active' ? '进行中' : '已结束'}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            {new Date(item.created_at).toLocaleString('zh-CN')}
                          </TableCell>
                          <TableCell>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => {
                                setQueryEnvelopeId(String(item.id))
                                refetchInfo()
                              }}
                            >
                              查看详情
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>

                  <div className="flex justify-between items-center">
                    <Button
                      variant="outline"
                      disabled={historyPage <= 1}
                      onClick={() => setHistoryPage(historyPage - 1)}
                    >
                      上一页
                    </Button>
                    <span className="text-sm text-gray-600">
                      第 {historyPage} 页，共 {Math.ceil((history.total || 0) / 20)} 页
                    </span>
                    <Button
                      variant="outline"
                      disabled={
                        !history.total || historyPage >= Math.ceil(history.total / 20)
                      }
                      onClick={() => setHistoryPage(historyPage + 1)}
                    >
                      下一页
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">暂无记录</div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

