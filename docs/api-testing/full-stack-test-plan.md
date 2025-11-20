# 🧪 全栈测试计划

## 📋 文档摘要

**创建时间**: 2025-11-15  
**目标**: 补齐并统一前后端关键功能测试，确保生产环境主要模块都能无错误运行  
**测试范围**: Web Admin API (8000) / MiniApp API (8080) / 前端项目

---

## 1. 已发现的测试框架和脚本

### 1.1 后端测试

| 测试框架 | 配置位置 | 测试目录 | 覆盖范围 | 状态 |
|---------|---------|---------|---------|------|
| **pytest** | `pytest.ini` | `tests/` | 单元测试、集成测试 | ✅ 已配置 |
| **FastAPI TestClient** | `tests/test_api_public_groups.py` | `tests/` | MiniApp API 单元测试 | ✅ 已有示例 |

**现有测试文件**:
- `tests/test_api_public_groups.py` - MiniApp API 公开群组测试
- `tests/test_miniapp_auth.py` - MiniApp 认证测试
- `tests/test_public_group_service.py` - 公开群组服务测试
- `tests/test_services.py` - 服务层测试
- `tests/test_models.py` - 数据模型测试
- 其他业务测试文件

**缺失的测试**:
- ⚠️ **后端 API 集成测试**（针对生产环境的 HTTP 端点测试）
- ⚠️ **Web Admin API 端点测试**（`/admin/api/v1/dashboard` 等）
- ⚠️ **MiniApp API 业务端点测试**（`/v1/groups/public`, `/v1/groups/public/activities` 等）

### 1.2 前端测试

| 前端项目 | 框架 | 测试配置 | 覆盖范围 | 状态 |
|---------|------|---------|---------|------|
| **frontend-next** | Next.js 16 | ❌ 无测试配置 | - | ⚠️ 缺失 |
| **miniapp-frontend** | Vite | ❌ 无测试配置 | - | ⚠️ 缺失 |

**缺失的测试**:
- ⚠️ **前端单元测试**（组件渲染、API 调用 mock）
- ⚠️ **前端集成测试**（页面加载、API 集成）
- ⚠️ **前端 e2e 测试**（完整用户流程）

### 1.3 PowerShell / Shell 测试脚本

| 脚本名称 | 位置 | 用途 | 覆盖范围 | 状态 |
|---------|------|------|---------|------|
| `test-api.ps1` | `docs/api-testing/test-api.ps1` | 基础 API 可访问性测试 | 健康检查端点 | ✅ 可用 |
| `run-comprehensive-test.ps1` | `docs/api-testing/run-comprehensive-test.ps1` | 全面 API 测试 | 健康检查、OpenAPI Schema、Swagger UI | ✅ 可用，需改进 |
| `comprehensive-api-test.ps1` | `docs/api-testing/comprehensive-api-test.ps1` | 全面 API 测试（旧版） | 同上 | ⚠️ 旧版 |

**需要改进的地方**:
- ⚠️ `/docs` 和 `/redoc` 返回 404 应视为「跳过」而非「失败」
- ⚠️ 缺少业务端点测试（Dashboard、群组列表等）
- ⚠️ 缺少性能指标记录和错误日志汇总

---

## 2. 应测试的关键接口与模块

### 2.1 Web Admin API (端口 8000)

#### 基础服务端点

| 端点 | 方法 | 预期状态码 | 需要认证 | 测试优先级 |
|------|------|-----------|---------|-----------|
| `/healthz` | GET | 200 | ❌ | ✅ 高 |
| `/readyz` | GET | 200 | ❌ | ✅ 高 |
| `/metrics` | GET | 200 | ❌ | ⚠️ 中 |
| `/openapi.json` | GET | 200 | ❌ | ✅ 高 |
| `/docs` | GET | 404 (已禁用) | ❌ | ⚠️ 跳过 |
| `/redoc` | GET | 404 (已禁用) | ❌ | ⚠️ 跳过 |

#### Dashboard / 统计端点

| 端点 | 方法 | 预期状态码 | 需要认证 | 测试优先级 |
|------|------|-----------|---------|-----------|
| `/admin/dashboard` | GET | 200/302 | ⚠️ 可能需要 | ⚠️ 中 |
| `/admin/api/v1/dashboard` | GET | 200/401 | ✅ 是 | ✅ 高 |
| `/admin/api/v1/dashboard/public` | GET | 200 | ❌ | ✅ 高 |

### 2.2 MiniApp API (端口 8080)

#### 基础服务端点

| 端点 | 方法 | 预期状态码 | 需要认证 | 测试优先级 |
|------|------|-----------|---------|-----------|
| `/healthz` | GET | 200 | ❌ | ✅ 高 |
| `/openapi.json` | GET | 200 | ❌ | ✅ 高 |
| `/docs` | GET | 404 (已禁用) | ❌ | ⚠️ 跳过 |

