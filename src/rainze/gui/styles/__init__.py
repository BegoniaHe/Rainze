"""
GUI 样式模块 / GUI Styles Module

提供样式文件加载功能。
Provides style file loading functionality.

样式文件位置: assets/ui/styles/
Style files location: assets/ui/styles/

Author: Rainze Team
Updated: 2026-01-01
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from rainze.core.resources import get_style

__all__ = ["load_styles", "load_style"]


def load_style(style_name: str) -> str:
    """
    加载单个样式文件
    Load a single style file
    
    Args:
        style_name: 样式文件名 / Style file name (e.g., "base" or "base.qss")
    
    Returns:
        样式文件内容 / Style file content
    
    Raises:
        FileNotFoundError: 样式文件不存在 / Style file not found
    """
    style_path = get_style(style_name)
    
    if not style_path.exists():
        raise FileNotFoundError(f"Style file not found: {style_path}")
    
    with open(style_path, 'r', encoding='utf-8') as f:
        return f.read()


def load_styles(*style_names: str) -> str:
    """
    加载多个样式文件并合并
    Load multiple style files and merge them
    
    Args:
        *style_names: 样式文件名列表 / Style file names
                     例如: "base", "chat_bubble", "menu"
    
    Returns:
        合并后的样式内容 / Merged style content
    
    Examples:
        >>> # 加载单个样式
        >>> stylesheet = load_styles("base")
        
        >>> # 加载多个样式
        >>> stylesheet = load_styles("base", "chat_bubble", "menu")
    """
    styles = []
    
    for style_name in style_names:
        try:
            content = load_style(style_name)
            styles.append(content)
        except FileNotFoundError:
            # 如果样式文件不存在，跳过
            # Skip if style file not found
            continue
    
    return "\n\n".join(styles)
