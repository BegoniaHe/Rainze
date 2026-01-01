"""
身份层 (Identity Layer) - 记忆系统 Layer 1
Identity Layer - Memory System Layer 1

本模块实现身份层，加载角色设定和用户资料。
This module implements identity layer, loading character settings and user profile.

身份层包含：
- 系统提示词（角色性格、说话风格、行为准则）
- 用户资料（昵称、生日、关系）

Identity layer contains:
- System prompt (character personality, speaking style, behavior guidelines)
- User profile (nickname, birthday, relationship)

Reference:
    - PRD §0.2.1: Layer 1 - Identity Layer
    - MOD-Memory.md §3.2: IdentityLayer

Author: Rainze Team
Created: 2026-01-01
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from rainze.core.config import ConfigManager


@dataclass
class UserProfile:
    """
    用户资料数据类
    User profile dataclass
    
    Attributes:
        nickname: 用户昵称 / User nickname
        birthday: 生日（格式: MM-DD）/ Birthday (format: MM-DD)
        relationship: 关系类型 / Relationship type
        timezone: 时区 / Timezone
        preferred_language: 首选语言 / Preferred language
        custom_facts: 自定义事实列表 / Custom facts list
    """
    
    nickname: str
    birthday: Optional[str] = None
    relationship: str = "friend"
    timezone: str = "Asia/Shanghai"
    preferred_language: str = "zh-CN"
    custom_facts: list[str] = None
    
    def __post_init__(self) -> None:
        """初始化后处理 / Post-initialization processing."""
        if self.custom_facts is None:
            self.custom_facts = []


@dataclass
class PetIdentity:
    """
    宠物身份数据类
    Pet identity dataclass
    
    Attributes:
        name: 英文名 / English name
        name_cn: 中文名 / Chinese name
        name_nickname: 昵称 / Nickname
        personality_archetype: 性格原型 / Personality archetype
        voice_style: 说话风格 / Voice style
    """
    
    name: str
    name_cn: str
    name_nickname: str
    personality_archetype: str
    voice_style: str


class IdentityLayerError(Exception):
    """
    身份层异常基类
    Base exception for identity layer
    """
    pass


class ConfigLoadError(IdentityLayerError):
    """
    配置加载错误
    Configuration loading error
    """
    pass


class IdentityLayer:
    """
    身份层 (Layer 1) - 永久存储的身份信息
    Identity Layer (Layer 1) - Permanently stored identity information
    
    职责 / Responsibilities:
    - 加载并缓存系统提示词和用户资料
    - 支持热重载（文件变更时自动刷新）
    - 提供格式化的身份上下文
    
    Attributes:
        _config_manager: 配置管理器 / Configuration manager
        _system_prompt: 系统提示词内容 / System prompt content
        _user_profile: 用户资料 / User profile
        _pet_identity: 宠物身份 / Pet identity
        _hot_reload_enabled: 是否启用热重载 / Whether hot reload is enabled
        _watch_task: 文件监控任务 / File watch task
    
    Example:
        >>> identity = IdentityLayer(config_manager)
        >>> await identity.initialize()
        >>> context = identity.get_context()
        >>> print(context)
        
    Reference:
        PRD §0.2.1: Identity Layer 定义
    """
    
    def __init__(self, config_manager: ConfigManager) -> None:
        """
        初始化身份层
        Initialize identity layer
        
        Args:
            config_manager: 配置管理器实例 / Configuration manager instance
        """
        self._config_manager = config_manager
        self._system_prompt: str = ""
        self._user_profile: Optional[UserProfile] = None
        self._pet_identity: Optional[PetIdentity] = None
        
        # 热重载相关 / Hot reload related
        self._hot_reload_enabled: bool = False
        self._watch_task: Optional[asyncio.Task] = None
        self._last_modified: Dict[str, float] = {}
    
    async def initialize(self) -> None:
        """
        初始化身份层，加载所有配置
        Initialize identity layer, load all configurations
        
        Raises:
            ConfigLoadError: 配置文件加载失败时 / When config file loading fails
        """
        try:
            # 加载身份配置 / Load identity configuration
            await self._load_identity_config()
            
            # 加载系统提示词 / Load system prompt
            await self._load_system_prompt()
            
            # 启动热重载监控（如果启用）/ Start hot reload monitor (if enabled)
            if self._hot_reload_enabled:
                self._watch_task = asyncio.create_task(self._watch_files())
                
        except Exception as e:
            raise ConfigLoadError(f"Failed to initialize identity layer / 身份层初始化失败: {e}") from e
    
    async def _load_identity_config(self) -> None:
        """
        加载身份配置文件
        Load identity configuration file
        
        Raises:
            ConfigLoadError: 配置文件格式错误时 / When config file format is invalid
        """
        config_path = Path("./config/identity.json")
        
        if not config_path.exists():
            raise ConfigLoadError(
                f"Identity config not found / 身份配置文件不存在: {config_path}"
            )
        
        try:
            with open(config_path, encoding="utf-8") as f:
                data = json.load(f)
            
            # 解析用户资料 / Parse user profile
            user_data = data.get("user_profile", {})
            self._user_profile = UserProfile(
                nickname=user_data.get("nickname", "主人"),
                birthday=user_data.get("birthday"),
                relationship=user_data.get("relationship", "friend"),
                timezone=user_data.get("timezone", "Asia/Shanghai"),
                preferred_language=user_data.get("preferred_language", "zh-CN"),
                custom_facts=user_data.get("custom_facts", []),
            )
            
            # 解析宠物身份 / Parse pet identity
            pet_data = data.get("pet_identity", {})
            self._pet_identity = PetIdentity(
                name=pet_data.get("name", "Rainze"),
                name_cn=pet_data.get("name_cn", "忆雨"),
                name_nickname=pet_data.get("name_nickname", "岚仔"),
                personality_archetype=pet_data.get("personality_archetype", "gentle_playful"),
                voice_style=pet_data.get("voice_style", "cute_casual"),
            )
            
            # 热重载配置 / Hot reload config
            hot_reload = data.get("hot_reload", {})
            self._hot_reload_enabled = hot_reload.get("enabled", True)
            
            # 记录文件修改时间 / Record file modification time
            self._last_modified[str(config_path)] = config_path.stat().st_mtime
            
        except (json.JSONDecodeError, KeyError) as e:
            raise ConfigLoadError(
                f"Invalid identity config format / 身份配置格式错误: {e}"
            ) from e
    
    async def _load_system_prompt(self) -> None:
        """
        加载系统提示词
        Load system prompt
        
        Raises:
            ConfigLoadError: 提示词文件不存在或读取失败时 / When prompt file not found or read fails
        """
        prompt_path = Path("./config/system_prompt.txt")
        
        if not prompt_path.exists():
            raise ConfigLoadError(
                f"System prompt not found / 系统提示词文件不存在: {prompt_path}"
            )
        
        try:
            with open(prompt_path, encoding="utf-8") as f:
                self._system_prompt = f.read().strip()
            
            # 记录文件修改时间 / Record file modification time
            self._last_modified[str(prompt_path)] = prompt_path.stat().st_mtime
            
        except Exception as e:
            raise ConfigLoadError(
                f"Failed to load system prompt / 系统提示词加载失败: {e}"
            ) from e
    
    async def _watch_files(self) -> None:
        """
        监控配置文件变化，支持热重载
        Watch configuration files for changes, support hot reload
        """
        while True:
            try:
                await asyncio.sleep(1)  # 每秒检查一次 / Check every second
                
                # 检查所有监控的文件 / Check all watched files
                files_to_check = [
                    Path("./config/identity.json"),
                    Path("./config/system_prompt.txt"),
                ]
                
                reload_needed = False
                for file_path in files_to_check:
                    if not file_path.exists():
                        continue
                    
                    current_mtime = file_path.stat().st_mtime
                    last_mtime = self._last_modified.get(str(file_path), 0)
                    
                    if current_mtime > last_mtime:
                        reload_needed = True
                        break
                
                # 如果需要重载 / If reload needed
                if reload_needed:
                    await asyncio.sleep(1)  # 延迟1秒避免文件写入未完成
                    await self._reload_config()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                # 记录错误但继续运行 / Log error but continue running
                print(f"Hot reload error / 热重载错误: {e}")
    
    async def _reload_config(self) -> None:
        """
        重新加载配置
        Reload configuration
        """
        try:
            await self._load_identity_config()
            await self._load_system_prompt()
            print("Identity layer config reloaded / 身份层配置已重载")
        except Exception as e:
            print(f"Failed to reload config / 配置重载失败: {e}")
    
    def get_context(self) -> str:
        """
        获取格式化的身份上下文
        Get formatted identity context
        
        此方法返回用于注入 Prompt 的身份层信息。
        This method returns identity layer info for prompt injection.
        
        Returns:
            格式化的身份上下文字符串 / Formatted identity context string
        
        Example:
            返回格式 / Return format:
            
            {Layer 1: Identity}
            [角色] 你是 Rainze（忆雨），一个可爱聪明的 AI 桌面宠物伴侣...
            [用户] 昵称: 海棠, 关系: 主人, 生日: 10-05
        
        Reference:
            PRD §0.5: Prompt 构建流程
        """
        if not self._user_profile or not self._pet_identity:
            return "{Layer 1: Identity}\n[未初始化 / Not initialized]"
        
        # 构建身份上下文 / Build identity context
        context_parts = ["{Layer 1: Identity}"]
        
        # 添加系统提示词 / Add system prompt
        context_parts.append(f"[角色设定 / Character]\n{self._system_prompt}\n")
        
        # 添加用户资料 / Add user profile
        birthday_str = f", 生日: {self._user_profile.birthday}" if self._user_profile.birthday else ""
        context_parts.append(
            f"[用户 / User] "
            f"昵称: {self._user_profile.nickname}, "
            f"关系: {self._user_profile.relationship}"
            f"{birthday_str}"
        )
        
        # 添加自定义事实（如果有）/ Add custom facts (if any)
        if self._user_profile.custom_facts:
            facts_str = "; ".join(self._user_profile.custom_facts)
            context_parts.append(f"[重要事实 / Important Facts] {facts_str}")
        
        return "\n".join(context_parts)
    
    def get_user_profile(self) -> Optional[UserProfile]:
        """
        获取用户资料
        Get user profile
        
        Returns:
            用户资料对象 / User profile object
        """
        return self._user_profile
    
    def get_pet_identity(self) -> Optional[PetIdentity]:
        """
        获取宠物身份
        Get pet identity
        
        Returns:
            宠物身份对象 / Pet identity object
        """
        return self._pet_identity
    
    def get_system_prompt(self) -> str:
        """
        获取系统提示词
        Get system prompt
        
        Returns:
            系统提示词字符串 / System prompt string
        """
        return self._system_prompt
    
    async def shutdown(self) -> None:
        """
        关闭身份层，停止热重载监控
        Shutdown identity layer, stop hot reload monitoring
        """
        if self._watch_task:
            self._watch_task.cancel()
            try:
                await self._watch_task
            except asyncio.CancelledError:
                pass


# 导出列表 / Export list
__all__ = [
    "IdentityLayer",
    "UserProfile",
    "PetIdentity",
    "IdentityLayerError",
    "ConfigLoadError",
]
