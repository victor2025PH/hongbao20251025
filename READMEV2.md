# 基于“小星星”积分驱动的公开交友群功能开发文档（整合版 V2）

面向：产品 / 设计 / 前端（MiniApp/WebApp）/ 后端 / Bot 工程 / 数据 / 运营 / 法务  
范围：在既有 Telegram 生态（机器人 Bot + MiniApp + 频道 + 群组、资料只读同步、Gift Groups、恋爱交友与“小星星”积分体系）的基础上，新增**“消耗星星创建公开交友群，并在 MiniApp 公示与加入”**的完整能力；引入**提示词优化器**（Prompt Optimizer）以规范文案与系统提示词；补充 Logo/品牌规范与接口、数据结构、风控、测试与上线策略。

---

## 1. 项目背景与目标

**目标**  
- 允许用户在 MiniApp 中**消耗“小星星”积分创建公开交友群**（Public Dating Group），群信息在 MiniApp 公示，所有用户可浏览、搜索、筛选与加入；加入用户可领取**进入奖励星星**。  
- 群内支持聊天与轻度游戏（与 Gift Groups 复用小游戏引擎）。  
- 全链路合规（无赌博/付费随机），资料**只读同步**自 Telegram；强化增长与留存。

**关键收益**  
- 把“赚星星”→“花星星”的经济闭环打通；  
- 强化 UGC 场景，形成“群广场”；  
- “进入即领”降低首次互动门槛，提升冷启动群活跃。

---

## 2. 品牌与系统组件

### 2.1 Logo 与品牌规范（摘要）
- **主色**：亮紫（社交感）+ 明亮蓝（可信度），与既有 Gift Groups 配色一致。  
- **图形元素**：星形（Stars）+ 对话气泡；群封面模板含渐变遮罩、群名与标签位。  
- **可访问性**：对比度 ≥ 4.5:1；按钮高度 ≥ 44px；字号 ≥ 15px。

### 2.2 提示词优化器（Prompt Optimizer）
面向**运营与研发**的文案/系统提示词治理工具，支撑：  
- **用户提示词**（群创建向导、规则提醒、冷却提示）统一管理；  
- **多语言**（EN/中文起步）与风格（简短、友好、合规用语白名单）一致；  
- 输出存入 `i18n_messages` 表，Bot 与 MiniApp 统一读取；  
- 提供“V1→V2”版本化与 A/B 标签；  
- 内置合规校验：黑名单词（bet/wager/jackpot/airdrop/ROI/profit/cash）拒绝发布。

---

## 3. 角色与权限

- **访客**：可浏览群广场与公开信息；加入需授权（与 Bot 建立会话）。  
- **注册用户**：可创建公开群（消耗星星）、邀请、举报、加入、领取进入奖励。  
- **群主（Creator）**：群设置、标签、招募文案、入群开关、管理员任命。  
- **管理员（Admin）**：协助审核成员、置顶破冰、踢人/禁言（Bot 辅助）。  
- **Host/客服**：处理举报与申诉、下架群、公示。  
- **系统（Platform）**：风控、榜单、抽奖、规则与活动脚本。

---

## 4. 星星经济（新增与调整）

### 4.1 既有规则（沿用）
- Bot 首会话：+1 星；MiniApp 首登：+10 星（幂等）。  
- **发送单位 5 星**；每日任务：当日发送 ≥50 星，+50 星（每日一次）。  
- **免费赠送**：对每位好友每日 5 星（不限好友数、系统池发放、发送者不扣余额）。  
- 排行榜（以累计获得 `lifetime_earned` 排序）每日 24:00 结算 Top100；  
- 抽奖资格：Top100 ∪ 累计获得 ≥500 星；每月一次、免费、数字权益奖品。

