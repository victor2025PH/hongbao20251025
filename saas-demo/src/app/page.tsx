import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Users,
  Activity,
  AlertCircle,
  Send,
  Clock,
  CheckCircle2,
  XCircle,
  ArrowUpRight,
  RefreshCw,
} from "lucide-react";

// 统计数据
const stats = [
  {
    label: "今日红包总数",
    value: "1,234",
    change: "+12.5%",
    trend: "up",
    icon: DollarSign,
    color: "text-red-600 dark:text-red-400",
  },
  {
    label: "成功发送",
    value: "1,189",
    change: "+8.3%",
    trend: "up",
    icon: CheckCircle2,
    color: "text-green-600 dark:text-green-400",
  },
  {
    label: "活跃用户",
    value: "8,542",
    change: "+15.2%",
    trend: "up",
    icon: Users,
    color: "text-blue-600 dark:text-blue-400",
  },
  {
    label: "错误/失败",
    value: "45",
    change: "-5.1%",
    trend: "down",
    icon: AlertCircle,
    color: "text-amber-600 dark:text-amber-400",
  },
];

// 最近任务
const recentTasks = [
  {
    id: "T001",
    type: "群发红包",
    status: "success",
    amount: "¥500",
    count: 50,
    time: "2 分钟前",
  },
  {
    id: "T002",
    type: "定时红包",
    status: "pending",
    amount: "¥200",
    count: 20,
    time: "5 分钟前",
  },
  {
    id: "T003",
    type: "个人红包",
    status: "success",
    amount: "¥100",
    count: 1,
    time: "10 分钟前",
  },
  {
    id: "T004",
    type: "群发红包",
    status: "failed",
    amount: "¥300",
    count: 30,
    time: "15 分钟前",
  },
  {
    id: "T005",
    type: "定时红包",
    status: "success",
    amount: "¥150",
    count: 15,
    time: "20 分钟前",
  },
];

