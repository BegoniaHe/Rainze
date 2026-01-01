"""
叠加特效层
Overlay Effect Layer

本模块实现 Layer 2 特效层，负责粒子和特效动画。
This module implements Layer 2 overlay for particle and effect animations.

特效类型 / Effect types:
- sparkle: 星星闪烁
- heart: 爱心
- tear_drop: 泪滴
- anger_mark: 怒气符号
- question_mark: 问号
- sweat: 汗滴
- zzzzz: 睡眠Z字

Reference:
    - PRD §0.14: Layer 4 Effect层
    - MOD: .github/prds/modules/MOD-Animation.md §3.5

Author: Rainze Team
Created: 2025-12-31
"""

from __future__ import annotations

import logging
import random
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from PySide6.QtGui import QPainter, QPixmap

from rainze.animation.frames import FramePlayer, FrameSequence
from rainze.animation.layers.base_layer import AnimationLayer
from rainze.animation.models import BlendMode

# 日志 / Logger
logger = logging.getLogger(__name__)

# 导出列表 / Export list
__all__ = [
    "EffectType",
    "EffectConfig",
    "ActiveEffect",
    "OverlayLayer",
]


class EffectType(Enum):
    """
    特效类型枚举
    Effect type enumeration

    Attributes:
        SPARKLE: 星星闪烁 / Sparkle stars
        STARS: 星星环绕 / Orbiting stars
        HEART: 爱心 / Hearts
        TEAR_DROP: 泪滴 / Tear drops
        ANGER_MARK: 怒气符号 / Anger marks
        QUESTION_MARK: 问号 / Question mark
        SWEAT: 汗滴 / Sweat drops
        ZZZZZ: 睡眠Z字 / Sleep Z's
    """

    SPARKLE = "sparkle"
    STARS = "stars"
    HEART = "heart"
    TEAR_DROP = "tear_drop"
    ANGER_MARK = "anger_mark"
    QUESTION_MARK = "question_mark"
    SWEAT = "sweat"
    ZZZZZ = "zzzzz"


# 情感到特效的映射 / Emotion to effect mapping
EMOTION_EFFECT_MAPPING: Dict[str, EffectType] = {
    "happy": EffectType.SPARKLE,
    "excited": EffectType.STARS,
    "sad": EffectType.TEAR_DROP,
    "angry": EffectType.ANGER_MARK,
    "shy": EffectType.HEART,
    "surprised": EffectType.QUESTION_MARK,
    "confused": EffectType.QUESTION_MARK,
    "anxious": EffectType.SWEAT,
    "tired": EffectType.ZZZZZ,
}


@dataclass
class EffectConfig:
    """
    特效配置
    Effect configuration

    Attributes:
        effect_type: 特效类型 / Effect type
        resource_path: 资源路径（可选）/ Resource path (optional)
        frame_count: 帧数 / Frame count
        loop: 是否循环 / Whether to loop
        default_duration_ms: 默认持续时间 / Default duration in ms
        scale: 缩放比例 / Scale factor
        offset: 默认偏移位置 / Default offset position
        particle_count: 粒子数量（用于粒子类特效）/ Particle count
    """

    effect_type: EffectType
    resource_path: Optional[str] = None
    frame_count: int = 4
    loop: bool = False
    default_duration_ms: int = 2000
    scale: float = 1.0
    offset: Tuple[int, int] = (0, -50)  # 默认在角色头顶 / Default above character
    particle_count: int = 3


# 默认特效配置 / Default effect configurations
DEFAULT_EFFECT_CONFIGS: Dict[EffectType, EffectConfig] = {
    EffectType.SPARKLE: EffectConfig(
        effect_type=EffectType.SPARKLE,
        frame_count=4,
        loop=True,
        default_duration_ms=1500,
        offset=(0, -40),
        particle_count=5,
    ),
    EffectType.STARS: EffectConfig(
        effect_type=EffectType.STARS,
        frame_count=8,
        loop=True,
        default_duration_ms=3000,
        offset=(0, -30),
        particle_count=3,
    ),
    EffectType.HEART: EffectConfig(
        effect_type=EffectType.HEART,
        frame_count=4,
        loop=False,
        default_duration_ms=1000,
        offset=(20, -50),
        particle_count=2,
    ),
    EffectType.TEAR_DROP: EffectConfig(
        effect_type=EffectType.TEAR_DROP,
        frame_count=4,
        loop=True,
        default_duration_ms=2000,
        offset=(-20, 0),
        particle_count=1,
    ),
    EffectType.ANGER_MARK: EffectConfig(
        effect_type=EffectType.ANGER_MARK,
        frame_count=2,
        loop=True,
        default_duration_ms=1500,
        offset=(30, -60),
        particle_count=1,
    ),
    EffectType.QUESTION_MARK: EffectConfig(
        effect_type=EffectType.QUESTION_MARK,
        frame_count=2,
        loop=True,
        default_duration_ms=2000,
        offset=(0, -70),
        particle_count=1,
    ),
    EffectType.SWEAT: EffectConfig(
        effect_type=EffectType.SWEAT,
        frame_count=3,
        loop=True,
        default_duration_ms=1500,
        offset=(30, -30),
        particle_count=1,
    ),
    EffectType.ZZZZZ: EffectConfig(
        effect_type=EffectType.ZZZZZ,
        frame_count=3,
        loop=True,
        default_duration_ms=3000,
        offset=(40, -60),
        particle_count=3,
    ),
}


