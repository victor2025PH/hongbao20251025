'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { LayoutDashboard, Users, Settings, FileSearch, Menu, X, Package, ListTodo, Gift, User, Wallet, LogOut } from 'lucide-react'
import { useState } from 'react'
import { useAuth } from '@/providers/AuthProvider'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { getTelegramInitData } from '@/utils/telegram'
import { useQuery } from '@tanstack/react-query'

const navItems = [
  { href: '/', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/redpacket', label: '红包功能', icon: Gift },
  { href: '/tasks', label: '任务列表', icon: ListTodo },
  { href: '/groups', label: '群组列表', icon: Users },
  { href: '/stats', label: '红包统计', icon: Package },
  { href: '/logs', label: '日志中心', icon: FileSearch },
  { href: '/settings', label: '设置', icon: Settings },
]

export function Navbar() {
  const pathname = usePathname()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const auth = useAuth()
  
  // 获取 Telegram 用户头像 URL
  const getAvatarUrl = () => {
    if (typeof window === 'undefined') return null
    const unsafe = (window as any)?.Telegram?.WebApp?.initDataUnsafe
    if (unsafe?.user?.photo_url) {
      return unsafe.user.photo_url
    }
    // 如果没有头像，使用默认头像生成 URL（基于用户 ID）
    if (auth.user?.tgId) {
      // Telegram 默认头像模式：https://api.telegram.org/file/bot<token>/photos/<file_id>
      // 简化处理：使用用户名首字母或默认图标
      return null
    }
    return null
  }
  
  // 获取用户显示名称
  const getDisplayName = () => {
    if (auth.user?.username) {
      return `@${auth.user.username}`
    }
    if (auth.user?.tgId) {
      return `用户 ${auth.user.tgId}`
    }
    return '未登录'
  }
  
  // 获取头像首字母（用作后备显示）
  const getInitials = () => {
    if (auth.user?.username) {
      return auth.user.username.charAt(0).toUpperCase()
    }
    if (auth.user?.tgId) {
      return String(auth.user.tgId).charAt(0)
    }
    return '?'
  }
  
  const avatarUrl = getAvatarUrl()
  const displayName = getDisplayName()

  return (
    <nav className="sticky top-0 z-50 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
              <LayoutDashboard className="h-5 w-5" />
            </div>
            <span className="text-lg font-semibold">红包系统</span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex md:items-center md:gap-1">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = pathname === item.href || (item.href !== '/' && pathname?.startsWith(item.href))
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-primary text-primary-foreground'
                      : 'text-muted-foreground hover:bg-accent hover:text-foreground'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  {item.label}
                </Link>
              )
            })}
          </div>

          {/* User Info (Desktop) */}
          {auth.status === 'authenticated' && auth.user && (
            <UserProfileDropdown
              avatarUrl={avatarUrl}
              displayName={displayName}
              initials={getInitials()}
              user={auth.user}
            />
          )}

          {/* Mobile Menu Button */}
          <button
            type="button"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden rounded-lg p-2 text-muted-foreground hover:bg-accent"
          >
            {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-border py-4">
            {/* User Info (Mobile) */}
            {auth.status === 'authenticated' && auth.user && (
              <UserProfileDropdown
                avatarUrl={avatarUrl}
                displayName={displayName}
                initials={getInitials()}
                user={auth.user}
                mobile
              />
            )}
            <div className="space-y-1">
              {navItems.map((item) => {
                const Icon = item.icon
                const isActive = pathname === item.href || (item.href !== '/' && pathname?.startsWith(item.href))
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    onClick={() => setMobileMenuOpen(false)}
                    className={`flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                      isActive
                        ? 'bg-primary text-primary-foreground'
                        : 'text-muted-foreground hover:bg-accent hover:text-foreground'
                    }`}
                  >
                    <Icon className="h-4 w-4" />
                    {item.label}
                  </Link>
                )
              })}
            </div>
          </div>
        )}
      </div>
    </nav>
  )
}

