"""
测试 services/safe_send.py
安全发送服务层测试
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from aiogram import Bot
from aiogram.types import Message, PhotoSize, Chat, User
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter, TelegramNetworkError


@pytest.fixture
def mock_bot():
    """创建模拟的 Bot 对象"""
    bot = MagicMock(spec=Bot)
    bot.send_photo = AsyncMock()
    bot.edit_message_text = AsyncMock()
    bot.edit_message_caption = AsyncMock()
    return bot


@pytest.fixture
def mock_message():
    """创建模拟的 Message 对象"""
    message = MagicMock(spec=Message)
    message.bot = MagicMock(spec=Bot)
    message.chat = MagicMock(spec=Chat)
    message.chat.id = 12345
    message.message_id = 67890
    return message


@pytest.mark.asyncio
async def test_send_photo_safe_with_file_id(mock_bot):
    """测试 send_photo_safe - 使用缓存的 file_id"""
    from services.safe_send import send_photo_safe, MediaCache
    
    # 设置缓存
    MediaCache.file_ids["test_key"] = "cached_file_id"
    
    # Mock 返回消息
    mock_msg = MagicMock()
    mock_bot.send_photo.return_value = mock_msg
    
    # 测试发送
    result = await send_photo_safe(
        mock_bot,
        chat_id=12345,
        path="/path/to/photo.jpg",
        cache_key="test_key",
    )
    
    assert result == mock_msg
    mock_bot.send_photo.assert_called_once()
    # 验证使用了 file_id
    call_args = mock_bot.send_photo.call_args
    assert call_args.kwargs["photo"] == "cached_file_id"


@pytest.mark.asyncio
async def test_send_photo_safe_first_upload(mock_bot):
    """测试 send_photo_safe - 首次上传"""
    from services.safe_send import send_photo_safe, MediaCache
    
    # 清空缓存
    MediaCache.file_ids.clear()
    
    # Mock 返回消息（带 photo 属性）
    mock_msg = MagicMock()
    mock_photo = MagicMock(spec=PhotoSize)
    mock_photo.file_id = "new_file_id"
    mock_msg.photo = [mock_photo]
    mock_bot.send_photo.return_value = mock_msg
    
    # 测试发送
    result = await send_photo_safe(
        mock_bot,
        chat_id=12345,
        path="/path/to/photo.jpg",
    )
    
    assert result == mock_msg
    mock_bot.send_photo.assert_called_once()
    # 验证缓存已更新
    assert "new_file_id" in MediaCache.file_ids.values()


@pytest.mark.asyncio
async def test_send_photo_safe_retry_after(mock_bot):
    """测试 send_photo_safe - 处理 RetryAfter 异常"""
    from services.safe_send import send_photo_safe, MediaCache
    
    # 清空缓存
    MediaCache.file_ids.clear()
    
    # Mock 第一次抛出 RetryAfter，第二次成功
    mock_msg = MagicMock()
    mock_photo = MagicMock(spec=PhotoSize)
    mock_photo.file_id = "file_id"
    mock_msg.photo = [mock_photo]
    
    retry_exception = TelegramRetryAfter(method="sendPhoto", message="Rate limit", retry_after=2)
    mock_bot.send_photo.side_effect = [retry_exception, mock_msg]
    
    # 测试发送（需要等待重试）
    result = await send_photo_safe(
        mock_bot,
        chat_id=12345,
        path="/path/to/photo.jpg",
        max_retries=3,
    )
    
    assert result == mock_msg
    assert mock_bot.send_photo.call_count == 2


@pytest.mark.asyncio
async def test_send_photo_safe_network_error(mock_bot):
    """测试 send_photo_safe - 处理网络错误"""
    from services.safe_send import send_photo_safe, MediaCache
    
    # 清空缓存
    MediaCache.file_ids.clear()
    
    # Mock 网络错误
    mock_bot.send_photo.side_effect = TelegramNetworkError(method="sendPhoto", message="Network error")
    
    # 测试发送（应该返回 None）
    result = await send_photo_safe(
        mock_bot,
        chat_id=12345,
        path="/path/to/photo.jpg",
        max_retries=2,
    )
    
    assert result is None
    assert mock_bot.send_photo.call_count == 2


@pytest.mark.asyncio
async def test_edit_text_or_caption_success(mock_bot):
    """测试 edit_text_or_caption - 成功编辑文本"""
    from services.safe_send import edit_text_or_caption
    
    # Mock 成功编辑
    mock_bot.edit_message_text.return_value = True
    
    # 测试编辑
    result = await edit_text_or_caption(
        mock_bot,
        chat_id=12345,
        message_id=67890,
        text="New text",
    )
    
    assert result is True
    mock_bot.edit_message_text.assert_called_once()


@pytest.mark.asyncio
async def test_edit_text_or_caption_not_modified(mock_bot):
    """测试 edit_text_or_caption - 消息未修改"""
    from services.safe_send import edit_text_or_caption
    
    # Mock 消息未修改异常
    mock_bot.edit_message_text.side_effect = TelegramBadRequest(
        method="editMessageText",
        message="message is not modified"
    )
    
    # 测试编辑（应该返回 True）
    result = await edit_text_or_caption(
        mock_bot,
        chat_id=12345,
        message_id=67890,
        text="Same text",
    )
    
    assert result is True


@pytest.mark.asyncio
async def test_edit_text_or_caption_fallback_to_caption(mock_bot):
    """测试 edit_text_or_caption - 回退到编辑 caption"""
    from services.safe_send import edit_text_or_caption
    
    # Mock 文本编辑失败，caption 编辑成功
    mock_bot.edit_message_text.side_effect = TelegramBadRequest(
        method="editMessageText",
        message="message can't be edited"
    )
    mock_bot.edit_message_caption.return_value = True
    
    # 测试编辑
    result = await edit_text_or_caption(
        mock_bot,
        chat_id=12345,
        message_id=67890,
        text="New caption",
    )
    
    assert result is True
    mock_bot.edit_message_text.assert_called_once()
    mock_bot.edit_message_caption.assert_called_once()


@pytest.mark.asyncio
async def test_edit_text_or_caption_by_message(mock_message):
    """测试 edit_text_or_caption_by_message"""
    from services.safe_send import edit_text_or_caption_by_message
    
    # Mock bot 方法
    mock_message.bot.edit_message_text = AsyncMock(return_value=True)
    
    # 测试编辑
    result = await edit_text_or_caption_by_message(
        mock_message,
        text="New text",
    )
    
    assert result is True
    mock_message.bot.edit_message_text.assert_called_once()


@pytest.mark.asyncio
async def test_edit_text_or_caption_retry_after(mock_bot):
    """测试 edit_text_or_caption - 处理 RetryAfter"""
    from services.safe_send import edit_text_or_caption
    
    # Mock 第一次 RetryAfter，第二次成功
    retry_exception = TelegramRetryAfter(method="editMessageText", message="Rate limit", retry_after=1)
    mock_bot.edit_message_text.side_effect = [retry_exception, True]
    
    # 测试编辑
    result = await edit_text_or_caption(
        mock_bot,
        chat_id=12345,
        message_id=67890,
        text="New text",
        max_retries=3,
    )
    
    assert result is True
    assert mock_bot.edit_message_text.call_count == 2

