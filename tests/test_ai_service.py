"""
测试 services/ai_service.py
AI 服务层测试
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock


def test_ensure_openai():
    """测试 _ensure_openai 函数"""
    from services import ai_service
    
    # 重置全局变量
    ai_service._openai_client = None
    
    # Mock OpenAI 和 settings（OpenAI 是在函数内部导入的，需要 patch openai.OpenAI）
    with patch("openai.OpenAI") as mock_openai:
        with patch("services.ai_service.settings") as mock_settings:
            mock_settings.OPENAI_API_KEY = "test_key"
            mock_client = MagicMock()
            mock_openai.return_value = mock_client
            
            result = ai_service._ensure_openai()
            
            assert result is not None
            mock_openai.assert_called_once_with(api_key="test_key")
            
            # 清理
            ai_service._openai_client = None


@pytest.mark.asyncio
async def test_ask_ai_openai():
    """测试 ask_ai - OpenAI 提供商"""
    from services.ai_service import ask_ai
    
    # Mock client 和响应
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "AI 回答"
    mock_client.chat.completions.create = MagicMock(return_value=mock_response)
    
    with patch("services.ai_service._ensure_openai", return_value=mock_client):
        with patch("services.ai_service.settings") as mock_settings:
            mock_settings.AI_PROVIDER = "openai"
            mock_settings.OPENAI_MODEL = "gpt-4o-mini"
            mock_settings.AI_MAX_TOKENS = 1000
            mock_settings.AI_TIMEOUT = 30
            
            with patch("asyncio.to_thread", new_callable=AsyncMock) as mock_to_thread:
                mock_to_thread.return_value = mock_response
                
                result = await ask_ai("测试问题", lang="zh")
                
                assert isinstance(result, str)
                assert "AI 回答" in result or len(result) > 0


@pytest.mark.asyncio
async def test_ask_ai_openrouter():
    """测试 ask_ai - OpenRouter 提供商"""
    from services.ai_service import ask_ai
    
    # Mock OpenAI 和响应（OpenAI 是在函数内部导入的，需要 patch openai.OpenAI）
    with patch("openai.OpenAI") as mock_openai:
        with patch("services.ai_service.settings") as mock_settings:
            mock_settings.AI_PROVIDER = "openrouter"
            mock_settings.OPENROUTER_API_KEY = "test_key"
            mock_settings.OPENROUTER_MODEL = "openai/gpt-4o-mini"
            mock_settings.AI_MAX_TOKENS = 1000
            mock_settings.AI_TIMEOUT = 30
            
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "AI 回答"
            mock_client.chat.completions.create = MagicMock(return_value=mock_response)
            mock_openai.return_value = mock_client
            
            with patch("asyncio.to_thread", new_callable=AsyncMock) as mock_to_thread:
                mock_to_thread.return_value = mock_response
                
                result = await ask_ai("测试问题", lang="zh")
                
                assert isinstance(result, str)
                mock_openai.assert_called_once_with(
                    api_key="test_key",
                    base_url="https://openrouter.ai/api/v1",
                )


@pytest.mark.asyncio
async def test_ask_ai_no_api_key():
    """测试 ask_ai - 缺少 API Key"""
    from services.ai_service import ask_ai
    
    with patch("services.ai_service.settings") as mock_settings:
        mock_settings.AI_PROVIDER = "openai"
        mock_settings.OPENAI_API_KEY = None
        
        result = await ask_ai("测试问题")
        
        assert isinstance(result, str)
        assert "OPENAI_API_KEY" in result or "配置" in result


@pytest.mark.asyncio
async def test_ask_ai_exception():
    """测试 ask_ai - 异常处理"""
    from services.ai_service import ask_ai
    
    # Mock client 抛出异常
    mock_client = MagicMock()
    mock_client.chat.completions.create = MagicMock(side_effect=Exception("API Error"))
    
    with patch("services.ai_service._ensure_openai", return_value=mock_client):
        with patch("services.ai_service.settings") as mock_settings:
            mock_settings.AI_PROVIDER = "openai"
            mock_settings.OPENAI_API_KEY = "test_key"
            mock_settings.OPENAI_MODEL = "gpt-4o-mini"
            mock_settings.AI_MAX_TOKENS = 1000
            mock_settings.AI_TIMEOUT = 30
            
            with patch("asyncio.to_thread", new_callable=AsyncMock) as mock_to_thread:
                mock_to_thread.side_effect = Exception("API Error")
                
                result = await ask_ai("测试问题")
                
                assert isinstance(result, str)
                assert "失败" in result or "Error" in result


@pytest.mark.asyncio
async def test_ask_ai_invalid_provider():
    """测试 ask_ai - 无效提供商"""
    from services.ai_service import ask_ai
    
    with patch("services.ai_service.settings") as mock_settings:
        mock_settings.AI_PROVIDER = "invalid"
        
        result = await ask_ai("测试问题")
        
        assert isinstance(result, str)
        assert "未知" in result or "unknown" in result.lower()


@pytest.mark.asyncio
async def test_ask_ai_with_user_ctx():
    """测试 ask_ai - 带用户上下文"""
    from services.ai_service import ask_ai
    
    # Mock client
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "回答"
    mock_client.chat.completions.create = MagicMock(return_value=mock_response)
    
    with patch("services.ai_service._ensure_openai", return_value=mock_client):
        with patch("services.ai_service.settings") as mock_settings:
            mock_settings.AI_PROVIDER = "openai"
            mock_settings.OPENAI_API_KEY = "test_key"
            mock_settings.OPENAI_MODEL = "gpt-4o-mini"
            mock_settings.AI_MAX_TOKENS = 1000
            mock_settings.AI_TIMEOUT = 30
            
            with patch("asyncio.to_thread", new_callable=AsyncMock) as mock_to_thread:
                mock_to_thread.return_value = mock_response
                
                user_ctx = {"user_id": 10001, "recent_actions": ["send", "grab"]}
                result = await ask_ai("测试问题", lang="zh", user_ctx=user_ctx)
                
                assert isinstance(result, str)

