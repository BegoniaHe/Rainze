"""
GUI 模块 - 图形用户界面
GUI Module - Graphical User Interface

本模块提供 Rainze 桌宠的图形界面组件。
This module provides GUI components for Rainze desktop pet.

Components / 组件:
- MainWindow: 桌宠主窗口 / Pet main window
- TransparentWidget: 透明窗口基类 / Transparent widget base
- ChatBubble: 聊天气泡 / Chat bubble
- SystemTray: 系统托盘 / System tray
- MenuSystem: 右键菜单系统 / Context menu system
- InputPanel: 输入面板 (Siri 风格) / Input panel (Siri-style)
- UICoordinator: UI 协调器 (弹性跟随) / UI coordinator (elastic following)

Reference:
    - MOD: .github/prds/modules/MOD-GUI.md

Author: Rainze Team
Created: 2025-12-30
Updated: 2026-01-01 - Added UICoordinator for elastic following
"""

from __future__ import annotations

from .chat_bubble import ChatBubble
from .input_panel import InputPanel
from .main_window import DisplayMode, MainWindow
from .menu_system import MenuItem, MenuSystem
from .system_tray import SystemTray
from .transparent_widget import TransparentWidget
from .ui_coordinator import AnchorConfig, SpringConfig, UICoordinator

__all__ = [
    "TransparentWidget",
    "MainWindow",
    "DisplayMode",
    "ChatBubble",
    "SystemTray",
    "MenuItem",
    "MenuSystem",
    "InputPanel",
    "UICoordinator",
    "SpringConfig",
    "AnchorConfig",
]