### 4.2 新增与本功能相关的星星规则
- **创建公开群消耗**：`GROUP_CREATE_COST = 100 星`（可配置，建议 50–200 的 A/B）。  
- **群曝光置顶消耗**（可选）：`GROUP_PIN_COST = 20 星 / 24h`，用于群广场置顶展示。  
- **进入奖励**：用户**首次进入该群**领取 `GROUP_ENTRY_REWARD = 5 星`（可配置）；每用户每群仅一次。  
- **冷启动奖励池**：新群在创建后 72 小时内，系统为“进入奖励”设立**上限池**（如 1,000 星），避免无限发放。  
- **反刷补充**：同账号/设备/网络在短期内密集进多个新群，进入奖励衰减或触发人工审核。

---

## 5. 端到端用户旅程

### 5.1 创建公开交友群（MiniApp）
1) 打开 MiniApp → **群广场** → 右上“创建群”；  
2) 只读资料面板展示余额（星星）与消耗规则；  
3) 填写：群名称、简介、标签（≤3）、语言、群封面模板（内置图）、是否允许“进入奖励”；  
4) 提交 → 检查余额 ≥ `GROUP_CREATE_COST` → 扣减 → 调用 Bot 建群（或使用预建群池 + 绑定为群主），设置群权限、邀请链接；  
5) 入库并**公示到群广场**，默认排序：新鲜度 + 热度（加入数/活跃度）；  
6) 若勾选置顶且余额足够 → 扣星并置顶 24h（可续费）。

### 5.2 浏览与加入（所有用户）
1) 浏览群广场：卡片展示群名、简介、标签、在线数、入群奖励徽标；  
2) 搜索/筛选：语言、标签、活跃度、是否有游戏；  
3) 点击进入详情 → “加入群” → 走 Telegram join request / invite link；  
4) **首次进入**通过后 → 回调发放 `GROUP_ENTRY_REWARD`（若冷却与池未耗尽）；  
5) Bot 发送欢迎与破冰、小游戏入口。

### 5.3 群内互动
- 文本/表情/基础多媒体；破冰与签到；60 秒小游戏；定时/里程碑礼物（与 Gift 引擎复用）；  
- 群主/管理员在 MiniApp 可看**基础数据**（新增成员、进入奖励发放、活跃度）。

---

## 6. 信息架构与界面（MiniApp）

- **群广场（列表）**：顶部搜索、标签与语言筛选、排序（新/热/置顶）；卡片含封面、群名、标签、在线人数、入群奖励徽标、创建时间。  
- **群详情**：简介、标签、群主昵称、规则（No gambling…）、入群奖励说明、加入按钮、举报按钮。  
- **创建群流程**：  
  - Step 1：填写基础信息（名称、简介、标签、语言）  
  - Step 2：选择封面模板与是否开“入群奖励”  
  - Step 3：确认消耗（显示余额与扣减后余额）→ 创建  
  - Step 4：分享卡片（可转发到频道/群）  
- **我的群**：我创建/管理的群列表；置顶续费、编辑简介/标签、关闭入群奖励开关。

---

## 7. 数据结构设计（新增/变更）

```sql
-- 群主数据与公开群定义
CREATE TABLE public_groups (
  id BIGSERIAL PRIMARY KEY,
  creator_user_id BIGINT NOT NULL REFERENCES users(id),
  tg_chat_id BIGINT UNIQUE,             -- Telegram 群唯一ID（创建后回填）
  name TEXT NOT NULL,
  description TEXT,
  tags TEXT[],                          -- ["music","games","study"]
  lang TEXT,                             -- "en","zh"
  cover_template TEXT,                   -- "gradient_blue","stars_v1" 等
  entry_reward_enabled BOOLEAN DEFAULT TRUE,
  entry_reward_points INT DEFAULT 5,     -- GROUP_ENTRY_REWARD
  entry_reward_pool INT DEFAULT 1000,    -- 冷启动奖励池上限
  is_pinned BOOLEAN DEFAULT FALSE,
  pinned_until TIMESTAMP,
  status TEXT NOT NULL DEFAULT 'active', -- active | paused | removed
  created_at TIMESTAMP NOT NULL DEFAULT now(),
  updated_at TIMESTAMP NOT NULL DEFAULT now()
);

-- 群创建扣费流水
CREATE TABLE group_cost_ledger (
  id BIGSERIAL PRIMARY KEY,
  group_id BIGINT NOT NULL REFERENCES public_groups(id),
  user_id BIGINT NOT NULL REFERENCES users(id),
  amount INT NOT NULL,                   -- 负数（扣星）
  reason TEXT NOT NULL,                  -- group_create | group_pin
  created_at TIMESTAMP NOT NULL DEFAULT now()
);

-- 群进入奖励发放去重与明细
CREATE TABLE group_entry_rewards (
  id BIGSERIAL PRIMARY KEY,
  group_id BIGINT NOT NULL REFERENCES public_groups(id),
  user_id BIGINT NOT NULL REFERENCES users(id),
  points INT NOT NULL,                   -- +5 等
  status TEXT NOT NULL,                  -- ok | pool_exhausted | cooldown
  created_at TIMESTAMP NOT NULL DEFAULT now(),
  UNIQUE (group_id, user_id)             -- 每用户每群仅一次
);

-- 群浏览索引（搜索/筛选/排序）
CREATE INDEX ON public_groups (status, lang);
CREATE INDEX ON public_groups USING GIN (tags);
CREATE INDEX ON public_groups (pinned_until DESC, created_at DESC);

-- 头像/资料只读（沿用）
-- star_accounts / star_ledger / daily_send_counter 等沿用既有表
```

