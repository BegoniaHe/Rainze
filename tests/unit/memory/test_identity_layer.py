"""
身份层单元测试
Identity Layer Unit Tests

测试身份层的配置加载、热重载等功能。
Test identity layer configuration loading, hot reload, etc.

Author: Rainze Team
Created: 2026-01-01
"""

from __future__ import annotations

import json
from unittest.mock import Mock

import pytest

from rainze.memory.layers import IdentityLayer


@pytest.fixture
def mock_config_manager():
    """创建模拟的配置管理器 / Create mock config manager."""
    mock = Mock()
    return mock


@pytest.fixture
def temp_config_dir(tmp_path):
    """
    创建临时配置目录
    Create temporary config directory
    """
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    
    # 创建身份配置文件 / Create identity config file
    identity_config = {
        "user_profile": {
            "nickname": "测试用户",
            "birthday": "01-01",
            "relationship": "friend",
            "timezone": "Asia/Shanghai",
            "preferred_language": "zh-CN",
            "custom_facts": ["喜欢编程", "喜欢咖啡"]
        },
        "pet_identity": {
            "name": "Rainze",
            "name_cn": "忆雨",
            "name_nickname": "岚仔",
            "personality_archetype": "gentle_playful",
            "voice_style": "cute_casual"
        },
        "system_prompt_path": "./config/system_prompt.txt",
        "hot_reload": {
            "enabled": False,
            "watch_files": [],
            "reload_delay_seconds": 1
        }
    }
    
    identity_path = config_dir / "identity.json"
    with open(identity_path, "w", encoding="utf-8") as f:
        json.dump(identity_config, f, ensure_ascii=False, indent=2)
    
    # 创建系统提示词文件 / Create system prompt file
    prompt_path = config_dir / "system_prompt.txt"
    with open(prompt_path, "w", encoding="utf-8") as f:
        f.write("你是测试角色，性格开朗，喜欢帮助别人。")
    
    return config_dir


class TestIdentityLayer:
    """身份层测试类 / Identity layer test class."""
    
    @pytest.mark.asyncio
    async def test_initialization(self, mock_config_manager, temp_config_dir, monkeypatch):
        """
        测试身份层初始化
        Test identity layer initialization
        """
        # 切换工作目录 / Change working directory
        monkeypatch.chdir(temp_config_dir.parent)
        
        # 创建身份层 / Create identity layer
        identity = IdentityLayer(mock_config_manager)
        
        # 初始化 / Initialize
        await identity.initialize()
        
        # 验证用户资料加载 / Verify user profile loaded
        profile = identity.get_user_profile()
        assert profile is not None
        assert profile.nickname == "测试用户"
        assert profile.birthday == "01-01"
        assert profile.relationship == "friend"
        assert len(profile.custom_facts) == 2
        
        # 验证宠物身份加载 / Verify pet identity loaded
        pet = identity.get_pet_identity()
        assert pet is not None
        assert pet.name == "Rainze"
        assert pet.name_cn == "忆雨"
        
        # 验证系统提示词加载 / Verify system prompt loaded
        prompt = identity.get_system_prompt()
        assert "测试角色" in prompt
        
        # 关闭 / Shutdown
        await identity.shutdown()
    
    @pytest.mark.asyncio
    async def test_get_context(self, mock_config_manager, temp_config_dir, monkeypatch):
        """
        测试获取身份上下文
        Test getting identity context
        """
        monkeypatch.chdir(temp_config_dir.parent)
        
        identity = IdentityLayer(mock_config_manager)
        await identity.initialize()
        
        # 获取上下文 / Get context
        context = identity.get_context()
        
        # 验证格式 / Verify format
        assert "{Layer 1: Identity}" in context
        assert "测试用户" in context
        assert "01-01" in context
        assert "friend" in context
        assert "喜欢编程" in context or "喜欢咖啡" in context
        
        await identity.shutdown()
    
    @pytest.mark.asyncio
    async def test_missing_config_file(self, mock_config_manager, tmp_path, monkeypatch):
        """
        测试配置文件缺失时的异常处理
        Test exception handling when config file is missing
        """
        monkeypatch.chdir(tmp_path)
        
        identity = IdentityLayer(mock_config_manager)
        
        # 应该抛出 ConfigLoadError / Should raise ConfigLoadError
        with pytest.raises(Exception):
            await identity.initialize()
    
    @pytest.mark.asyncio
    async def test_context_before_initialization(self, mock_config_manager):
        """
        测试初始化前获取上下文
        Test getting context before initialization
        """
        identity = IdentityLayer(mock_config_manager)
        
        # 初始化前获取上下文应该返回未初始化提示
        # Getting context before init should return not initialized message
        context = identity.get_context()
        assert "未初始化" in context or "Not initialized" in context


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
