import { useQuery, type UseQueryOptions } from '@tanstack/react-query'

import { listPublicGroups, listActivities, listBookmarkedGroups, listHistory } from '../api/publicGroups'
import type {
  PublicGroupListParams,
  PublicGroupSummary,
  PublicGroupActivity,
  PublicGroupHistoryItem,
} from '../types/publicGroups'

type GroupsQueryOptions = Omit<
  UseQueryOptions<PublicGroupSummary[], Error, PublicGroupSummary[], [string, PublicGroupListParams]>,
  'queryKey' | 'queryFn'
>

type ActivitiesQueryOptions = Omit<
  UseQueryOptions<PublicGroupActivity[], Error, PublicGroupActivity[], [string]>,
  'queryKey' | 'queryFn'
>

type BookmarkQueryOptions = Omit<
  UseQueryOptions<PublicGroupSummary[], Error, PublicGroupSummary[], [string, string]>,
  'queryKey' | 'queryFn'
>

type HistoryQueryOptions = Omit<
  UseQueryOptions<PublicGroupHistoryItem[], Error, PublicGroupHistoryItem[], [string, { limit?: number }]>,
  'queryKey' | 'queryFn'
>

export function usePublicGroups(params: PublicGroupListParams = {}, options?: GroupsQueryOptions) {
  return useQuery<PublicGroupSummary[], Error, PublicGroupSummary[], [string, PublicGroupListParams]>({
    queryKey: ['public-groups', params],
    queryFn: () => listPublicGroups(params),
    ...options,
  })
}

export function usePublicGroupActivities(options?: ActivitiesQueryOptions) {
  return useQuery<PublicGroupActivity[], Error, PublicGroupActivity[], [string]>({
    queryKey: ['public-group-activities'],
    queryFn: () => listActivities(),
    ...options,
  })
}

export function useBookmarkedGroups(options?: BookmarkQueryOptions) {
  return useQuery<PublicGroupSummary[], Error, PublicGroupSummary[], [string, string]>({
    queryKey: ['public-groups', 'bookmarks'],
    queryFn: () => listBookmarkedGroups(),
    ...options,
  })
}

export function usePublicGroupHistory(params: { limit?: number } = {}, options?: HistoryQueryOptions) {
  return useQuery<PublicGroupHistoryItem[], Error, PublicGroupHistoryItem[], [string, { limit?: number }]>({
    queryKey: ['public-group-history', params],
    queryFn: () => listHistory(params),
    ...options,
  })
}
