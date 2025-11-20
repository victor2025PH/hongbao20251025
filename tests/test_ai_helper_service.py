"""
测试 services/ai_helper.py
AI 辅助服务层测试
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock


def test_mk_client_openai():
    """测试 _mk_client - OpenAI 提供商"""
    from services.ai_helper import _mk_client
    
    # Mock settings 和 AsyncOpenAI
    with patch("services.ai_helper.AsyncOpenAI") as mock_openai:
        with patch("services.ai_helper.settings") as mock_settings:
            mock_settings.AI_PROVIDER = "openai"
            mock_settings.OPENAI_API_KEY = "test_key"
            mock_client = MagicMock()
            mock_openai.return_value = mock_client
            
            result = _mk_client()
            
            assert result is not None
            mock_openai.assert_called_once_with(api_key="test_key")


def test_mk_client_openrouter():
    """测试 _mk_client - OpenRouter 提供商"""
    from services.ai_helper import _mk_client
    
    # Mock settings 和 AsyncOpenAI
    with patch("services.ai_helper.AsyncOpenAI") as mock_openai:
        with patch("services.ai_helper.settings") as mock_settings:
            mock_settings.AI_PROVIDER = "openrouter"
            mock_settings.OPENROUTER_API_KEY = "test_key"
            mock_client = MagicMock()
            mock_openai.return_value = mock_client
            
            result = _mk_client()
            
            assert result is not None
            mock_openai.assert_called_once_with(
                api_key="test_key",
                base_url="https://openrouter.ai/api/v1",
            )


def test_mk_client_no_key():
    """测试 _mk_client - 缺少 API Key"""
    from services.ai_helper import _mk_client
    
    with patch("services.ai_helper.AsyncOpenAI") as mock_openai:
        with patch("services.ai_helper.settings") as mock_settings:
            mock_settings.AI_PROVIDER = "openai"
            mock_settings.OPENAI_API_KEY = None
            
            result = _mk_client()
            
            assert result is None
            mock_openai.assert_not_called()


def test_mk_client_no_sdk():
    """测试 _mk_client - SDK 未安装"""
    from services.ai_helper import _mk_client
    
    with patch("services.ai_helper.AsyncOpenAI", None):
        result = _mk_client()
        assert result is None


def test_sys_prompt_zh():
    """测试 _sys_prompt - 中文"""
    from services.ai_helper import _sys_prompt
    
    result = _sys_prompt("zh")
    assert isinstance(result, str)
    assert len(result) > 0
    assert "红包" in result or "机器人" in result


def test_sys_prompt_en():
    """测试 _sys_prompt - 英文"""
    from services.ai_helper import _sys_prompt
    
    result = _sys_prompt("en")
    assert isinstance(result, str)
    assert len(result) > 0
    assert "Red Packet" in result or "bot" in result.lower()


def test_trim_context():
    """测试 _trim_context 函数"""
    from services.ai_helper import _trim_context
    
    # 测试空上下文
    assert _trim_context(None) == []
    assert _trim_context([]) == []
    
    # 测试正常上下文
    context = [
        ("user", "问题1"),
        ("assistant", "回答1"),
        ("user", "问题2"),
    ]
    result = _trim_context(context, max_items=5, max_chars=1000)
    assert len(result) == 3
    
    # 测试超过最大条数
    large_context = [("user", f"问题{i}") for i in range(10)]
    result = _trim_context(large_context, max_items=5)
    assert len(result) <= 5


def test_trim_context_max_chars():
    """测试 _trim_context - 字符数限制"""
    from services.ai_helper import _trim_context
    
    # 创建长文本上下文
    context = [
        ("user", "A" * 500),
        ("assistant", "B" * 500),
        ("user", "C" * 500),
    ]
    result = _trim_context(context, max_items=10, max_chars=800)
    # 应该被裁剪
    total_chars = sum(len(text) for _, text in result)
    assert total_chars <= 800 or len(result) < len(context)


@pytest.mark.asyncio
async def test_ai_answer_success():
    """测试 ai_answer - 成功调用"""
    from services.ai_helper import ai_answer
    
    # Mock client 和响应
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "这是 AI 的回答"
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
    
    with patch("services.ai_helper._mk_client", return_value=mock_client):
        with patch("services.ai_helper.settings") as mock_settings:
            mock_settings.AI_PROVIDER = "openai"
            mock_settings.OPENAI_MODEL = "gpt-4o-mini"
            mock_settings.AI_MAX_TOKENS = 1000
            mock_settings.AI_TIMEOUT = 30
            
            result = await ai_answer("测试问题", lang="zh")
            
            assert result == "这是 AI 的回答"
            mock_client.chat.completions.create.assert_called_once()


@pytest.mark.asyncio
async def test_ai_answer_no_client():
    """测试 ai_answer - 无客户端"""
    from services.ai_helper import ai_answer
    
    with patch("services.ai_helper._mk_client", return_value=None):
        result = await ai_answer("测试问题")
        assert result is None


@pytest.mark.asyncio
async def test_ai_answer_empty_response():
    """测试 ai_answer - 空响应"""
    from services.ai_helper import ai_answer
    
    # Mock client 返回空内容
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = ""
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
    
    with patch("services.ai_helper._mk_client", return_value=mock_client):
        with patch("services.ai_helper.settings") as mock_settings:
            mock_settings.AI_PROVIDER = "openai"
            mock_settings.OPENAI_MODEL = "gpt-4o-mini"
            mock_settings.AI_MAX_TOKENS = 1000
            mock_settings.AI_TIMEOUT = 30
            
            result = await ai_answer("测试问题")
            assert result is None


@pytest.mark.asyncio
async def test_ai_answer_exception():
    """测试 ai_answer - 异常处理"""
    from services.ai_helper import ai_answer
    
    # Mock client 抛出异常
    mock_client = AsyncMock()
    mock_client.chat.completions.create = AsyncMock(side_effect=Exception("API Error"))
    
    with patch("services.ai_helper._mk_client", return_value=mock_client):
        with patch("services.ai_helper.settings") as mock_settings:
            mock_settings.AI_PROVIDER = "openai"
            mock_settings.OPENAI_MODEL = "gpt-4o-mini"
            mock_settings.AI_MAX_TOKENS = 1000
            mock_settings.AI_TIMEOUT = 30
            
            result = await ai_answer("测试问题")
            assert result is None


@pytest.mark.asyncio
async def test_ai_answer_with_context():
    """测试 ai_answer - 带上下文"""
    from services.ai_helper import ai_answer
    
    # Mock client
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "回答"
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
    
    with patch("services.ai_helper._mk_client", return_value=mock_client):
        with patch("services.ai_helper.settings") as mock_settings:
            mock_settings.AI_PROVIDER = "openai"
            mock_settings.OPENAI_MODEL = "gpt-4o-mini"
            mock_settings.AI_MAX_TOKENS = 1000
            mock_settings.AI_TIMEOUT = 30
            
            context = [("user", "之前的问题"), ("assistant", "之前的回答")]
            result = await ai_answer("新问题", lang="zh", context=context)
            
            assert result is not None
            # 验证调用了 create，并且 messages 包含上下文
            call_args = mock_client.chat.completions.create.call_args
            assert call_args is not None
            messages = call_args.kwargs.get("messages", [])
            assert len(messages) > 2  # system + context + question

