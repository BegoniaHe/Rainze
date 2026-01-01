"""
资源路径管理模块
Resource Path Management Module

提供统一的资源路径获取方式，兼容开发环境和打包环境。
Provides unified resource path access, compatible with dev and packaged environments.

Author: Rainze Team
Created: 2026-01-01
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

__all__ = ["ResourceManager", "get_assets_dir", "get_config_dir"]


class ResourceManager:
    """
    资源管理器
    Resource Manager
    
    自动检测运行环境，提供正确的资源路径。
    Automatically detects runtime environment and provides correct resource paths.
    """
    
    _instance: Optional[ResourceManager] = None
    _assets_dir: Optional[Path] = None
    _config_dir: Optional[Path] = None
    
    def __new__(cls) -> ResourceManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        if self._assets_dir is None:
            self._initialize_paths()
    
    def _initialize_paths(self) -> None:
        """初始化资源路径 / Initialize resource paths"""
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller 打包后 / After PyInstaller packaging
            base_path = Path(sys._MEIPASS)
            
            # macOS .app bundle: _MEIPASS 在 Contents/MacOS，资源在 Contents/Resources
            # macOS .app bundle: _MEIPASS is Contents/MacOS, assets in Contents/Resources
            if sys.platform == 'darwin' and base_path.name == 'MacOS':
                resources_path = base_path.parent / 'Resources'
                self._assets_dir = resources_path / 'assets'
                self._config_dir = resources_path / 'config'
            else:
                # Windows/Linux: 资源直接在 _MEIPASS 下
                # Windows/Linux: assets directly under _MEIPASS
                self._assets_dir = base_path / 'assets'
                self._config_dir = base_path / 'config'
        else:
            # 开发环境 / Development environment
            # 假设此文件在 src/rainze/core/resources.py
            # Assuming this file is at src/rainze/core/resources.py
            project_root = Path(__file__).parent.parent.parent.parent
            self._assets_dir = project_root / 'assets'
            self._config_dir = project_root / 'config'
    
    @property
    def assets_dir(self) -> Path:
        """获取 assets 目录 / Get assets directory"""
        if self._assets_dir is None:
            self._initialize_paths()
        return self._assets_dir  # type: ignore
    
    @property
    def config_dir(self) -> Path:
        """获取 config 目录 / Get config directory"""
        if self._config_dir is None:
            self._initialize_paths()
        return self._config_dir  # type: ignore
    
    def get_asset(self, relative_path: str) -> Path:
        """
        获取资源文件路径
        Get asset file path
        
        Args:
            relative_path: 相对于 assets 目录的路径 / Path relative to assets dir
                          例如: "ui/icons/tray_icon.png"
        
        Returns:
            完整的资源文件路径 / Full asset file path
        """
        return self.assets_dir / relative_path
    
    def get_config(self, relative_path: str) -> Path:
        """
        获取配置文件路径
        Get config file path
        
        Args:
            relative_path: 相对于 config 目录的路径 / Path relative to config dir
                          例如: "settings.json"
        
        Returns:
            完整的配置文件路径 / Full config file path
        """
        return self.config_dir / relative_path
    
    def get_animation_dir(self, animation_name: str, variant: str = "default") -> Path:
        """
        获取动画目录
        Get animation directory
        
        Args:
            animation_name: 动画名称 / Animation name (e.g., "idle", "happy")
            variant: 变体名称 / Variant name (default: "default")
        
        Returns:
            动画目录路径 / Animation directory path
        """
        return self.assets_dir / "animations" / animation_name / variant
    
    def get_style(self, style_name: str) -> Path:
        """
        获取样式文件路径
        Get style file path
        
        Args:
            style_name: 样式文件名 / Style file name (e.g., "base.qss")
        
        Returns:
            样式文件路径 / Style file path
        """
        if not style_name.endswith('.qss'):
            style_name = f"{style_name}.qss"
        return self.assets_dir / "ui" / "styles" / style_name
    
    def get_icon(self, icon_name: str) -> Path:
        """
        获取图标文件路径
        Get icon file path
        
        Args:
            icon_name: 图标文件名 / Icon file name (e.g., "tray_icon.png")
        
        Returns:
            图标文件路径 / Icon file path
        """
        return self.assets_dir / "ui" / "icons" / icon_name


# 全局实例 / Global instance
_resource_manager = ResourceManager()


def get_assets_dir() -> Path:
    """
    获取 assets 目录路径（快捷函数）
    Get assets directory path (shortcut function)
    
    Returns:
        assets 目录路径 / Assets directory path
    """
    return _resource_manager.assets_dir


def get_config_dir() -> Path:
    """
    获取 config 目录路径（快捷函数）
    Get config directory path (shortcut function)
    
    Returns:
        config 目录路径 / Config directory path
    """
    return _resource_manager.config_dir


def get_asset(relative_path: str) -> Path:
    """
    获取资源文件路径（快捷函数）
    Get asset file path (shortcut function)
    
    Args:
        relative_path: 相对路径 / Relative path
    
    Returns:
        完整路径 / Full path
    """
    return _resource_manager.get_asset(relative_path)


def get_animation_dir(animation_name: str, variant: str = "default") -> Path:
    """
    获取动画目录（快捷函数）
    Get animation directory (shortcut function)
    
    Args:
        animation_name: 动画名称 / Animation name
        variant: 变体名称 / Variant name
    
    Returns:
        动画目录路径 / Animation directory path
    """
    return _resource_manager.get_animation_dir(animation_name, variant)


def get_style(style_name: str) -> Path:
    """
    获取样式文件路径（快捷函数）
    Get style file path (shortcut function)
    
    Args:
        style_name: 样式文件名 / Style file name
    
    Returns:
        样式文件路径 / Style file path
    """
    return _resource_manager.get_style(style_name)


def get_icon(icon_name: str) -> Path:
    """
    获取图标文件路径（快捷函数）
    Get icon file path (shortcut function)
    
    Args:
        icon_name: 图标文件名 / Icon file name
    
    Returns:
        图标文件路径 / Icon file path
    """
    return _resource_manager.get_icon(icon_name)
