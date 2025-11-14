import { adminApiClient } from '@/api/admin'
import { MOCK_DASHBOARD } from '@/mock/dashboard'
import { MOCK_GROUPS } from '@/mock/groups'
import { MOCK_LOGS } from '@/mock/logs'
import { MOCK_RED_PACKET_STATS } from '@/mock/stats'
import { MOCK_USER } from '@/mock/user'

// 错误类型辅助
interface ApiError {
  response?: {
    status?: number
    data?: {
      detail?: string
    }
  }
  message?: string
}

export interface DashboardStats {
  user_count: number
  active_envelopes: number
  last_7d_amount: string
  last_7d_orders: number
  pending_recharges: number
  success_recharges: number
  since: string
  until: string
}

export type DashboardTrends = Array<{
  date: string
  users: number
  envelopes: number
  amount: number
}>

export interface DashboardData {
  stats: DashboardStats
  trends?: DashboardTrends
  recent_tasks?: {
    id: string
    task: string
    status: 'success' | 'pending' | 'failed'
    group: string
    amount: string
    time: string
  }[]
  isMock?: boolean  // 标识是否使用 mock 数据
}

export interface AuditLogItem {
  id: number
  created_at: string
  type: string
  token: string
  amount: number
  note: string | null
  tg_id: number | null
  username: string | null
  user_id: number | null
  envelope_id: number | null
  order_id: number | null
  operator_id: number | null
}

export interface AuditLogsResponse {
  items: AuditLogItem[]
  pagination: {
    page: number
    per_page: number
    total: number
    total_pages: number
  }
  sum_amount: number
}

export interface AuditLogsParams {
  page?: number
  per_page?: number
  ltype?: string
  types?: string[]
  token?: string
  user?: string
  operator?: number
  min_amount?: number
  max_amount?: number
  start?: string
  end?: string
  q?: string
}

/**
 * 通用 API 调用函数（带 mock fallback）
 */
async function apiCallWithMock<T>(
  apiCall: () => Promise<T>,
  mockData: T,
  apiName: string
): Promise<T> {
  try {
    return await apiCall()
  } catch (error: unknown) {
    // 如果是 404 或 500，使用 mock 数据
    const apiError = error as ApiError
    if (apiError?.response?.status === 404 || apiError?.response?.status === 500 || !apiError?.response) {
      console.warn(`[${apiName}] 接口不可用，使用 mock 数据:`, apiError?.message)
      return mockData
    }
    // 其他错误也使用 mock 数据
    console.warn(`[${apiName}] 请求失败，使用 mock 数据:`, apiError?.message)
    return mockData
  }
}

/**
 * 获取趋势统计数据
 */
export interface StatsTrendsResponse {
  trends: DashboardTrends
  period: {
    days: number
    start: string
    end: string
  }
}

export async function getStatsTrends(days: number = 7): Promise<DashboardTrends> {
  try {
    const { data } = await adminApiClient.get<StatsTrendsResponse>('/admin/api/v1/stats', {
      params: { days },
    })
    return data.trends
  } catch (error: unknown) {
    const apiError = error as ApiError
    console.warn('[Stats] 无法从后端获取趋势数据，使用 mock 数据:', apiError?.message)
    return MOCK_DASHBOARD.trends ?? []
  }
}

/**
 * 获取仪表盘完整数据（包括统计、趋势、任务）
 * 优先使用 /admin/api/v1/dashboard 接口（字段名与前端一致）
 */
