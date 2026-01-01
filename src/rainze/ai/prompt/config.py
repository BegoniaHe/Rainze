"""
Prompt 构建器配置 / Prompt Builder Configuration

定义 Prompt 构建的各种配置参数。
Defines various configuration parameters for prompt building.

Reference:
    - PRD §0.5: AI提示词构建流程 (增量式 + 索引式)
    - PRD §0.5: Token预算分配

Author: Rainze Team
Created: 2026-01-01
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict


class PromptMode(str, Enum):
    """
    Prompt 模式枚举 / Prompt mode enumeration
    
    定义三种不同的 Prompt 构建模式，每种模式有不同的 Token 预算分配。
    Defines three different prompt building modes with different token budget allocations.
    
    Reference:
        PRD §0.5: Token预算分配 - 用户可选模式
    """
    
    LITE = "lite"          # 轻量模式 (16k) / Lite mode (16k)
    STANDARD = "standard"  # 标准模式 (32k) / Standard mode (32k) - 默认
    DEEP = "deep"          # 深度模式 (64k) / Deep mode (64k)


@dataclass
class TokenBudget:
    """
    Token 预算配置 / Token budget configuration
    
    定义 Prompt 各部分的 Token 预算分配。
    Defines token budget allocation for each part of the prompt.
    
    Attributes:
        core_identity: 核心身份层预算 (Layer 1) / Core identity layer budget
        working_memory: 工作记忆预算 (Layer 2) / Working memory budget
        environment: 环境感知预算 / Environment context budget
        semantic_summary: 语义摘要预算 (Layer 3 Facts) / Semantic summary budget
        memory_index: 记忆索引预算 (Layer 3 索引) / Memory index budget
        memory_fulltext: 记忆全文预算 (Layer 3 全文) / Memory fulltext budget
        instructions: 系统指令预算 / System instructions budget
        reserved_output: 保留输出空间 / Reserved output space
        total: 总预算 / Total budget
    
    Reference:
        PRD §0.5: Token预算分配 (所有数值均可配置)
    """
    
    core_identity: int      # Layer 1: Identity Layer
    working_memory: int     # Layer 2: Working Memory
    environment: int        # Layer 2: Environment Context
    semantic_summary: int   # Layer 3: Facts Summary
    memory_index: int       # Layer 3: Memory Index (索引列表)
    memory_fulltext: int    # Layer 3: Memory Full-text (完整内容)
    instructions: int       # System Instructions
    reserved_output: int    # Reserved for model output
    total: int              # Total budget


# 预定义的三种模式预算 / Predefined mode budgets
# Reference: PRD §0.5 - Token预算分配
TOKEN_BUDGETS: Dict[PromptMode, TokenBudget] = {
    # 轻量模式 (16k) - 适用于新用户、低配设备、快速响应需求
    # Lite Mode (16k) - For new users, low-spec devices, fast response
    PromptMode.LITE: TokenBudget(
        core_identity=1500,      # 角色设定 + 用户资料
        working_memory=4000,     # 最近对话 + 实时状态
        environment=500,         # 时间/天气/系统状态
        semantic_summary=1500,   # 用户偏好摘要
        memory_index=1500,       # 记忆索引列表
        memory_fulltext=1500,    # 高优先级记忆全文
        instructions=500,        # 系统指令
        reserved_output=5000,    # 模型输出空间
        total=16000,
    ),
    
    # 标准模式 (32k) - 大多数用户、日常陪伴 (默认)
    # Standard Mode (32k) - For most users, daily companion (default)
    PromptMode.STANDARD: TokenBudget(
        core_identity=2500,      # 角色设定 + 用户资料
        working_memory=8000,     # 最近对话 + 实时状态
        environment=1000,        # 时间/天气/系统状态
        semantic_summary=2500,   # 用户偏好摘要
        memory_index=3000,       # 记忆索引列表
        memory_fulltext=5000,    # 高优先级记忆全文
        instructions=1000,       # 系统指令
        reserved_output=9000,    # 模型输出空间
        total=32000,
    ),
    
    # 深度模式 (64k) - 老用户、深度对话、复杂任务
    # Deep Mode (64k) - For experienced users, deep conversations, complex tasks
    PromptMode.DEEP: TokenBudget(
        core_identity=4000,      # 角色设定 + 用户资料
        working_memory=16000,    # 最近对话 + 实时状态
        environment=2000,        # 时间/天气/系统状态
        semantic_summary=4000,   # 用户偏好摘要
        memory_index=6000,       # 记忆索引列表
        memory_fulltext=10000,   # 高优先级记忆全文
        instructions=2000,       # 系统指令
        reserved_output=20000,   # 模型输出空间
        total=64000,
    ),
}


@dataclass
class PromptBuilderConfig:
    """
    Prompt 构建器配置 / Prompt builder configuration
    
    完整的 Prompt 构建器配置，包括模式选择、缓存策略、记忆索引等。
    Complete prompt builder configuration including mode selection, cache strategy, memory index, etc.
    
    Attributes:
        mode: Prompt 模式 / Prompt mode
        enable_memory_index: 是否启用记忆索引模式 / Enable memory index mode
        memory_index_count: 记忆索引数量 (默认30) / Memory index count (default 30)
        memory_fulltext_count: 记忆全文数量 (默认3) / Memory fulltext count (default 3)
        enable_cache: 是否启用缓存 / Enable cache
        static_cache_ttl: 静态上下文缓存TTL (秒，0表示永不过期) / Static cache TTL (seconds, 0 = never expire)
        semi_static_cache_ttl: 半静态上下文缓存TTL (秒) / Semi-static cache TTL (seconds)
        enable_compression: 是否启用内容压缩 (超出预算时) / Enable compression (when exceeding budget)
        compression_ratio: 压缩比例 (0.0-1.0) / Compression ratio (0.0-1.0)
        enable_token_counting: 是否启用精确 Token 计数 / Enable accurate token counting
    
    Reference:
        PRD §0.5: 增量式 Prompt Builder
    """
    
    # 模式选择 / Mode selection
    mode: PromptMode = PromptMode.STANDARD
    
    # 记忆索引策略 / Memory index strategy
    enable_memory_index: bool = True           # 启用索引模式
    memory_index_count: int = 30               # 索引列表数量 (PRD 默认30)
    memory_fulltext_count: int = 3             # 全文注入数量 (PRD 默认3)
    
    # 缓存策略 / Cache strategy
    enable_cache: bool = True                  # 启用缓存
    static_cache_ttl: int = 0                  # 静态上下文永不过期
    semi_static_cache_ttl: int = 600           # 半静态上下文 10分钟
    
    # 内容压缩 / Content compression
    enable_compression: bool = True            # 启用压缩
    compression_ratio: float = 0.8             # 压缩到80%
    
    # Token 计数 / Token counting
    enable_token_counting: bool = True         # 启用精确计数
    
    # 动态调整 / Dynamic adjustment
    auto_adjust_mode: bool = True              # 根据记忆总量自动调整模式
    memory_count_threshold_lite: int = 100     # <100条记忆 → 轻量模式
    memory_count_threshold_standard: int = 1000  # 100-1000条 → 标准模式
    # >1000条 → 深度模式
    
    @property
    def token_budget(self) -> TokenBudget:
        """
        获取当前模式的 Token 预算 / Get token budget for current mode
        
        Returns:
            当前模式对应的 TokenBudget / TokenBudget for current mode
        """
        return TOKEN_BUDGETS[self.mode]
    
    def adjust_mode_by_memory_count(self, memory_count: int) -> PromptMode:
        """
        根据记忆总量动态调整模式 / Dynamically adjust mode by memory count
        
        Args:
            memory_count: 当前记忆总数 / Current memory count
        
        Returns:
            推荐的 Prompt 模式 / Recommended prompt mode
        
        Reference:
            PRD §0.5: 动态预算调整
        """
        if not self.auto_adjust_mode:
            return self.mode
        
        if memory_count < self.memory_count_threshold_lite:
            # 新用户：减少索引预算，增加对话历史
            # New user: reduce index budget, increase conversation history
            return PromptMode.LITE
        elif memory_count < self.memory_count_threshold_standard:
            # 标准用户：平衡配置
            # Standard user: balanced configuration
            return PromptMode.STANDARD
        else:
            # 老用户：增加索引和全文预算
            # Experienced user: increase index and fulltext budget
            return PromptMode.DEEP


# 默认配置 / Default configuration
DEFAULT_PROMPT_CONFIG = PromptBuilderConfig()


# 导出列表 / Export list
__all__ = [
    "PromptMode",
    "TokenBudget",
    "TOKEN_BUDGETS",
    "PromptBuilderConfig",
    "DEFAULT_PROMPT_CONFIG",
]
