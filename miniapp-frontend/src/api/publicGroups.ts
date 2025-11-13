import { apiClient } from './http'
import type {
  PublicGroupActivity,
  PublicGroupListParams,
  PublicGroupSummary,
  BookmarkStatusResponse,
  PublicGroupActivityDetail,
  PublicGroupJoinResponse,
  PublicGroupHistoryItem,
} from '../types/publicGroups'

export async function listPublicGroups(params: PublicGroupListParams = {}): Promise<PublicGroupSummary[]> {
  const { data } = await apiClient.get<PublicGroupSummary[]>('/groups/public', { params })
  return data
}

export async function listBookmarkedGroups(): Promise<PublicGroupSummary[]> {
  const { data } = await apiClient.get<PublicGroupSummary[]>('/groups/public/bookmarks')
  return data
}

export async function listActivities(): Promise<PublicGroupActivity[]> {
  const { data } = await apiClient.get<PublicGroupActivity[]>('/groups/public/activities')
  return data
}

export async function getActivityDetail(activityId: number): Promise<PublicGroupActivityDetail> {
  const { data } = await apiClient.get<PublicGroupActivityDetail>(`/groups/public/activities/${activityId}`)
  return data
}

export async function listHistory(params: { limit?: number } = {}): Promise<PublicGroupHistoryItem[]> {
  const { data } = await apiClient.get<PublicGroupHistoryItem[]>('/groups/public/history', { params })
  return data
}

export async function bookmarkGroup(groupId: number): Promise<BookmarkStatusResponse> {
  const { data } = await apiClient.post<BookmarkStatusResponse>(`/groups/public/${groupId}/bookmark`)
  return data
}

export async function unbookmarkGroup(groupId: number): Promise<BookmarkStatusResponse> {
  const { data } = await apiClient.delete<BookmarkStatusResponse>(`/groups/public/${groupId}/bookmark`)
  return data
}

export async function joinPublicGroup(groupId: number): Promise<PublicGroupJoinResponse> {
  const { data } = await apiClient.post<PublicGroupJoinResponse>(`/groups/public/${groupId}/join`)
  return data
}

export async function trackGroupEvent(
  groupId: number,
  eventType: 'view' | 'click' | 'join',
  context?: Record<string, unknown>,
): Promise<void> {
  await apiClient.post(`/groups/public/${groupId}/events`, {
    event_type: eventType,
    context,
  })
}
