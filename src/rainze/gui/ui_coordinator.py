"""
UI 协调器 - 弹性跟随系统
UI Coordinator - Elastic Following System

本模块管理桌宠主体、聊天气泡、输入面板三个组件的位置关系，
实现拖拽时的弹性跟随效果。

This module manages position relationships between pet, chat bubble,
and input panel, implementing elastic following on drag.

设计原理 / Design Principles:
- 弹簧物理模型: 使用弹簧阻尼系统实现自然的跟随效果
- 锚点系统: 每个组件相对于桌宠有固定的锚点偏移
- 解耦设计: 协调器不持有组件，通过信号槽通信

Reference:
    - MOD: .github/prds/modules/MOD-GUI.md §3
    - 弹簧物理: F = -k*x - c*v (胡克定律 + 阻尼)

Author: Rainze Team
Created: 2026-01-01
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

from PySide6.QtCore import QObject, QPoint, QPointF, QTimer, Signal

if TYPE_CHECKING:
    from PySide6.QtCore import QSize

    from .chat_bubble import ChatBubble
    from .input_panel import InputPanel
    from .main_window import MainWindow

logger = logging.getLogger(__name__)

__all__ = ["UICoordinator", "AnchorConfig", "SpringConfig"]


# ========================================
# 配置数据类 / Configuration Data Classes
# ========================================


@dataclass
class SpringConfig:
    """
    弹簧物理配置
    Spring Physics Configuration

    控制弹性跟随的物理参数。
    Controls physics parameters for elastic following.

    Attributes:
        stiffness: 弹簧刚度 (k)，越大跟随越紧 / Spring stiffness
        damping: 阻尼系数 (c)，越大减振越快 / Damping coefficient
        mass: 质量，影响惯性 / Mass, affects inertia
        threshold: 停止阈值，速度低于此值停止 / Stop threshold
    """

    stiffness: float = 180.0  # 弹簧刚度 / Stiffness (k)
    damping: float = 18.0  # 阻尼系数 / Damping (c)
    mass: float = 1.0  # 质量 / Mass
    threshold: float = 0.5  # 停止阈值 / Stop threshold (px/frame)


@dataclass
class AnchorConfig:
    """
    锚点配置
    Anchor Configuration

    定义组件相对于桌宠的锚点位置。
    Defines component anchor positions relative to pet.

    Attributes:
        bubble_offset: 气泡相对桌宠的偏移 (x, y) / Bubble offset from pet
        input_offset: 输入框相对桌宠的偏移 (x, y) / Input offset from pet
        bubble_anchor_point: 气泡锚点位置 / Bubble anchor point
            "top_center" - 桌宠头顶中心 / Top center of pet
            "top_left" - 桌宠头顶左侧 / Top left of pet
        input_anchor_point: 输入框锚点位置 / Input anchor point
            "bottom_center" - 桌宠底部中心 / Bottom center of pet
    """

    bubble_offset_y: int = -25  # 气泡在桌宠上方的距离 / Bubble above pet
    input_offset_y: int = 15  # 输入框在桌宠下方的距离 / Input below pet
    bubble_anchor_point: str = "top_center"
    input_anchor_point: str = "bottom_center"


# ========================================
# 弹簧状态 / Spring State
# ========================================


@dataclass
class SpringState:
    """
    单个弹簧的状态
    Single Spring State

    追踪位置和速度用于弹簧物理计算。
    Tracks position and velocity for spring physics.
    """

    position: QPointF = field(default_factory=lambda: QPointF(0, 0))
    velocity: QPointF = field(default_factory=lambda: QPointF(0, 0))
    target: QPointF = field(default_factory=lambda: QPointF(0, 0))
    is_active: bool = False


# ========================================
# UI 协调器 / UI Coordinator
# ========================================


class UICoordinator(QObject):
    """
    UI 协调器 - 管理组件位置和弹性跟随
    UI Coordinator - Manages component positions and elastic following

    职责 / Responsibilities:
    - 监听桌宠位置变化
    - 计算气泡和输入框的目标位置
    - 使用弹簧物理实现平滑跟随
    - 处理屏幕边界约束

    Signals:
        bubble_position_updated: 气泡位置更新 (QPoint)
        input_position_updated: 输入框位置更新 (QPoint)
        animation_started: 弹性动画开始
        animation_stopped: 弹性动画停止

    Attributes:
        _main_window: 桌宠主窗口引用 / Main window reference
        _chat_bubble: 聊天气泡引用 / Chat bubble reference
        _input_panel: 输入面板引用 / Input panel reference
        _spring_config: 弹簧配置 / Spring configuration
        _anchor_config: 锚点配置 / Anchor configuration
    """

    # 信号定义 / Signal definitions
    bubble_position_updated = Signal(QPoint)
    input_position_updated = Signal(QPoint)
    animation_started = Signal()
    animation_stopped = Signal()

    def __init__(
        self,
        parent: Optional[QObject] = None,
        *,
        spring_config: Optional[SpringConfig] = None,
        anchor_config: Optional[AnchorConfig] = None,
        update_interval_ms: int = 16,  # ~60 FPS
    ) -> None:
        """
        初始化 UI 协调器
        Initialize UI Coordinator

        Args:
            parent: 父对象 / Parent object
            spring_config: 弹簧配置 / Spring configuration
            anchor_config: 锚点配置 / Anchor configuration
            update_interval_ms: 动画更新间隔 / Animation update interval
        """
        super().__init__(parent)

        # 配置 / Configuration
        self._spring_config = spring_config or SpringConfig()
        self._anchor_config = anchor_config or AnchorConfig()
        self._update_interval_ms = update_interval_ms

        # 组件引用 / Component references
        self._main_window: Optional["MainWindow"] = None
        self._chat_bubble: Optional["ChatBubble"] = None
        self._input_panel: Optional["InputPanel"] = None

        # 弹簧状态 / Spring states
        self._bubble_spring = SpringState()
        self._input_spring = SpringState()

        # 动画定时器 / Animation timer
        self._animation_timer = QTimer(self)
        self._animation_timer.timeout.connect(self._on_animation_tick)

        # 是否正在拖拽 / Whether dragging
        self._is_dragging = False

        logger.debug("UICoordinator initialized")

    # ========================================
    # 组件注册 / Component Registration
    # ========================================

    def register_components(
        self,
        main_window: "MainWindow",
        chat_bubble: "ChatBubble",
        input_panel: "InputPanel",
    ) -> None:
        """
        注册 UI 组件
        Register UI Components

        连接信号并初始化位置。
        Connect signals and initialize positions.

        Args:
            main_window: 桌宠主窗口 / Main window
            chat_bubble: 聊天气泡 / Chat bubble
            input_panel: 输入面板 / Input panel
        """
        self._main_window = main_window
        self._chat_bubble = chat_bubble
        self._input_panel = input_panel

        # 连接信号 / Connect signals
        self._connect_signals()

        # 初始化位置 / Initialize positions
        self._initialize_positions()

        logger.info("UI components registered and connected")

    def _connect_signals(self) -> None:
        """
        连接组件信号
        Connect component signals
        """
        if not self._main_window:
            return

        # 桌宠位置变化 → 更新目标位置
        # Pet position change → update target positions
        self._main_window.position_changed.connect(self._on_pet_position_changed)

        # 拖拽开始/结束 → 控制动画
        # Drag start/end → control animation
        self._main_window.drag_started.connect(self._on_drag_started)
        self._main_window.drag_ended.connect(self._on_drag_ended)

        # 连接位置更新信号到组件
        # Connect position update signals to components
        if self._chat_bubble:
            self.bubble_position_updated.connect(self._move_bubble)
        if self._input_panel:
            self.input_position_updated.connect(self._move_input)

    def _initialize_positions(self) -> None:
        """
        初始化组件位置
        Initialize component positions

        将气泡和输入框立即定位到目标位置（无动画）。
        Immediately position bubble and input to targets (no animation).
        """
        if not self._main_window:
            return

        pet_pos = self._main_window.pos()
        pet_size = self._main_window.size()

        # 计算目标位置 / Calculate target positions
        bubble_target = self._calculate_bubble_target(pet_pos, pet_size)
        input_target = self._calculate_input_target(pet_pos, pet_size)

        # 直接设置位置（无弹簧效果）/ Set positions directly (no spring)
        self._bubble_spring.position = QPointF(bubble_target)
        self._bubble_spring.target = QPointF(bubble_target)
        self._input_spring.position = QPointF(input_target)
        self._input_spring.target = QPointF(input_target)

        # 应用位置 / Apply positions
        self.bubble_position_updated.emit(bubble_target)
        self.input_position_updated.emit(input_target)

    # ========================================
    # 位置计算 / Position Calculation
    # ========================================

    def _calculate_bubble_target(self, pet_pos: QPoint, pet_size: "QSize") -> QPoint:
        """
        计算气泡目标位置
        Calculate bubble target position

        Args:
            pet_pos: 桌宠位置 / Pet position
            pet_size: 桌宠尺寸 / Pet size

        Returns:
            气泡目标位置 / Bubble target position
        """
        if not self._chat_bubble:
            return QPoint(0, 0)

        bubble_width = self._chat_bubble.width()
        bubble_height = self._chat_bubble.height()

        # 计算锚点 (桌宠头顶中心) / Calculate anchor (pet top center)
        anchor_x = pet_pos.x() + pet_size.width() // 2
        anchor_y = pet_pos.y()

        # 气泡位置 (在锚点上方，横向居中) / Bubble position (above anchor, centered)
        x = anchor_x - bubble_width // 2
        y = anchor_y - bubble_height + self._anchor_config.bubble_offset_y

        # 屏幕边界约束 / Screen boundary constraints
        constrained = self._constrain_to_screen(x, y, bubble_width, bubble_height)

        return QPoint(int(constrained[0]), int(constrained[1]))

    def _calculate_input_target(self, pet_pos: QPoint, pet_size: "QSize") -> QPoint:
        """
        计算输入框目标位置
        Calculate input panel target position

        Args:
            pet_pos: 桌宠位置 / Pet position
            pet_size: 桌宠尺寸 / Pet size

        Returns:
            输入框目标位置 / Input target position
        """
        if not self._input_panel:
            return QPoint(0, 0)

        input_width = self._input_panel.width()
        input_height = self._input_panel.height()

        # 计算锚点 (桌宠底部中心) / Calculate anchor (pet bottom center)
        anchor_x = pet_pos.x() + pet_size.width() // 2
        anchor_y = pet_pos.y() + pet_size.height()

        # 输入框位置 (在锚点下方，横向居中) / Input position (below anchor, centered)
        x = anchor_x - input_width // 2
        y = anchor_y + self._anchor_config.input_offset_y

        # 屏幕边界约束 / Screen boundary constraints
        constrained = self._constrain_to_screen(x, y, input_width, input_height)

        return QPoint(int(constrained[0]), int(constrained[1]))

    def _constrain_to_screen(
        self,
        x: float,
        y: float,
        width: int,
        height: int,
        margin: int = 10,
    ) -> tuple[float, float]:
        """
        屏幕边界约束
        Constrain to screen boundaries

        Args:
            x: X 坐标 / X coordinate
            y: Y 坐标 / Y coordinate
            width: 组件宽度 / Component width
            height: 组件高度 / Component height
            margin: 边距 / Margin

        Returns:
            约束后的坐标 (x, y) / Constrained coordinates
        """
        if not self._main_window:
            return x, y

        screen = self._main_window.get_screen_geometry()

        # 左右边界 / Left-right bounds
        x = max(margin, min(x, screen.width() - width - margin))

        # 上下边界 / Top-bottom bounds
        y = max(margin, min(y, screen.height() - height - margin))

        return x, y

    # ========================================
    # 弹簧物理 / Spring Physics
    # ========================================

    def _on_animation_tick(self) -> None:
        """
        动画帧更新
        Animation frame update

        使用弹簧-阻尼系统计算新位置:
        F = -k * (x - target) - c * v
        a = F / m
        v' = v + a * dt
        x' = x + v' * dt
        """
        dt = self._update_interval_ms / 1000.0  # 转换为秒 / Convert to seconds
        config = self._spring_config

        bubble_settled = self._update_spring(self._bubble_spring, dt, config)
        input_settled = self._update_spring(self._input_spring, dt, config)

        # 发出位置更新信号 / Emit position update signals
        if self._bubble_spring.is_active:
            self.bubble_position_updated.emit(
                QPoint(
                    int(self._bubble_spring.position.x()),
                    int(self._bubble_spring.position.y()),
                )
            )

        if self._input_spring.is_active:
            self.input_position_updated.emit(
                QPoint(
                    int(self._input_spring.position.x()),
                    int(self._input_spring.position.y()),
                )
            )

        # 检查是否应该停止动画 / Check if animation should stop
        if bubble_settled and input_settled and not self._is_dragging:
            self._stop_animation()

    def _update_spring(
        self,
        spring: SpringState,
        dt: float,
        config: SpringConfig,
    ) -> bool:
        """
        更新单个弹簧状态
        Update single spring state

        Args:
            spring: 弹簧状态 / Spring state
            dt: 时间步长 (秒) / Time step (seconds)
            config: 弹簧配置 / Spring config

        Returns:
            是否已稳定 / Whether settled
        """
        if not spring.is_active:
            return True

        # 计算位移 / Calculate displacement
        dx = spring.position.x() - spring.target.x()
        dy = spring.position.y() - spring.target.y()

        # 计算弹簧力: F = -k * x - c * v
        # Spring force: F = -k * x - c * v
        fx = -config.stiffness * dx - config.damping * spring.velocity.x()
        fy = -config.stiffness * dy - config.damping * spring.velocity.y()

        # 计算加速度: a = F / m
        ax = fx / config.mass
        ay = fy / config.mass

        # 更新速度: v' = v + a * dt
        new_vx = spring.velocity.x() + ax * dt
        new_vy = spring.velocity.y() + ay * dt
        spring.velocity = QPointF(new_vx, new_vy)

        # 更新位置: x' = x + v * dt
        new_x = spring.position.x() + new_vx * dt
        new_y = spring.position.y() + new_vy * dt
        spring.position = QPointF(new_x, new_y)

        # 检查是否稳定 / Check if settled
        speed = (new_vx**2 + new_vy**2) ** 0.5
        distance = (dx**2 + dy**2) ** 0.5

        if speed < config.threshold and distance < 1.0:
            # 直接移动到目标位置 / Snap to target
            spring.position = QPointF(spring.target)
            spring.velocity = QPointF(0, 0)
            return True

        return False

    # ========================================
    # 事件处理 / Event Handlers
    # ========================================

    def _on_pet_position_changed(self, new_pos: QPoint) -> None:
        """
        桌宠位置变化处理
        Pet position change handler

        Args:
            new_pos: 新位置 / New position
        """
        if not self._main_window:
            return

        pet_size = self._main_window.size()

        # 更新目标位置 / Update target positions
        bubble_target = self._calculate_bubble_target(new_pos, pet_size)
        input_target = self._calculate_input_target(new_pos, pet_size)

        self._bubble_spring.target = QPointF(bubble_target)
        self._input_spring.target = QPointF(input_target)

        # 激活弹簧 / Activate springs
        if self._chat_bubble and self._chat_bubble.isVisible():
            self._bubble_spring.is_active = True

        if self._input_panel and self._input_panel.isVisible():
            self._input_spring.is_active = True

        # 确保动画运行 / Ensure animation is running
        self._start_animation()

    def _on_drag_started(self) -> None:
        """
        拖拽开始处理
        Drag started handler
        """
        self._is_dragging = True
        logger.debug("Drag started, elastic following activated")

    def _on_drag_ended(self, final_pos: QPoint) -> None:
        """
        拖拽结束处理
        Drag ended handler

        Args:
            final_pos: 最终位置 / Final position
        """
        self._is_dragging = False
        logger.debug(f"Drag ended at {final_pos}")

    # ========================================
    # 动画控制 / Animation Control
    # ========================================

    def _start_animation(self) -> None:
        """
        启动动画
        Start animation
        """
        if not self._animation_timer.isActive():
            self._animation_timer.start(self._update_interval_ms)
            self.animation_started.emit()
            logger.debug("Animation started")

    def _stop_animation(self) -> None:
        """
        停止动画
        Stop animation
        """
        if self._animation_timer.isActive():
            self._animation_timer.stop()
            self.animation_stopped.emit()
            logger.debug("Animation stopped")

    # ========================================
    # 组件移动 / Component Movement
    # ========================================

    def _move_bubble(self, pos: QPoint) -> None:
        """
        移动气泡
        Move bubble

        Args:
            pos: 目标位置 / Target position
        """
        if self._chat_bubble and self._chat_bubble.isVisible():
            self._chat_bubble.move(pos)

    def _move_input(self, pos: QPoint) -> None:
        """
        移动输入框
        Move input panel

        Args:
            pos: 目标位置 / Target position
        """
        if self._input_panel and self._input_panel.isVisible():
            self._input_panel.move(pos)

    # ========================================
    # 公共方法 / Public Methods
    # ========================================

    def update_positions_immediately(self) -> None:
        """
        立即更新位置（无弹性效果）
        Update positions immediately (no elastic effect)

        用于初始显示或需要立即定位的场景。
        Used for initial display or when immediate positioning is needed.
        """
        self._initialize_positions()

    def show_bubble_with_position(self) -> None:
        """
        显示气泡并更新位置
        Show bubble and update position
        """
        if not self._main_window or not self._chat_bubble:
            return

        pet_pos = self._main_window.pos()
        pet_size = self._main_window.size()
        target = self._calculate_bubble_target(pet_pos, pet_size)

        # 设置初始位置 / Set initial position
        self._bubble_spring.position = QPointF(target)
        self._bubble_spring.target = QPointF(target)
        self._bubble_spring.velocity = QPointF(0, 0)
        self._bubble_spring.is_active = True

        self._chat_bubble.move(target)

    def show_input_with_position(self) -> None:
        """
        显示输入框并更新位置
        Show input panel and update position
        """
        if not self._main_window or not self._input_panel:
            return

        pet_pos = self._main_window.pos()
        pet_size = self._main_window.size()
        target = self._calculate_input_target(pet_pos, pet_size)

        # 设置初始位置 / Set initial position
        self._input_spring.position = QPointF(target)
        self._input_spring.target = QPointF(target)
        self._input_spring.velocity = QPointF(0, 0)
        self._input_spring.is_active = True

        self._input_panel.move(target)

    def set_spring_config(self, config: SpringConfig) -> None:
        """
        设置弹簧配置
        Set spring configuration

        Args:
            config: 新的弹簧配置 / New spring config
        """
        self._spring_config = config

    def set_anchor_config(self, config: AnchorConfig) -> None:
        """
        设置锚点配置
        Set anchor configuration

        Args:
            config: 新的锚点配置 / New anchor config
        """
        self._anchor_config = config

    def cleanup(self) -> None:
        """
        清理资源
        Cleanup resources
        """
        self._stop_animation()
        self._main_window = None
        self._chat_bubble = None
        self._input_panel = None
        logger.debug("UICoordinator cleaned up")
