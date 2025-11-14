'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

import { getSettings, updateSettings, type SystemSettings, type SettingsUpdate } from '@/lib/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import LoadingSkeleton from '@/components/shared/LoadingSkeleton'
import ErrorNotice from '@/components/shared/ErrorNotice'
import { ArrowLeft, Save, RefreshCw, ExternalLink } from 'lucide-react'

export default function SettingsPage() {
  const queryClient = useQueryClient()
  
  const { data: systemSettings, isLoading, error, refetch } = useQuery({
    queryKey: ['system-settings'],
    queryFn: getSettings,
  })

  const [localSettings, setLocalSettings] = useState<SettingsUpdate>({
    amount_limits: {},
    risk_control: {},
    notifications: {},
  })

  const [isSaving, setIsSaving] = useState(false)
  const [saveMessage, setSaveMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  useEffect(() => {
    if (systemSettings) {
      setLocalSettings({
        amount_limits: {
          max_single: systemSettings.amount_limits.max_single,
          min_single: systemSettings.amount_limits.min_single,
          daily_total: systemSettings.amount_limits.daily_total,
        },
        risk_control: {
          enable_rate_limit: systemSettings.risk_control.enable_rate_limit,
          enable_blacklist: systemSettings.risk_control.enable_blacklist,
          max_per_user_per_day: systemSettings.risk_control.max_per_user_per_day,
        },
        notifications: {
          notify_on_failure: systemSettings.notifications.notify_on_failure,
          notify_on_critical: systemSettings.notifications.notify_on_critical,
        },
      })
    }
  }, [systemSettings])

  const updateMutation = useMutation({
    mutationFn: updateSettings,
    onSuccess: (data) => {
      setSaveMessage({ type: 'success', text: data.message || '设置已保存' })
      void queryClient.invalidateQueries({ queryKey: ['system-settings'] })
      setTimeout(() => setSaveMessage(null), 3000)
    },
    onError: (error: unknown) => {
      const apiError = error as { response?: { data?: { detail?: string } }; message?: string }
      setSaveMessage({
        type: 'error',
        text: apiError?.response?.data?.detail || apiError?.message || '保存失败，请重试',
      })
      setTimeout(() => setSaveMessage(null), 5000)
    },
  })

  const handleSave = async () => {
    setIsSaving(true)
    setSaveMessage(null)
    try {
      await updateMutation.mutateAsync(localSettings)
    } finally {
      setIsSaving(false)
    }
  }

  if (isLoading) {
    return (
      <div className="container mx-auto space-y-8 p-6 lg:p-8">
        <LoadingSkeleton lines={10} />
      </div>
    )
  }

  if (error) {
    return (
      <div className="container mx-auto space-y-8 p-6 lg:p-8">
        <ErrorNotice message="無法載入系統設置" onRetry={() => refetch()} />
      </div>
    )
  }

  return (
    <div className="container mx-auto space-y-8 p-6 lg:p-8">
      <Link
        href="/"
        className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground"
      >
        <ArrowLeft className="h-4 w-4" />
        返回首页
      </Link>

      <header className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
          系统设置
        </h1>
        <p className="text-muted-foreground sm:max-w-2xl">
          配置系统参数、通知偏好和界面选项
        </p>
      </header>

      {saveMessage && (
        <Card className={saveMessage.type === 'success' ? 'border-green-300 bg-green-50 dark:border-green-700 dark:bg-green-950/20' : 'border-red-300 bg-red-50 dark:border-red-700 dark:bg-red-950/20'}>
          <CardContent className="pt-6">
            <p className={`text-sm ${saveMessage.type === 'success' ? 'text-green-800 dark:text-green-200' : 'text-red-800 dark:text-red-200'}`}>
              {saveMessage.text}
            </p>
          </CardContent>
        </Card>
      )}

      {/* 金额限制 */}
      <Card>
        <CardHeader>
          <CardTitle>金额限制</CardTitle>
          <CardDescription>配置红包金额的上限和下限</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label htmlFor="max-single" className="text-sm font-medium">
              单个红包最大金额
            </label>
            <input
              id="max-single"
              type="number"
              step="0.01"
              min="0"
              value={localSettings.amount_limits?.max_single ?? 0}
              onChange={(e) =>
                setLocalSettings({
                  ...localSettings,
                  amount_limits: {
                    ...localSettings.amount_limits,
                    max_single: parseFloat(e.target.value) || 0,
                  },
                })
              }
              className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            />
            <p className="text-xs text-muted-foreground">
              单个红包允许的最大金额（单位：元）
            </p>
          </div>
          <div className="space-y-2">
            <label htmlFor="min-single" className="text-sm font-medium">
              单个红包最小金额
            </label>
            <input
              id="min-single"
              type="number"
              step="0.01"
              min="0"
              value={localSettings.amount_limits?.min_single ?? 0}
              onChange={(e) =>
                setLocalSettings({
                  ...localSettings,
                  amount_limits: {
                    ...localSettings.amount_limits,
                    min_single: parseFloat(e.target.value) || 0,
                  },
                })
              }
              className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            />
            <p className="text-xs text-muted-foreground">
              单个红包允许的最小金额（单位：元）
            </p>
          </div>
          <div className="space-y-2">
            <label htmlFor="daily-total" className="text-sm font-medium">
              每日总限额
            </label>
            <input
              id="daily-total"
              type="number"
              step="0.01"
              min="0"
              value={localSettings.amount_limits?.daily_total ?? 0}
              onChange={(e) =>
                setLocalSettings({
                  ...localSettings,
                  amount_limits: {
                    ...localSettings.amount_limits,
                    daily_total: parseFloat(e.target.value) || 0,
                  },
                })
              }
              className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            />
            <p className="text-xs text-muted-foreground">
              系统每日允许发送的红包总金额（单位：元）
            </p>
          </div>
        </CardContent>
      </Card>

      {/* 风控策略 */}
      <Card>
        <CardHeader>
          <CardTitle>风控策略</CardTitle>
          <CardDescription>配置风险控制相关参数</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <label htmlFor="enable-rate-limit" className="text-sm font-medium">
                启用频率限制
              </label>
              <p className="text-xs text-muted-foreground">
                限制用户发送红包的频率
              </p>
            </div>
            <input
              id="enable-rate-limit"
              type="checkbox"
              checked={localSettings.risk_control?.enable_rate_limit ?? false}
              onChange={(e) =>
                setLocalSettings({
                  ...localSettings,
                  risk_control: {
                    ...localSettings.risk_control,
                    enable_rate_limit: e.target.checked,
                  },
                })
              }
              className="h-4 w-4 rounded border-input"
            />
          </div>
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <label htmlFor="enable-blacklist" className="text-sm font-medium">
                启用黑名单
              </label>
              <p className="text-xs text-muted-foreground">
                阻止黑名单用户发送红包
              </p>
            </div>
            <input
              id="enable-blacklist"
              type="checkbox"
              checked={localSettings.risk_control?.enable_blacklist ?? false}
              onChange={(e) =>
                setLocalSettings({
                  ...localSettings,
                  risk_control: {
                    ...localSettings.risk_control,
                    enable_blacklist: e.target.checked,
                  },
                })
              }
              className="h-4 w-4 rounded border-input"
            />
          </div>
          <div className="space-y-2">
            <label htmlFor="max-per-user-per-day" className="text-sm font-medium">
              每用户每日最大发送数
            </label>
            <input
              id="max-per-user-per-day"
              type="number"
              min="0"
              value={localSettings.risk_control?.max_per_user_per_day ?? 0}
              onChange={(e) =>
                setLocalSettings({
                  ...localSettings,
                  risk_control: {
                    ...localSettings.risk_control,
                    max_per_user_per_day: parseInt(e.target.value, 10) || 0,
                  },
                })
              }
              className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            />
            <p className="text-xs text-muted-foreground">
              单个用户每日最多可发送的红包数量
            </p>
          </div>
        </CardContent>
      </Card>

      {/* 通知设置 */}
      <Card>
        <CardHeader>
          <CardTitle>通知设置</CardTitle>
          <CardDescription>管理系统通知偏好</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <label htmlFor="notify-on-failure" className="text-sm font-medium">
                失败时通知管理员
              </label>
              <p className="text-xs text-muted-foreground">
                当红包发送失败时通知管理员
              </p>
            </div>
            <input
              id="notify-on-failure"
              type="checkbox"
              checked={localSettings.notifications?.notify_on_failure ?? false}
              onChange={(e) =>
                setLocalSettings({
                  ...localSettings,
                  notifications: {
                    ...localSettings.notifications,
                    notify_on_failure: e.target.checked,
                  },
                })
              }
              className="h-4 w-4 rounded border-input"
            />
          </div>
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <label htmlFor="notify-on-critical" className="text-sm font-medium">
                严重错误时通知
              </label>
              <p className="text-xs text-muted-foreground">
                当出现严重系统错误时通知管理员
              </p>
            </div>
            <input
              id="notify-on-critical"
              type="checkbox"
              checked={localSettings.notifications?.notify_on_critical ?? false}
              onChange={(e) =>
                setLocalSettings({
                  ...localSettings,
                  notifications: {
                    ...localSettings.notifications,
                    notify_on_critical: e.target.checked,
                  },
                })
              }
              className="h-4 w-4 rounded border-input"
            />
          </div>
        </CardContent>
      </Card>

      {/* 操作按钮 */}
      <div className="flex items-center justify-end gap-3">
        <a
          href="http://localhost:8000/admin/dashboard"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 rounded-lg border border-border bg-background px-4 py-2 text-sm font-medium transition-colors hover:bg-accent"
        >
          <ExternalLink className="h-4 w-4" />
          旧版后台
        </a>
        <button
          type="button"
          onClick={() => refetch()}
          className="inline-flex items-center gap-2 rounded-lg border border-border bg-background px-4 py-2 text-sm font-medium transition-colors hover:bg-accent"
        >
          <RefreshCw className="h-4 w-4" />
          刷新
        </button>
        <button
          type="button"
          onClick={handleSave}
          disabled={isSaving}
          className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90 disabled:opacity-50"
        >
          <Save className="h-4 w-4" />
          {isSaving ? '保存中...' : '保存设置'}
        </button>
      </div>
    </div>
  )
}
