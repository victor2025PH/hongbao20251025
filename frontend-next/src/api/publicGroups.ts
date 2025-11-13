import { miniappApiClient } from './miniapp'
import type {
  PublicGroupActivity,
  PublicGroupListParams,
  PublicGroupSummary,
  BookmarkStatusResponse,
  PublicGroupActivityDetail,
  PublicGroupJoinResponse,
  PublicGroupHistoryItem,
} from '@/types/publicGroups'

export async function listPublicGroups(params: PublicGroupListParams = {}): Promise<PublicGroupSummary[]> {
  const { data } = await miniappApiClient.get<PublicGroupSummary[]>('/v1/groups/public', { params })
  return data
}

export async function listBookmarkedGroups(): Promise<PublicGroupSummary[]> {
  const { data } = await miniappApiClient.get<PublicGroupSummary[]>('/v1/groups/public/bookmarks')
  return data
}

export async function getPublicGroupDetail(groupId: number): Promise<PublicGroupSummary> {
  const { data } = await miniappApiClient.get<PublicGroupSummary>(`/v1/groups/public/${groupId}`)
  return data
}

export async function listActivities(): Promise<PublicGroupActivity[]> {
  const { data } = await miniappApiClient.get<PublicGroupActivity[]>('/v1/groups/public/activities')
  return data
}

export async function getActivityDetail(activityId: number): Promise<PublicGroupActivityDetail> {
  const { data } = await miniappApiClient.get<PublicGroupActivityDetail>(`/v1/groups/public/activities/${activityId}`)
  return data
}

export async function listHistory(params: { limit?: number } = {}): Promise<PublicGroupHistoryItem[]> {
  const { data } = await miniappApiClient.get<PublicGroupHistoryItem[]>('/v1/groups/public/history', { params })
  return data
}

export async function bookmarkGroup(groupId: number): Promise<BookmarkStatusResponse> {
  const { data } = await miniappApiClient.post<BookmarkStatusResponse>(`/v1/groups/public/${groupId}/bookmark`)
  return data
}

export async function unbookmarkGroup(groupId: number): Promise<BookmarkStatusResponse> {
  const { data } = await miniappApiClient.delete<BookmarkStatusResponse>(`/v1/groups/public/${groupId}/bookmark`)
  return data
}

export async function joinPublicGroup(groupId: number): Promise<PublicGroupJoinResponse> {
  const { data } = await miniappApiClient.post<PublicGroupJoinResponse>(`/v1/groups/public/${groupId}/join`)
  return data
}

export async function trackGroupEvent(
  groupId: number,
  eventType: 'view' | 'click' | 'join',
  context?: Record<string, unknown>,
): Promise<void> {
  await miniappApiClient.post(`/v1/groups/public/${groupId}/events`, {
    event_type: eventType,
    context,
  })
}
