/**
 * 群组列表 Mock 数据
 */

export interface GroupItem {
  id: number
  name: string
  description: string
  members_count: number
  tags: string[]
  language: string
  status: 'active' | 'paused' | 'review' | 'removed'
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

export const MOCK_GROUPS: GroupListResponse = {
  items: Array.from({ length: 20 }, (_, i) => ({
    id: i + 1,
    name: `测试群组 ${i + 1}`,
    description: `这是测试群组 ${i + 1} 的描述信息`,
    members_count: Math.floor(Math.random() * 1000) + 100,
    tags: ['测试', '红包', '活动'].slice(0, Math.floor(Math.random() * 3) + 1),
    language: ['zh', 'en'][Math.floor(Math.random() * 2)],
    status: (['active', 'paused', 'review'][Math.floor(Math.random() * 3)] || 'active') as 'active' | 'paused' | 'review',
    invite_link: `https://t.me/test_group_${i + 1}`,
    entry_reward_enabled: Math.random() > 0.5,
    entry_reward_points: Math.floor(Math.random() * 10) + 5,
    is_bookmarked: Math.random() > 0.7,
    created_at: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
  })),
  pagination: {
    page: 1,
    per_page: 20,
    total: 100,
    total_pages: 5,
  },
}

