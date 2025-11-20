# 🚀 CI/CD 集成指南

## 📋 概述

本文档说明如何配置和使用 CI/CD 流水线，实现自动化构建、测试和部署。

---

## 🔧 GitHub Actions 配置

### 1. 工作流文件

**位置**: `.github/workflows/ci-cd.yml`

**触发条件**:
- 推送到 `main` 分支
- 推送到 `release/*` 分支
- 对 `main` 和 `release/*` 分支的 Pull Request

### 2. 工作流任务

#### Job 1: `build-and-test`

**功能**: 构建 Docker 镜像、启动服务、执行全栈测试

**步骤**:
1. ✅ Checkout 代码
2. ✅ 设置 Python 环境并安装依赖
3. ✅ 设置 Docker 和 Docker Compose
4. ✅ 创建测试用 `.env` 文件
5. ✅ 构建 Docker 镜像
6. ✅ 启动服务
7. ✅ 等待服务就绪
8. ✅ 运行后端 pytest API 测试
9. ✅ 运行 PowerShell API 测试（通过 pwsh）
10. ✅ 收集测试报告
11. ✅ 上传测试报告作为构建工件
12. ✅ 清理环境

**输出**:
- 测试报告（HTML、CSV、日志）
- Docker 日志

#### Job 2: `deploy-production`（可选）

**功能**: 自动部署到生产环境

**触发条件**:
- `build-and-test` 任务成功
- 推送到 `main` 分支（非 PR）

**步骤**:
1. ✅ Checkout 代码
2. ✅ 设置 Docker
3. ✅ 配置 SSH 密钥
4. ✅ SSH 到生产服务器并执行部署
5. ✅ 验证部署

---

## 🔐 GitHub Secrets 配置

### 必需 Secrets（用于生产部署）

| Secret 名称 | 说明 | 示例 | 必填 |
|------------|------|------|------|
| `SSH_PRIVATE_KEY` | SSH 私钥（用于连接生产服务器） | `-----BEGIN OPENSSH PRIVATE KEY-----...` | ✅ 是（如果启用自动部署） |
| `PROD_HOST` | 生产服务器 IP 或域名 | `165.154.233.55` | ✅ 是（如果启用自动部署） |
| `PROD_USER` | 生产服务器 SSH 用户名 | `ubuntu` | ✅ 是（如果启用自动部署） |
| `PROD_PATH` | 生产服务器项目路径 | `/opt/redpacket` | ⚠️ 可选（有默认值） |
| `PROD_ADMIN_BASE_URL` | 生产环境 Web Admin API 地址 | `http://165.154.233.55:8000` | ⚠️ 可选（有默认值） |
| `PROD_MINIAPP_BASE_URL` | 生产环境 MiniApp API 地址 | `http://165.154.233.55:8080` | ⚠️ 可选（有默认值） |

### 如何配置 GitHub Secrets

1. 打开 GitHub 仓库
2. 进入 **Settings** → **Secrets and variables** → **Actions**
3. 点击 **New repository secret**
4. 输入 Secret 名称和值
5. 点击 **Add secret**

---

## 🔄 CI/CD 流程说明

### 1. 构建和测试流程

```mermaid
graph TD
    A[Push to main/PR] --> B[Checkout Code]
    B --> C[Setup Python & Docker]
    C --> D[Build Docker Images]
    D --> E[Start Services]
    E --> F[Wait for Services]
    F --> G[Run pytest Tests]
    G --> H[Run PowerShell Tests]
    H --> I[Collect Reports]
    I --> J[Upload Artifacts]
    J --> K{All Tests Pass?}
    K -->|Yes| L[Continue]
    K -->|No| M[Mark as Failed]
```

### 2. 生产部署流程

```mermaid
graph TD
    A[Push to main] --> B[Build & Test Success]
    B --> C[SSH to Production]
    C --> D[Pull Latest Code]
    D --> E[Run deploy-production.ps1]
    E --> F[Wait for Services]
    F --> G[Run Full Stack Tests]
    G --> H{All Tests Pass?}
    H -->|Yes| I[Deployment Success]
    H -->|No| J[Deployment Failed]
```

---

## 📊 测试报告

### 报告位置

CI/CD 运行后，测试报告可以在以下位置找到：

1. **GitHub Actions 界面**:
   - 进入 **Actions** 标签
   - 选择对应的运行
   - 在 **Artifacts** 部分下载 `test-reports`

2. **本地运行**:
   - `docs/api-testing/output/full-stack-test-YYYYMMDD-HHMMSS/`

### 报告内容

- ✅ `ci-backend-pytest-report.html` - 后端 pytest 测试报告
- ✅ `ci-api-powershell-tests.csv` - PowerShell API 测试结果
- ✅ `docker-logs.txt` - Docker 容器日志

---

## 🎯 测试在 CI/CD 中的作用

### 阻断部署的测试

以下测试失败会**阻止**部署继续进行：

- ✅ 后端服务无法启动
- ✅ 健康检查失败（`/healthz` 返回非 200）
- ✅ 后端 pytest 测试失败（核心 API 端点）

### 仅作为告警的测试

以下测试失败**不会阻止**部署，但会标记为警告：

- ⚠️ PowerShell API 测试部分失败（某些端点不可用）
- ⚠️ 性能指标超出阈值（响应时间过长）

---

## 🔧 本地测试 CI/CD 流程

### 使用 act 工具（可选）

```bash
# 安装 act（本地运行 GitHub Actions）
# macOS: brew install act
# Linux: 参考 https://github.com/nektos/act

# 运行 CI/CD 工作流
act -j build-and-test
```

---

## 📝 自定义配置

### 修改测试超时时间

编辑 `.github/workflows/ci-cd.yml`:

```yaml
- name: Wait for services to be ready
  run: |
    timeout=120  # 修改为 120 秒
```

### 添加更多测试步骤

在 `build-and-test` job 中添加新步骤:

```yaml
- name: Run custom tests
  run: |
    # 你的测试命令
```

### 禁用自动部署

在 `.github/workflows/ci-cd.yml` 中注释掉 `deploy-production` job，或删除该 job。

---

## 🐛 故障排查

### 问题 1: Docker 构建失败

**可能原因**:
- Dockerfile 语法错误
- 依赖安装失败

**解决方案**:
1. 检查 GitHub Actions 日志
2. 本地运行 `docker-compose build` 验证
3. 检查 `requirements.txt` 或 `package.json` 依赖

### 问题 2: 服务无法启动

**可能原因**:
- 端口冲突
- 环境变量缺失

**解决方案**:
1. 检查 Docker 日志
2. 验证 `.env` 文件配置
3. 检查端口占用

### 问题 3: 测试失败

**可能原因**:
- 服务未完全启动
- 网络连接问题

**解决方案**:
1. 增加等待时间
2. 检查服务健康检查端点
3. 查看测试报告了解详细错误

### 问题 4: SSH 部署失败

**可能原因**:
- SSH 密钥配置错误
- 服务器连接问题

**解决方案**:
1. 验证 SSH 密钥格式
2. 测试 SSH 连接: `ssh -i ~/.ssh/key user@host`
3. 检查 GitHub Secrets 配置

---

## 📚 相关文档

- [自动部署指南](README-AUTO-DEPLOY.md) - 一键部署说明
- [环境变量配置指南](ENV-CONFIG-GUIDE.md) - 环境变量说明
- [全栈测试指南](../api-testing/README-FULL-STACK-TESTING.md) - 测试框架说明

---

**最后更新**: 2025-11-15

