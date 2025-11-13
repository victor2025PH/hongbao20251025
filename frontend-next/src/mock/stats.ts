/**
 * 红包统计 Mock 数据
 */

export interface RedPacketStats {
  total_sent: number
  total_amount: string
  success_rate: number
  avg_amount: string
  by_type: {
    type: string
    count: number
    amount: string
  }[]
  by_hour: {
    hour: number
    count: number
    amount: string
  }[]
  recent_7_days: {
    date: string
    count: number
    amount: string
    success: number
    failed: number
  }[]
}

export const MOCK_RED_PACKET_STATS: RedPacketStats = {
  total_sent: 12345,
  total_amount: '123456.78',
  success_rate: 98.5,
  avg_amount: '10.00',
  by_type: [
    { type: '群发红包', count: 8000, amount: '80000.00' },
    { type: '个人红包', count: 3000, amount: '30000.00' },
    { type: '定时红包', count: 1000, amount: '10000.00' },
    { type: '活动红包', count: 345, amount: '3456.78' },
  ],
  by_hour: Array.from({ length: 24 }, (_, i) => ({
    hour: i,
    count: Math.floor(Math.random() * 100) + 50,
    amount: (Math.random() * 1000 + 500).toFixed(2),
  })),
  recent_7_days: Array.from({ length: 7 }, (_, i) => {
    const date = new Date()
    date.setDate(date.getDate() - (6 - i))
    return {
      date: date.toISOString().split('T')[0],
      count: Math.floor(Math.random() * 500) + 1000,
      amount: (Math.random() * 10000 + 5000).toFixed(2),
      success: Math.floor(Math.random() * 450) + 950,
      failed: Math.floor(Math.random() * 50) + 10,
    }
  }),
}