export async function getDashboard(): Promise<DashboardData & { isMock?: boolean }> {
  try {
    // 先尝试获取统计数据（主接口，字段名与前端一致）
    const { data: statsData } = await adminApiClient.get<DashboardStats>('/admin/api/v1/dashboard')
    
    // 尝试获取趋势数据
    let trendsData: DashboardTrends = MOCK_DASHBOARD.trends ?? []
    try {
      trendsData = await getStatsTrends(7)
    } catch (trendsError: unknown) {
      const apiError = trendsError as ApiError
      console.warn('[Dashboard] 无法获取趋势数据，使用 mock:', apiError?.message)
    }
    
    // 返回真实数据（trends 使用真实接口，tasks 暂时用 mock）
    return {
      stats: statsData,
      trends: trendsData,
      recent_tasks: MOCK_DASHBOARD.recent_tasks,
      isMock: false,
    }
  } catch (error: unknown) {
    // 如果失败，尝试公开接口
    const apiError = error as ApiError
    if (apiError?.response?.status === 401 || apiError?.response?.status === 403) {
      try {
        const { data: statsData } = await adminApiClient.get<DashboardStats>('/admin/api/v1/dashboard/public')
        // 尝试获取趋势数据
        let trendsData: DashboardTrends = MOCK_DASHBOARD.trends ?? []
        try {
          trendsData = await getStatsTrends(7)
        } catch (trendsError: unknown) {
          const apiError = trendsError as ApiError
          console.warn('[Dashboard] 无法获取趋势数据，使用 mock:', apiError?.message)
        }
        return {
          stats: statsData,
          trends: trendsData,
          recent_tasks: MOCK_DASHBOARD.recent_tasks,
          isMock: false,
        }
      } catch (publicError: unknown) {
        const apiError = publicError as ApiError
        console.warn('[Dashboard] 无法从后端获取数据，使用 mock 数据:', apiError?.message)
        return {
          stats: MOCK_DASHBOARD.stats,
          trends: MOCK_DASHBOARD.trends,
          recent_tasks: MOCK_DASHBOARD.recent_tasks,
          isMock: true,
        }
      }
    }
    // 如果是 404 或其他网络错误，尝试公开接口
    if (apiError?.response?.status === 404 || !apiError?.response) {
      try {
        const { data: statsData } = await adminApiClient.get<DashboardStats>('/admin/api/v1/dashboard/public')
        // 尝试获取趋势数据
        let trendsData: DashboardTrends = MOCK_DASHBOARD.trends ?? []
        try {
          trendsData = await getStatsTrends(7)
        } catch (trendsError: unknown) {
          const apiError = trendsError as ApiError
          console.warn('[Dashboard] 无法获取趋势数据，使用 mock:', apiError?.message)
        }
        return {
          stats: statsData,
          trends: trendsData,
          recent_tasks: MOCK_DASHBOARD.recent_tasks,
          isMock: false,
        }
      } catch (publicError: unknown) {
        const apiError = publicError as ApiError
        console.warn('[Dashboard] 无法从后端获取数据，使用 mock 数据:', apiError?.message)
        return {
          stats: MOCK_DASHBOARD.stats,
          trends: MOCK_DASHBOARD.trends,
          recent_tasks: MOCK_DASHBOARD.recent_tasks,
          isMock: true,
        }
      }
    }
    // 其他错误也使用 mock 数据
    console.warn('[Dashboard] 后端请求失败，使用 mock 数据:', apiError?.message)
    return {
      stats: MOCK_DASHBOARD.stats,
      trends: MOCK_DASHBOARD.trends,
      recent_tasks: MOCK_DASHBOARD.recent_tasks,
      isMock: true,
    }
  }
}

/**
 * 获取仪表盘统计数据（兼容旧接口）
 */
export async function getDashboardStats(): Promise<DashboardStats> {
  const dashboard = await getDashboard()
  return dashboard.stats
}

/**
 * 获取审计日志列表
 */
export async function getAuditLogs(params: AuditLogsParams = {}): Promise<AuditLogsResponse> {
  return apiCallWithMock(
    async () => {
      const { data } = await adminApiClient.get<AuditLogsResponse>('/admin/api/v1/audit', { params })
      return data
    },
    {
      items: MOCK_LOGS.items.map((log) => {
        const userId = log.extra?.user_id
        const numericUserId = typeof userId === 'number' ? userId : null
        return {
          id: log.id,
          created_at: log.timestamp,
          type: log.level.toUpperCase(),
          token: 'USDT',
          amount: 0,
          note: log.message,
          tg_id: numericUserId,
          username: null,
          user_id: numericUserId,
          envelope_id: null,
          order_id: null,
          operator_id: null,
        }
      }),
      pagination: MOCK_LOGS.pagination,
      sum_amount: 0,
    },
    'AuditLogs'
  )
}

/**
 * 获取群组列表
 */
export interface GroupListParams {
  page?: number
  per_page?: number
  q?: string
  tags?: string[]
  status?: string
}

export interface GroupItem {
  id: number
  name: string
  description: string
  members_count: number
  tags: string[]
  language: string
  status: string
  invite_link: string
  entry_reward_enabled: boolean
  entry_reward_points: number
  is_bookmarked: boolean
  created_at: string
}

export interface GroupListResponse {
  items: GroupItem[]
  pagination: {
    page: number
    per_page: number
    total: number
    total_pages: number
  }
}

export async function getGroupList(params: GroupListParams = {}): Promise<GroupListResponse> {
  return apiCallWithMock(
    async () => {
      const { data } = await adminApiClient.get<GroupListResponse>('/admin/api/v1/group-list', { params })
      return data
    },
    MOCK_GROUPS,
    'GroupList'
  )
}

/**
 * 获取日志列表
 */
export interface LogListParams {
  page?: number
  per_page?: number
  level?: 'info' | 'warn' | 'error'
  module?: string
  start?: string
  end?: string
  q?: string
}

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

export async function getLogs(params: LogListParams = {}): Promise<LogListResponse> {
  return apiCallWithMock(
    async () => {
      const { data } = await adminApiClient.get<LogListResponse>('/admin/api/v1/logs', { params })
      return data
    },
    MOCK_LOGS,
    'Logs'
  )
}

/**
 * 获取红包统计
 */
