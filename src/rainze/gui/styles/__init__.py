"""
GUI 样式管理模块
GUI Style Management Module

本模块提供 QSS 样式加载和管理功能。
This module provides QSS style loading and management.

Reference:
    - MOD: .github/prds/modules/MOD-GUI.md §4: 样式系统

Author: Rainze Team
Created: 2025-12-31
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict

from PySide6.QtWidgets import QWidget

logger = logging.getLogger(__name__)

# 样式文件目录 / Style files directory
_STYLE_DIR = Path(__file__).parent

# 样式缓存 / Style cache
_style_cache: Dict[str, str] = {}


def get_style_path(name: str) -> Path:
    """
    获取样式文件路径
    Get style file path

    Args:
        name: 样式名称 (不含扩展名) / Style name (without extension)

    Returns:
        样式文件的完整路径 / Full path to style file
    """
    return _STYLE_DIR / f"{name}.qss"


def load_style(name: str, *, use_cache: bool = True) -> str:
    """
    加载 QSS 样式
    Load QSS style

    Args:
        name: 样式名称 / Style name
        use_cache: 是否使用缓存 / Whether to use cache

    Returns:
        QSS 样式字符串 / QSS style string

    Raises:
        FileNotFoundError: 样式文件不存在 / Style file not found
    """
    # 检查缓存 / Check cache
    if use_cache and name in _style_cache:
        return _style_cache[name]

    # 加载文件 / Load file
    path = get_style_path(name)
    if not path.exists():
        raise FileNotFoundError(f"Style file not found: {path}")

    content = path.read_text(encoding="utf-8")

    # 写入缓存 / Write to cache
    if use_cache:
        _style_cache[name] = content

    logger.debug(f"Loaded style: {name} ({len(content)} chars)")
    return content


def load_styles(*names: str) -> str:
    """
    加载并合并多个样式
    Load and merge multiple styles

    Args:
        *names: 样式名称列表 / Style names

    Returns:
        合并后的 QSS 字符串 / Merged QSS string
    """
    parts = []
    for name in names:
        try:
            parts.append(load_style(name))
        except FileNotFoundError:
            logger.warning(f"Style not found, skipping: {name}")
    return "\n".join(parts)


def apply_style(widget: QWidget, name: str) -> bool:
    """
    应用样式到组件
    Apply style to widget

    Args:
        widget: 目标组件 / Target widget
        name: 样式名称 / Style name

    Returns:
        是否成功应用 / Whether applied successfully
    """
    try:
        style = load_style(name)
        widget.setStyleSheet(style)
        return True
    except FileNotFoundError:
        logger.warning(f"Failed to apply style '{name}' to {widget.__class__.__name__}")
        return False


def apply_styles(widget: QWidget, *names: str) -> bool:
    """
    应用多个样式到组件
    Apply multiple styles to widget

    Args:
        widget: 目标组件 / Target widget
        *names: 样式名称列表 / Style names

    Returns:
        是否成功应用 / Whether applied successfully
    """
    style = load_styles(*names)
    if style:
        widget.setStyleSheet(style)
        return True
    return False


def clear_cache() -> None:
    """
    清空样式缓存
    Clear style cache
    """
    _style_cache.clear()
    logger.debug("Style cache cleared")


def reload_style(name: str) -> str:
    """
    重新加载样式（跳过缓存）
    Reload style (skip cache)

    Args:
        name: 样式名称 / Style name

    Returns:
        QSS 样式字符串 / QSS style string
    """
    # 清除该样式的缓存 / Clear cache for this style
    _style_cache.pop(name, None)
    return load_style(name, use_cache=True)


__all__ = [
    "get_style_path",
    "load_style",
    "load_styles",
    "apply_style",
    "apply_styles",
    "clear_cache",
    "reload_style",
]
