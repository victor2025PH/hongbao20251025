import { useState, type ReactElement } from 'react'
import { Link } from 'react-router-dom'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Badge } from '../components/ui/badge'
import { ArrowLeft, Save, RefreshCw } from 'lucide-react'

export default function Settings(): ReactElement {
  const [settings, setSettings] = useState({
    apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api',
    enableNotifications: true,
    autoRefresh: false,
    refreshInterval: 30,
    theme: 'auto',
    language: 'zh-TW',
  })

  const [isSaving, setIsSaving] = useState(false)

  const handleSave = async () => {
    setIsSaving(true)
    // 模拟保存
    await new Promise((resolve) => setTimeout(resolve, 1000))
    setIsSaving(false)
    alert('设置已保存')
  }

  return (
    <div className="container mx-auto space-y-8 p-6 lg:p-8">
      {/* 返回按钮 */}
      <Link
        to="/"
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

      {/* API 配置 */}
      <Card>
        <CardHeader>
          <CardTitle>API 配置</CardTitle>
          <CardDescription>配置后端 API 连接地址</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label htmlFor="api-url" className="text-sm font-medium">
              API 基础地址
            </label>
            <input
              id="api-url"
              type="text"
              value={settings.apiBaseUrl}
              onChange={(e) => setSettings({ ...settings, apiBaseUrl: e.target.value })}
              className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              placeholder="http://localhost:8080/api"
            />
            <p className="text-xs text-muted-foreground">
              修改后需要刷新页面才能生效
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
              <label htmlFor="notifications" className="text-sm font-medium">
                启用通知
              </label>
              <p className="text-xs text-muted-foreground">
                接收系统重要事件通知
              </p>
            </div>
            <input
              id="notifications"
              type="checkbox"
              checked={settings.enableNotifications}
              onChange={(e) =>
                setSettings({ ...settings, enableNotifications: e.target.checked })
              }
              className="h-4 w-4 rounded border-input"
            />
          </div>
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <label htmlFor="auto-refresh" className="text-sm font-medium">
                自动刷新
              </label>
              <p className="text-xs text-muted-foreground">
                定期自动刷新数据
              </p>
            </div>
            <input
              id="auto-refresh"
              type="checkbox"
              checked={settings.autoRefresh}
              onChange={(e) => setSettings({ ...settings, autoRefresh: e.target.checked })}
              className="h-4 w-4 rounded border-input"
            />
          </div>
          {settings.autoRefresh && (
            <div className="space-y-2">
              <label htmlFor="refresh-interval" className="text-sm font-medium">
                刷新间隔（秒）
              </label>
              <input
                id="refresh-interval"
                type="number"
                min="10"
                max="300"
                value={settings.refreshInterval}
                onChange={(e) =>
                  setSettings({ ...settings, refreshInterval: Number(e.target.value) })
                }
                className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              />
            </div>
          )}
        </CardContent>
      </Card>

      {/* 界面设置 */}
      <Card>
        <CardHeader>
          <CardTitle>界面设置</CardTitle>
          <CardDescription>自定义界面外观和语言</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label htmlFor="theme" className="text-sm font-medium">
              主题模式
            </label>
            <select
              id="theme"
              value={settings.theme}
              onChange={(e) => setSettings({ ...settings, theme: e.target.value })}
              className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            >
              <option value="auto">自动</option>
              <option value="light">浅色</option>
              <option value="dark">深色</option>
            </select>
          </div>
          <div className="space-y-2">
            <label htmlFor="language" className="text-sm font-medium">
              语言
            </label>
            <select
              id="language"
              value={settings.language}
              onChange={(e) => setSettings({ ...settings, language: e.target.value })}
              className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            >
              <option value="zh-TW">繁體中文</option>
              <option value="zh-CN">简体中文</option>
              <option value="en">English</option>
            </select>
          </div>
        </CardContent>
      </Card>

      {/* 操作按钮 */}
      <div className="flex items-center justify-end gap-3">
        <button
          type="button"
          onClick={() => window.location.reload()}
          className="inline-flex items-center gap-2 rounded-lg border border-border bg-background px-4 py-2 text-sm font-medium transition-colors hover:bg-accent"
        >
          <RefreshCw className="h-4 w-4" />
          重置
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

