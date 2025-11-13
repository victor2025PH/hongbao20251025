import Link from 'next/link'
import type { ReactElement } from 'react'
import type { PublicGroupSummary } from '@/types/publicGroups'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

interface Props {
  group: PublicGroupSummary
  onToggleBookmark?: (groupId: number, nextValue: boolean) => void
  onOpen?: (group: PublicGroupSummary) => void
}

export function GroupCard({ group, onToggleBookmark, onOpen }: Props): ReactElement {
  const handleToggle = (e: React.MouseEvent) => {
    e.stopPropagation()
    if (onToggleBookmark) {
      onToggleBookmark(group.id, !group.is_bookmarked)
    }
  }

  const handleOpen = (e: React.MouseEvent) => {
    e.stopPropagation()
    if (onOpen) {
      onOpen(group)
    }
  }

  return (
    <Card className="transition-all duration-200 hover:shadow-lg">
      <CardHeader>
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1">
            <Link href={`/groups/${group.id}`}>
              <CardTitle className="text-lg hover:text-primary transition-colors">
                {group.name}
              </CardTitle>
            </Link>
            {group.language && (
              <p className="mt-1 text-xs uppercase tracking-wide text-muted-foreground">
                {group.language}
              </p>
            )}
          </div>
          <div className="flex items-center gap-2">
            {group.entry_reward_enabled && (
              <Badge variant="outline" className="border-red-300 text-red-700 dark:text-red-400">
                +{group.entry_reward_points} 星
              </Badge>
            )}
            <button
              type="button"
              onClick={handleToggle}
              className={`rounded-full border px-3 py-1 text-xs transition ${
                group.is_bookmarked
                  ? 'border-yellow-300 bg-yellow-100 text-yellow-700 dark:border-yellow-600 dark:bg-yellow-900/30 dark:text-yellow-400'
                  : 'border-border bg-background hover:bg-accent'
              }`}
            >
              {group.is_bookmarked ? '已收藏' : '收藏'}
            </button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {group.description && (
          <p className="text-sm text-muted-foreground line-clamp-2">{group.description}</p>
        )}

        {onOpen && (
          <div className="flex justify-end">
            <button
              type="button"
              onClick={handleOpen}
              className="rounded-lg border border-border bg-background px-3 py-1.5 text-xs font-medium transition-colors hover:bg-accent"
            >
              開啟群組
            </button>
          </div>
        )}

        <div className="flex flex-wrap items-center gap-2 text-xs">
          {group.tags.slice(0, 4).map((tag) => (
            <Badge key={tag} variant="secondary" className="text-xs">
              #{tag}
            </Badge>
          ))}
          <span className="ml-auto text-muted-foreground">
            成員 {group.members_count.toLocaleString()}
          </span>
        </div>
      </CardContent>
    </Card>
  )
}

export default GroupCard