// 用户资料下拉菜单组件
function UserProfileDropdown({
  avatarUrl,
  displayName,
  initials,
  user,
  mobile = false,
}: {
  avatarUrl: string | null
  displayName: string
  initials: string
  user: { tgId: number; username?: string | null; isAdmin: boolean }
  mobile?: boolean
}) {
  const API_BASE = process.env.NEXT_PUBLIC_ADMIN_API_BASE_URL || 'http://localhost:8001'
  
  // 查询用户余额
  const { data: balance, isLoading: balanceLoading } = useQuery({
    queryKey: ['user-balance', user.tgId],
    queryFn: async () => {
      const response = await fetch(`${API_BASE}/admin/api/v1/redpacket/balance`, {
        credentials: 'include',
      })
      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: '查询失败' }))
        throw new Error(error.detail || '查询失败')
      }
      return response.json()
    },
    enabled: !!user.tgId,
    retry: false,
  })

  const handleLogout = () => {
    // 清除认证信息
    window.location.href = '/'
  }

  const content = (
    <DropdownMenuContent align="end" className="w-64">
      <DropdownMenuLabel className="flex flex-col gap-1">
        <div className="flex items-center gap-2">
          <Avatar className="h-10 w-10">
            {avatarUrl ? (
              <AvatarImage src={avatarUrl} alt={displayName} />
            ) : null}
            <AvatarFallback className="bg-primary text-primary-foreground">
              {initials}
            </AvatarFallback>
          </Avatar>
          <div className="flex flex-col flex-1">
            <span className="text-sm font-medium">{displayName}</span>
            {user.isAdmin && (
              <span className="text-xs text-muted-foreground">管理员</span>
            )}
          </div>
        </div>
      </DropdownMenuLabel>
      <DropdownMenuSeparator />
      <DropdownMenuLabel className="text-xs text-muted-foreground">
        登录信息
      </DropdownMenuLabel>
      <DropdownMenuItem className="flex flex-col items-start gap-1 cursor-default">
        <span className="text-xs text-muted-foreground">Telegram ID</span>
        <span className="text-sm font-mono">{user.tgId}</span>
      </DropdownMenuItem>
      {user.username && (
        <DropdownMenuItem className="flex flex-col items-start gap-1 cursor-default">
          <span className="text-xs text-muted-foreground">用户名</span>
          <span className="text-sm">@{user.username}</span>
        </DropdownMenuItem>
      )}
      <DropdownMenuSeparator />
      <DropdownMenuLabel className="text-xs text-muted-foreground flex items-center gap-2">
        <Wallet className="h-3 w-3" />
        余额信息
      </DropdownMenuLabel>
      {balanceLoading ? (
        <DropdownMenuItem className="cursor-default">
          <span className="text-xs text-muted-foreground">加载中...</span>
        </DropdownMenuItem>
      ) : balance ? (
        <>
          <DropdownMenuItem className="flex flex-col items-start gap-1 cursor-default">
            <span className="text-xs text-muted-foreground">USDT</span>
            <span className="text-sm font-medium">{balance.balance_usdt || '0.00'}</span>
          </DropdownMenuItem>
          <DropdownMenuItem className="flex flex-col items-start gap-1 cursor-default">
            <span className="text-xs text-muted-foreground">TON</span>
            <span className="text-sm font-medium">{balance.balance_ton || '0.00'}</span>
          </DropdownMenuItem>
          <DropdownMenuItem className="flex flex-col items-start gap-1 cursor-default">
            <span className="text-xs text-muted-foreground">POINT</span>
            <span className="text-sm font-medium">{balance.balance_point || '0'}</span>
          </DropdownMenuItem>
        </>
      ) : (
        <DropdownMenuItem className="cursor-default">
          <span className="text-xs text-red-500">无法加载余额信息</span>
        </DropdownMenuItem>
      )}
      <DropdownMenuSeparator />
      <DropdownMenuItem onClick={handleLogout} className="text-red-600 cursor-pointer">
        <LogOut className="h-4 w-4 mr-2" />
        退出登录
      </DropdownMenuItem>
    </DropdownMenuContent>
  )

  if (mobile) {
    return (
      <div className="px-3 py-3 mb-4 bg-muted/50 rounded-lg">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button className="flex items-center gap-3 w-full text-left">
              <Avatar className="h-10 w-10">
                {avatarUrl ? (
                  <AvatarImage src={avatarUrl} alt={displayName} />
                ) : null}
                <AvatarFallback className="bg-primary text-primary-foreground">
                  {initials}
                </AvatarFallback>
              </Avatar>
              <div className="flex flex-col flex-1">
                <span className="text-sm font-medium">{displayName}</span>
                {user.isAdmin && (
                  <span className="text-xs text-muted-foreground">管理员</span>
                )}
              </div>
            </button>
          </DropdownMenuTrigger>
          {content}
        </DropdownMenu>
      </div>
    )
  }

  return (
    <div className="hidden md:flex md:items-center md:gap-3 ml-4 pl-4 border-l border-border">
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <button className="flex items-center gap-2 hover:opacity-80 transition-opacity">
            <Avatar className="h-8 w-8">
              {avatarUrl ? (
                <AvatarImage src={avatarUrl} alt={displayName} />
              ) : null}
              <AvatarFallback className="bg-primary text-primary-foreground text-xs">
                {initials}
              </AvatarFallback>
            </Avatar>
            <div className="flex flex-col">
              <span className="text-sm font-medium">{displayName}</span>
              {user.isAdmin && (
                <span className="text-xs text-muted-foreground">管理员</span>
              )}
            </div>
          </button>
        </DropdownMenuTrigger>
        {content}
      </DropdownMenu>
    </div>
  )
}

