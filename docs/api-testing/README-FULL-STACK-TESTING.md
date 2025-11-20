# 🧪 全栈测试指南

## 📋 概述

本文档介绍如何使用统一的全栈测试框架，一次性执行所有测试并生成结构化报告。

---

## 🚀 快速开始

### 1. 设置测试环境

确保已安装必要的依赖：

```bash
# 安装 Python 测试依赖
pip install pytest pytest-html requests urllib3
```

### 2. 执行全栈测试

#### 本地开发环境

```powershell
# 设置测试目标地址（本地）
$env:API_TEST_ADMIN_BASE_URL = "http://localhost:8000"
$env:API_TEST_MINIAPP_BASE_URL = "http://localhost:8080"

# 执行测试
cd docs/api-testing
.\run-full-stack-tests.ps1
```

#### 生产环境

```powershell
# 设置测试目标地址（生产）
$env:API_TEST_ADMIN_BASE_URL = "http://165.154.233.55:8000"
$env:API_TEST_MINIAPP_BASE_URL = "http://165.154.233.55:8080"

# 执行测试
cd docs/api-testing
.\run-full-stack-tests.ps1
```

或直接使用参数：

```powershell
.\run-full-stack-tests.ps1 -AdminBaseUrl "http://165.154.233.55:8000" -MiniAppBaseUrl "http://165.154.233.55:8080"
```

---

## 📊 测试输出结构

测试完成后，所有结果保存在带时间戳的输出目录中：

```
docs/api-testing/output/
└── full-stack-test-20251115-120000/
    ├── summary.json                    # 测试汇总 JSON
    ├── summary.csv                     # 测试汇总 CSV
    ├── full-stack-test-report.html     # 统一 HTML 报告 ⭐
    ├── api-powershell-tests.csv        # PowerShell API 测试结果
    ├── api-powershell-error.log        # PowerShell 错误日志
    ├── backend-pytest-report.html      # pytest HTML 报告
    └── backend-pytest-output.log       # pytest 输出日志
```

---

## 📋 测试内容

### 1. PowerShell API 测试

**脚本**: `run-comprehensive-test-improved.ps1`

**测试端点**:
- ✅ Web Admin API:
  - `/healthz` - 健康检查
  - `/readyz` - 就绪检查
  - `/metrics` - Prometheus 指标
  - `/openapi.json` - OpenAPI Schema
  - `/admin/api/v1/dashboard/public` - Dashboard 公开数据
  - ⏭️ `/docs` - Swagger UI（已禁用，跳过）
- ✅ MiniApp API:
  - `/healthz` - 健康检查
  - `/openapi.json` - OpenAPI Schema
  - `/v1/groups/public` - 公开群组列表
  - `/v1/groups/public/activities` - 群组活动列表
  - ⏭️ `/docs` - Swagger UI（已禁用，跳过）

### 2. 后端 pytest API 测试

**目录**: `tests/api/`

**测试文件**:
- `test_admin_api_endpoints.py` - Web Admin API 端点测试
- `test_miniapp_api_endpoints.py` - MiniApp API 端点测试

**测试内容**: 与 PowerShell 测试类似，但使用 pytest 框架，支持更详细的断言和报告。

### 3. 前端 Smoke Test

**状态**: ✅ 已配置（基础 smoke test）

**测试内容**:
- 前端首页可访问性（`/`）
- 前端群组页面可访问性（`/groups`）

**测试方式**: PowerShell HTTP 请求测试（页面状态码检查）

**报告位置**: `frontend-smoke-test-report.html`

**注意**: 
- 当前为简单的 smoke test（页面可访问性检查）
- 如需完整的前端单元测试/E2E 测试，需要配置测试框架（Vitest/Jest + Playwright）

---

## 📄 报告内容

### 统一 HTML 报告

生成的 `full-stack-test-report.html` 包含：

1. **测试概览**
   - 测试时间、环境、目标 IP/域名
   - 总测试数、通过/失败/跳过数量
   - 成功率、总耗时

2. **性能指标**
   - 每个测试阶段的耗时
   - 平均响应时间（从 PowerShell 测试结果）

3. **测试阶段详情**
   - PowerShell API 测试结果（表格）
   - 后端 pytest 测试结果（链接到详细报告）
   - 前端 Smoke Test 结果（表格）

4. **详细测试结果**
   - 每个测试用例的状态、响应时间、状态码
   - 链接到原始测试报告（`backend-pytest-report.html`、`frontend-smoke-test-report.html`）

5. **错误日志摘要**
   - PowerShell 错误日志预览
   - 后端 pytest 输出预览
   - 前端测试输出预览（如果有）
   - 完整日志文件路径

---

## 🔧 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|-------|------|--------|
| `API_TEST_ADMIN_BASE_URL` | Web Admin API 基础地址 | `http://165.154.233.55:8000` |
| `API_TEST_MINIAPP_BASE_URL` | MiniApp API 基础地址 | `http://165.154.233.55:8080` |

### 测试脚本参数

`run-full-stack-tests.ps1` 支持的参数：

- `-AdminBaseUrl`: Web Admin API 基础地址
- `-MiniAppBaseUrl`: MiniApp API 基础地址
- `-OutputRoot`: 输出根目录（默认: `docs/api-testing/output`）