@dataclass
class ActiveEffect:
    """
    活动特效实例
    Active effect instance

    Attributes:
        effect_type: 特效类型 / Effect type
        config: 特效配置 / Effect configuration
        elapsed_ms: 已播放时间 / Elapsed time in ms
        duration_ms: 总持续时间 / Total duration in ms
        position: 位置偏移 / Position offset
        particles: 粒子位置和状态列表 / Particle positions and states
        frame_player: 帧播放器（如果使用精灵动画）/ Frame player
    """

    effect_type: EffectType
    config: EffectConfig
    elapsed_ms: int = 0
    duration_ms: int = 2000
    position: Tuple[int, int] = (0, 0)
    particles: List[Dict[str, float]] = field(default_factory=list)
    frame_player: Optional[FramePlayer] = None

    def __post_init__(self) -> None:
        """初始化粒子 / Initialize particles"""
        if not self.particles:
            self._init_particles()

    def _init_particles(self) -> None:
        """初始化粒子位置和状态 / Initialize particle positions and states"""
        base_x, base_y = self.config.offset

        for i in range(self.config.particle_count):
            # 随机偏移 / Random offset
            offset_x = random.randint(-30, 30)
            offset_y = random.randint(-20, 20)

            self.particles.append({
                "x": base_x + offset_x,
                "y": base_y + offset_y,
                "phase": random.uniform(0, 6.28),  # 随机相位
                "speed": random.uniform(0.8, 1.2),  # 速度变化
                "alpha": 1.0,
                "scale": random.uniform(0.8, 1.2),
            })