---

## 8. 接口定义（REST/JSON）

> 鉴权：MiniApp 通过 `POST /v1/session/open` 校验 `initData` 后获取 JWT。Bot Webhook 负责群创建与 join 回调。  
> 时间与结算：默认时区 Asia/Manila；排行榜每日 24:00 结算。

### 8.1 群广场与详情

**GET `/v1/groups/public?query=&tags=&lang=&sort=new|hot|pin&page=1&page_size=20`**  
- 出参（示例）：
```json
{
  "items": [
    {
      "group_id": 31001,
      "name": "Games & Chill Meetup",
      "tags": ["games","music"],
      "lang": "en",
      "online_estimate": 87,
      "entry_reward_badge": true,
      "cover_url": "https://cdn/cover/pg_31001.png",
      "pinned": true,
      "created_at": "2025-11-09T08:00:00Z"
    }
  ],
  "page": 1, "page_size": 20, "total": 4321
}
```

**GET `/v1/groups/public/{group_id}`**  
- 出参：名称、简介、标签、群主昵称、入群奖励说明、加入链接（由 Bot 生成的 invite link 或加入请求）。

### 8.2 创建与置顶

**POST `/v1/groups/public`**（创建公开交友群，扣 `GROUP_CREATE_COST`）  
- 入参：
```json
{
  "name": "Study & Coffee",
  "description": "Daily Pomodoro and chill",
  "tags": ["study","chill"],
  "lang": "en",
  "cover_template": "gradient_blue",
  "entry_reward_enabled": true
}
```
- 返回：
```json
{
  "group_id": 32088,
  "tg_chat_id": null,
  "cost": 100,
  "balance_after": 540
}
```
- 说明：后端事务内**扣星**与**建群任务入队**；Bot 完成建群后回调 `tg_chat_id` 并设置 join 权限与邀请链接。

**POST `/v1/groups/public/{group_id}/pin`**（置顶 24h，扣 `GROUP_PIN_COST`）  
- 出参：`{ "pinned_until": "2025-11-10T00:00:00Z", "balance_after": 520 }`

### 8.3 加入与进入奖励

**GET `/v1/groups/public/{group_id}/join_link`**  
- 出参：`{ "invite_link": "https://t.me/+XXXX" }`（或触发 join request）。

**Bot Webhook → POST `/internal/tg/joined`**（系统内部）  
- 入参：
```json
{ "tg_chat_id": -1001234567890, "tg_user_id": 555111222 }
```
- 逻辑：映射到 `group_id` 和 `user_id`，尝试发放进入奖励：  
  - 若 `entry_reward_enabled` 且该用户**未领取**且奖励池 `entry_reward_pool > 0` →  
    - 事务：`group_entry_rewards` 插入唯一记录 → `star_accounts.balance += entry_reward_points`、`lifetime_earned += entry_reward_points`、`entry_reward_pool -= entry_reward_points`；写 `star_ledger`。  
  - Bot 发送“+5 Stars 入群奖励已到账”。

