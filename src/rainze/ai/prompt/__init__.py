"""
Prompt 模块 / Prompt Module

提供增量式 Prompt 构建功能，支持静态/半静态/动态上下文缓存。
Provides incremental prompt building with static/semi-static/dynamic context caching.

Reference:
    - PRD §0.5: AI提示词构建流程 (增量式 + 索引式)
    - PRD §0.5a: 统一上下文管理器

Author: Rainze Team
Created: 2026-01-01
"""

from rainze.ai.prompt.builder import PromptBuilder
from rainze.ai.prompt.cache import ContextCache
from rainze.ai.prompt.config import (
    DEFAULT_PROMPT_CONFIG,
    TOKEN_BUDGETS,
    PromptBuilderConfig,
    PromptMode,
    TokenBudget,
)

__all__ = [
    "PromptBuilder",
    "ContextCache",
    "PromptBuilderConfig",
    "PromptMode",
    "TokenBudget",
    "TOKEN_BUDGETS",
    "DEFAULT_PROMPT_CONFIG",
]
