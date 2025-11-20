# 🔧 修復 Docker 鏡像錯誤 - 最終方案

## 📊 問題說明

從終端輸出看到 Docker 構建錯誤：
```
ERROR [bot] exporting to image
ERROR [web_admin] exporting to image
target bot: failed to solve: image "docker.io/redpacket/backend:latest": already exists
```

**注意：** 這些是錯誤信息，不是命令！請不要直接複製錯誤信息執行。

---

## ✅ 解決方案（一鍵修復）

**請在服務器終端中執行以下修復命令（複製所有命令，一次性執行）：**

```bash
cd /opt/redpacket && \
echo "====================================" && \
echo "🔧 開始修復 Docker 構建問題" && \
echo "====================================" && \
echo "" && \
echo "🗑️  步驟 1: 停止並刪除現有容器..." && \
docker compose -f docker-compose.production.yml down 2>/dev/null || echo "  沒有運行中的容器" && \
echo "" && \
echo "🗑️  步驟 2: 刪除舊的 Docker 鏡像..." && \
docker rmi redpacket/backend:latest redpacket/frontend:latest 2>/dev/null || echo "  鏡像不存在或已被使用" && \
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
curl -s http://127.0.0.1:8000/healthz && echo "" || echo "⚠️  Web Admin 健康檢查失敗，請查看日誌" && \
echo "" && \
echo "====================================" && \
echo "✅ 修復完成！" && \
echo "===================================="
```

---

## 📋 分步執行（如果一鍵命令有問題）

### 步驟 1: 停止並刪除現有容器

```bash
cd /opt/redpacket
docker compose -f docker-compose.production.yml down
```

### 步驟 2: 刪除舊的 Docker 鏡像

```bash
# 查看現有鏡像
docker images | grep redpacket

# 刪除舊鏡像（如果存在）
docker rmi redpacket/backend:latest redpacket/frontend:latest

# 如果鏡像被容器使用，先強制刪除容器
docker rm -f $(docker ps -aq) 2>/dev/null || true
docker rmi redpacket/backend:latest redpacket/frontend:latest 2>/dev/null || true
```

### 步驟 3: 重新構建鏡像

```bash
cd /opt/redpacket

# 構建所有服務（不使用緩存）
docker compose -f docker-compose.production.yml build --no-cache

# 如果構建時間太長，可以單獨構建：
# docker compose -f docker-compose.production.yml build --no-cache web_admin
# docker compose -f docker-compose.production.yml build --no-cache frontend
```

### 步驟 4: 啟動所有服務

```bash
cd /opt/redpacket
docker compose -f docker-compose.production.yml up -d
```

### 步驟 5: 檢查服務狀態

```bash
# 等待服務啟動
sleep 30

# 查看服務狀態
docker compose -f docker-compose.production.yml ps

# 查看日誌
docker compose -f docker-compose.production.yml logs --tail 50
```

### 步驟 6: 測試健康檢查

```bash
# Web Admin 健康檢查
curl http://127.0.0.1:8000/healthz

# MiniApp API 健康檢查
curl http://127.0.0.1:8080/healthz

# 前端服務測試
curl http://127.0.0.1:3001 | head -20
```

---

## 🔍 常見問題

### 問題 1: 鏡像無法刪除（被容器使用）

**解決方案：**

```bash
# 強制停止並刪除所有容器
docker compose -f docker-compose.production.yml down --rmi all

# 或者手動刪除
docker stop $(docker ps -aq) 2>/dev/null || true
docker rm $(docker ps -aq) 2>/dev/null || true
docker rmi redpacket/backend:latest redpacket/frontend:latest 2>/dev/null || true
```

### 問題 2: 構建時間太長

**解決方案：**

```bash
# 只構建需要的服務
docker compose -f docker-compose.production.yml build --no-cache web_admin
docker compose -f docker-compose.production.yml build --no-cache frontend
```

### 問題 3: 磁盤空間不足

**解決方案：**

```bash
# 清理 Docker 系統
docker system prune -a -f

# 查看磁盤使用
df -h
docker system df
```

### 問題 4: 構建仍然失敗

**解決方案：**

```bash
# 查看詳細構建日誌
docker compose -f docker-compose.production.yml build --no-cache 2>&1 | tee build.log

# 查看錯誤信息
grep -i error build.log

# 查看特定服務的構建
docker compose -f docker-compose.production.yml build --no-cache web_admin --progress=plain
```

---

## ✅ 驗證部署成功

部署成功後，應該滿足：

- [ ] ✅ 所有 Docker 鏡像構建成功（無錯誤）
- [ ] ✅ 所有容器狀態為 `Up` 或 `healthy`
- [ ] ✅ Web Admin 健康檢查通過：`curl http://127.0.0.1:8000/healthz` 返回 `{"ok": true}`
- [ ] ✅ MiniApp API 健康檢查通過：`curl http://127.0.0.1:8080/healthz` 返回 `{"ok": true}`
- [ ] ✅ 前端服務可訪問：`curl http://127.0.0.1:3001`
- [ ] ✅ 服務日誌無嚴重錯誤

---

## 📞 需要幫助？

如果遇到問題，請：

1. **查看服務日誌**：
   ```bash
   docker compose -f docker-compose.production.yml logs -f
   ```

2. **檢查服務狀態**：
   ```bash
   docker compose -f docker-compose.production.yml ps
   ```

3. **查看構建日誌**：
   ```bash
   docker compose -f docker-compose.production.yml build --no-cache 2>&1 | tee build.log
   ```

---

**現在請在服務器終端中執行上面的修復命令！**

**記住：只複製上面的命令，不要複製錯誤信息！**

