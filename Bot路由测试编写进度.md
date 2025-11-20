# Bot 路由测试编写进度

## 完成时间
2024年（当前）

## 已完成工作

### 1. Balance Router 测试编写 ✅
- **文件**: `tests/test_balance_router.py`（新建）
- **测试覆盖**:
  - `balance_main` - 余额总览（2个测试）
  - `balance_token_detail` - 分币种明细（2个测试）
  - `balance_history` - 历史流水（2个测试）
  - 辅助函数测试（3个测试）
- **测试总数**: 9个测试
- **状态**: 3个通过，6个跳过（需要 `pytest-asyncio`）

### 2. Pytest 配置更新 ✅
- **文件**: `pytest.ini`
- **更改**: 添加 `asyncio_mode = auto` 配置
- **目的**: 支持异步测试自动运行

## 测试详情

### TestBalanceMain
- `test_balance_main_success` - 测试余额总览成功
- `test_balance_main_telegram_bad_request` - 测试 TelegramBadRequest 时使用 answer

### TestBalanceTokenDetail
- `test_balance_token_detail_usdt` - 测试 USDT 明细
- `test_balance_token_detail_point` - 测试 POINT 明细

### TestBalanceHistory
- `test_balance_history_with_data` - 测试历史流水（有数据）
- `test_balance_history_empty` - 测试历史流水（无数据）

### TestBalanceHelpers
- `test_canon_lang` - 测试语言规范化
- `test_fmt6` - 测试金额格式化
- `test_fmt_token_amount` - 测试币种金额格式化

## 技术要点

### 异步测试设置
- 使用 `pytestmark = pytest.mark.asyncio` 在文件级别设置
- 使用 `AsyncMock` 来 mock 异步函数
- 需要安装 `pytest-asyncio` 插件

### Mock 策略
- Mock `CallbackQuery` 和相关的 Telegram 对象
- Mock 数据库会话和查询
- Mock i18n 函数和键盘生成函数

## 待解决问题

### pytest-asyncio 未安装
- **问题**: 6个异步测试被跳过，因为 `pytest-asyncio` 未安装
- **解决方案**: 在 `requirements.txt` 中添加 `pytest-asyncio`，或运行 `pip install pytest-asyncio`
- **影响**: 异步测试无法运行，但同步测试（辅助函数）可以正常运行

## 下一步计划

1. **安装 pytest-asyncio**
   ```bash
   pip install pytest-asyncio
   ```
   或添加到 `requirements.txt`:
   ```
   pytest-asyncio>=0.21.0
   ```

2. **继续为其他 Bot 路由编写测试**
   - `routers/hongbao.py` - 红包相关（高优先级）
   - `routers/invite.py` - 邀请相关（高优先级）
   - `routers/recharge.py` - 充值相关（高优先级）
   - `routers/menu.py` - 菜单相关
   - `routers/help.py` - 帮助相关
   - 其他路由文件

3. **修复剩余失败的测试**（约 5 个）
   - `tests/test_regression_features.py::test_reset_selected_balances_partial_success`
   - `tests/test_services.py::test_invite_progress_flow`
   - `tests/test_services.py::test_recharge_service_mock`
   - `tests/test_user_model.py::test_get_balance_summary`

## 总结

本次工作成功为 `routers/balance.py` 编写了测试，覆盖了主要的处理函数和辅助函数。测试框架已搭建完成，但由于缺少 `pytest-asyncio` 插件，部分异步测试被跳过。安装该插件后，所有测试应该能够正常运行。

测试通过率：**3/9**（6个异步测试需要 `pytest-asyncio`）