export interface RedPacketStats {
  total_sent: number
  total_amount: string
  success_rate: number
  avg_amount: string
  by_type: Array<{
    type: string
    count: number
    amount: string
  }>
  by_hour: Array<{
    hour: number
    count: number
    amount: string
  }>
  recent_7_days: Array<{
    date: string
    count: number
    amount: string
    success: number
    failed: number
  }>
}

export async function getRedPacketStats(): Promise<RedPacketStats> {
  return apiCallWithMock(
    async () => {
      const { data } = await adminApiClient.get<RedPacketStats>('/admin/api/v1/stats')
      return data
    },
    MOCK_RED_PACKET_STATS,
    'RedPacketStats'
  )
}

/**
 * 获取用户信息
 */
export interface UserInfo {
  id: number
  username: string
  tg_id: number
  roles: string[]
  is_admin: boolean
}

export async function getUserInfo(): Promise<UserInfo> {
  return apiCallWithMock(
    async () => {
      const { data } = await adminApiClient.get<UserInfo>('/admin/api/v1/user')
      return data
    },
    MOCK_USER,
    'UserInfo'
  )
}

/**
 * 获取红包任务列表
 */
export interface TaskItem {
  id: number
  type: string
  group_name: string
  amount: number
  count: number
  status: string
  created_at: string | null
  remain_count: number
}

export interface TaskListResponse {
  items: TaskItem[]
  pagination: {
    page: number
    per_page: number
    total: number
    total_pages: number
  }
}

export interface TaskListParams {
  page?: number
  per_page?: number
  status?: 'active' | 'closed' | 'failed' | ''
  q?: string
  group_id?: number
}

export async function getTasks(params: TaskListParams = {}): Promise<TaskListResponse> {
  return apiCallWithMock(
    async () => {
      const { data } = await adminApiClient.get<TaskListResponse>('/admin/api/v1/tasks', { params })
      return data
    },
    {
      items: [],
      pagination: {
        page: 1,
        per_page: 20,
        total: 0,
        total_pages: 0,
      },
    },
    'Tasks'
  )
}

/**
 * 获取红包任务详情
 */
export interface TaskDetail {
  id: number
  token: string
  total_amount: number
  total_count: number
  claimed_amount: number
  claimed_count: number
  remain_amount: number
  remain_count: number
  created_at: string | null
  closed_at: string | null
  creator: {
    tg_id: number | null
    username: string | null
  } | null
  lucky: {
    tg_id: number
    username: string | null
    amount: number
  } | null
  claims: Array<{
    user_id: number | null
    username: string | null
    amount: number
    created_at: string | null
    note: string | null
  }>
  total_claims: number
}

export async function getTaskDetail(taskId: number): Promise<TaskDetail> {
  return apiCallWithMock(
    async () => {
      const { data } = await adminApiClient.get<TaskDetail>(`/admin/api/v1/tasks/${taskId}`)
      return data
    },
    {
      id: taskId,
      token: 'USDT',
      total_amount: 0,
      total_count: 0,
      claimed_amount: 0,
      claimed_count: 0,
      remain_amount: 0,
      remain_count: 0,
      created_at: null,
      closed_at: null,
      creator: null,
      lucky: null,
      claims: [],
      total_claims: 0,
    },
    'TaskDetail'
  )
}

/**
 * 获取系统设置
 */
export interface SystemSettings {
  amount_limits: {
    max_single: number
    min_single: number
    daily_total: number
  }
  risk_control: {
    enable_rate_limit: boolean
    enable_blacklist: boolean
    max_per_user_per_day: number
  }
  notifications: {
    notify_on_failure: boolean
    notify_on_critical: boolean
  }
  feature_flags: Record<string, unknown>
}

export async function getSettings(): Promise<SystemSettings> {
  return apiCallWithMock(
    async () => {
      const { data } = await adminApiClient.get<SystemSettings>('/admin/api/v1/settings')
      return data
    },
    {
      amount_limits: {
        max_single: 1000.0,
        min_single: 0.01,
        daily_total: 10000.0,
      },
      risk_control: {
        enable_rate_limit: true,
        enable_blacklist: true,
        max_per_user_per_day: 10,
      },
      notifications: {
        notify_on_failure: true,
        notify_on_critical: true,
      },
      feature_flags: {},
    },
    'Settings'
  )
}

/**
 * 更新系统设置
 */
export interface SettingsUpdate {
  amount_limits?: {
    max_single?: number
    min_single?: number
    daily_total?: number
  }
  risk_control?: {
    enable_rate_limit?: boolean
    enable_blacklist?: boolean
    max_per_user_per_day?: number
  }
  notifications?: {
    notify_on_failure?: boolean
    notify_on_critical?: boolean
  }
}

export async function updateSettings(settings: SettingsUpdate): Promise<{ success: boolean; message: string }> {
  const { data } = await adminApiClient.put<{ success: boolean; message: string }>('/admin/api/v1/settings', settings)
  return data
}