---

## 📝 已知限制

1. **已禁用的端点**: `/docs` 和 `/redoc` 在生产环境返回 404（设计上已禁用），测试会自动标记为「跳过」而非「失败」。

2. **认证端点**: 某些需要认证的端点（如 `/admin/api/v1/dashboard`）在测试中会返回 401/302，这是预期行为。测试中会优先测试公开端点。

3. **前端测试**: 当前前端测试为简单的 smoke test（页面可访问性检查）。如需完整的前端单元测试/E2E 测试，需要配置测试框架（Vitest/Jest + Playwright）。

4. **PDF 报告**: 当前仅生成 HTML 报告。PDF 报告功能待实现。

---

## 🐛 故障排查

### 问题 1: pytest 未找到

**错误**: `pytest not found`

**解决方案**:
```bash
pip install pytest pytest-html
```

### 问题 2: 测试失败（连接超时）

**错误**: `Connection timed out` 或 `Unable to connect`

**解决方案**:
1. 检查服务器是否运行
2. 检查防火墙/安全组配置
3. 确认测试目标地址正确

### 问题 3: 报告生成失败

**错误**: `Report generation failed`

**解决方案**:
1. 确认 Python 已安装
2. 检查 `render-full-stack-report.py` 是否存在
3. 查看错误日志了解详细信息

---

## 🔗 前端与后端集成配置

### 构建前环境变量设置

在构建前端 Docker 镜像之前，必须确保以下环境变量已设置：

#### Next.js 前端（frontend-next）

**必需环境变量**:
- `NEXT_PUBLIC_ADMIN_API_BASE_URL` - Web Admin API 基础地址
- `NEXT_PUBLIC_MINIAPP_API_BASE_URL` - MiniApp API 基础地址

**配置方式**:

1. **Docker Compose 环境变量**（推荐）
   ```yaml
   frontend:
     environment:
       NEXT_PUBLIC_ADMIN_API_BASE_URL: ${NEXT_PUBLIC_ADMIN_API_BASE_URL:-http://localhost:8000}
       NEXT_PUBLIC_MINIAPP_API_BASE_URL: ${NEXT_PUBLIC_MINIAPP_API_BASE_URL:-http://localhost:8080}
   ```

2. **构建参数**（Dockerfile）
   ```dockerfile
   ARG NEXT_PUBLIC_ADMIN_API_BASE_URL
   ARG NEXT_PUBLIC_MINIAPP_API_BASE_URL
   ENV NEXT_PUBLIC_ADMIN_API_BASE_URL=$NEXT_PUBLIC_ADMIN_API_BASE_URL
   ENV NEXT_PUBLIC_MINIAPP_API_BASE_URL=$NEXT_PUBLIC_MINIAPP_API_BASE_URL
   ```

3. **.env 文件**
   ```bash
   # .env.production
   NEXT_PUBLIC_ADMIN_API_BASE_URL=http://165.154.233.55:8000
   NEXT_PUBLIC_MINIAPP_API_BASE_URL=http://165.154.233.55:8080
   ```

**⚠️ 重要**: Next.js 的 `NEXT_PUBLIC_*` 变量在**构建时**注入，运行时无法修改。因此：
- 本地开发: 使用 `http://localhost:8000`
- 生产环境: 使用公网 IP 或域名（如 `http://165.154.233.55:8000`）

### 前端调用后端的方式

前端通过以下方式调用后端 API：

1. **Web Admin API** (`frontend-next/src/api/admin.ts`)
   ```typescript
   const ADMIN_API_BASE_URL = process.env.NEXT_PUBLIC_ADMIN_API_BASE_URL || 'http://localhost:8000'
   ```

2. **MiniApp API** (`frontend-next/src/api/miniapp.ts`)
   ```typescript
   const MINIAPP_API_BASE_URL = process.env.NEXT_PUBLIC_MINIAPP_API_BASE_URL || 'http://localhost:8080'
   ```

### 测试前端与后端集成

当前测试框架主要测试后端 API，前端测试暂时未配置。如果需要在测试中验证前端与后端的集成：

1. **E2E 测试**（如果配置了 Playwright / Cypress）:
   - 测试页面加载和 API 调用
   - 验证前端能正确调用后端 API
   - 验证前端能正确处理后端响应

2. **手动验证**:
   - 访问前端页面: `http://localhost:3001`（本地）或生产地址
   - 检查浏览器开发者工具 Network 标签
   - 验证 API 请求是否发送到正确的后端地址

---

## 📚 相关文档

- [全栈测试计划](full-stack-test-plan.md) - 详细的测试计划和实现说明
- [环境与连接性检查报告](env-and-connectivity-check.md) - 环境配置检查报告
- [完整 API 测试清单](完整API测试清单.md) - 所有待测试的 API 端点清单
- [自动部署指南](../deployment/README-AUTO-DEPLOY.md) - 一键部署说明

---

## 🔄 更新日志

- **2025-11-15**: 创建全栈测试框架
  - 添加 PowerShell API 测试脚本（支持跳过已禁用端点）
  - 添加后端 pytest API 测试
  - 添加统一入口脚本
  - 添加报告生成脚本

---

**最后更新**: 2025-11-15

