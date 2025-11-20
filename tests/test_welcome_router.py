"""
测试 routers/welcome.py
欢迎消息路由测试
"""
import pytest
pytestmark = pytest.mark.asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from aiogram.types import Message, User as TgUser, Chat
from aiogram.exceptions import TelegramBadRequest


@pytest.fixture
def mock_message():
    """创建模拟的 Message"""
    msg = Mock(spec=Message)
    msg.from_user = Mock(spec=TgUser)
    msg.from_user.id = 12345
    msg.from_user.username = "testuser"
    msg.from_user.language_code = "zh"
    msg.chat = Mock(spec=Chat)
    msg.chat.id = 12345
    msg.chat.type = "private"
    msg.text = "/start"
    msg.answer = AsyncMock()
    msg.answer_photo = AsyncMock()
    return msg


class TestFirstTimeWelcome:
    """测试 first_time_welcome 处理函数"""
    
    async def test_first_time_welcome_success(self, mock_message):
        """测试首次欢迎成功"""
        mock_message.text = "/start"
        mock_message.from_user.first_name = "Test"
        
        with patch("routers.welcome._canon_lang", return_value="zh"):
            with patch("routers.welcome._ensure_user_and_check_new", return_value=True):
                with patch("routers.welcome._build_welcome_text", return_value="欢迎"):
                    with patch("routers.welcome._find_cover_image", return_value=None):
                        with patch("routers.welcome.t", return_value="欢迎"):
                            with patch("routers.welcome.main_menu", return_value=Mock()):
                                with patch("routers.welcome._is_admin", return_value=False):
                                    from routers.welcome import first_time_welcome
                                    await first_time_welcome(mock_message)
                                    
                                    # 验证调用了 answer 或 answer_photo
                                    assert mock_message.answer.called or mock_message.answer_photo.called
    
    async def test_first_time_welcome_with_photo(self, mock_message):
        """测试带图片的欢迎消息"""
        mock_message.text = "/start"
        mock_message.from_user.first_name = "Test"
        
        with patch("routers.welcome._canon_lang", return_value="zh"):
            with patch("routers.welcome._ensure_user_and_check_new", return_value=True):
                with patch("routers.welcome._build_welcome_text", return_value="欢迎"):
                    with patch("routers.welcome._find_cover_image", return_value="/path/to/cover.jpg"):
                        with patch("routers.welcome._send_photo_safe", new_callable=AsyncMock) as mock_send_photo:
                            with patch("routers.welcome.t", return_value="欢迎"):
                                with patch("routers.welcome.main_menu", return_value=Mock()):
                                    with patch("routers.welcome._is_admin", return_value=False):
                                        from routers.welcome import first_time_welcome
                                        await first_time_welcome(mock_message)
                                        
                                        # 验证调用了 _send_photo_safe
                                        assert mock_send_photo.called


class TestWelcomeHelpers:
    """测试辅助函数"""
    
    def test_media_cache_load(self):
        """测试媒体缓存加载"""
        from routers.welcome import _media_cache_load, _media_cache
        
        # 函数应该能正常执行（即使文件不存在）
        _media_cache_load()
        assert isinstance(_media_cache, dict)
    
    def test_media_cache_save(self):
        """测试媒体缓存保存"""
        from routers.welcome import _media_cache_save
        
        # 函数应该能正常执行
        _media_cache_save()
        assert True  # 如果没有异常就通过
