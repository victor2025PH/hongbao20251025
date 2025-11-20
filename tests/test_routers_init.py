"""
测试 routers/__init__.py
路由初始化测试
"""
import pytest
from unittest.mock import Mock, patch, MagicMock

from aiogram import Dispatcher, Router


class TestFlagOn:
    """测试 _flag_on 函数"""
    
    def test_flag_on_default_true(self):
        """测试默认返回 True"""
        with patch("routers.__init__._ff", None):
            from routers.__init__ import _flag_on
            assert _flag_on("routers.menu", default=True) is True
            assert _flag_on("routers.menu", default=False) is False
    
    def test_flag_on_with_flags(self):
        """测试有 flags 配置时"""
        mock_flags = Mock()
        mock_flags.flags = Mock()
        mock_flags.flags.ENABLE_MENU = True
        
        with patch("routers.__init__._ff", mock_flags):
            from routers.__init__ import _flag_on
            assert _flag_on("routers.menu", default=False) is True
    
    def test_flag_on_exception(self):
        """测试异常情况"""
        with patch("routers.__init__._ff") as mock_ff:
            mock_ff.flags = Mock(side_effect=AttributeError("test"))
            from routers.__init__ import _flag_on
            # 异常时应该返回默认值
            assert _flag_on("routers.menu", default=True) is True


class TestTryGetRouter:
    """测试 _try_get_router 函数"""
    
    def test_try_get_router_success(self):
        """测试成功获取 router"""
        mock_router = Mock(spec=Router)
        mock_module = Mock()
        mock_module.router = mock_router
        
        with patch("routers.__init__.importlib.import_module", return_value=mock_module):
            from routers.__init__ import _try_get_router
            result = _try_get_router("routers.menu")
            assert result == mock_router
    
    def test_try_get_router_module_not_found(self):
        """测试模块不存在"""
        with patch("routers.__init__.importlib.import_module", side_effect=ModuleNotFoundError("test")):
            from routers.__init__ import _try_get_router
            result = _try_get_router("routers.nonexistent")
            assert result is None
    
    def test_try_get_router_no_router(self):
        """测试模块没有 router"""
        mock_module = Mock()
        mock_module.router = None
        
        with patch("routers.__init__.importlib.import_module", return_value=mock_module):
            from routers.__init__ import _try_get_router
            result = _try_get_router("routers.menu")
            assert result is None
    
    def test_try_get_router_exception(self):
        """测试导入异常"""
        with patch("routers.__init__.importlib.import_module", side_effect=Exception("test")):
            from routers.__init__ import _try_get_router
            result = _try_get_router("routers.menu")
            assert result is None


class TestSetupRouters:
    """测试 setup_routers 函数"""
    
    def test_setup_routers_success(self):
        """测试成功注册路由"""
        mock_dp = Mock(spec=Dispatcher)
        mock_router = Mock(spec=Router)
        
        with patch("routers.__init__._flag_on", return_value=True):
            with patch("routers.__init__._try_get_router", return_value=mock_router):
                from routers.__init__ import setup_routers
                result = setup_routers(mock_dp)
                
                # 验证调用了 include_router
                assert mock_dp.include_router.called
                # 验证返回了注册的路由列表
                assert isinstance(result, list)
    
    def test_setup_routers_flag_off(self):
        """测试功能开关关闭"""
        mock_dp = Mock(spec=Dispatcher)
        
        with patch("routers.__init__._flag_on", return_value=False):
            from routers.__init__ import setup_routers
            result = setup_routers(mock_dp)
            
            # 不应该调用 include_router
            assert not mock_dp.include_router.called
            # 返回空列表
            assert result == []
    
    def test_setup_routers_no_router(self):
        """测试无法获取 router"""
        mock_dp = Mock(spec=Dispatcher)
        
        with patch("routers.__init__._flag_on", return_value=True):
            with patch("routers.__init__._try_get_router", return_value=None):
                from routers.__init__ import setup_routers
                result = setup_routers(mock_dp)
                
                # 不应该调用 include_router
                assert not mock_dp.include_router.called
                # 返回空列表
                assert result == []

