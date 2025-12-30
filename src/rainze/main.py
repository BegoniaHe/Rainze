"""
Rainze 应用主入口
Rainze Application Main Entry

本模块提供应用的命令行入口点。
This module provides the CLI entry point for the application.

Usage / 使用方式:
    $ rainze              # 启动应用 / Start application
    $ python -m rainze    # 模块方式启动 / Start as module

Reference:
    - TECH: .github/techstacks/TECH-Rainze.md §7.2
    - MOD: .github/prds/modules/MOD-Core.md

Author: Rainze Team
Created: 2025-12-30
"""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    """
    应用主入口函数
    Application main entry function

    初始化并运行 Rainze 应用。
    Initializes and runs the Rainze application.

    Returns:
        退出码 / Exit code (0 = 成功 / success)
    """
    # 导入 PySide6（延迟导入以加速启动）
    # Import PySide6 (lazy import for faster startup)
    from PySide6.QtCore import QPoint
    from PySide6.QtWidgets import QApplication

    from rainze.core import EventBus
    from rainze.gui import ChatBubble, MainWindow, SystemTray

    # 1. 创建 Qt 应用 / Create Qt application
    qt_app = QApplication(sys.argv)
    qt_app.setApplicationName("Rainze")
    qt_app.setApplicationVersion("0.1.0")
    qt_app.setQuitOnLastWindowClosed(False)  # 托盘模式 / Tray mode

    # 2. 确定配置目录 / Determine config directory
    config_dir = Path("./config")
    if not config_dir.exists():
        config_dir.mkdir(parents=True, exist_ok=True)

    # 3. 创建事件总线（独立于 Application，用于 GUI）
    # Create event bus (independent from Application, for GUI)
    event_bus = EventBus()

    # 4. 创建 GUI 组件 / Create GUI components
    assets_dir = Path("./assets")

    # 主窗口 / Main window
    main_window = MainWindow(
        event_bus=event_bus,
        default_size=(200, 200),
        assets_dir=assets_dir,
    )

    # 聊天气泡 / Chat bubble
    chat_bubble = ChatBubble(
        show_feedback_buttons=False,
        auto_hide_ms=10000,
        typing_speed_ms=50,
    )

    # 系统托盘 / System tray
    system_tray = SystemTray(
        event_bus=event_bus,
        icon_path=assets_dir / "ui" / "icons" / "tray_icon.png",
        app_name="Rainze",
    )

    # 5. 连接信号 / Connect signals

    # 窗口显示/隐藏 / Window show/hide
    def on_show_requested() -> None:
        main_window.show()
        system_tray.update_toggle_text(True)

    def on_hide_requested() -> None:
        main_window.hide()
        system_tray.update_toggle_text(False)

    system_tray.show_requested.connect(on_show_requested)
    system_tray.hide_requested.connect(on_hide_requested)
    system_tray.quit_requested.connect(qt_app.quit)

    # 点击显示气泡 / Click shows bubble
    def on_pet_clicked() -> None:
        # 在桌宠头顶显示气泡 / Show bubble above pet
        anchor = QPoint(
            main_window.x() + main_window.width() // 2,
            main_window.y(),
        )
        chat_bubble.show_text(
            "你好呀~ 点击我可以和我聊天哦！喵~",
            use_typing_effect=True,
            anchor_point=anchor,
        )

    main_window.pet_clicked.connect(on_pet_clicked)

    # 双击切换模式 / Double click toggles mode
    main_window.pet_double_clicked.connect(main_window.toggle_display_mode)

    # 6. 显示窗口 / Show window
    main_window.move_to_corner("bottom_right")
    main_window.show()
    system_tray.show()

    # 7. 显示欢迎消息 / Show welcome message
    system_tray.show_notification(
        "Rainze",
        "桌宠已启动！点击我开始互动吧~ 喵~",
    )

    # 8. 运行事件循环 / Run event loop
    return qt_app.exec()


if __name__ == "__main__":
    sys.exit(main())
