/**
 * Dashboard Mock 数据
 */

export interface DashboardData {
  stats: {
    user_count: number
    active_envelopes: number
    last_7d_amount: string
    last_7d_orders: number
    pending_recharges: number
    success_recharges: number
    since: string
    until: string
  }
  trends: {
    date: string
    users: number
    envelopes: number
    amount: number
  }[]
  recent_tasks: {
    id: string
    task: string
    status: 'success' | 'pending' | 'failed'
    group: string
    amount: string
    time: string
  }[]
}

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
  ],
}

