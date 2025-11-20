# 红包系统自动化部署 Makefile

.PHONY: help deploy deploy-staging deploy-production setup test clean

# 配置（可以通过环境变量覆盖）
DEPLOY_HOST ?= 165.154.233.55
DEPLOY_USER ?= ubuntu
DEPLOY_PORT ?= 22
DEPLOY_PATH ?= /opt/redpacket
SSH_KEY ?= ~/.ssh/id_rsa

help: ## 显示帮助信息
	@echo "可用命令:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""

setup: ## 设置自动化部署环境
	@echo "🔧 设置自动化部署环境..."
	@bash deploy/scripts/setup_auto_deploy.sh

deploy: ## 部署到默认环境（生产）
	@echo "🚀 部署到生产环境..."
	@bash deploy/scripts/auto_deploy_pipeline.sh $(DEPLOY_HOST) $(DEPLOY_USER)

deploy-remote: ## 使用远程部署脚本部署（推荐）
	@echo "🚀 使用远程部署脚本部署..."
	@bash deploy/scripts/deploy_remote.sh $(DEPLOY_BRANCH)

deploy-staging: ## 部署到测试环境
	@echo "🚀 部署到测试环境..."
	@DEPLOY_PATH=/opt/redpacket-staging bash deploy/scripts/auto_deploy_pipeline.sh $(DEPLOY_HOST) $(DEPLOY_USER)

deploy-production: deploy ## 部署到生产环境（deploy 的别名）
	@true

test-ssh: ## 测试 SSH 连接
	@echo "🔍 测试 SSH 连接..."
	@ssh -i $(SSH_KEY) -p $(DEPLOY_PORT) -o ConnectTimeout=5 \
		-o StrictHostKeyChecking=no \
		$(DEPLOY_USER)@$(DEPLOY_HOST) \
		"echo '✅ SSH 连接成功' && uname -a"

check-env: ## 检查本地环境
	@echo "🔍 检查本地环境..."
	@which git > /dev/null || (echo "❌ Git 未安装" && exit 1)
	@which ssh > /dev/null || (echo "❌ SSH 未安装" && exit 1)
	@which docker > /dev/null || (echo "⚠️  Docker 未安装（可选）" || true)
	@echo "✅ 环境检查通过"

status: ## 查看服务器服务状态
	@echo "📊 查看服务器服务状态..."
	@ssh -i $(SSH_KEY) -p $(DEPLOY_PORT) $(DEPLOY_USER)@$(DEPLOY_HOST) \
		"cd $(DEPLOY_PATH) && docker compose -f docker-compose.production.yml ps"

logs: ## 查看服务器日志
	@echo "📋 查看服务器日志..."
	@ssh -i $(SSH_KEY) -p $(DEPLOY_PORT) $(DEPLOY_USER)@$(DEPLOY_HOST) \
		"cd $(DEPLOY_PATH) && docker compose -f docker-compose.production.yml logs --tail 100"

webhook-start: ## 启动 Webhook 接收器（本地）
	@echo "🚀 启动 Webhook 接收器..."
	@python deploy/scripts/webhook_receiver.py

clean: ## 清理本地临时文件
	@echo "🧹 清理临时文件..."
	@rm -f .env.deploy
	@rm -f deploy.log

# 快速命令
quick-deploy: check-env test-ssh deploy ## 快速部署（检查 + 测试 + 部署）