#### 公开群组端点

| 端点 | 方法 | 预期状态码 | 需要认证 | 测试优先级 |
|------|------|-----------|---------|-----------|
| `/v1/groups/public` | GET | 200 | ❌ (可选) | ✅ 高 |
| `/v1/groups/public/{id}` | GET | 200/404 | ❌ (可选) | ⚠️ 中 |
| `/v1/groups/public/activities` | GET | 200 | ❌ (可选) | ✅ 高 |

#### 认证端点

| 端点 | 方法 | 预期状态码 | 需要认证 | 测试优先级 |
|------|------|-----------|---------|-----------|
| `/api/auth/login` | POST | 200/400/401 | ❌ | ⚠️ 中（需要测试账号） |

---

## 3. 测试实现计划

### 3.1 后端 API 测试（Python pytest）

**目标**: 创建针对生产环境 HTTP 端点的集成测试

**实现内容**:
1. ✅ `tests/api/test_admin_api_endpoints.py` - Web Admin API 端点测试
2. ✅ `tests/api/test_miniapp_api_endpoints.py` - MiniApp API 端点测试
3. ✅ 使用 `httpx` 或 `requests` 发送 HTTP 请求
4. ✅ 从环境变量读取 Base URL（`API_TEST_ADMIN_BASE_URL`, `API_TEST_MINIAPP_BASE_URL`）
5. ✅ 记录响应时间和性能指标
6. ✅ 生成 pytest HTML 报告

### 3.2 前端测试（Next.js / React）

**目标**: 至少保证页面能正常加载并成功调用后端的关键接口

**实现内容**:
1. ⚠️ **最小可用方案**: 如果前端测试框架缺失，先创建简单的 smoke test
2. ⚠️ **可选**: 引入 Vitest 或 Jest 进行单元测试
3. ⚠️ **可选**: 引入 Playwright 或 Cypress 进行 e2e 测试
4. ✅ 配置测试脚本在 `package.json` 中

### 3.3 PowerShell 测试脚本改进

**目标**: 统一入口脚本，一次执行完成所有测试

**实现内容**:
1. ✅ 修改 `run-comprehensive-test.ps1` 支持跳过已禁用端点
2. ✅ 创建 `run-full-stack-tests.ps1` 统一入口脚本
3. ✅ 创建带时间戳的输出目录
4. ✅ 收集所有测试结果和日志

### 3.4 统一测试报告生成

**目标**: 自动生成结构化 HTML 报告（可选 PDF）

**实现内容**:
1. ✅ `docs/api-testing/render-full-stack-report.py` - 报告生成脚本
2. ✅ 整合所有测试结果（PowerShell CSV、pytest HTML、前端测试报告）
3. ✅ 性能指标汇总
4. ✅ 错误日志摘要和完整日志路径

---

## 4. 当前缺失的测试类型

### 4.1 后端测试缺失

- ⚠️ **HTTP 端点集成测试**（针对生产环境的真实 HTTP 请求）
- ⚠️ **Web Admin API 业务端点测试**（Dashboard、统计等）
- ⚠️ **MiniApp API 业务端点测试**（群组列表、活动列表等）
- ⚠️ **性能测试**（响应时间、并发请求）

### 4.2 前端测试缺失

- ⚠️ **前端单元测试**（组件渲染、函数逻辑）
- ⚠️ **前端集成测试**（API 调用、页面加载）
- ⚠️ **前端 e2e 测试**（完整用户流程）

### 4.3 测试工具缺失

- ⚠️ **pytest-html**（生成 HTML 报告）
- ⚠️ **前端测试框架**（Vitest / Jest / Playwright）

---

## 5. 测试执行流程

### 5.1 本地开发环境测试

```powershell
# 1. 设置测试目标地址（本地）
$env:API_TEST_ADMIN_BASE_URL = "http://localhost:8000"
$env:API_TEST_MINIAPP_BASE_URL = "http://localhost:8080"

# 2. 执行全栈测试
cd docs/api-testing
.\run-full-stack-tests.ps1
```

### 5.2 生产环境测试

```powershell
# 1. 设置测试目标地址（生产）
$env:API_TEST_ADMIN_BASE_URL = "http://165.154.233.55:8000"
$env:API_TEST_MINIAPP_BASE_URL = "http://165.154.233.55:8080"

# 2. 执行全栈测试
cd docs/api-testing
.\run-full-stack-tests.ps1
```

### 5.3 测试输出结构