### 8.4 编辑、举报与上下架

**PATCH `/v1/groups/public/{group_id}`**（群主）  
- 可更新：简介、标签、语言、封面模板、开关入群奖励。  
- 不可更名超过每日 1 次。  

**POST `/v1/groups/public/{group_id}/report`**  
- 入参：`{ "reason": "spam|abuse|misleading|other", "details": "..." }`  
- 进入风控队列，必要时**暂停展示**或下架，写审计日志。

---

## 9. Bot 协同流程

- **建群任务**：服务端扣费成功 → 发送“建群任务”到队列 → Bot 调用 Telegram API（或使用预建群池）创建/绑定群：  
  - 群名/头像（模板）、简介、语言标签、Bot 设为管理员、启用加入请求或生成邀请链接；  
  - 回写 `tg_chat_id` 与 `invite_link` 到 `public_groups`。  
- **加入回调**：监听 `chat_join_request` / `chat_member` 变更 → 命中后调用 `/internal/tg/joined` 发进入奖励。  
- **欢迎消息**：发送规则卡（No gambling / No cash rewards）+ 破冰/小游戏入口。

---

## 10. 业务规则与风控

- **创建门槛**：余额必须 ≥ `GROUP_CREATE_COST`；每日最多创建 `GROUP_CREATE_DAILY_LIMIT`（建议 3）。  
- **置顶限额**：同一群同时最多 1 条置顶；续期需余额足够。  
- **进入奖励反刷**：  
  - 进入奖励**每用户每群仅一次**；  
  - 奖励池耗尽后不再发放；  
  - 同设备/IP/指纹在短期内进入多个新群 → 递减奖励或人工审核；  
  - 新群前 N 个进入奖励正常发放，N 后进入“低信任期”（降低奖励）。  
- **举报与治理**：多次命中的群自动降权或下架；群主可申诉。  
- **合规**：全局统一规则文案；禁用敏感词；不出现“下注/抽奖现金/收益”等词汇。

---

## 11. 状态机与并发

### 11.1 群创建状态
`draft → charging (扣费) → creating (Bot 执行) → active (成功) ｜ failed (失败退款) ｜ removed (下架)`

### 11.2 并发锁与幂等
- 创建与置顶：`SELECT ... FOR UPDATE` 锁账户 + 幂等键（`user_id + name + ts_bucket`）。  
- 进入奖励：`UNIQUE(group_id,user_id)` + Redis 瞬时锁；奖池扣减与发放同事务。  
- 头像与资料：已有只读机制与 ETag 缓存。

---

## 12. 埋点与看板（新增事件）

- `group_create_click` / `group_create_success` / `group_create_fail`  
- `group_pin_success`  
- `group_list_view` / `group_detail_view` / `group_search` / `group_filter`  
- `group_join_click` / `group_join_success`  
- `group_entry_reward_awarded` / `group_entry_reward_pool_exhausted`  
- 看板新增指标：  
  - 创建转化率、创建成本均值、置顶续费率；  
  - 群进入奖励成本/用户获取成本、奖励池耗尽时间；  
  - 新群 72h 留存与首贴率。

---

## 13. 提示词优化器（接口与规范）

**目的**：集中管理提示/话术，输出多语言与 A/B 版本，自动校验合规词。

**数据结构（简化）**
```sql
CREATE TABLE i18n_messages (
  key TEXT NOT NULL,            -- e.g., "group.create.confirm"
  lang TEXT NOT NULL,           -- "en","zh"
  variant TEXT DEFAULT 'V2',    -- "V1","V2","A","B"
  text TEXT NOT NULL,
  updated_at TIMESTAMP NOT NULL DEFAULT now(),
  PRIMARY KEY (key, lang, variant)
);
```

**示例文案（EN/中文）**
- `group.create.confirm`  
  - EN: *Spend **100 Stars** to create this group? You can pin it for more visibility.*  
  - ZH: *确认消耗 **100 星**创建该群？你可额外置顶以提升曝光。*
