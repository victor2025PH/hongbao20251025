export interface PublicGroupSummary {
  id: number
  name: string
  description?: string | null
  language?: string | null
  tags: string[]
  invite_link: string
  cover_template?: string | null
  entry_reward_enabled: boolean
  entry_reward_points: number
  entry_reward_pool: number
  entry_reward_pool_max: number
  is_pinned: boolean
  pinned_until?: string | null
  status: string
  risk_score: number
  risk_flags: string[]
  members_count: number
  created_at?: string | null
  is_bookmarked: boolean
}

export interface PublicGroupListParams {
  limit?: number
  q?: string
  tags?: string[]
  sort?: 'default' | 'new' | 'members' | 'reward'
  include_review?: boolean
  language?: string
}

export interface ActivityFrontCard {
  title?: string
  subtitle?: string
  cta_label?: string
  cta_link?: string
  badge?: string
  priority?: number
  countdown_seconds?: number | null
  countdown_text?: string | null
  metrics?: string | null
}

export interface ActivityRuleItem {
  key: string
  label: string
  value?: number | string | null
  remaining?: number | null
}

export interface PublicGroupActivity {
  id: number
  name: string
  description?: string | null
  activity_type: string
  start_at?: string | null
  end_at?: string | null
  reward_points: number
  bonus_points: number
  highlight_slots: number
  highlight_enabled: boolean
  highlight_badge?: string | null
  headline?: string | null
  countdown_text?: string | null
  daily_cap?: number | null
  total_cap?: number | null
  remaining_daily?: number | null
  remaining_total?: number | null
  status: string
  time_left_seconds?: number | null
  config?: Record<string, unknown>
  front_priority: number
  has_participated: boolean
  front_card?: ActivityFrontCard
}

export interface BookmarkStatusResponse {
  bookmarked: boolean
}

export interface PublicGroupActivityDetail extends PublicGroupActivity {
  total_points: number
  eligible: boolean
  in_time_window: boolean
  rules: ActivityRuleItem[]
}

export interface PublicGroupJoinResponse {
  membership_created: boolean
  reward_claimed: boolean
  reward_points: number
  reward_status: string
  entry_reward_pool: number
  bonus_points: number
  bonus_details: Array<Record<string, unknown>>
}

export interface PublicGroupHistoryItem {
  group: PublicGroupSummary
  last_event_type: string
  last_event_at?: string | null
  last_context?: Record<string, unknown>
}