class OverlayLayer(AnimationLayer):
    """
    叠加特效层 (Layer 2)
    Overlay effect layer

    管理粒子特效动画，可与角色层叠加显示。
    Manages particle effect animations, overlaid on character layer.

    Attributes:
        _active_effects: 当前激活的特效列表 / Active effects list
        _effect_configs: 特效配置映射 / Effect configuration mapping
        _resource_path: 特效资源路径 / Effect resource path
        _canvas_size: 画布大小 / Canvas size

    Example:
        >>> overlay = OverlayLayer(resource_path="assets/effects")
        >>> overlay.play_effect(EffectType.SPARKLE, duration_ms=2000)
        >>> # In render loop:
        >>> overlay.update(delta_ms)
        >>> pixmap = overlay.get_current_frame()

    Reference:
        PRD §0.14: 特效层
    """

    def __init__(
        self,
        resource_path: Optional[str] = None,
        canvas_size: Tuple[int, int] = (256, 256),
    ) -> None:
        """
        初始化特效层
        Initialize effect layer

        Args:
            resource_path: 特效资源根目录 / Effect resource root path
            canvas_size: 画布大小 / Canvas size (width, height)
        """
        super().__init__(
            name="Overlay",
            index=2,
            blend_mode=BlendMode.NORMAL,
        )

        self._resource_path = Path(resource_path) if resource_path else None
        self._canvas_size = canvas_size

        # 激活的特效列表 / Active effects list
        self._active_effects: List[ActiveEffect] = []

        # 特效配置（可被资源覆盖）/ Effect configs (can be overridden by resources)
        self._effect_configs: Dict[EffectType, EffectConfig] = (
            DEFAULT_EFFECT_CONFIGS.copy()
        )

        # 缓存的特效帧序列 / Cached effect frame sequences
        self._cached_sequences: Dict[EffectType, FrameSequence] = {}

        # 渲染缓存 / Render cache
        self._cached_frame: Optional[QPixmap] = None
        self._cache_dirty: bool = True

    # ==================== 特效控制 / Effect Control ====================

    def play_effect(
        self,
        effect_type: EffectType,
        duration_ms: Optional[int] = None,
        position: Optional[Tuple[int, int]] = None,
    ) -> None:
        """
        播放特效
        Play effect

        Args:
            effect_type: 特效类型 / Effect type
            duration_ms: 持续时间，None 使用默认值 / Duration, None for default
            position: 相对位置，None 使用默认位置 / Position, None for default
        """
        config = self._effect_configs.get(effect_type)
        if not config:
            logger.warning(f"未知特效类型: {effect_type}")
            return

        # 确定持续时间 / Determine duration
        actual_duration = duration_ms or config.default_duration_ms

        # 确定位置 / Determine position
        actual_position = position or config.offset

        # 创建特效实例 / Create effect instance
        effect = ActiveEffect(
            effect_type=effect_type,
            config=config,
            duration_ms=actual_duration,
            position=actual_position,
        )

        # 尝试加载帧序列 / Try to load frame sequence
        sequence = self._load_effect_sequence(effect_type)
        if sequence:
            player = FramePlayer()
            player.set_sequence(sequence, auto_play=True)
            effect.frame_player = player

        self._active_effects.append(effect)
        self._cache_dirty = True

        logger.debug(f"播放特效: {effect_type.value}, 时长: {actual_duration}ms")

    def play_effect_for_emotion(
        self,
        emotion_tag: str,
        intensity: float = 0.5,
    ) -> None:
        """
        根据情感播放对应特效
        Play effect based on emotion

        Args:
            emotion_tag: 情感标签 / Emotion tag
            intensity: 强度 (0.0-1.0) / Intensity
        """
        effect_type = EMOTION_EFFECT_MAPPING.get(emotion_tag)
        if not effect_type:
            return

        # 强度影响持续时间 / Intensity affects duration
        config = self._effect_configs.get(effect_type)
        if config:
            duration = int(config.default_duration_ms * (0.5 + intensity * 0.5))
            self.play_effect(effect_type, duration_ms=duration)

    def stop_effect(self, effect_type: EffectType) -> None:
        """
        停止指定特效
        Stop specific effect

        Args:
            effect_type: 特效类型 / Effect type
        """
        self._active_effects = [
            e for e in self._active_effects if e.effect_type != effect_type
        ]
        self._cache_dirty = True

    def stop_all_effects(self) -> None:
        """
        停止所有特效
        Stop all effects
        """
        self._active_effects.clear()
        self._cache_dirty = True

    def get_active_effects(self) -> List[EffectType]:
        """
        获取当前激活的特效列表
        Get list of active effects

        Returns:
            激活的特效类型列表 / List of active effect types
        """
        return [e.effect_type for e in self._active_effects]

    # ==================== 资源加载 / Resource Loading ====================

    def _load_effect_sequence(self, effect_type: EffectType) -> Optional[FrameSequence]:
        """
        加载特效帧序列（内部方法）
        Load effect frame sequence (internal method)

        Args:
            effect_type: 特效类型

        Returns:
            帧序列或 None
        """
        # 检查缓存 / Check cache
        if effect_type in self._cached_sequences:
            return self._cached_sequences[effect_type]

        # 如果没有资源路径，返回 None（使用程序化渲染）
        # If no resource path, return None (use procedural rendering)
        if not self._resource_path:
            return None

        effect_path = self._resource_path / "effects" / effect_type.value
        if not effect_path.exists():
            return None

        # 尝试加载 / Try to load
        try:
            from rainze.animation.frames import AnimationLoader

            loader = AnimationLoader()
            config = self._effect_configs.get(effect_type)
            loop = config.loop if config else False

            sequence = loader.load(effect_path, name=effect_type.value, loop=loop)
            self._cached_sequences[effect_type] = sequence
            return sequence
        except Exception as e:
            logger.warning(f"加载特效资源失败: {effect_type.value}, {e}")
            return None

    # ==================== 抽象方法实现 / Abstract Method Implementation ====================

    def get_current_frame(self) -> Optional[QPixmap]:
        """
        获取当前帧图像
        Get current frame image

        合成所有激活特效到单张图像。
        Composites all active effects into single image.

        Returns:
            合成后的特效图像，无特效返回 None
        """
        if not self._active_effects:
            return None

        # 如果缓存有效，直接返回 / Return cache if valid
        if not self._cache_dirty and self._cached_frame:
            return self._cached_frame

        # 创建透明画布 / Create transparent canvas
        canvas = QPixmap(self._canvas_size[0], self._canvas_size[1])
        canvas.fill()  # 透明填充

        painter = QPainter(canvas)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 渲染每个特效 / Render each effect
        for effect in self._active_effects:
            self._render_effect(painter, effect)

        painter.end()

        self._cached_frame = canvas
        self._cache_dirty = False
        return canvas

    def _render_effect(self, painter: QPainter, effect: ActiveEffect) -> None:
        """
        渲染单个特效（内部方法）
        Render single effect (internal method)

        Args:
            painter: QPainter 实例
            effect: 特效实例
        """
        # 计算中心位置 / Calculate center position
        center_x = self._canvas_size[0] // 2
        center_y = self._canvas_size[1] // 2

        # 如果有帧播放器，使用帧动画 / Use frame animation if player exists
        if effect.frame_player:
            pixmap = effect.frame_player.get_current_pixmap()
            if pixmap and not pixmap.isNull():
                x = center_x + effect.position[0] - pixmap.width() // 2
                y = center_y + effect.position[1] - pixmap.height() // 2
                painter.drawPixmap(x, y, pixmap)
            return

        # 否则使用程序化渲染 / Otherwise use procedural rendering
        self._render_procedural_effect(painter, effect, center_x, center_y)

    def _render_procedural_effect(
        self,
        painter: QPainter,
        effect: ActiveEffect,
        center_x: int,
        center_y: int,
    ) -> None:
        """
        程序化渲染特效（内部方法）
        Procedurally render effect (internal method)

        为没有资源的特效提供简单的程序化渲染。
        Provides simple procedural rendering for effects without resources.
        """
        import math

        from PySide6.QtGui import QBrush, QColor, QFont, QPen

        # 计算动画进度 / Calculate animation progress
        progress = effect.elapsed_ms / effect.duration_ms if effect.duration_ms > 0 else 0
        time_factor = effect.elapsed_ms / 1000.0  # 秒

        effect_type = effect.effect_type

        for particle in effect.particles:
            px = int(center_x + particle["x"])
            py = int(center_y + particle["y"])
            phase = particle["phase"]
            speed = particle["speed"]
            scale = particle["scale"]

            # 根据特效类型渲染 / Render based on effect type
            if effect_type == EffectType.SPARKLE:
                # 闪烁星星 / Twinkling stars
                alpha = 0.5 + 0.5 * math.sin(time_factor * speed * 5 + phase)
                size = int(8 * scale * (0.8 + 0.2 * math.sin(time_factor * 3 + phase)))

                painter.setPen(QPen(QColor(255, 255, 100, int(255 * alpha)), 2))
                painter.setBrush(QBrush(QColor(255, 255, 200, int(200 * alpha))))

                # 画星星形状 / Draw star shape
                self._draw_star(painter, px, py, size, 4)

            elif effect_type == EffectType.HEART:
                # 上升的爱心 / Rising hearts
                float_y = py - int(progress * 30)
                alpha = 1.0 - progress * 0.5

                painter.setPen(QPen(QColor(255, 100, 150, int(255 * alpha)), 1))
                painter.setBrush(QBrush(QColor(255, 150, 180, int(200 * alpha))))

                size = int(12 * scale)
                self._draw_heart(painter, px, float_y, size)

            elif effect_type == EffectType.TEAR_DROP:
                # 下落的泪滴 / Falling tear drops
                float_y = py + int((time_factor * speed * 20) % 40)
                alpha = 0.7

                painter.setPen(QPen(QColor(100, 150, 255, int(255 * alpha)), 1))
                painter.setBrush(QBrush(QColor(150, 200, 255, int(180 * alpha))))

                self._draw_teardrop(painter, px, float_y, int(6 * scale))

            elif effect_type == EffectType.ANGER_MARK:
                # 怒气符号 / Anger mark
                alpha = 0.8 + 0.2 * math.sin(time_factor * 8)
                painter.setPen(QPen(QColor(255, 50, 50, int(255 * alpha)), 3))

                size = int(15 * scale)
                # 画十字形 / Draw cross shape
                painter.drawLine(px - size, py - size, px + size, py + size)
                painter.drawLine(px + size, py - size, px - size, py + size)

            elif effect_type == EffectType.QUESTION_MARK:
                # 问号 / Question mark
                alpha = 0.7 + 0.3 * math.sin(time_factor * 2)
                float_y = py + int(3 * math.sin(time_factor * 2))

                painter.setPen(QPen(QColor(100, 100, 100, int(255 * alpha)), 2))
                font = QFont("Arial", int(20 * scale), QFont.Weight.Bold)
                painter.setFont(font)
                painter.drawText(px - 6, float_y, "?")

            elif effect_type == EffectType.SWEAT:
                # 汗滴 / Sweat drop
                float_y = py + int((time_factor * speed * 15) % 25)
                alpha = 0.6

                painter.setPen(QPen(QColor(100, 180, 255, int(255 * alpha)), 1))
                painter.setBrush(QBrush(QColor(180, 220, 255, int(180 * alpha))))

                self._draw_teardrop(painter, px, float_y, int(5 * scale))

            elif effect_type == EffectType.ZZZZZ:
                # 睡眠Z字 / Sleep Z's
                float_y = py - int((time_factor * speed * 10) % 30)
                alpha = 1.0 - ((time_factor * speed * 10) % 30) / 30

                painter.setPen(QPen(QColor(150, 150, 200, int(255 * alpha)), 2))
                font = QFont("Arial", int(14 * scale * (1 + phase * 0.1)), QFont.Weight.Bold)
                painter.setFont(font)
                painter.drawText(px, int(float_y), "Z")

            elif effect_type == EffectType.STARS:
                # 环绕星星 / Orbiting stars
                angle = time_factor * speed * 2 + phase
                radius = 25 * scale
                orbit_x = px + int(radius * math.cos(angle))
                orbit_y = py + int(radius * math.sin(angle) * 0.5)  # 椭圆轨道
                alpha = 0.8

                painter.setPen(QPen(QColor(255, 255, 150, int(255 * alpha)), 1))
                painter.setBrush(QBrush(QColor(255, 255, 200, int(200 * alpha))))

                self._draw_star(painter, orbit_x, orbit_y, int(6 * scale), 5)

    def _draw_star(
        self,
        painter: QPainter,
        cx: int,
        cy: int,
        size: int,
        points: int,
    ) -> None:
        """绘制星星形状 / Draw star shape"""
        import math

        from PySide6.QtCore import QPointF
        from PySide6.QtGui import QPolygonF

        polygon = QPolygonF()
        for i in range(points * 2):
            angle = i * math.pi / points - math.pi / 2
            r = size if i % 2 == 0 else size // 2
            polygon.append(QPointF(cx + r * math.cos(angle), cy + r * math.sin(angle)))

        painter.drawPolygon(polygon)

    def _draw_heart(self, painter: QPainter, cx: int, cy: int, size: int) -> None:
        """绘制爱心形状 / Draw heart shape"""
        from PySide6.QtGui import QPainterPath

        path = QPainterPath()
        path.moveTo(cx, cy + size // 3)
        path.cubicTo(
            cx - size, cy - size // 2,
            cx - size // 2, cy - size,
            cx, cy - size // 2,
        )
        path.cubicTo(
            cx + size // 2, cy - size,
            cx + size, cy - size // 2,
            cx, cy + size // 3,
        )
        painter.drawPath(path)

    def _draw_teardrop(self, painter: QPainter, cx: int, cy: int, size: int) -> None:
        """绘制泪滴形状 / Draw teardrop shape"""
        from PySide6.QtGui import QPainterPath

        path = QPainterPath()
        path.moveTo(cx, cy - size)
        path.cubicTo(
            cx - size, cy,
            cx - size // 2, cy + size,
            cx, cy + size,
        )
        path.cubicTo(
            cx + size // 2, cy + size,
            cx + size, cy,
            cx, cy - size,
        )
        painter.drawPath(path)

    def update(self, delta_ms: int) -> None:
        """
        更新动画状态
        Update animation state

        Args:
            delta_ms: 距上次更新的毫秒数 / Milliseconds since last update
        """
        if not self._active_effects:
            return

        self._elapsed_ms += delta_ms
        self._cache_dirty = True

        # 更新每个特效 / Update each effect
        effects_to_remove: List[ActiveEffect] = []

        for effect in self._active_effects:
            effect.elapsed_ms += delta_ms

            # 更新帧播放器 / Update frame player
            if effect.frame_player:
                effect.frame_player.update(delta_ms)

            # 检查是否超时（非循环特效）/ Check if expired (non-looping)
            if not effect.config.loop and effect.elapsed_ms >= effect.duration_ms:
                effects_to_remove.append(effect)

        # 移除过期特效 / Remove expired effects
        for effect in effects_to_remove:
            self._active_effects.remove(effect)

    def reset(self) -> None:
        """
        重置到初始状态
        Reset to initial state
        """
        self.stop_all_effects()
        self._elapsed_ms = 0
        self._cache_dirty = True
