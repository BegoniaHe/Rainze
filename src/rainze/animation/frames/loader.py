"""
动画资源加载器
Animation Resource Loader

本模块提供多格式动画资源加载功能。
This module provides multi-format animation resource loading.

支持格式 / Supported formats:
- PNG 序列 / PNG sequences
- GIF 动画 / GIF animations
- Sprite Sheet 精灵图 / Sprite sheets

Reference:
    - MOD: .github/prds/modules/MOD-Animation.md §3.6

Author: Rainze Team
Created: 2025-12-31
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional

from PySide6.QtCore import QBuffer, QByteArray, QIODevice
from PySide6.QtGui import QImage, QImageReader, QPixmap

if TYPE_CHECKING:
    from rainze.animation.frames.sequence import FrameSequence

from rainze.animation.models import AnimationFrame

# 日志 / Logger
logger = logging.getLogger(__name__)

# 导出列表 / Export list
__all__ = [
    "AnimationLoader",
    "LoaderFormat",
    "SpriteSheetConfig",
]


class LoaderFormat(Enum):
    """
    加载器支持的格式
    Supported loader formats

    Attributes:
        PNG_SEQUENCE: PNG 序列（目录内多个 PNG 文件）
        GIF: GIF 动画文件
        SPRITE_SHEET: 精灵图（单张图片切片）
        AUTO: 自动检测格式
    """

    PNG_SEQUENCE = auto()
    GIF = auto()
    SPRITE_SHEET = auto()
    AUTO = auto()


@dataclass
class SpriteSheetConfig:
    """
    精灵图配置
    Sprite sheet configuration

    Attributes:
        columns: 列数 / Number of columns
        rows: 行数 / Number of rows
        frame_width: 帧宽度（像素），None 为自动计算 / Frame width in px
        frame_height: 帧高度（像素），None 为自动计算 / Frame height in px
        frame_count: 帧数量，None 为 columns * rows / Total frame count
        frame_order: 帧顺序 "row" 或 "column" / Frame order
        duration_ms: 每帧持续时间 / Duration per frame in ms
    """

    columns: int
    rows: int
    frame_width: Optional[int] = None
    frame_height: Optional[int] = None
    frame_count: Optional[int] = None
    frame_order: str = "row"  # "row" (left-right, top-bottom) or "column"
    duration_ms: int = 100


class AnimationLoader:
    """
    动画资源加载器
    Animation resource loader

    提供统一接口加载多种格式的动画资源。
    Provides unified interface to load various animation formats.

    支持：
    - PNG 序列：目录下的 frame_001.png, frame_002.png, ...
    - GIF 动画：单个 .gif 文件
    - Sprite Sheet：单张大图切片

    Example:
        >>> loader = AnimationLoader()
        >>> # 加载 PNG 序列 / Load PNG sequence
        >>> sequence = loader.load("assets/animations/idle/default")
        >>> # 加载 GIF / Load GIF
        >>> sequence = loader.load("assets/animations/wave.gif")
        >>> # 加载 Sprite Sheet / Load sprite sheet
        >>> config = SpriteSheetConfig(columns=4, rows=2)
        >>> sequence = loader.load("assets/sprites/walk.png", sprite_config=config)

    Reference:
        PRD §0.14: 动画资源规格
    """

    # 支持的 PNG 文件名模式 / Supported PNG filename patterns
    PNG_PATTERNS = ["frame_*.png", "*.png"]

    def __init__(self, default_duration_ms: int = 100) -> None:
        """
        初始化加载器
        Initialize loader

        Args:
            default_duration_ms: 默认每帧持续时间 / Default frame duration in ms
        """
        self._default_duration_ms = default_duration_ms

    def load(
        self,
        path: str | Path,
        format_hint: LoaderFormat = LoaderFormat.AUTO,
        sprite_config: Optional[SpriteSheetConfig] = None,
        name: Optional[str] = None,
        loop: bool = True,
    ) -> "FrameSequence":
        """
        加载动画资源
        Load animation resource

        根据路径和格式提示自动选择加载方式。
        Automatically selects loading method based on path and format hint.

        Args:
            path: 资源路径（目录或文件）/ Resource path (directory or file)
            format_hint: 格式提示 / Format hint
            sprite_config: 精灵图配置（仅 SPRITE_SHEET 格式需要）
            name: 序列名称，None 为自动生成 / Sequence name
            loop: 是否循环 / Whether to loop

        Returns:
            加载的帧序列 / Loaded frame sequence

        Raises:
            FileNotFoundError: 路径不存在
            ValueError: 格式不支持或配置错误
        """
        # 延迟导入避免循环依赖 / Lazy import to avoid circular dependency
        from rainze.animation.frames.sequence import FrameSequence

        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"路径不存在 / Path not found: {path}")

        # 自动检测格式 / Auto-detect format
        if format_hint == LoaderFormat.AUTO:
            format_hint = self._detect_format(path, sprite_config)

        # 生成名称 / Generate name
        if name is None:
            name = path.stem if path.is_file() else path.name

        # 根据格式加载 / Load based on format
        if format_hint == LoaderFormat.PNG_SEQUENCE:
            frames = self._load_png_sequence(path)
        elif format_hint == LoaderFormat.GIF:
            frames = self._load_gif(path)
        elif format_hint == LoaderFormat.SPRITE_SHEET:
            if sprite_config is None:
                raise ValueError(
                    "Sprite Sheet 格式需要提供 sprite_config / "
                    "sprite_config required for SPRITE_SHEET format"
                )
            frames = self._load_sprite_sheet(path, sprite_config)
        else:
            raise ValueError(f"不支持的格式 / Unsupported format: {format_hint}")

        # 创建序列 / Create sequence
        sequence = FrameSequence(name=name, loop=loop)
        sequence.add_frames(frames)

        logger.info(
            f"加载动画: {name}, 格式: {format_hint.name}, "
            f"帧数: {len(frames)}, 总时长: {sequence.total_duration_ms}ms"
        )

        return sequence

    def _detect_format(
        self,
        path: Path,
        sprite_config: Optional[SpriteSheetConfig],
    ) -> LoaderFormat:
        """
        自动检测格式（内部方法）
        Auto-detect format (internal method)

        Args:
            path: 资源路径
            sprite_config: 精灵图配置

        Returns:
            检测到的格式
        """
        # 如果提供了 sprite_config，则为 Sprite Sheet
        # If sprite_config provided, it's a Sprite Sheet
        if sprite_config is not None:
            return LoaderFormat.SPRITE_SHEET

        # 如果是目录，则为 PNG 序列
        # If directory, it's PNG sequence
        if path.is_dir():
            return LoaderFormat.PNG_SEQUENCE

        # 根据扩展名判断 / Check by extension
        suffix = path.suffix.lower()
        if suffix == ".gif":
            return LoaderFormat.GIF
        if suffix == ".png":
            # 单个 PNG 可能是 Sprite Sheet，但没有配置则报错
            # Single PNG might be sprite sheet, but error without config
            raise ValueError(
                f"单个 PNG 文件需要提供 sprite_config / "
                f"Single PNG requires sprite_config: {path}"
            )

        raise ValueError(f"无法识别的格式 / Unknown format: {path}")

    def _load_png_sequence(self, directory: Path) -> List[AnimationFrame]:
        """
        加载 PNG 序列（内部方法）
        Load PNG sequence (internal method)

        Args:
            directory: PNG 序列目录

        Returns:
            帧列表
        """
        frames: List[AnimationFrame] = []

        # 首先尝试加载清单文件 / First try to load manifest
        manifest_path = directory.parent / "manifest.json"
        frame_configs = None

        if manifest_path.exists():
            try:
                with open(manifest_path, encoding="utf-8") as f:
                    manifest = json.load(f)
                    anim_name = directory.parent.name
                    anim_config = manifest.get("animations", {}).get(anim_name)
                    if anim_config:
                        frame_configs = anim_config.get("frames")
            except Exception as e:
                logger.warning(f"加载清单失败: {e}")

        # 如果有清单配置，按配置加载 / If manifest exists, load per config
        if frame_configs:
            for frame_cfg in frame_configs:
                frame_file = directory / frame_cfg["file"]
                duration_ms = frame_cfg.get("duration_ms", self._default_duration_ms)

                if frame_file.exists():
                    pixmap = QPixmap(str(frame_file))
                    if not pixmap.isNull():
                        frames.append(AnimationFrame(
                            pixmap=pixmap,
                            duration_ms=duration_ms,
                        ))
        else:
            # 回退到自动发现 / Fallback to auto-discovery
            png_files: List[Path] = []

            for pattern in self.PNG_PATTERNS:
                found = sorted(directory.glob(pattern))
                if found:
                    png_files = found
                    break

            if not png_files:
                logger.warning(f"目录中未找到 PNG 文件: {directory}")
                return frames

            for png_file in png_files:
                pixmap = QPixmap(str(png_file))
                if not pixmap.isNull():
                    frames.append(AnimationFrame(
                        pixmap=pixmap,
                        duration_ms=self._default_duration_ms,
                    ))

        return frames

    def _load_gif(self, gif_path: Path) -> List[AnimationFrame]:
        """
        加载 GIF 动画（内部方法）
        Load GIF animation (internal method)

        使用 Qt 的 QImageReader 逐帧读取 GIF。
        Uses Qt's QImageReader to read GIF frames.

        Args:
            gif_path: GIF 文件路径

        Returns:
            帧列表
        """
        frames: List[AnimationFrame] = []

        reader = QImageReader(str(gif_path))

        if not reader.canRead():
            logger.warning(f"无法读取 GIF: {gif_path}")
            return frames

        # 检查是否支持动画 / Check if animation is supported
        if not reader.supportsAnimation():
            # 静态图片，作为单帧处理 / Static image, treat as single frame
            image = reader.read()
            if not image.isNull():
                pixmap = QPixmap.fromImage(image)
                frames.append(AnimationFrame(
                    pixmap=pixmap,
                    duration_ms=self._default_duration_ms,
                ))
            return frames

        # 读取所有帧 / Read all frames
        while reader.canRead():
            image = reader.read()
            if image.isNull():
                break

            pixmap = QPixmap.fromImage(image)

            # 获取帧延迟（GIF 以 10ms 为单位）
            # Get frame delay (GIF uses 10ms units)
            delay = reader.nextImageDelay()
            if delay <= 0:
                delay = self._default_duration_ms

            frames.append(AnimationFrame(
                pixmap=pixmap,
                duration_ms=delay,
            ))

        return frames

    def _load_sprite_sheet(
        self,
        sheet_path: Path,
        config: SpriteSheetConfig,
    ) -> List[AnimationFrame]:
        """
        加载 Sprite Sheet（内部方法）
        Load sprite sheet (internal method)

        将单张大图切分为多帧。
        Splits single large image into multiple frames.

        Args:
            sheet_path: 精灵图路径
            config: 精灵图配置

        Returns:
            帧列表
        """
        frames: List[AnimationFrame] = []

        # 加载完整图片 / Load full image
        full_image = QImage(str(sheet_path))
        if full_image.isNull():
            logger.warning(f"无法加载精灵图: {sheet_path}")
            return frames

        # 计算帧尺寸 / Calculate frame dimensions
        img_width = full_image.width()
        img_height = full_image.height()

        frame_width = config.frame_width or (img_width // config.columns)
        frame_height = config.frame_height or (img_height // config.rows)

        # 计算总帧数 / Calculate total frames
        total_frames = config.frame_count or (config.columns * config.rows)

        # 切分帧 / Extract frames
        frame_index = 0
        if config.frame_order == "row":
            # 行优先：从左到右，从上到下
            # Row-major: left-to-right, top-to-bottom
            for row in range(config.rows):
                for col in range(config.columns):
                    if frame_index >= total_frames:
                        break

                    x = col * frame_width
                    y = row * frame_height

                    # 裁剪帧 / Crop frame
                    frame_image = full_image.copy(x, y, frame_width, frame_height)
                    pixmap = QPixmap.fromImage(frame_image)

                    frames.append(AnimationFrame(
                        pixmap=pixmap,
                        duration_ms=config.duration_ms,
                    ))
                    frame_index += 1

                if frame_index >= total_frames:
                    break
        else:
            # 列优先：从上到下，从左到右
            # Column-major: top-to-bottom, left-to-right
            for col in range(config.columns):
                for row in range(config.rows):
                    if frame_index >= total_frames:
                        break

                    x = col * frame_width
                    y = row * frame_height

                    frame_image = full_image.copy(x, y, frame_width, frame_height)
                    pixmap = QPixmap.fromImage(frame_image)

                    frames.append(AnimationFrame(
                        pixmap=pixmap,
                        duration_ms=config.duration_ms,
                    ))
                    frame_index += 1

                if frame_index >= total_frames:
                    break

        return frames

    def load_from_bytes(
        self,
        data: bytes,
        format_type: str = "gif",
        name: str = "unnamed",
        loop: bool = True,
        sprite_config: Optional[SpriteSheetConfig] = None,
    ) -> "FrameSequence":
        """
        从字节数据加载动画
        Load animation from bytes data

        用于从网络或内存加载动画。
        Used for loading animations from network or memory.

        Args:
            data: 图像字节数据 / Image bytes data
            format_type: 格式类型 ("gif", "png") / Format type
            name: 序列名称 / Sequence name
            loop: 是否循环 / Whether to loop
            sprite_config: 精灵图配置（仅 PNG 需要）

        Returns:
            加载的帧序列 / Loaded frame sequence
        """
        from rainze.animation.frames.sequence import FrameSequence

        frames: List[AnimationFrame] = []

        if format_type.lower() == "gif":
            frames = self._load_gif_from_bytes(data)
        elif format_type.lower() == "png":
            if sprite_config:
                frames = self._load_sprite_sheet_from_bytes(data, sprite_config)
            else:
                # 单帧 PNG / Single frame PNG
                image = QImage()
                image.loadFromData(QByteArray(data))
                if not image.isNull():
                    pixmap = QPixmap.fromImage(image)
                    frames.append(AnimationFrame(
                        pixmap=pixmap,
                        duration_ms=self._default_duration_ms,
                    ))

        sequence = FrameSequence(name=name, loop=loop)
        sequence.add_frames(frames)
        return sequence

    def _load_gif_from_bytes(self, data: bytes) -> List[AnimationFrame]:
        """
        从字节加载 GIF（内部方法）
        Load GIF from bytes (internal method)
        """
        frames: List[AnimationFrame] = []

        # 使用 QBuffer 包装字节数据 / Wrap bytes with QBuffer
        byte_array = QByteArray(data)
        buffer = QBuffer(byte_array)
        buffer.open(QIODevice.OpenModeFlag.ReadOnly)

        reader = QImageReader(buffer, b"GIF")

        if not reader.canRead():
            return frames

        while reader.canRead():
            image = reader.read()
            if image.isNull():
                break

            pixmap = QPixmap.fromImage(image)
            delay = reader.nextImageDelay()
            if delay <= 0:
                delay = self._default_duration_ms

            frames.append(AnimationFrame(
                pixmap=pixmap,
                duration_ms=delay,
            ))

        buffer.close()
        return frames

    def _load_sprite_sheet_from_bytes(
        self,
        data: bytes,
        config: SpriteSheetConfig,
    ) -> List[AnimationFrame]:
        """
        从字节加载 Sprite Sheet（内部方法）
        Load sprite sheet from bytes (internal method)
        """
        full_image = QImage()
        full_image.loadFromData(QByteArray(data))

        if full_image.isNull():
            return []

        # 复用切片逻辑 / Reuse slicing logic
        frames: List[AnimationFrame] = []

        img_width = full_image.width()
        img_height = full_image.height()

        frame_width = config.frame_width or (img_width // config.columns)
        frame_height = config.frame_height or (img_height // config.rows)
        total_frames = config.frame_count or (config.columns * config.rows)

        frame_index = 0
        for row in range(config.rows):
            for col in range(config.columns):
                if frame_index >= total_frames:
                    break

                x = col * frame_width
                y = row * frame_height

                frame_image = full_image.copy(x, y, frame_width, frame_height)
                pixmap = QPixmap.fromImage(frame_image)

                frames.append(AnimationFrame(
                    pixmap=pixmap,
                    duration_ms=config.duration_ms,
                ))
                frame_index += 1

            if frame_index >= total_frames:
                break

        return frames
