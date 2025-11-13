# 多語翻譯執行計劃

> 目標語言：  
> 歐美 — 英語 (基準)、西班牙語、法語、德語、葡萄牙語  
> 東南亞 — 繁中/簡中、泰語、越南語、印尼語、馬來語、菲律賓語 (Tagalog)  
> 涵蓋介面：Telegram Bot、MiniApp、Web Admin、自動化活動與批量工具

---

## 1. 現況摘要

| 語言 | 缺漏鍵數（相對英文） | 備註 |
| --- | --- | --- |
| de | 420 | 中大型缺口，以 Web Admin 相關字串為主 |
| es | 421 | 與德語同級缺口 |
| fr | 419 | 與西語相近 |
| hi | 421 | 需補 Web Admin 與報表字串 |
| th | 713 | Bot/MiniApp + 後台幾乎皆缺，需要全面翻譯 |
| vi | 578 | 後台、活動流程缺口大 |
| zh | 30 | 補齊英文新增的提示語即可 |
| pt | 新增 | 需建立完整翻譯檔 |
| id | 新增 | 同上 |
| ms | 新增 | 同上 |
| fil | 新增 | 同上 |

詳細缺漏清單匯出為 `i18n_missing_summary.csv`（UTF-8 with BOM），方便翻譯業務分配。

---

## 2. 作業流程

1. **準備英文本基準**  
   - 確認 `core/i18n/messages/en.yml` 為最新版本，所有新增功能先補英文。  
   - 請開發者在提交新功能時同步維護英文 key。

2. **產生翻譯模板**  
   - 使用 `scripts/export_translations.py` 將 `en.yml` 展平成 `key,en` CSV：  
     ```bash
     python scripts/export_translations.py --output translations_export.csv \
       --langs es fr de pt th vi id ms fil zh
     ```  
   - CSV 欄位至少包含：`key`、`en`、各語言翻譯欄，必要時可自行新增註解欄位。

3. **翻譯作業**  
   - 分派語言給翻譯夥伴，參考 `docs/branding_guidelines.md` 的語調與 CTA 模板。  
   - 東南亞語系注意：  
     - 使用常見貨幣縮寫（USDT、TON、Points）。  
     - 菲律賓語可混合英語確保可讀性。  
     - 泰語/越語避免過度音譯，使用當地常用詞。  
   - 翻譯完成後以 CSV 形式回傳。

4. **載入翻譯**  
   - 透過 `scripts/import_translations.py` 回填：  
     ```bash
     python scripts/import_translations.py --input translations_export.csv
     ```  
     （如需限制語言可加 `--langs es fr`，若希望空白也覆蓋原值加 `--overwrite-empty`）  
   - 確保 YAML 結構、縮排、字串轉義（特別是 `:`、`{}`、`%`）正確。

5. **檢查與 QA**  
   - 執行缺漏檢查： `python scripts/check_i18n_gaps.py`（待新增，現階段可重用分析腳本）。  
   - 針對重大介面做語言切換檢查：Web Admin、MiniApp 卡片/Bot 訊息。  
   - 使用者測試：邀請目標語言母語者審閱關鍵流程。

6. **持續維護**  
   - 在 PR 模板加入「是否新增 i18n key」，提醒開發者同步翻譯。  
   - 建議每次發版前重新輸出缺漏清單，確保沒有遺漏。  
   - 建立 CI 檢查腳本（阻擋缺漏 key 或檢測格式）。

---

## 3. 開發任務拆解

| 任務 | 內容 | 優先順序 |
| --- | --- | --- |
| A. CSV 導出腳本 | 將英文 key 展平成翻譯模板 | 高 |
| B. CSV → YAML 回填 | 讀取翻譯 CSV 更新各語言 yml | 高 |
| C. 缺漏檢查 CI | 在 CI/PR 阶段檢查缺漏及非法字元 | 中 |
| D. 文案審核流程 | 建立 Slack/Issue 模板收集翻譯回饋 | 中 |

---

## 4. 建議排程與人力

1. **第 1 週**：完善腳本工具（A+B），產出翻譯模板，發送翻譯需求。  
2. **第 2–3 週**：收集翻譯結果、回填 YAML、進行 QA。  
3. **第 4 週**：整體語言切換測試，更新文檔，啟用 CI 檢查。  
4. **後續維護**：每個迭代統一檢查一次翻譯缺漏與品牌一致性。

如需加速，可將缺漏最多的語言（th、vi）優先安排翻譯，並同步處理新增語言檔案（pt、id、ms、fil）。

---

## 5. 參考資源

- `i18n_missing_summary.csv`：每個語言缺漏統計，可使用 `scripts/export_translations.py` 重建。  
- `docs/branding_guidelines.md`：語調、CTA、品牌配色。  
- `core/i18n/messages/en.yml`：翻譯基準檔。  
- `scripts/export_translations.py`、`scripts/import_translations.py`：翻譯工作流工具。

若後續增加語言或產生新功能，請回到本計劃更新相關任務與腳本。*** End Patch

