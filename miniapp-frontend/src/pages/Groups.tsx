import { useMemo, useState, type ReactElement, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

import { useAuth } from '../providers/AuthProvider'
import { usePublicGroups } from '../hooks/usePublicGroups'
import { bookmarkGroup, unbookmarkGroup, trackGroupEvent } from '../api/publicGroups'
import GroupCard from '../components/GroupCard'
import LoadingSkeleton from '../components/LoadingSkeleton'
import ErrorNotice from '../components/ErrorNotice'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { openTelegramLink } from '../utils/telegram'
import type { PublicGroupSummary } from '../types/publicGroups'

const MAX_GROUPS = 50

export default function Groups(): ReactElement {
  const auth = useAuth()
  const queryClient = useQueryClient()

  const [searchInput, setSearchInput] = useState('')
  const [filters, setFilters] = useState<{ q: string; tags: string[] }>({ q: '', tags: [] })
  const [showBookmarkedOnly, setShowBookmarkedOnly] = useState(false)

  const groupsQuery = usePublicGroups(
    {
      limit: MAX_GROUPS,
      sort: 'members',
      q: filters.q ? filters.q : undefined,
      tags: filters.tags.length ? filters.tags : undefined,
    },
    { enabled: auth.status === 'authenticated' },
  )

  const tags = useMemo(() => {
    const tagSet = new Set<string>()
    groupsQuery.data?.forEach((group) => {
      group.tags.forEach((tag) => tagSet.add(tag))
    })
    return Array.from(tagSet).sort()
  }, [groupsQuery.data])

  const filteredGroups = useMemo(() => {
    let list: PublicGroupSummary[] = groupsQuery.data ?? []
    if (showBookmarkedOnly) {
      list = list.filter((group) => group.is_bookmarked)
    }
    return list
  }, [groupsQuery.data, showBookmarkedOnly])

  const bookmarkMutation = useMutation({
    mutationFn: async ({ groupId, nextValue }: { groupId: number; nextValue: boolean }) => {
      if (nextValue) {
        return bookmarkGroup(groupId)
      }
      return unbookmarkGroup(groupId)
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['public-groups'] })
      void queryClient.invalidateQueries({ queryKey: ['public-groups', 'bookmarks'] })
    },
  })

  const handleBookmarkToggle = useCallback(
    (groupId: number, nextValue: boolean) => {
      bookmarkMutation.mutate({ groupId, nextValue })
    },
    [bookmarkMutation],
  )

  const handleOpenGroup = useCallback((group: PublicGroupSummary, source: string) => {
    openTelegramLink(group.invite_link)
    trackGroupEvent(group.id, 'click', { source }).catch(() => undefined)
  }, [])

  const toggleTag = useCallback(
    (tag: string) => {
      setFilters((prev) => {
        const exists = prev.tags.includes(tag)
        const tags = exists ? prev.tags.filter((item) => item !== tag) : [...prev.tags, tag]
        return { ...prev, tags }
      })
    },
    [setFilters],
  )

  const submitSearch = (event: React.FormEvent) => {
    event.preventDefault()
    setFilters((prev) => ({ ...prev, q: searchInput.trim() }))
  }

  const resetFilters = () => {
    setSearchInput('')
    setFilters({ q: '', tags: [] })
    setShowBookmarkedOnly(false)
  }

  return (
    <div className="container mx-auto space-y-8 p-6 lg:p-8">
      <header className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="space-y-2">
          <h1 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
            群组列表
          </h1>
          <p className="text-muted-foreground sm:max-w-2xl">
            浏览和管理所有公开群组，支持搜索、筛选和收藏
          </p>
        </div>
        <Link
          to="/"
          className="rounded-lg border border-border bg-background px-4 py-2 text-sm font-medium transition-colors hover:bg-accent"
        >
          返回首页
        </Link>
      </header>

      <Card>
        <CardHeader>
          <CardTitle>搜索与筛选</CardTitle>
          <CardDescription>使用关键词搜索或标签筛选群组</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <form onSubmit={submitSearch} className="flex flex-col gap-3 sm:flex-row">
            <input
              value={searchInput}
              onChange={(event) => setSearchInput(event.target.value)}
              placeholder="輸入名稱或描述關鍵字"
              className="flex-1 rounded-lg border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            />
            <div className="flex items-center gap-3">
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={showBookmarkedOnly}
                  onChange={(event) => setShowBookmarkedOnly(event.target.checked)}
                  className="h-4 w-4 rounded border-input"
                />
                只顯示收藏
              </label>
              <button
                type="submit"
                className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
              >
                搜尋
              </button>
              <button
                type="button"
                onClick={resetFilters}
                className="rounded-lg border border-border bg-background px-4 py-2 text-sm font-medium transition-colors hover:bg-accent"
              >
                清除
              </button>
            </div>
          </form>

          {tags.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {tags.map((tag) => {
                const active = filters.tags.includes(tag)
                return (
                  <button
                    key={tag}
                    type="button"
                    onClick={() => toggleTag(tag)}
                    className={`rounded-full px-3 py-1 text-xs font-medium transition ${
                      active
                        ? 'bg-primary text-primary-foreground'
                        : 'border border-border bg-background hover:bg-accent'
                    }`}
                  >
                    #{tag}
                  </button>
                )
              })}
            </div>
          )}
        </CardContent>
      </Card>

      {groupsQuery.isLoading && <LoadingSkeleton lines={5} />}
      {groupsQuery.isError && (
        <ErrorNotice message="無法載入公開群資料" onRetry={() => groupsQuery.refetch()} />
      )}

      {!groupsQuery.isLoading && filteredGroups.length === 0 && (
        <Card>
          <CardContent className="py-12 text-center text-sm text-muted-foreground">
            目前沒有符合條件的公開群，請調整篩選條件。
          </CardContent>
        </Card>
      )}

      {filteredGroups.length > 0 && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {filteredGroups.map((group) => (
            <GroupCard
              key={group.id}
              group={group}
              onToggleBookmark={handleBookmarkToggle}
              onOpen={(item) => handleOpenGroup(item, 'groups-list')}
            />
          ))}
        </div>
      )}
    </div>
  )
}

