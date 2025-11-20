# 监控与告警检查清单

本文档列出核心监控指标、合理阈值建议、告警触发时的排查步骤，以及如何从日志和审计中快速定位问题。

---

## 目录

- [监控指标](#监控指标)
- [告警阈值与排查步骤](#告警阈值与排查步骤)
- [日志与审计定位](#日志与审计定位)
- [Prometheus 指标](#prometheus-指标)

---

## 监控指标

### 1. 红包发送失败率

**指标名称**: `envelope_send_failure_rate`  
**计算方式**: `失败次数 / 总发送次数 * 100%`  
**数据来源**: `envelopes` 表（`status` 字段）

**合理阈值**:
- **警告**: > 5%
- **严重**: > 10%

**告警触发排查步骤**:
1. 检查数据库连接是否正常
2. 检查 Telegram Bot API 是否可用（`BOT_TOKEN` 是否有效）
3. 查看失败红包的 `error_message` 字段
4. 检查是否有大量"用户不存在"错误（可能是数据同步问题）
5. 检查是否有大量"余额不足"错误（可能是业务逻辑问题）
6. 查看最近 1 小时的错误日志

**相关日志**:
- `web_admin/controllers/envelopes.py` 中的错误日志
- `services/hongbao_service.py` 中的发送失败日志

---

### 2. 任务队列堆积

**指标名称**: `task_queue_pending_count`  
**计算方式**: `SELECT COUNT(*) FROM envelopes WHERE status = 'pending'`  
**数据来源**: `envelopes` 表

**合理阈值**:
- **警告**: > 100
- **严重**: > 500

**告警触发排查步骤**:
1. 检查任务处理服务是否正常运行
2. 检查是否有任务处理进程卡死
3. 查看最近 10 个待处理任务的创建时间
4. 检查是否有任务长时间未处理（> 1 小时）
5. 检查数据库连接池是否耗尽
6. 查看任务处理日志，查找错误或异常

**相关日志**:
- 任务处理服务的日志
- `services/hongbao_service.py` 中的处理日志

---

### 3. 外部 API 调用错误数

**指标名称**: `external_api_error_count`  
**计算方式**: 统计 NowPayments、OpenAI 等外部 API 的 4xx/5xx 错误数  
**数据来源**: 应用日志或 Prometheus 指标

**合理阈值**:
- **警告**: > 10 次/小时
- **严重**: > 50 次/小时

**告警触发排查步骤**:
1. **NowPayments API 错误**:
   - 检查 `NOWPAYMENTS_API_KEY` 是否有效
   - 检查 API 配额是否超限
   - 查看 NowPayments 服务状态页面
   - 检查 IPN 回调地址是否可访问

2. **OpenAI/OpenRouter API 错误**:
   - 检查 `OPENAI_API_KEY` 或 `OPENROUTER_API_KEY` 是否有效
   - 检查 API 配额是否超限
   - 检查请求频率是否超限
   - 查看 API 响应错误信息

3. **Telegram Bot API 错误**:
   - 检查 `BOT_TOKEN` 是否有效
   - 检查 Bot 是否被封禁
   - 查看 Telegram API 状态页面

**相关日志**:
- `core/clients/nowpayments.py` 中的错误日志
- `services/ai_service.py` 中的错误日志
- `services/hongbao_service.py` 中的 Telegram API 错误日志

---

### 4. 响应时间 p95

**指标名称**: `http_request_duration_seconds` (p95)  
**计算方式**: 统计 HTTP 请求响应时间的 95 分位数  
**数据来源**: Prometheus 指标或应用日志

**合理阈值**:
- **警告**: > 1 秒
- **严重**: > 3 秒

**告警触发排查步骤**:
1. 检查数据库查询性能（慢查询日志）
2. 检查是否有数据库连接池耗尽
3. 检查是否有外部 API 调用超时
4. 检查服务器 CPU/内存使用率
5. 检查是否有大量并发请求
6. 查看最近 10 个最慢的请求（端点、响应时间）

**相关日志**:
- Web 服务器访问日志（Nginx/Apache）
- 应用日志中的慢请求记录
- Prometheus 指标 `/metrics`

---

### 5. 充值订单失败率

**指标名称**: `recharge_order_failure_rate`  
**计算方式**: `失败订单数 / 总订单数 * 100%`  
**数据来源**: `recharge_orders` 表（`status` 字段）

**合理阈值**:
- **警告**: > 10%
- **严重**: > 20%

**告警触发排查步骤**:
1. 检查 NowPayments API 是否可用
2. 检查 IPN 回调是否正常（查看 `web_admin/controllers/ipn.py` 日志）
3. 查看失败订单的 `error_message` 字段
4. 检查是否有大量订单超时（`expire_minutes` 配置）
5. 检查订单金额是否在 NowPayments 支持的范围内
6. 查看最近 1 小时的 IPN 回调日志

**相关日志**:
- `web_admin/controllers/ipn.py` 中的 IPN 处理日志
- `services/recharge_service.py` 中的订单处理日志

---

### 6. 数据库连接池使用率

**指标名称**: `database_connection_pool_usage`  
**计算方式**: `当前连接数 / 最大连接数 * 100%`  
**数据来源**: SQLAlchemy 连接池统计

**合理阈值**:
- **警告**: > 80%
- **严重**: > 95%

**告警触发排查步骤**:
1. 检查是否有长时间运行的查询（慢查询）
2. 检查是否有未关闭的数据库连接（连接泄漏）
3. 检查是否有大量并发请求
4. 考虑增加连接池大小（`pool_size` 参数）
5. 检查数据库服务器资源使用率

**相关日志**:
- 数据库慢查询日志
- 应用日志中的数据库连接错误

---

### 7. 公开群组创建失败率

**指标名称**: `public_group_create_failure_rate`  
**计算方式**: `创建失败次数 / 总创建次数 * 100%`  
**数据来源**: `public_groups` 表或应用日志

**合理阈值**:
- **警告**: > 5%
- **严重**: > 10%

**告警触发排查步骤**:
1. 检查用户余额是否充足（创建群组需要消耗星星）
2. 检查风险评分是否过高（`risk_score`）
3. 查看失败原因（`services/public_group_service.py` 日志）
4. 检查是否有重复的 `invite_link`（唯一约束）
5. 检查 Telegram Bot 是否可用（创建群组需要 Bot 协助）

**相关日志**:
- `services/public_group_service.py` 中的创建失败日志
- `miniapp/main.py` 中的 API 错误日志

---

## 告警阈值与排查步骤

### 告警级别定义

- **警告 (Warning)**: 需要关注，但不会立即影响服务
- **严重 (Critical)**: 需要立即处理，可能影响用户体验

### 告警通知渠道

**建议配置**:
- **邮件**: 发送到运维团队邮箱
- **Slack/Telegram**: 发送到运维频道
- **PagerDuty/Opsgenie**: 严重告警时触发电话/短信

**告警频率限制**:
- 同一告警在 1 小时内最多发送 1 次（避免告警风暴）
- 告警恢复时发送恢复通知

---

## 日志与审计定位

### 系统日志

#### Web Admin 日志

**位置**: 应用日志（标准输出或日志文件）

**关键日志点**:
1. **红包发送**: `services/hongbao_service.py`
   - 搜索: `send_envelope`, `envelope_send_failed`
   - 查看: 发送失败原因、用户 ID、金额

2. **充值订单**: `services/recharge_service.py`, `web_admin/controllers/ipn.py`
   - 搜索: `recharge_order`, `ipn_callback`
   - 查看: 订单状态、IPN 回调结果

3. **公开群组**: `services/public_group_service.py`
   - 搜索: `create_group`, `group_create_failed`
   - 查看: 创建失败原因、风险评分

**日志格式示例**:
```
[2025-01-XX 12:00:00] ERROR [hongbao_service] send_envelope failed: user_id=123, amount=10, error=insufficient_balance
[2025-01-XX 12:00:01] INFO [ipn] IPN callback received: order_id=456, status=confirmed
```

---

#### MiniApp API 日志

**位置**: 应用日志（标准输出或日志文件）

**关键日志点**:
1. **认证失败**: `miniapp/auth.py`
   - 搜索: `login_failed`, `invalid_token`
   - 查看: 用户 ID、失败原因

2. **API 错误**: `miniapp/main.py`
   - 搜索: `api_error`, `HTTPException`
   - 查看: 端点、错误码、错误信息

**日志格式示例**:
```
[2025-01-XX 12:00:00] WARNING [miniapp.auth] login_failed: tg_id=123, reason=invalid_code
[2025-01-XX 12:00:01] ERROR [miniapp.api] api_error: endpoint=/v1/groups/public, status=500, error=internal_error
```

---

### 审计日志

#### 审计日志 API

**端点**: `GET /admin/api/v1/audit`  
**数据来源**: `audit` 表（通过 `web_admin/controllers/audit.py`）

**关键字段**:
- `type`: 操作类型（如 `recharge`, `adjust`, `envelope_send`）
- `token`: 币种（如 `USDT`, `TON`, `POINT`）
- `amount`: 金额
- `note`: 备注信息
- `user_id`: 用户 ID
- `created_at`: 创建时间

**查询示例**:
```bash
# 查询最近 1 小时的充值记录
curl "http://localhost:8000/admin/api/v1/audit?types=recharge&start=2025-01-XXT11:00:00Z&end=2025-01-XXT12:00:00Z"

# 查询特定用户的操作记录
curl "http://localhost:8000/admin/api/v1/audit?user=123456"
```

---

#### 快速定位问题

**场景 1: 用户投诉充值未到账**

1. **查询审计日志**:
   ```bash
   curl "http://localhost:8000/admin/api/v1/audit?user=USER_ID&types=recharge"
   ```

2. **检查订单状态**:
   ```sql
   SELECT * FROM recharge_orders WHERE user_id = USER_ID ORDER BY created_at DESC LIMIT 10;
   ```

3. **检查 IPN 回调日志**:
   - 查看 `web_admin/controllers/ipn.py` 日志
   - 搜索订单 ID 或用户 ID

4. **检查账本记录**:
   ```sql
   SELECT * FROM ledger WHERE user_id = USER_ID AND type = 'recharge' ORDER BY created_at DESC LIMIT 10;
   ```

---

**场景 2: 红包发送失败率高**

1. **查询失败红包**:
   ```sql
   SELECT * FROM envelopes WHERE status = 'failed' ORDER BY created_at DESC LIMIT 20;
   ```

2. **统计失败原因**:
   ```sql
   SELECT error_message, COUNT(*) as count 
   FROM envelopes 
   WHERE status = 'failed' AND created_at > NOW() - INTERVAL '1 hour'
   GROUP BY error_message 
   ORDER BY count DESC;
   ```

3. **检查用户余额**:
   ```sql
   SELECT user_id, balance FROM users WHERE user_id IN (SELECT DISTINCT user_id FROM envelopes WHERE status = 'failed');
   ```

4. **查看服务日志**:
   - 搜索 `services/hongbao_service.py` 中的 `send_envelope failed`

---

**场景 3: 外部 API 调用错误**

1. **检查 NowPayments API**:
   - 查看 `core/clients/nowpayments.py` 日志
   - 搜索 `nowpayments_api_error`, `HTTPError`

2. **检查 OpenAI/OpenRouter API**:
   - 查看 `services/ai_service.py` 日志
   - 搜索 `openai_api_error`, `openrouter_api_error`

3. **检查 API 密钥**:
   - 验证环境变量中的 API 密钥是否有效
   - 检查 API 配额是否超限

---

## Prometheus 指标

### 指标端点

**Web Admin**: `GET /metrics`  
**格式**: Prometheus 文本格式

### 内置指标

1. **应用运行时间**:
   ```
   app_uptime_seconds 3600
   ```

2. **应用信息**:
   ```
   app_info{app="telegram-hongbao-web-admin"} 1
   ```

### 自定义指标（通过 monitoring/metrics.py）

**Counter 指标**:
```python
from monitoring.metrics import counter

REQUEST_COUNTER = counter(
    "app_request_total",
    "Total requests handled.",
    label_names=("endpoint", "status"),
)

# 使用
REQUEST_COUNTER.inc(endpoint="/admin/api/v1/dashboard", status="200")
```

**Histogram 指标**:
```python
from monitoring.metrics import histogram

LATENCY_HIST = histogram(
    "app_request_seconds",
    "Request latency in seconds.",
    label_names=("endpoint", "status"),
)

# 使用
LATENCY_HIST.observe(0.5, endpoint="/admin/api/v1/dashboard", status="200")
```

### Prometheus 配置示例

```yaml
scrape_configs:
  - job_name: 'hongbao-web-admin'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 15s
```

### Grafana 仪表板建议

**关键面板**:
1. **请求速率**: `rate(app_request_total[5m])`
2. **错误率**: `rate(app_request_total{status=~"5.."}[5m]) / rate(app_request_total[5m])`
3. **响应时间 p95**: `histogram_quantile(0.95, rate(app_request_seconds_bucket[5m]))`
4. **应用运行时间**: `app_uptime_seconds`

---

## TODO

- [ ] 添加更多业务指标（红包发送成功率、充值转化率等）
- [ ] 添加数据库查询性能指标
- [ ] 添加外部 API 调用延迟指标
- [ ] 配置告警规则（Prometheus Alertmanager）
- [ ] 创建 Grafana 仪表板模板
- [ ] 添加日志聚合（ELK/Loki）
- [ ] 添加分布式追踪（Jaeger/Zipkin）

---

*最后更新: 2025-01-XX*

