"""
动画层模块
Animation Layers Module

本模块提供动画层的基类和各层实现。
This module provides base class and implementations for animation layers.

3层动画架构 / 3-Layer Animation Architecture:
- Layer 0: Background (背景层) - 阴影、背景装饰
- Layer 1: Character (角色层) - 完整角色帧动画
- Layer 2: Overlay (叠加层) - 特效、粒子、指示符

Exports / 导出:
- AnimationLayer: 动画层抽象基类 / Animation layer abstract base class
- OverlayLayer: 叠加特效层 / Overlay effect layer
- EffectType: 特效类型枚举 / Effect type enumeration

Reference:
    - MOD: .github/prds/modules/MOD-Animation.md §1.2

Author: Rainze Team
Created: 2025-12-30
"""

from __future__ import annotations

from .base_layer import AnimationLayer
from .overlay import EffectType, OverlayLayer

__all__ = [
    "AnimationLayer",
    "EffectType",
    "OverlayLayer",
]
