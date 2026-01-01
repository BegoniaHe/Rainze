"""
用户偏好数据模型 / User preference data model

存储用户的偏好事实（Facts 子类型）。
Stores user preference facts (Facts subtype).

Reference:
    - PRD §0.2.3: Layer 3 - Long-term Memory (Facts)
    - config/database/schema.sql: user_preferences table

Author: Rainze Team
Created: 2026-01-01
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class UserPreference:
    """
    用户偏好记录 / User preference record
    
    Attributes:
        id: 唯一标识符 / Unique identifier
        category: 偏好类别 / Preference category (food, hobby, work等)
        key: 偏好键 / Preference key
        value: 偏好值 / Preference value
        confidence: 置信度 / Confidence (0.0-1.0)
        evidence_count: 证据计数 / Evidence count
        source: 来源 / Source (conversation, observation, explicit)
        notes: 备注 / Notes
        created_at: 创建时间 / Creation time
        updated_at: 更新时间 / Update time
    
    Example:
        >>> pref = UserPreference(
        ...     category="food",
        ...     key="favorite_fruit",
        ...     value="apple",
        ...     confidence=0.9,
        ...     source="conversation"
        ... )
    """
    
    category: str
    key: str
    value: str
    confidence: float = 1.0
    evidence_count: int = 1
    source: Optional[str] = None
    notes: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self) -> None:
        """验证字段 / Validate fields"""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0 and 1, got {self.confidence}")
        
        if self.evidence_count < 1:
            raise ValueError(f"Evidence count must be >= 1, got {self.evidence_count}")


@dataclass
class BehaviorPattern:
    """
    行为模式记录 / Behavior pattern record
    
    Attributes:
        id: 唯一标识符 / Unique identifier
        pattern_type: 模式类型 / Pattern type (sleep, work, active等)
        description: 描述 / Description
        frequency: 频率 / Frequency (daily, weekly, monthly)
        time_window: 时间窗口 (JSON) / Time window (JSON)
        weekday_pattern: 星期模式 (JSON) / Weekday pattern (JSON)
        confidence: 置信度 / Confidence (0.0-1.0)
        sample_count: 样本数量 / Sample count
        last_observed_at: 最后观察时间 / Last observed time
        created_at: 创建时间 / Creation time
        updated_at: 更新时间 / Update time
    
    Example:
        >>> pattern = BehaviorPattern(
        ...     pattern_type="sleep",
        ...     description="通常在晚上11点后睡觉",
        ...     frequency="daily",
        ...     time_window='{"start": "23:00", "end": "07:00"}',
        ...     confidence=0.8,
        ...     sample_count=15
        ... )
    """
    
    pattern_type: str
    description: str
    frequency: Optional[str] = None
    time_window: Optional[str] = None
    weekday_pattern: Optional[str] = None
    confidence: float = 0.5
    sample_count: int = 1
    last_observed_at: Optional[datetime] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self) -> None:
        """验证字段 / Validate fields"""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0 and 1, got {self.confidence}")
        
        if self.sample_count < 1:
            raise ValueError(f"Sample count must be >= 1, got {self.sample_count}")


@dataclass
class Relation:
    """
    实体关系记录 / Entity relation record
    
    存储三元组关系 (subject, predicate, object)。
    Stores triple relations (subject, predicate, object).
    
    Attributes:
        id: 唯一标识符 / Unique identifier
        subject: 主体 / Subject (主人, 用户)
        predicate: 关系 / Predicate (喜欢, 讨厌, 擅长)
        object: 客体 / Object (苹果, 加班, 编程)
        strength: 关系强度 / Relation strength (-1.0 to 1.0)
        evidence_count: 证据计数 / Evidence count
        evidence_episodes: 证据 episode IDs (JSON) / Evidence episode IDs (JSON)
        notes: 备注 / Notes
        created_at: 创建时间 / Creation time
        updated_at: 更新时间 / Update time
    
    Example:
        >>> relation = Relation(
        ...     subject="主人",
        ...     predicate="喜欢",
        ...     object="苹果",
        ...     strength=0.8,
        ...     evidence_count=3
        ... )
    """
    
    subject: str
    predicate: str
    object: str
    strength: float = 0.5
    evidence_count: int = 1
    evidence_episodes: Optional[str] = None
    notes: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self) -> None:
        """验证字段 / Validate fields"""
        if not -1.0 <= self.strength <= 1.0:
            raise ValueError(f"Strength must be between -1 and 1, got {self.strength}")
        
        if self.evidence_count < 1:
            raise ValueError(f"Evidence count must be >= 1, got {self.evidence_count}")


# 导出列表 / Export list
__all__ = [
    "UserPreference",
    "BehaviorPattern",
    "Relation",
]
