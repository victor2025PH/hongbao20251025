/**
 * Dashboard Mock 数据
 * 注意：此文件只导出数据对象，不包含 interface/type 定义
 * 类型定义请参考 @/lib/api.ts 中的 DashboardData
 */

import type { DashboardData } from '@/lib/api'

export const MOCK_DASHBOARD: DashboardData = {
  stats: {
    user_count: 1234,
    active_envelopes: 56,
    last_7d_amount: '12345.67',
    last_7d_orders: 890,
    pending_recharges: 12,
    success_recharges: 345,
    since: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
    until: new Date().toISOString(),
  },
  trends: Array.from({ length: 7 }, (_, i) => {
    const date = new Date()
    date.setDate(date.getDate() - (6 - i))
    return {
      date: date.toISOString().split('T')[0],
      users: Math.floor(Math.random() * 100) + 1000,
      envelopes: Math.floor(Math.random() * 20) + 40,
      amount: Math.floor(Math.random() * 5000) + 10000,
    }
  }),
  recent_tasks: [
    {
      id: 'T001',
      task: '群发红包',
      status: 'success' as const,
      group: '测试群组 A',
      amount: '¥500',
      time: '14:32:15',
    },
    {
      id: 'T002',
      task: '定时红包',
      status: 'pending' as const,
      group: '测试群组 B',
      amount: '¥200',
      time: '14:28:42',
    },
    {
      id: 'T003',
      task: '个人红包',
      status: 'success' as const,
      group: '测试群组 C',
      amount: '¥100',
      time: '14:25:10',
    },
    {
      id: 'T004',
      task: '群发红包',
      status: 'failed' as const,
      group: '测试群组 D',
      amount: '¥300',
      time: '14:20:33',
    },
    {
      id: 'T005',
      task: '定时红包',
      status: 'success' as const,
      group: '测试群组 E',
      amount: '¥150',
      time: '14:15:08',
    },
  ],
  isMock: true,
}

export default MOCK_DASHBOARD

