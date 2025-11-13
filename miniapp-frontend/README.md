# MiniApp 前端 (React + Vite)

此專案為 Telegram MiniApp 的前端介面，串接同倉庫的 FastAPI 後端。提供自動登入、公開群列表與活動面板等功能，並預留擴展空間。

## ✨ 技術棧
- React 19 + TypeScript
- Vite 7
- Tailwind CSS 3
- @tanstack/react-query + React Query Devtools
- Axios + 自訂 API 驗證攔截器
- 可選 Telegram WebApp SDK (`@twa-dev/sdk`)

## 🔧 快速開始
```bash
# 進入專案
cd miniapp-frontend

# 安裝依賴
npm install

# 啟動開發伺服器（預設 http://localhost:5173）
npm run dev -- --host
```

開發時請同時啟動後端 API (`miniapp.main:app`)，以確保登入與資料拉取正常。

## ⚙️ 環境變數
在專案根目錄建立 `.env.local`（不納入版本控制），範例如下：
```
VITE_API_BASE_URL=http://localhost:8080/api
VITE_DEV_USERNAME=miniapp_admin
VITE_DEV_PASSWORD=admin-secret
VITE_DEV_TG_ID=99999
VITE_DEFAULT_LANG=zh
VITE_ENABLE_DEVTOOLS=true
```
- `VITE_API_BASE_URL`：後端 API 根路徑。
- `VITE_DEV_*`：本地測試用的密碼模式登入帳密（對應後端 `/api/auth/login`）。
- `VITE_ENABLE_DEVTOOLS`：是否啟用 React Query Devtools。

若在 Telegram 真實環境（具備 `initData`），會優先採用 `initData` 自動登入；無資料時則退回 DEV 登入。

## 📁 目錄結構
```
src/
├── api/                # axios 實例與 API 呼叫封裝
├── components/         # UI 元件（群卡片、活動卡片、錯誤提示等）
├── hooks/              # React Query hooks
├── providers/          # AuthProvider 管理登入狀態
├── types/              # TypeScript 型別
├── utils/              # Telegram 工具
├── App.tsx             # 首頁版面
└── main.tsx            # React 入口
```

## 🚀 後續擴充建議
- 整合 Telegram WebApp SDK 的 UI 元件（關閉按鈕、主題切換、跳轉等）。
- 完善公開群搜尋、篩選、收藏狀態同步邏輯。
- 活動詳情頁、批次加入 / 曝光提醒。
- 加入 E2E 測試與視覺測試流程。

如需與後端同步調整（登入格式、API 變更），請同步更新 `src/api` 與對應 TypeScript 型別。