- 合规提醒：*No gambling. No cash rewards. Points unlock digital perks only.*

---

## 14. API 摘要（与既有接口协同）

- `POST /v1/session/open`（已有）  
- `GET /v1/groups/public` 列表  
- `GET /v1/groups/public/{id}` 详情  
- `POST /v1/groups/public` 创建（扣费）  
- `POST /v1/groups/public/{id}/pin` 置顶（扣费）  
- `GET /v1/groups/public/{id}/join_link` 获取加入链接  
- `POST /v1/groups/public/{id}/report` 举报  
- `PATCH /v1/groups/public/{id}` 编辑  
- 内部：`POST /internal/tg/joined` 入群回调发奖励  
- 星星沿用：`POST /v1/stars/send`、`POST /v1/stars/free_gift`、`POST /v1/mission/daily/claim` 等

---

## 15. 测试计划

### 15.1 功能测试
- 创建扣费幂等、失败退款；置顶扣费与到期自动下架；  
- 进入奖励唯一性、奖池耗尽分支、冷却/锁并发；  
- 列表筛选/搜索/排序正确；  
- 编辑与举报流程闭环；  
- Bot 建群回填、加入回调链路。

### 15.2 体验测试
- 创建 3 步 ≤ 30 秒；余额与扣费提示清晰；  
- 群详情信息充分，加入流程可达性高；  
- 入群奖励到账反馈 ≤ 1 秒（消息+面板同步）。

### 15.3 性能与稳定性
- 群广场列表 P95 < 150ms；创建高峰 200 RPS 不丢单；  
- 加入回调峰值 2k QPS 奖励准确无重付；  
- CDN 命中率 ≥ 90%，MiniApp 首屏 < 2s。

### 15.4 安全与风控
- 敏感词检测、举报→处置→公示；  
- 批量刷入群与批量建群的限速生效；  
- 审计日志可回溯；合规词黑名单拦截。

---

## 16. 上线与迭代

- **灰度**：按 `user_id % 10` 分桶（10%→50%→100%）；  
- **A/B**：`GROUP_CREATE_COST`（100 vs 150）、`GROUP_ENTRY_REWARD`（5 vs 8）、置顶价格；  
- **里程碑**：  
  - M1：列表/详情/创建（扣费）/Bot 建群；  
  - M2：加入回调与进入奖励池；  
  - M3：置顶与举报、风控；  
  - M4：小游戏整合与群数据面板；  
  - M5：优化与国际化扩展（ES/DE）。

---

## 17. 合规模板（摘要）

- 全局规则：*No gambling. No cash rewards. Points unlock digital perks only.*  
- 群规则：友善、反垃圾、内容标准；违规处理与申诉窗口；  
- 抽奖继续沿用“免费参与 + AMOE + 数字权益奖品”机制。

---

### 附：关键常量（建议值，可配置）
```yaml
TIMEZONE: Asia/Manila
GROUP_CREATE_COST: 100
GROUP_PIN_COST: 20
GROUP_PIN_DURATION_HOURS: 24
GROUP_ENTRY_REWARD: 5
GROUP_ENTRY_REWARD_POOL: 1000
GROUP_CREATE_DAILY_LIMIT: 3
SEND_UNIT: 5
DAILY_MISSION_THRESHOLD: 50
DAILY_MISSION_REWARD: 50
FREE_GIFT_PER_FRIEND_PER_DAY: 5
LEADERBOARD_TOP_N: 100
```

---

本版本文档与既有生态无缝衔接，明确了**星星获取与消耗闭环、公开交友群创建与公示、加入即领奖励、风控与并发安全、接口与数据结构**，并引入**提示词优化器**和**品牌规范**以保障一致性与可持续迭代。开发可据此直接进入任务拆解与实现。

---

## 18. 项目总览架构图说明

### 18.1 系统组件

本系统是一个基于 Telegram 生态的红包系统，包含以下主要组件：

1. **Telegram Bot** (`app.py`): 
   - 使用 aiogram 框架
   - 处理用户命令和消息
   - 发送红包、处理充值、管理群组等

