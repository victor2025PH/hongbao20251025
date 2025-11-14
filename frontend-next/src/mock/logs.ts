/**
 * 日志 Mock 数据
 */

export interface LogItem {
  id: number
  level: 'info' | 'warn' | 'error'
  message: string
  timestamp: string
  module: string
  extra?: Record<string, unknown>
}

export interface LogListResponse {
  items: LogItem[]
  pagination: {
    page: number
    per_page: number
    total: number
    total_pages: number
  }
}

export const MOCK_LOGS: LogListResponse = {
  items: Array.from({ length: 50 }, (_, i) => ({
    id: i + 1,
    level: (['info', 'warn', 'error'][Math.floor(Math.random() * 3)] || 'info') as 'info' | 'warn' | 'error',
    message: [
      '红包发送成功',
      '用户登录',
      '群组创建',
      '充值完成',
      '系统错误',
      '数据库连接失败',
      'API 请求超时',
    ][Math.floor(Math.random() * 7)],
    timestamp: new Date(Date.now() - i * 60000).toISOString(),
    module: ['api', 'database', 'auth', 'payment', 'group'][Math.floor(Math.random() * 5)],
    extra: {
      user_id: Math.floor(Math.random() * 1000),
      group_id: Math.floor(Math.random() * 100),
    },
  })),
  pagination: {
    page: 1,
    per_page: 50,
    total: 500,
    total_pages: 10,
  },
}