```
docs/api-testing/output/
├── full-stack-test-20251115-120000/
│   ├── summary.json                    # 测试汇总 JSON
│   ├── summary.csv                     # 测试汇总 CSV
│   ├── full-stack-test-report.html     # 统一 HTML 报告
│   ├── api-powershell-tests.csv        # PowerShell API 测试结果
│   ├── api-powershell-error.log        # PowerShell 错误日志
│   ├── backend-pytest-report.html      # pytest HTML 报告
│   ├── backend-pytest-output.log       # pytest 输出日志
│   ├── frontend-unit-report.html       # 前端单元测试报告（如果有）
│   ├── frontend-unit-output.log        # 前端单元测试输出（如果有）
│   └── frontend-e2e-report.html        # 前端 e2e 测试报告（如果有）
```

---

## 6. 测试覆盖目标

### 6.1 后端 API 测试覆盖

- ✅ **基础服务端点**: `/healthz`, `/readyz`, `/metrics`, `/openapi.json`
- ✅ **Web Admin Dashboard**: `/admin/api/v1/dashboard/public`
- ✅ **MiniApp 公开群组**: `/v1/groups/public`, `/v1/groups/public/activities`
- ⚠️ **认证端点**: `/api/auth/login`（需测试账号或跳过）

### 6.2 前端测试覆盖（如果实现）

- ⚠️ **页面渲染**: Dashboard、群组列表等关键页面
- ⚠️ **API 集成**: 后端 API 调用和响应处理
- ⚠️ **用户流程**: 登录、浏览、操作等完整流程

### 6.3 性能指标收集

- ✅ **响应时间**: 每个测试用例的响应时间（ms）
- ✅ **整体耗时**: 每个测试阶段的总体耗时
- ⚠️ **并发性能**: 并发请求测试（可选）

---

## 7. 已知问题和限制

### 7.1 生产环境禁用端点

- `/docs` 和 `/redoc` 在生产环境返回 404（设计上已禁用）
- **处理方式**: 在测试中标记为「跳过」而非「失败」

### 7.2 认证端点测试

- `/admin/api/v1/dashboard` 需要认证（Session Cookie 或 JWT）
- `/api/auth/login` 需要有效的测试账号
- **处理方式**: 
  - 对于需要认证的端点，优先测试公开端点（如 `/admin/api/v1/dashboard/public`）
  - 认证端点可以标记为「跳过」并添加 TODO 注释

### 7.3 前端测试依赖

- 前端项目当前没有测试框架配置
- **处理方式**: 
  - 创建最小可用的 smoke test（使用简单 HTTP 请求检查页面可访问性）
  - 或暂时跳过前端测试，仅执行后端测试

---

## 8. 部署与回归测试策略

### 8.1 每次部署自动执行的测试

当执行 `docs/deployment/deploy-local.ps1` 或 `deploy-production.ps1` 时，会自动执行以下测试：

1. **健康检查测试**
   - Web Admin API `/healthz`
   - MiniApp API `/healthz`
   - Web Admin API `/readyz`（数据库连接检查）

2. **API 端点测试**
   - OpenAPI Schema 验证（`/openapi.json`）
   - Dashboard 公开数据接口（`/admin/api/v1/dashboard/public`）
   - 公开群组列表接口（`/v1/groups/public`）
   - 群组活动列表接口（`/v1/groups/public/activities`）

3. **性能测试**
   - 每个端点的响应时间测量
   - 平均响应时间统计

### 8.2 阻断部署的测试失败

以下测试失败会**阻止**部署继续或标记部署为失败：

- ❌ **健康检查失败**: `/healthz` 返回非 200
- ❌ **就绪检查失败**: `/readyz` 返回非 200（数据库连接失败）
- ❌ **后端 pytest 核心测试失败**: 基本 API 端点测试失败
- ❌ **服务无法启动**: Docker Compose 启动失败

### 8.3 仅作为告警的测试失败

以下测试失败**不会阻止**部署，但会在测试报告中标记为警告：

- ⚠️ **部分端点测试失败**: 某些非核心端点不可用（如 `/docs` 已禁用）
- ⚠️ **性能指标超出阈值**: 响应时间过长（> 1000ms），但功能正常
- ⚠️ **前端测试失败**: 前端测试配置缺失或部分失败

### 8.4 测试报告集成

部署脚本会自动：
1. ✅ 执行 `docs/api-testing/run-full-stack-tests.ps1`
2. ✅ 生成测试报告到 `docs/api-testing/output/full-stack-test-YYYYMMDD-HHMMSS/`
3. ✅ 在控制台显示测试报告路径
4. ✅ 根据测试结果决定退出码（生产环境）

---

## 9. 下一步行动

1. ✅ **创建测试计划文档**（本文档）
2. ✅ **创建后端 API pytest 测试**
3. ✅ **更新 requirements.txt 添加测试依赖**
4. ✅ **修改 PowerShell 测试脚本支持跳过端点**
5. ✅ **创建统一入口脚本**
6. ✅ **创建报告生成脚本**
7. ✅ **集成到部署流程**
8. ⏳ **执行测试并验证**

---

**最后更新**: 2025-11-15

