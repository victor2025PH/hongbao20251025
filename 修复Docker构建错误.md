# 🔧 修復 Docker 構建錯誤

## 📊 問題診斷

從終端輸出看到：

**錯誤訊息：**
```
ERROR [bot] exporting to image
ERROR [web_admin] exporting to image
target bot: failed to solve: image "docker.io/redpacket/backend:latest": already exists
```

**問題原因：**
- Docker 鏡像 `docker.io/redpacket/backend:latest` 已經存在
- 構建時無法覆蓋已存在的鏡像
- 需要先刪除舊鏡像或使用強制重建

---

## 🔧 解決方案

### 方法 1: 刪除舊鏡像並重新構建（推薦）

**一鍵修復命令（複製所有命令，一次性執行）：**

```bash
cd /opt/redpacket && \
echo "🗑️  步驟 1: 刪除舊的 Docker 鏡像..." && \
docker rmi redpacket/backend:latest 2>/dev/null || echo "  鏡像不存在或已被使用，將使用 --no-cache 重建" && \
docker rmi redpacket/frontend:latest 2>/dev/null || echo "  前端鏡像不存在或已被使用，將使用 --no-cache 重建" && \
echo "" && \
echo "🔨 步驟 2: 停止並刪除現有容器..." && \
docker compose -f docker-compose.production.yml down 2>/dev/null || echo "  沒有運行中的容器" && \
echo "" && \
echo "🔨 步驟 3: 重新構建鏡像（不使用緩存）..." && \
docker compose -f docker-compose.production.yml build --no-cache && \
echo "" && \
echo "🚀 步驟 4: 啟動所有服務..." && \
docker compose -f docker-compose.production.yml up -d && \
echo "" && \
echo "⏳ 步驟 5: 等待服務啟動（30秒）..." && \
sleep 30 && \
echo "" && \
echo "📊 步驟 6: 檢查服務狀態..." && \
docker compose -f docker-compose.production.yml ps && \
echo "" && \
echo "🧪 步驟 7: 測試健康檢查..." && \
curl -s http://127.0.0.1:8000/healthz && echo "" || echo "⚠️  Web Admin 健康檢查失敗"
```

---

### 方法 2: 分步執行（更安全）

```bash
# 步驟 1: 停止並刪除現有容器
cd /opt/redpacket
docker compose -f docker-compose.production.yml down

# 步驟 2: 刪除舊的 Docker 鏡像（如果存在）
docker rmi redpacket/backend:latest redpacket/frontend:latest 2>/dev/null || true

# 步驟 3: 清理 Docker 系統（可選，釋放空間）
docker system prune -f

# 步驟 4: 重新構建鏡像（不使用緩存）
docker compose -f docker-compose.production.yml build --no-cache

# 步驟 5: 啟動所有服務
docker compose -f docker-compose.production.yml up -d

# 步驟 6: 等待並檢查
sleep 30
docker compose -f docker-compose.production.yml ps

# 步驟 7: 測試健康檢查
curl http://127.0.0.1:8000/healthz
curl http://127.0.0.1:8080/healthz
```

---

### 方法 3: 使用強制重建（如果鏡像被容器使用）

如果鏡像被容器使用無法刪除：

```bash
cd /opt/redpacket

# 強制停止並刪除所有容器和鏡像
docker compose -f docker-compose.production.yml down --rmi all

# 重新構建
docker compose -f docker-compose.production.yml build --no-cache

# 啟動服務
docker compose -f docker-compose.production.yml up -d

# 檢查狀態
sleep 30
docker compose -f docker-compose.production.yml ps
```

---

## 🔍 故障排查

### 如果構建仍然失敗

**檢查 Docker 鏡像和容器：**

```bash
# 查看所有鏡像
docker images | grep redpacket

# 查看所有容器
docker ps -a | grep redpacket

# 查看構建日誌
docker compose -f docker-compose.production.yml build 2>&1 | tee build.log

# 查看錯誤信息
grep -i error build.log
```

### 如果前端構建被取消

**前端構建可能需要較長時間，可以單獨構建：**

```bash
cd /opt/redpacket

# 只構建前端
docker compose -f docker-compose.production.yml build --no-cache frontend

# 然後構建其他服務
docker compose -f docker-compose.production.yml build --no-cache
```

### 如果空間不足

**清理 Docker 系統：**

```bash
# 查看 Docker 磁盤使用情況
docker system df

# 清理未使用的資源
docker system prune -a -f

# 清理 volumes（小心：會刪除數據）
# docker volume prune -f
```

---

## ✅ 預期結果

修復後，您應該看到：

```
✅ 所有鏡像構建成功
✅ 所有容器狀態為 "Up" 或 "healthy"
✅ /healthz 返回 {"ok": true, "ts": "..."}
✅ 無錯誤日誌
```

---

**請執行上面的修復命令，告訴我結果！**

