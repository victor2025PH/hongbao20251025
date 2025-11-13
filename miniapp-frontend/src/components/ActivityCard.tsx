import type { ReactElement } from 'react'
import type { PublicGroupActivity } from '../types/publicGroups'

interface Props {
  activity: PublicGroupActivity
  onSelect?: (activity: PublicGroupActivity) => void
}

export function ActivityCard({ activity, onSelect }: Props): ReactElement {
  const handleClick = () => {
    if (onSelect) {
      onSelect(activity)
    }
  }

  const participated = activity.has_participated

  return (
    <button
      type="button"
      onClick={handleClick}
      className="grid gap-3 rounded-2xl border border-brand-primary/30 bg-brand-primary/10 p-5 text-left transition hover:border-brand-primary/60 hover:bg-brand-primary/20 focus:outline-none focus:ring-2 focus:ring-brand-primary/60"
    >
      <header className="flex items-start justify-between gap-3">
        <div>
          <h3 className="text-lg font-semibold text-white">{activity.name}</h3>
          {activity.countdown_text && (
            <p className="text-xs text-brand-primary/90">{activity.countdown_text}</p>
          )}
        </div>
        <div className="flex items-center gap-2">
          {(activity.highlight_enabled || activity.highlight_badge) && (
            <span className="rounded-full bg-brand-secondary/30 px-3 py-1 text-xs font-semibold text-brand-secondary">
              {activity.highlight_badge ?? 'Highlight'}
            </span>
          )}
          {participated && (
            <span className="rounded-full bg-emerald-400/20 px-3 py-1 text-xs font-semibold text-emerald-300">
              已參與
            </span>
          )}
        </div>
      </header>

      {activity.headline && <p className="text-sm text-slate-200">{activity.headline}</p>}

      <footer className="flex flex-wrap items-center gap-3 text-xs text-slate-200">
        <span className="rounded-md bg-black/40 px-2 py-0.5">基礎 {activity.reward_points} 星</span>
        {activity.bonus_points > 0 && (
          <span className="rounded-md bg-black/40 px-2 py-0.5">加碼 +{activity.bonus_points} 星</span>
        )}
        {activity.remaining_daily != null && (
          <span className="rounded-md bg-black/40 px-2 py-0.5">今日剩餘 {activity.remaining_daily}</span>
        )}
        {activity.remaining_total != null && (
          <span className="rounded-md bg-black/40 px-2 py-0.5">總剩餘 {activity.remaining_total}</span>
        )}
        <span className="ml-auto rounded-md bg-white/10 px-2 py-0.5 text-white/80">
          優先級 {activity.front_priority}
        </span>
      </footer>
    </button>
  )
}

export default ActivityCard
