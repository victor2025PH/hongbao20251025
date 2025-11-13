import { useEffect, useMemo, useState, type ReactElement } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'

import { getActivityDetail, joinPublicGroup } from '../api/publicGroups'
import type { PublicGroupActivityDetail, PublicGroupJoinResponse } from '../types/publicGroups'
import LoadingSkeleton from './LoadingSkeleton'
import ErrorNotice from './ErrorNotice'
import { openTelegramLink } from '../utils/telegram'

interface Props {
  activityId: number | null
  onClose: () => void
  onParticipated?: () => void
}

export function ActivityDetailDialog({ activityId, onClose, onParticipated }: Props): ReactElement | null {
  const [feedback, setFeedback] = useState<string | null>(null)

  const detailQuery = useQuery<PublicGroupActivityDetail, Error, PublicGroupActivityDetail, [string, number]>(
    {
      queryKey: ['activity-detail', activityId ?? 0],
      queryFn: () => getActivityDetail(activityId as number),
      enabled: activityId !== null,
      staleTime: 30_000,
    },
  )

  useEffect(() => {
    setFeedback(null)
  }, [activityId])

  const detail = detailQuery.data

  const ctaLink = detail?.front_card?.cta_link
  const ctaLabel = detail?.front_card?.cta_label ?? (ctaLink ? '前往活動' : '了解活動流程')

  const parsedGroupId = useMemo(() => {
    if (!detail || !detail.config) return undefined
    const raw = (detail.config as Record<string, unknown>)['group_id'] ?? (detail.config as Record<string, unknown>)['groupId']
    if (typeof raw === 'number' && Number.isFinite(raw)) {
      return raw
    }
    if (typeof raw === 'string') {
      const num = Number.parseInt(raw, 10)
      if (Number.isFinite(num)) {
        return num
      }
    }
    return undefined
  }, [detail])

  const joinMutation = useMutation<PublicGroupJoinResponse, Error, number>({
    mutationFn: (groupId: number) => joinPublicGroup(groupId),
    onSuccess: (result) => {
      const total = result.reward_points + (result.bonus_points ?? 0)
      const rewardSummary = total > 0 ? `成功領取 ${total} 星` : '已記錄參與'
      const extra = result.reward_status ? `（狀態：${result.reward_status}）` : ''
      setFeedback(`${rewardSummary}${extra}`)
      void detailQuery.refetch()
      onParticipated?.()
    },
    onError: (error) => {
      setFeedback(error.message || '標記參與時發生錯誤')
    },
  })

  if (activityId === null) {
    return null
  }

  const loading = detailQuery.isLoading
  const error = detailQuery.error

  const renderBody = () => {
    if (loading) {
      return <LoadingSkeleton lines={6} />
    }

    if (error) {
      return <ErrorNotice message="無法載入活動詳情" onRetry={() => detailQuery.refetch()} />
    }

    if (!detail) {
      return <p className="text-sm text-slate-300">找不到活動內容，請稍後再試。</p>
    }

    const ruleLabelMap: Record<string, string> = {
      reward_points: '基礎獎勵',
      bonus_points: '額外加碼',
      daily_cap: '每日名額',
      total_cap: '總名額',
    }

    return (
      <div className="grid gap-4">
        <header className="flex flex-col gap-2">
          <div className="flex items-start justify-between gap-3">
            <div>
              <h3 className="text-2xl font-semibold text-white">{detail.name}</h3>
              {detail.countdown_text && (
                <p className="text-sm text-brand-primary/80">{detail.countdown_text}</p>
              )}
            </div>
            <div className="flex flex-wrap justify-end gap-2 text-xs">
              {(detail.highlight_enabled || detail.highlight_badge) && (
                <span className="rounded-full bg-brand-secondary/30 px-3 py-1 font-semibold text-brand-secondary">
                  {detail.highlight_badge ?? 'Highlight'}
                </span>
              )}
              {detail.has_participated && (
                <span className="rounded-full bg-emerald-500/20 px-3 py-1 font-semibold text-emerald-200">
                  已參與
                </span>
              )}
              {!detail.in_time_window && (
                <span className="rounded-full bg-slate-500/30 px-3 py-1 font-semibold text-slate-200">
                  已超出活動時間
                </span>
              )}
            </div>
          </div>
          {detail.description && <p className="text-sm text-slate-200">{detail.description}</p>}
        </header>

        <section className="grid gap-3 rounded-xl border border-white/10 bg-black/40 p-4 text-sm text-slate-200">
          <div className="flex flex-wrap items-center gap-3 text-base text-white">
            <span>總計可得：<strong className="text-brand-secondary">{detail.total_points}</strong> 星</span>
            <span className="rounded-md bg-white/10 px-2 py-0.5 text-xs text-slate-200">
              基礎 {detail.reward_points} 星
            </span>
            {detail.bonus_points > 0 && (
              <span className="rounded-md bg-white/10 px-2 py-0.5 text-xs text-slate-200">加碼 +{detail.bonus_points} 星</span>
            )}
          </div>
          <p className="text-xs text-slate-400">
            {detail.eligible
              ? '符合條件即可參與並領取獎勵。'
              : detail.has_participated
                ? '您已參與過此活動，若需重領請等待下一輪或聯繫客服。'
                : '目前無法參與，可能因名額已滿或不在活動時間內。'}
          </p>
          <div className="flex flex-wrap gap-2 text-xs text-slate-300">
            {detail.remaining_daily != null && (
              <span className="rounded-md bg-white/5 px-2 py-0.5">今日剩餘 {detail.remaining_daily}</span>
            )}
            {detail.remaining_total != null && (
              <span className="rounded-md bg-white/5 px-2 py-0.5">總剩餘 {detail.remaining_total}</span>
            )}
          </div>
        </section>

        {detail.rules.length > 0 && (
          <section className="rounded-xl border border-white/10 bg-white/5 p-4">
            <h4 className="mb-3 text-sm font-semibold text-white/90">活動規則</h4>
            <ul className="grid gap-2 text-xs text-slate-200">
              {detail.rules.map((rule) => {
                const label = ruleLabelMap[rule.key] ?? rule.label ?? rule.key
                return (
                  <li key={`${rule.key}-${String(rule.value)}`} className="flex items-center justify-between gap-3">
                    <span className="font-medium text-white/90">{label}</span>
                    <span>
                      {rule.value ?? '—'}
                      {rule.remaining != null && `（剩餘 ${rule.remaining}）`}
                    </span>
                  </li>
                )}
              )}
            </ul>
          </section>
        )}

        {detail.front_card?.subtitle && (
          <section className="rounded-xl border border-brand-primary/20 bg-brand-primary/5 p-4 text-xs text-slate-100">
            <h4 className="mb-2 text-sm font-semibold text-brand-primary">活動說明</h4>
            <p>{detail.front_card.subtitle}</p>
            {detail.front_card.metrics && (
              <p className="mt-2 text-[11px] text-brand-primary/70">{detail.front_card.metrics}</p>
            )}
          </section>
        )}
      </div>
    )
  }

  const handleParticipateClick = () => {
    if (!detail) {
      return
    }
    if (ctaLink) {
      openTelegramLink(ctaLink)
    }
    if (!ctaLink) {
      setFeedback('請依照活動說明完成指定條件後，再點選「標記已完成」領取獎勵。')
    }
  }

  const handleJoinClick = () => {
    if (!parsedGroupId) {
      setFeedback('此活動未指定自動領取群組，請依說明手動完成。')
      return
    }
    joinMutation.mutate(parsedGroupId)
  }

  return (
    <div className="fixed inset-0 z-40 flex items-start justify-center overflow-y-auto bg-black/70 px-4 py-10">
      <div className="relative w-full max-w-xl rounded-3xl border border-white/10 bg-slate-950/95 p-6 shadow-2xl shadow-brand-primary/10 backdrop-blur-lg">
        <button
          type="button"
          onClick={onClose}
          className="absolute right-4 top-4 rounded-full border border-white/10 bg-white/10 px-2 py-1 text-xs text-white/70 transition hover:border-white/30 hover:bg-white/20"
        >
          關閉
        </button>

        {renderBody()}

        <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:justify-between">
          <div className="text-xs text-slate-400">
            點擊「{ctaLabel}」依照 Telegram 或網頁流程參與，完成後可用「標記已完成」同步狀態。
          </div>
          <div className="flex flex-col gap-2 sm:flex-row">
            <button
              type="button"
              onClick={handleParticipateClick}
              className="rounded-lg border border-brand-primary/50 bg-brand-primary/20 px-4 py-2 text-sm font-medium text-brand-primary transition hover:bg-brand-primary/30"
            >
              {ctaLabel}
            </button>
            <button
              type="button"
              onClick={handleJoinClick}
              disabled={joinMutation.isPending}
              className="rounded-lg border border-emerald-400/50 bg-emerald-400/20 px-4 py-2 text-sm font-medium text-emerald-200 transition hover:bg-emerald-400/30 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {joinMutation.isPending ? '同步中...' : '標記已完成'}
            </button>
          </div>
        </div>

        {feedback && (
          <div className="mt-4 rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-xs text-slate-100">
            {feedback}
          </div>
        )}
      </div>
    </div>
  )
}

export default ActivityDetailDialog

