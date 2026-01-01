"""
上下文缓存管理器 / Context Cache Manager

实现静态、半静态、动态三层缓存机制。
Implements three-tier caching mechanism: static, semi-static, and dynamic.

Reference:
    - PRD §0.5: 增量式 Prompt 构建流程
    - PRD §0.5: 静态/半静态/动态上下文

Author: Rainze Team
Created: 2026-01-01
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass
from typing import Dict, Optional, Tuple


@dataclass
class CacheEntry:
    """
    缓存条目 / Cache entry
    
    Attributes:
        content: 缓存内容 / Cached content
        timestamp: 创建时间戳 / Creation timestamp
        ttl: 生存时间 (秒，0表示永不过期) / Time-to-live (seconds, 0 = never expire)
        token_count: Token 数量估计 / Estimated token count
    """
    
    content: str
    timestamp: float
    ttl: int
    token_count: int
    
    def is_expired(self) -> bool:
        """
        检查是否过期 / Check if expired
        
        Returns:
            是否过期 / Whether expired
        """
        if self.ttl == 0:
            return False  # 永不过期 / Never expire
        
        return (time.time() - self.timestamp) > self.ttl


class ContextCache:
    """
    上下文缓存管理器 / Context cache manager
    
    实现三层缓存机制：
    Implements three-tier caching:
    
    1. 静态上下文 (Static Context): 启动时加载，文件变更时热重载
       - Layer 1: Identity Layer (system_prompt + user_profile)
       - TTL: 0 (永不过期，除非文件变更)
    
    2. 半静态上下文 (Semi-Static Context): 状态变化时刷新
       - Layer 3: Facts 摘要 (用户偏好、行为模式)
       - TTL: 10分钟 (可配置)
    
    3. 动态上下文 (Dynamic Context): 每次生成时刷新
       - Layer 2: Working Memory (对话历史、实时状态、环境感知)
       - 不缓存
    
    Attributes:
        static_cache: 静态上下文缓存 / Static context cache
        semi_static_cache: 半静态上下文缓存 / Semi-static context cache
        retrieval_cache: 检索结果缓存 / Retrieval result cache
    
    Example:
        >>> cache = ContextCache()
        >>> cache.set_static("identity", identity_content, ttl=0)
        >>> content = cache.get_static("identity")
        
    Reference:
        PRD §0.5: 增量式 Prompt 构建流程
    """
    
    def __init__(self) -> None:
        """初始化缓存管理器 / Initialize cache manager"""
        # 静态上下文缓存 (Layer 1) / Static context cache
        self.static_cache: Dict[str, CacheEntry] = {}
        
        # 半静态上下文缓存 (Layer 3 Facts) / Semi-static context cache
        self.semi_static_cache: Dict[str, CacheEntry] = {}
        
        # 检索结果缓存 (Layer 3 Episodes) / Retrieval result cache
        # Key: hash(event_type + context_keywords)
        self.retrieval_cache: Dict[str, CacheEntry] = {}
    
    def set_static(
        self,
        key: str,
        content: str,
        ttl: int = 0,
        token_count: Optional[int] = None,
    ) -> None:
        """
        设置静态上下文缓存 / Set static context cache
        
        Args:
            key: 缓存键 / Cache key
            content: 缓存内容 / Cache content
            ttl: 生存时间 (秒，0表示永不过期) / TTL (seconds, 0 = never expire)
            token_count: Token 数量 (可选) / Token count (optional)
        
        Example:
            >>> cache.set_static("identity", identity_layer_context, ttl=0)
        """
        if token_count is None:
            token_count = self._estimate_tokens(content)
        
        self.static_cache[key] = CacheEntry(
            content=content,
            timestamp=time.time(),
            ttl=ttl,
            token_count=token_count,
        )
    
    def get_static(self, key: str) -> Optional[str]:
        """
        获取静态上下文缓存 / Get static context cache
        
        Args:
            key: 缓存键 / Cache key
        
        Returns:
            缓存内容，如果不存在或已过期则返回 None / Cache content or None
        
        Example:
            >>> content = cache.get_static("identity")
        """
        entry = self.static_cache.get(key)
        if entry is None:
            return None
        
        if entry.is_expired():
            del self.static_cache[key]
            return None
        
        return entry.content
    
    def set_semi_static(
        self,
        key: str,
        content: str,
        ttl: int = 600,
        token_count: Optional[int] = None,
    ) -> None:
        """
        设置半静态上下文缓存 / Set semi-static context cache
        
        Args:
            key: 缓存键 / Cache key
            content: 缓存内容 / Cache content
            ttl: 生存时间 (秒，默认10分钟) / TTL (seconds, default 10 minutes)
            token_count: Token 数量 (可选) / Token count (optional)
        
        Example:
            >>> cache.set_semi_static("facts_summary", summary, ttl=600)
        """
        if token_count is None:
            token_count = self._estimate_tokens(content)
        
        self.semi_static_cache[key] = CacheEntry(
            content=content,
            timestamp=time.time(),
            ttl=ttl,
            token_count=token_count,
        )
    
    def get_semi_static(self, key: str) -> Optional[str]:
        """
        获取半静态上下文缓存 / Get semi-static context cache
        
        Args:
            key: 缓存键 / Cache key
        
        Returns:
            缓存内容，如果不存在或已过期则返回 None / Cache content or None
        """
        entry = self.semi_static_cache.get(key)
        if entry is None:
            return None
        
        if entry.is_expired():
            del self.semi_static_cache[key]
            return None
        
        return entry.content
    
    def set_retrieval(
        self,
        event_type: str,
        context_keywords: str,
        content: str,
        ttl: int = 300,
        token_count: Optional[int] = None,
    ) -> None:
        """
        设置检索结果缓存 / Set retrieval result cache
        
        Args:
            event_type: 事件类型 / Event type
            context_keywords: 上下文关键词 / Context keywords
            content: 缓存内容 / Cache content
            ttl: 生存时间 (秒，默认5分钟) / TTL (seconds, default 5 minutes)
            token_count: Token 数量 (可选) / Token count (optional)
        
        Example:
            >>> cache.set_retrieval("conversation", "工作 压力", retrieved_memories, ttl=300)
        """
        cache_key = self._generate_retrieval_key(event_type, context_keywords)
        
        if token_count is None:
            token_count = self._estimate_tokens(content)
        
        self.retrieval_cache[cache_key] = CacheEntry(
            content=content,
            timestamp=time.time(),
            ttl=ttl,
            token_count=token_count,
        )
    
    def get_retrieval(
        self,
        event_type: str,
        context_keywords: str,
    ) -> Optional[str]:
        """
        获取检索结果缓存 / Get retrieval result cache
        
        Args:
            event_type: 事件类型 / Event type
            context_keywords: 上下文关键词 / Context keywords
        
        Returns:
            缓存内容，如果不存在或已过期则返回 None / Cache content or None
        
        Example:
            >>> content = cache.get_retrieval("conversation", "工作 压力")
        """
        cache_key = self._generate_retrieval_key(event_type, context_keywords)
        entry = self.retrieval_cache.get(cache_key)
        
        if entry is None:
            return None
        
        if entry.is_expired():
            del self.retrieval_cache[cache_key]
            return None
        
        return entry.content
    
    def invalidate_static(self, key: str) -> None:
        """
        使静态缓存失效 / Invalidate static cache
        
        Args:
            key: 缓存键 / Cache key
        
        Example:
            >>> cache.invalidate_static("identity")  # 文件变更时调用
        """
        if key in self.static_cache:
            del self.static_cache[key]
    
    def invalidate_semi_static(self, key: str) -> None:
        """
        使半静态缓存失效 / Invalidate semi-static cache
        
        Args:
            key: 缓存键 / Cache key
        
        Example:
            >>> cache.invalidate_semi_static("facts_summary")  # 偏好变化时调用
        """
        if key in self.semi_static_cache:
            del self.semi_static_cache[key]
    
    def clear_retrieval_cache(self) -> None:
        """
        清空检索缓存 / Clear retrieval cache
        
        Example:
            >>> cache.clear_retrieval_cache()
        """
        self.retrieval_cache.clear()
    
    def clear_all(self) -> None:
        """
        清空所有缓存 / Clear all caches
        
        Example:
            >>> cache.clear_all()
        """
        self.static_cache.clear()
        self.semi_static_cache.clear()
        self.retrieval_cache.clear()
    
    def get_cache_stats(self) -> Dict[str, int]:
        """
        获取缓存统计信息 / Get cache statistics
        
        Returns:
            缓存统计字典 / Cache statistics dictionary
        
        Example:
            >>> stats = cache.get_cache_stats()
            >>> print(f"Static: {stats['static_count']}, Total tokens: {stats['total_tokens']}")
        """
        # 清理过期缓存 / Clean expired caches
        self._cleanup_expired()
        
        static_tokens = sum(entry.token_count for entry in self.static_cache.values())
        semi_static_tokens = sum(entry.token_count for entry in self.semi_static_cache.values())
        retrieval_tokens = sum(entry.token_count for entry in self.retrieval_cache.values())
        
        return {
            "static_count": len(self.static_cache),
            "semi_static_count": len(self.semi_static_cache),
            "retrieval_count": len(self.retrieval_cache),
            "static_tokens": static_tokens,
            "semi_static_tokens": semi_static_tokens,
            "retrieval_tokens": retrieval_tokens,
            "total_tokens": static_tokens + semi_static_tokens + retrieval_tokens,
        }
    
    def _generate_retrieval_key(self, event_type: str, context_keywords: str) -> str:
        """
        生成检索缓存键 / Generate retrieval cache key
        
        Args:
            event_type: 事件类型 / Event type
            context_keywords: 上下文关键词 / Context keywords
        
        Returns:
            缓存键 (hash) / Cache key (hash)
        """
        combined = f"{event_type}_{context_keywords}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _estimate_tokens(self, content: str) -> int:
        """
        估计 Token 数量 / Estimate token count
        
        使用简单的字符数估计：英文按空格分词，中文按字符计数。
        Uses simple character-based estimation: words for English, characters for Chinese.
        
        Args:
            content: 文本内容 / Text content
        
        Returns:
            估计的 Token 数量 / Estimated token count
        """
        # 简单估计：中文字符 * 1.5 + 英文单词
        # Simple estimation: Chinese chars * 1.5 + English words
        chinese_chars = sum(1 for c in content if '\u4e00' <= c <= '\u9fff')
        english_words = len([w for w in content.split() if w.isascii()])
        
        return int(chinese_chars * 1.5 + english_words)
    
    def _cleanup_expired(self) -> None:
        """
        清理过期缓存 / Cleanup expired caches
        """
        # 清理静态缓存 / Cleanup static cache
        expired_static = [k for k, v in self.static_cache.items() if v.is_expired()]
        for key in expired_static:
            del self.static_cache[key]
        
        # 清理半静态缓存 / Cleanup semi-static cache
        expired_semi_static = [k for k, v in self.semi_static_cache.items() if v.is_expired()]
        for key in expired_semi_static:
            del self.semi_static_cache[key]
        
        # 清理检索缓存 / Cleanup retrieval cache
        expired_retrieval = [k for k, v in self.retrieval_cache.items() if v.is_expired()]
        for key in expired_retrieval:
            del self.retrieval_cache[key]


# 导出列表 / Export list
__all__ = [
    "CacheEntry",
    "ContextCache",
]
