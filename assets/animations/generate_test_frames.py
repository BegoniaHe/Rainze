#!/usr/bin/env python
"""
测试帧生成脚本
Test Frame Generator Script

生成占位符动画帧用于测试和开发。
Generates placeholder animation frames for testing and development.

Usage / 使用方法:
    # 生成所有默认动画 / Generate all default animations
    python generate_test_frames.py

    # 生成指定动画 / Generate specific animation
    python generate_test_frames.py --name idle --frames 8 --color "100,150,200"

    # 自定义尺寸 / Custom size
    python generate_test_frames.py --name custom --frames 4 --size 128

Author: Rainze Team
Created: 2025-12-31
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Tuple

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QImage, QPainter, QPen
from PySide6.QtWidgets import QApplication


def create_placeholder_frame(
    path: Path,
    text: str,
    color: Tuple[int, int, int],
    size: int = 256,
) -> None:
    """
    创建占位符动画帧
    Create placeholder animation frame

    Args:
        path: 输出文件路径 / Output file path
        text: 帧文本标签 / Frame text label
        color: RGB 颜色元组 / RGB color tuple
        size: 图像尺寸（正方形）/ Image size (square)
    """
    img = QImage(size, size, QImage.Format.Format_ARGB32)
    img.fill(Qt.GlobalColor.transparent)

    painter = QPainter(img)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # 绘制圆形背景 / Draw circle background
    painter.setBrush(QColor(*color, 200))
    painter.setPen(QPen(QColor(*color), 3))
    margin = size // 12
    painter.drawEllipse(margin, margin, size - 2 * margin, size - 2 * margin)

    # 绘制文本 / Draw text
    painter.setPen(QColor(255, 255, 255))
    font_size = max(10, size // 18)
    font = QFont("Arial", font_size, QFont.Weight.Bold)
    painter.setFont(font)
    painter.drawText(img.rect(), Qt.AlignmentFlag.AlignCenter, text)

    painter.end()

    # 确保目录存在 / Ensure directory exists
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(path), "PNG")
    print(f"Created: {path}")


def generate_animation(
    base_dir: Path,
    name: str,
    frame_count: int,
    color: Tuple[int, int, int],
    size: int = 256,
    variant: str = "default",
) -> None:
    """
    生成动画帧序列
    Generate animation frame sequence

    Args:
        base_dir: 动画根目录 / Animation root directory
        name: 动画名称 / Animation name
        frame_count: 帧数 / Frame count
        color: RGB 颜色 / RGB color
        size: 帧尺寸 / Frame size
        variant: 变体名称 / Variant name
    """
    anim_dir = base_dir / name / variant

    for i in range(1, frame_count + 1):
        text = f"{name}\n{i}/{frame_count}"
        create_placeholder_frame(
            anim_dir / f"frame_{i:03d}.png",
            text,
            color,
            size,
        )

    print(f"Generated {frame_count} frames for '{name}/{variant}'")


def parse_color(color_str: str) -> Tuple[int, int, int]:
    """
    解析颜色字符串
    Parse color string

    Args:
        color_str: 逗号分隔的 RGB 值，如 "255,100,50"

    Returns:
        RGB 元组
    """
    parts = color_str.split(",")
    if len(parts) != 3:
        raise ValueError(f"Invalid color format: {color_str}")
    return (int(parts[0]), int(parts[1]), int(parts[2]))


# 默认动画配置 / Default animation configurations
DEFAULT_ANIMATIONS = {
    "idle": {"frames": 8, "color": (100, 150, 200)},
    "happy": {"frames": 6, "color": (255, 200, 100)},
    "thinking": {"frames": 4, "color": (150, 100, 200)},
    "ear_wiggle": {"frames": 3, "color": (200, 150, 150)},
    "head_pat": {"frames": 2, "color": (255, 180, 200)},
    "sad": {"frames": 4, "color": (100, 100, 180)},
    "angry": {"frames": 4, "color": (220, 80, 80)},
    "surprised": {"frames": 3, "color": (255, 220, 100)},
    "sleepy": {"frames": 6, "color": (150, 150, 180)},
    "wave": {"frames": 6, "color": (180, 200, 150)},
}


def main() -> int:
    """主函数 / Main function"""
    parser = argparse.ArgumentParser(
        description="Generate placeholder animation frames for testing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate all default animations
  python generate_test_frames.py

  # Generate specific animation
  python generate_test_frames.py --name idle --frames 8

  # Custom color and size
  python generate_test_frames.py --name custom --frames 4 --color "255,100,50" --size 128

  # List available presets
  python generate_test_frames.py --list
        """,
    )

    parser.add_argument(
        "--name",
        type=str,
        help="Animation name (generates single animation)",
    )
    parser.add_argument(
        "--frames",
        type=int,
        default=4,
        help="Number of frames (default: 4)",
    )
    parser.add_argument(
        "--color",
        type=str,
        default="100,150,200",
        help="RGB color as 'R,G,B' (default: 100,150,200)",
    )
    parser.add_argument(
        "--size",
        type=int,
        default=256,
        help="Frame size in pixels (default: 256)",
    )
    parser.add_argument(
        "--variant",
        type=str,
        default="default",
        help="Animation variant name (default: default)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=".",
        help="Output directory (default: current directory)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Generate all default animations",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available preset animations",
    )

    args = parser.parse_args()

    # 列出预设 / List presets
    if args.list:
        print("Available preset animations:")
        print("-" * 40)
        for name, config in DEFAULT_ANIMATIONS.items():
            color_str = ",".join(map(str, config["color"]))
            print(f"  {name:12} - {config['frames']} frames, color=({color_str})")
        return 0

    # 初始化 Qt / Initialize Qt
    app = QApplication.instance() or QApplication(sys.argv)

    base_dir = Path(args.output)

    # 生成所有默认动画 / Generate all defaults
    if args.all or (args.name is None):
        print(f"Generating all default animations in: {base_dir.absolute()}")
        print("=" * 50)

        for name, config in DEFAULT_ANIMATIONS.items():
            generate_animation(
                base_dir,
                name,
                config["frames"],
                config["color"],
                args.size,
            )

        print("=" * 50)
        print(f"All animations generated! Total: {len(DEFAULT_ANIMATIONS)}")
        return 0

    # 生成单个动画 / Generate single animation
    try:
        color = parse_color(args.color)
    except ValueError as e:
        print(f"Error: {e}")
        return 1

    # 检查是否是预设 / Check if it's a preset
    if args.name in DEFAULT_ANIMATIONS and args.frames == 4:
        preset = DEFAULT_ANIMATIONS[args.name]
        args.frames = preset["frames"]
        color = preset["color"]
        print(f"Using preset config for '{args.name}'")

    generate_animation(
        base_dir,
        args.name,
        args.frames,
        color,
        args.size,
        args.variant,
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