// 系统日志
const systemLogs = [
  {
    level: "info",
    message: "红包任务 T001 执行成功",
    time: "14:32:15",
  },
  {
    level: "warning",
    message: "检测到异常请求，已自动拦截",
    time: "14:28:42",
  },
  {
    level: "info",
    message: "定时红包任务已创建",
    time: "14:25:10",
  },
  {
    level: "error",
    message: "红包发送失败：余额不足",
    time: "14:20:33",
  },
  {
    level: "info",
    message: "用户登录：admin@example.com",
    time: "14:15:08",
  },
];

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted/20">
      <div className="container mx-auto space-y-8 p-6 lg:p-8">
        {/* 顶部标题栏 */}
        <header className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="space-y-2">
            <h1 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
              红包系统控制台
            </h1>
            <p className="text-muted-foreground sm:max-w-2xl">
              实时监控红包发送状态、用户活跃度与系统运行情况
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline" className="gap-2">
              <RefreshCw className="h-4 w-4" />
              刷新数据
            </Button>
            <Button className="gap-2 bg-red-600 hover:bg-red-700 dark:bg-red-500 dark:hover:bg-red-600">
              <Send className="h-4 w-4" />
              发送红包
              <ArrowUpRight className="h-4 w-4" />
            </Button>
          </div>
        </header>

        {/* 统计卡片区 */}
        <section className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {stats.map((stat) => {
            const Icon = stat.icon;
            const isPositive = stat.trend === "up";
            return (
              <Card
                key={stat.label}
                className="border-border/70 shadow-sm transition-all duration-200 hover:-translate-y-1 hover:shadow-lg"
              >
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    {stat.label}
                  </CardTitle>
                  <Icon className={`h-5 w-5 ${stat.color}`} />
                </CardHeader>
                <CardContent>
                  <div className="flex items-baseline justify-between">
                    <p className="text-2xl font-bold">{stat.value}</p>
                    <Badge
                      variant={isPositive ? "default" : "secondary"}
                      className={`gap-1 text-xs font-medium ${
                        isPositive
                          ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                          : "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400"
                      }`}
                    >
                      {isPositive ? (
                        <TrendingUp className="h-3 w-3" />
                      ) : (
                        <TrendingDown className="h-3 w-3" />
                      )}
                      {stat.change}
                    </Badge>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </section>

        {/* 主要内容区：任务列表和日志 */}
        <section className="grid gap-6 lg:grid-cols-[2fr_1fr]">
          {/* 最近任务表格 */}
          <Card className="shadow-sm">
            <CardHeader>
              <CardTitle>最近任务</CardTitle>
              <CardDescription>
                查看最近的红包发送任务执行情况
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="all" className="space-y-4">
                <TabsList className="w-full justify-start bg-muted/60">
                  <TabsTrigger value="all">全部</TabsTrigger>
                  <TabsTrigger value="success">成功</TabsTrigger>
                  <TabsTrigger value="pending">进行中</TabsTrigger>
                  <TabsTrigger value="failed">失败</TabsTrigger>
                </TabsList>
                <TabsContent value="all" className="space-y-0">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>任务ID</TableHead>
                        <TableHead>类型</TableHead>
                        <TableHead>金额</TableHead>
                        <TableHead>数量</TableHead>
                        <TableHead>状态</TableHead>
                        <TableHead className="text-right">时间</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {recentTasks.map((task) => (
                        <TableRow key={task.id}>
                          <TableCell className="font-mono text-sm">
                            {task.id}
                          </TableCell>
                          <TableCell>{task.type}</TableCell>
                          <TableCell className="font-semibold text-red-600 dark:text-red-400">
                            {task.amount}
                          </TableCell>
                          <TableCell>{task.count} 个</TableCell>
                          <TableCell>
                            <Badge
                              variant={
                                task.status === "success"
                                  ? "default"
                                  : task.status === "pending"
                                    ? "secondary"
                                    : "destructive"
                              }
                              className={
                                task.status === "success"
                                  ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                                  : task.status === "pending"
                                    ? "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"
                                    : ""
                              }
                            >
                              {task.status === "success"
                                ? "成功"
                                : task.status === "pending"
                                  ? "进行中"
                                  : "失败"}
                            </Badge>
                          </TableCell>
                          <TableCell className="text-right text-sm text-muted-foreground">
                            {task.time}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TabsContent>
                <TabsContent value="success">
                  <div className="py-8 text-center text-sm text-muted-foreground">
                    显示成功的任务...
                  </div>
                </TabsContent>
                <TabsContent value="pending">
                  <div className="py-8 text-center text-sm text-muted-foreground">
                    显示进行中的任务...
                  </div>
                </TabsContent>
                <TabsContent value="failed">
                  <div className="py-8 text-center text-sm text-muted-foreground">
                    显示失败的任务...
                  </div>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>

          {/* 系统日志 */}
          <div className="space-y-6">
            <Card className="shadow-sm">
              <CardHeader>
                <CardTitle>系统日志</CardTitle>
                <CardDescription>
                  实时查看系统运行状态与事件记录
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {systemLogs.map((log, index) => (
                  <div
                    key={index}
                    className="flex items-start gap-3 rounded-lg border border-border/60 bg-card p-3 text-sm transition hover:border-primary/40 hover:shadow-sm"
                  >
                    <div
                      className={`mt-0.5 flex h-5 w-5 items-center justify-center rounded-full ${
                        log.level === "error"
                          ? "bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400"
                          : log.level === "warning"
                            ? "bg-amber-100 text-amber-600 dark:bg-amber-900/30 dark:text-amber-400"
                            : "bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400"
                      }`}
                    >
                      {log.level === "error" ? (
                        <XCircle className="h-3 w-3" />
                      ) : log.level === "warning" ? (
                        <AlertCircle className="h-3 w-3" />
                      ) : (
                        <Activity className="h-3 w-3" />
                      )}
                    </div>
                    <div className="flex-1 space-y-1">
                      <p className="text-foreground">{log.message}</p>
                      <p className="text-xs text-muted-foreground">
                        <Clock className="mr-1 inline h-3 w-3" />
                        {log.time}
                      </p>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* 快速操作 */}
            <Card className="shadow-sm">
              <CardHeader>
                <CardTitle>快速操作</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <Button className="w-full justify-start gap-2" variant="outline">
                  <Send className="h-4 w-4" />
                  创建红包任务
                </Button>
                <Button className="w-full justify-start gap-2" variant="outline">
                  <Users className="h-4 w-4" />
                  用户管理
                </Button>
                <Button className="w-full justify-start gap-2" variant="outline">
                  <Activity className="h-4 w-4" />
                  查看统计报表
                </Button>
              </CardContent>
            </Card>
          </div>
        </section>
      </div>
    </div>
  );
}