2. **Web Admin** (`web_admin/main.py`, 端口 8000):
   - FastAPI 应用
   - 提供 HTML 管理界面和 REST API
   - 处理红包任务、充值订单、用户管理、公开群组审核等

3. **MiniApp API** (`miniapp/main.py`, 端口 8080):
   - FastAPI 应用
   - 提供 Telegram MiniApp 后端 API
   - 处理公开群组创建、加入、活动管理等
   - 使用 JWT 认证

4. **前端控制台** (`frontend-next/`, 端口 3001):
   - Next.js 应用
   - 提供现代化的管理控制台界面
   - 展示 Dashboard、任务列表、群组管理、统计图表等

5. **数据库** (SQLite/PostgreSQL/MySQL):
   - 存储用户、红包、订单、群组等数据
   - 通过 SQLAlchemy ORM 访问

6. **外部服务**:
   - **Telegram Bot API**: Bot 发送消息、创建群组等
   - **NowPayments**: 处理加密货币充值
   - **OpenAI/OpenRouter**: AI 功能（活动生成等）
   - **Google Sheets**: 用户数据同步（可选）

---

### 18.2 调用关系

#### Telegram Bot → Web Admin

**协议**: HTTP (内部调用)  
**场景**: 
- Bot 需要查询用户余额、创建红包任务时，调用 Web Admin API
- Bot 处理 IPN 回调时，调用 Web Admin 的 IPN 处理接口

**示例**:
```
Bot → POST http://localhost:8000/admin/api/v1/envelopes
Bot → POST http://localhost:8000/admin/ipn
```

---

#### MiniApp API → 数据库

**协议**: SQLAlchemy ORM (直接数据库访问)  
**场景**:
- 查询公开群组列表
- 创建公开群组
- 处理用户加入群组
- 发放进入奖励

**数据流**:
```
MiniApp API → SQLAlchemy → Database
```

---

#### 前端控制台 → Web Admin API

**协议**: HTTP REST API  
**场景**:
- Dashboard 数据: `GET /admin/api/v1/dashboard`
- 任务列表: `GET /admin/api/v1/tasks`
- 群组列表: `GET /admin/api/v1/group-list`
- 统计数据: `GET /admin/api/v1/stats`
- 审计日志: `GET /admin/api/v1/audit`
- 系统设置: `GET /admin/api/v1/settings`, `PUT /admin/api/v1/settings`

**数据流**:
```
前端控制台 (Next.js) → HTTP → Web Admin (FastAPI) → Database
```

---

#### 前端控制台 → MiniApp API

**协议**: HTTP REST API  
**场景**:
- 群组详情: `GET /v1/groups/public/{id}`
- 群组活动: `GET /v1/groups/public/activities`

**数据流**:
```
前端控制台 (Next.js) → HTTP → MiniApp API (FastAPI) → Database
```

---

#### Web Admin → 外部服务

**协议**: HTTP REST API  
**场景**:

1. **NowPayments**:
   - 创建支付订单: `POST https://api.nowpayments.io/v1/payment`
   - 查询订单状态: `GET https://api.nowpayments.io/v1/payment/{payment_id}`
   - 接收 IPN 回调: `POST /admin/ipn` (NowPayments → Web Admin)

2. **OpenAI/OpenRouter**:
   - 生成活动文案: `POST https://api.openai.com/v1/chat/completions`
   - 或: `POST https://openrouter.ai/api/v1/chat/completions`

3. **Telegram Bot API**:
   - 发送消息: `POST https://api.telegram.org/bot{token}/sendMessage`
   - 创建群组: `POST https://api.telegram.org/bot{token}/createChat`
   - 处理加入请求: `POST https://api.telegram.org/bot{token}/approveChatJoinRequest`

**数据流**:
```
Web Admin → HTTP → NowPayments/OpenAI/Telegram API
```

---

#### Telegram Bot → Telegram Bot API

**协议**: HTTP REST API (通过 aiogram)  
**场景**:
- 发送红包消息
- 处理用户命令
- 管理群组
- 处理加入请求

**数据流**:
```
Telegram Bot (aiogram) → HTTP → Telegram Bot API
```

---

### 18.3 数据流示例

