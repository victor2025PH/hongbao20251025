/**
 * 用户 Mock 数据
 */

export interface UserInfo {
  id: number
  username: string
  tg_id: number
  roles: string[]
  is_admin: boolean
}

export const MOCK_USER: UserInfo = {
  id: 1,
  username: 'admin',
  tg_id: 123456789,
  roles: ['admin'],
  is_admin: true,
}

