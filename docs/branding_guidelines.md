# 品牌與多語一致性指引

> 適用範圍：Telegram Bot、MiniApp、Web Admin（含自動化活動、報表、批量工具）  
> 目標市場：歐美（英語、西班牙語、法語、德語、葡萄牙語），東南亞（繁中/簡中、泰語、越南語、印尼語、馬來語、菲律賓語）

本文件提供統一的視覺語言、文案語氣與 CTA 模板，確保不同客群與介面維持一致品牌體驗。

---

## 1. 核心品牌要素

### 1.1 色彩系統
| 類別 | HEX | Tailwind 建議 | 使用情境 |
| --- | --- | --- | --- |
| Primary / Brand | `#FF675C` | `bg-[#FF675C]` 系列 | Bot 重點文字、MiniApp 卡片標題、Web Admin 主按鈕/強調標籤 |
| Primary Light | `#FFF0E8` | `bg-[#FFF0E8]` | 卡片背景、通知條、Hover 狀態 |
| Secondary | `#3B82F6` | `bg-blue-500` | 操作按鈕（次要 CTA）、連結 |
| Success | `#16A34A` | `bg-emerald-500` | 完成提示、成功徽章 |
| Warning | `#F59E0B` | `bg-amber-500` | 提醒、名額將滿倒數 |
| Danger | `#EF4444` | `bg-red-500` | 風險警告、錯誤提示 |
| Neutral Dark | `#111827` | `text-gray-900` | 主要文字 |
| Neutral Mid | `#6B7280` | `text-gray-500` | 次要說明、輔助資訊 |
| Neutral Light | `#E5E7EB` | `border-gray-200` | 分隔線、邊框 |

- 優先使用 Tailwind 配色，必要時使用原始 HEX。  
- 同一畫面最多使用 1 個主色、1 個次色、1 個強調色，避免視覺噪音。  
- 圖像/封面應保留品牌色為主基底（參考《公開群營運手冊》既有建議）。

### 1.2 字體 / 排版
- **Web Admin**：沿用 Tailwind `font-sans` （系統 UI 字型），標題 `font-semibold`、內文 `font-normal`，行距 1.5。  
- **MiniApp / Bot**：遵循 Telegram 預設，標題字串可加入 Emoji 突出主題，內文保持 18–22 字元換行。  
- 數字、幣別、百分比使用等寬數字格式（Tailwind `font-mono`）。

### 1.3 圖示與 Emoji
- 允許搭配品牌相關 emoji（🧧、🎉、📊），但每句不超過 2 個。  
- 功能按鈕（Bot inline keyboard、MiniApp CTA）使用 icon + 動詞：`🧧 發紅包`、`📊 查看報表`。  
- Web Admin 使用 Heroicons/Tailwind 預設 icon，如需自製 SVG，線條粗細 1.5px，圓角對齊 4px。

---

## 2. 文案語氣與 CTA

### 2.1 整體語調
- 友善、指引式、強調獎勵與安全性。  
- 句子簡潔，中文 ≤ 20 字，英文 ≤ 110 字元。  
- 關鍵詞統一：`紅包` (zh)、`Red Packet` (en)、`Paquete` (es)、`Angpao` (id/ms) 等。

### 2.2 CTA 模板（主副文案）
| 場景 | 主 CTA | 副文案 / 補充 |
| --- | --- | --- |
| MiniApp 卡片 | `立即領取 {points} 星` / `Claim {points} pts now` | `剩餘 {count} 名額` / `Only {count} slots left` |
| Bot 訊息 | `🧧 發紅包`、`🤲 立即搶` | `限 {token}`、`倒數 {timer}` |
| Web Admin 主按鈕 | `保存設定` / `Save changes` | `已套用即時更新` |
| 批量操作 | `批量暫停` / `Pause selected` | `已選 {count} 筆` |
| 報表匯出 | `匯出 CSV` / `Export CSV` | `含轉化率/失敗次數` |

> 多語落地：建立 CTA 字串對照表（英文為主），翻譯時保留動詞開頭、避免直譯。  
> 東南亞語系可沿用拉丁字母（vi、id、ms、fil）或原文（th）。

### 2.3 Tone 指南（語系重點）
- **英文**：專業但友善，使用第二人稱 `you`。  
- **西/法/德/葡**：保持敬語（`¡Hola!` / `Bonjour !`），CTA 以命令式動詞開頭。  
- **泰/越/印尼/馬來**：盡量使用常見數字+拉丁術語（USDT、TON），避免過度音譯。  
- **繁中/簡中**：維持既有語氣（「立即」、「請先」、「成功」），簡中避免台灣用語。  
- **菲律賓**：建議混用英/塔加洛語（例：`I-claim na ang 10 star reward!`）。

---

## 3. 介面實作建議

### 3.1 Telegram Bot 範本
```
🎉 {activity_name}
🎁 基礎獎勵：{reward_points} 星
⚡ 限時加碼：{bonus_points} 星（剩餘 {slots} 名）
⏳ 倒數：{hours_left} 小時
📌 規則概覽：{rule_short}
👉 點選按鈕即可參加
```
按鈕：`🤲 立即參加` / `🧧 發紅包`。資訊過多時可加入 `查看更多` 連結到 MiniApp。

### 3.2 MiniApp 卡片
- 標題：主色字，20 字以內。  
- 副標：次色字，突出獎勵/名額。  
- Badge：使用 Primary Light 背景 + Primary 字體。  
- CTA：Primary 背景 + 白字；次要 CTA 使用 Secondary。  
- 倒數與餘額以 Warning 色呈現。

### 3.3 Web Admin
- 頁首與導航沿用 Neutral 色系，主按鈕才使用品牌色，避免視覺疲勞。  
- 通知條：成功 -> `bg-emerald-50 text-emerald-700`；錯誤 -> `bg-red-50 text-red-700`。  
- 批量工具列：Primary Light 背景、藍色或品牌色按鈕，保持對比度 ≥ 4.5。  
- 圖表/報表：建議使用單色漸層（品牌色 → 60% 透明），搭配 Neutral 線條。

---

## 4. 多語翻譯輸出流程
1. 以 `en.yml` 為母版，將所有 key 匯出 CSV (`key,en`)。  
2. 建立各語系對照欄（`es, fr, de, pt, th, vi, id, ms, fil, zh-Hant, zh-Hans`）。  
3. 翻譯時參考 CTA 模板與語氣指引，必要時補充註解。  
4. 完成後重新產生 `*.yml`（保持 key 順序與縮排）。  
5. 每次發版前跑自動檢查腳本（`gap_counts.py`）確保無缺漏。

---

## 5. 品牌檢查清單
- [ ] 所有新增頁面/訊息都引用品牌色而非任意 HEX。  
- [ ] CTA 文案符合語氣指南、已提供主要語言翻譯。  
- [ ] Emoji 使用在 2 個以內，保留易讀性。  
- [ ] 圖片/封面採用品牌主色＋淺底色。  
- [ ] 翻譯檔 `*.yml` 不含硬編碼 HTML/CSS，交由模板控制。  
- [ ] 在 README / Ops 文檔引用品牌指引連結，提醒專案成員遵循。

如需進一步的樣式套件（CSS variables、Tailwind preset）或翻譯表模板，可在此文件基礎上擴充。歡迎隨著品牌調性調整而更新本文件。*** End Patch