#### 红包发送流程

```
1. 用户发送命令 → Telegram Bot
2. Telegram Bot → Web Admin API (创建红包任务)
3. Web Admin → Database (保存任务)
4. Web Admin → Telegram Bot API (发送红包消息)
5. 用户领取红包 → Telegram Bot
6. Telegram Bot → Web Admin API (更新任务状态)
7. Web Admin → Database (更新余额、记录流水)
```

---

#### 充值流程

```
1. 用户在前端创建充值订单 → 前端控制台
2. 前端控制台 → Web Admin API (创建订单)
3. Web Admin → Database (保存订单)
4. Web Admin → NowPayments API (创建支付)
5. NowPayments → Web Admin (IPN 回调)
6. Web Admin → Database (更新订单状态、用户余额)
7. Web Admin → Telegram Bot API (通知用户)
```

---

#### 公开群组创建流程

```
1. 用户在 MiniApp 创建群组 → MiniApp API
2. MiniApp API → Database (检查余额、创建群组记录)
3. MiniApp API → Web Admin API (创建 Telegram 群组任务)
4. Web Admin → Telegram Bot API (创建群组)
5. Telegram Bot → Web Admin API (回填群组 ID)
6. Web Admin → Database (更新群组信息)
7. MiniApp API → Database (群组状态更新为 active)
```

---

### 18.4 认证与授权

#### Web Admin 认证

**方式**: Session Cookie  
**流程**:
1. 用户访问 `/admin/login`
2. 输入用户名和密码
3. Web Admin 验证后设置 Session Cookie
4. 后续请求携带 Cookie，Web Admin 验证 Session

**保护范围**: 所有 `/admin/*` 路径（除 `/admin/login` 和 `/admin/api/v1/dashboard/public`）

---

#### MiniApp API 认证

**方式**: JWT Token  
**流程**:
1. 用户通过 Telegram `initData` 登录
2. MiniApp API 验证 `initData` 并生成 JWT Token
3. 后续请求在 `Authorization: Bearer <token>` 头中携带 Token
4. MiniApp API 验证 Token 并提取用户信息

**保护范围**: 所有 `/v1/*` 路径（除 `/healthz` 和部分公开接口）

---

### 18.5 端口与服务映射

| 服务 | 端口 | 协议 | 说明 |
|------|------|------|------|
| Web Admin | 8000 | HTTP | FastAPI Web 管理后台 |
| MiniApp API | 8080 | HTTP | FastAPI MiniApp 后端 |
| 前端控制台 | 3001 | HTTP | Next.js 前端应用 |
| 数据库 | 5432 (PostgreSQL) / 3306 (MySQL) | SQL | 数据库服务 |

---

### 18.6 部署架构建议

#### 开发环境

```
┌─────────────┐
│  Developer  │
└──────┬──────┘
       │
       ├─→ http://localhost:3001 (前端控制台)
       ├─→ http://localhost:8000 (Web Admin)
       ├─→ http://localhost:8080 (MiniApp API)
       └─→ sqlite:///./data.sqlite (本地数据库)
```

---

#### 生产环境

```
                    ┌──────────────┐
                    │   Nginx      │
                    │  (反向代理)   │
                    └──────┬───────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐       ┌─────▼─────┐      ┌─────▼─────┐
   │  Web    │       │  MiniApp  │      │  Frontend │
   │  Admin  │       │    API    │      │  (Next.js)│
   │  :8000  │       │   :8080   │      │   :3001   │
   └────┬────┘       └─────┬─────┘      └───────────┘
        │                  │
        └──────────┬───────┘
                   │
            ┌──────▼──────┐
            │  Database   │
            │ (PostgreSQL)│
            └─────────────┘
```

**说明**:
- Nginx 作为反向代理，处理 HTTPS、负载均衡、静态文件
- Web Admin 和 MiniApp API 可以部署在同一服务器或不同服务器
- 前端可以部署为静态文件（通过 `npm run build`）或使用 Next.js 服务器模式
- 数据库建议使用 PostgreSQL（生产环境）

---

*架构说明最后更新: 2025-01-XX*
