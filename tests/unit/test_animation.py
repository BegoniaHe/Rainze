"""
动画系统单元测试
Animation System Unit Tests

测试动画加载器、帧序列、帧播放器和特效层。
Tests for animation loader, frame sequence, frame player, and overlay layer.

Reference:
    - MOD: .github/prds/modules/MOD-Animation.md

Author: Rainze Team
Created: 2025-12-31
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QImage, QPainter, QPixmap
from PySide6.QtWidgets import QApplication

if TYPE_CHECKING:
    pass


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture(scope="module")
def qapp():
    """
    创建 QApplication 实例（模块级别）
    Create QApplication instance (module-level)
    
    PySide6 需要 QApplication 才能使用 QPixmap 等图形类。
    PySide6 requires QApplication for QPixmap and other graphics classes.
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def animation_dir(tmp_path: Path) -> Path:
    """
    创建临时动画目录结构
    Create temporary animation directory structure
    """
    anim_dir = tmp_path / "animations"
    anim_dir.mkdir()
    return anim_dir


@pytest.fixture
def sample_frames(qapp: QApplication, animation_dir: Path) -> Path:
    """
    创建测试用帧图像
    Create test frame images
    """
    frames_dir = animation_dir / "test_anim" / "default"
    frames_dir.mkdir(parents=True)
    
    # 创建 4 帧测试图像 / Create 4 test frame images
    colors = [
        QColor(255, 0, 0),    # Red
        QColor(0, 255, 0),    # Green
        QColor(0, 0, 255),    # Blue
        QColor(255, 255, 0),  # Yellow
    ]
    
    for i, color in enumerate(colors, 1):
        img = QImage(64, 64, QImage.Format.Format_ARGB32)
        img.fill(color)
        img.save(str(frames_dir / f"frame_{i:03d}.png"), "PNG")
    
    return frames_dir


@pytest.fixture
def sample_sprite_sheet(qapp: QApplication, animation_dir: Path) -> Path:
    """
    创建测试用精灵图
    Create test sprite sheet
    """
    sheet_path = animation_dir / "sprite_sheet.png"
    
    # 创建 4x2 精灵图 (每帧 32x32) / Create 4x2 sprite sheet (32x32 per frame)
    img = QImage(128, 64, QImage.Format.Format_ARGB32)
    img.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(img)
    colors = [
        QColor(255, 0, 0), QColor(0, 255, 0),
        QColor(0, 0, 255), QColor(255, 255, 0),
        QColor(255, 0, 255), QColor(0, 255, 255),
        QColor(128, 128, 128), QColor(255, 128, 0),
    ]
    
    for i, color in enumerate(colors):
        col = i % 4
        row = i // 4
        painter.fillRect(col * 32, row * 32, 32, 32, color)
    
    painter.end()
    img.save(str(sheet_path), "PNG")
    
    return sheet_path


# ============================================================================
# AnimationLoader Tests
# ============================================================================


class TestAnimationLoader:
    """AnimationLoader 测试类"""
    
    def test_load_png_sequence(
        self,
        qapp: QApplication,
        sample_frames: Path,
    ) -> None:
        """测试加载 PNG 序列 / Test loading PNG sequence"""
        from rainze.animation.frames import AnimationLoader
        
        loader = AnimationLoader(default_duration_ms=100)
        sequence = loader.load(sample_frames)
        
        assert sequence.name == "default"
        assert len(sequence.frames) == 4
        assert sequence.total_duration_ms == 400
        assert sequence.loop is True
    
    def test_load_png_sequence_custom_name(
        self,
        qapp: QApplication,
        sample_frames: Path,
    ) -> None:
        """测试自定义序列名称 / Test custom sequence name"""
        from rainze.animation.frames import AnimationLoader
        
        loader = AnimationLoader()
        sequence = loader.load(sample_frames, name="custom_name", loop=False)
        
        assert sequence.name == "custom_name"
        assert sequence.loop is False
    
    def test_load_sprite_sheet(
        self,
        qapp: QApplication,
        sample_sprite_sheet: Path,
    ) -> None:
        """测试加载精灵图 / Test loading sprite sheet"""
        from rainze.animation.frames import AnimationLoader, SpriteSheetConfig
        
        loader = AnimationLoader()
        config = SpriteSheetConfig(
            columns=4,
            rows=2,
            frame_width=32,
            frame_height=32,
            duration_ms=50,
        )
        
        sequence = loader.load(sample_sprite_sheet, sprite_config=config)
        
        assert len(sequence.frames) == 8
        assert sequence.total_duration_ms == 400
        
        # 验证帧尺寸 / Verify frame dimensions
        for frame in sequence.frames:
            assert frame.pixmap.width() == 32
            assert frame.pixmap.height() == 32
    
    def test_load_sprite_sheet_partial(
        self,
        qapp: QApplication,
        sample_sprite_sheet: Path,
    ) -> None:
        """测试加载部分精灵图帧 / Test loading partial sprite sheet frames"""
        from rainze.animation.frames import AnimationLoader, SpriteSheetConfig
        
        loader = AnimationLoader()
        config = SpriteSheetConfig(
            columns=4,
            rows=2,
            frame_count=5,  # 只取 5 帧 / Only take 5 frames
            duration_ms=100,
        )
        
        sequence = loader.load(sample_sprite_sheet, sprite_config=config)
        
        assert len(sequence.frames) == 5
    
    def test_load_nonexistent_path(self, qapp: QApplication) -> None:
        """测试加载不存在的路径 / Test loading non-existent path"""
        from rainze.animation.frames import AnimationLoader
        
        loader = AnimationLoader()
        
        with pytest.raises(FileNotFoundError):
            loader.load("nonexistent/path")
    
    def test_load_from_bytes_png(self, qapp: QApplication) -> None:
        """测试从字节加载 PNG / Test loading PNG from bytes"""
        from rainze.animation.frames import AnimationLoader
        
        # 创建测试图像字节 / Create test image bytes
        img = QImage(32, 32, QImage.Format.Format_ARGB32)
        img.fill(QColor(255, 0, 0))
        
        from PySide6.QtCore import QBuffer, QByteArray, QIODevice
        
        buffer = QByteArray()
        buf = QBuffer(buffer)
        buf.open(QIODevice.OpenModeFlag.WriteOnly)
        img.save(buf, "PNG")  # type: ignore[arg-type]
        buf.close()
        
        loader = AnimationLoader()
        sequence = loader.load_from_bytes(
            bytes(buffer.data()),
            format_type="png",
            name="from_bytes",
        )
        
        assert len(sequence.frames) == 1
        assert sequence.frames[0].pixmap.width() == 32


# ============================================================================
# FrameSequence Tests
# ============================================================================


class TestFrameSequence:
    """FrameSequence 测试类"""
    
    def test_empty_sequence(self, qapp: QApplication) -> None:
        """测试空序列 / Test empty sequence"""
        from rainze.animation.frames import FrameSequence
        
        seq = FrameSequence(name="empty")
        
        assert seq.is_empty
        assert seq.frame_count == 0
        assert seq.total_duration_ms == 0
    
    def test_add_frame(self, qapp: QApplication) -> None:
        """测试添加帧 / Test adding frames"""
        from rainze.animation.frames import FrameSequence
        from rainze.animation.models import AnimationFrame
        
        seq = FrameSequence(name="test")
        
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor(255, 0, 0))
        
        seq.add_frame(AnimationFrame(pixmap=pixmap, duration_ms=100))
        seq.add_frame(AnimationFrame(pixmap=pixmap, duration_ms=150))
        
        assert seq.frame_count == 2
        assert seq.total_duration_ms == 250
    
    def test_get_frame_at_time(self, qapp: QApplication) -> None:
        """测试按时间获取帧 / Test getting frame at time"""
        from rainze.animation.frames import FrameSequence
        from rainze.animation.models import AnimationFrame
        
        seq = FrameSequence(name="test", loop=False)
        
        colors = [QColor(255, 0, 0), QColor(0, 255, 0), QColor(0, 0, 255)]
        for color in colors:
            pixmap = QPixmap(32, 32)
            pixmap.fill(color)
            seq.add_frame(AnimationFrame(pixmap=pixmap, duration_ms=100))
        
        # 时间 0-99ms 应返回第一帧 / Time 0-99ms should return first frame
        assert seq.get_frame_index_at_time(0) == 0
        assert seq.get_frame_index_at_time(50) == 0
        assert seq.get_frame_index_at_time(99) == 0
        
        # 时间 100-199ms 应返回第二帧 / Time 100-199ms should return second frame
        assert seq.get_frame_index_at_time(100) == 1
        assert seq.get_frame_index_at_time(150) == 1
        
        # 时间 200-299ms 应返回第三帧 / Time 200-299ms should return third frame
        assert seq.get_frame_index_at_time(200) == 2
    
    def test_get_frame_at_time_looping(self, qapp: QApplication) -> None:
        """测试循环模式下按时间获取帧 / Test getting frame at time with looping"""
        from rainze.animation.frames import FrameSequence
        from rainze.animation.models import AnimationFrame
        
        seq = FrameSequence(name="test", loop=True)
        
        pixmap = QPixmap(32, 32)
        seq.add_frame(AnimationFrame(pixmap=pixmap, duration_ms=100))
        seq.add_frame(AnimationFrame(pixmap=pixmap, duration_ms=100))
        
        # 总时长 200ms，循环后 250ms 应等于 50ms
        # Total 200ms, after loop 250ms should equal 50ms
        assert seq.get_frame_index_at_time(250) == 0
        assert seq.get_frame_index_at_time(350) == 1
    
    def test_from_pixmaps_factory(self, qapp: QApplication) -> None:
        """测试工厂方法 / Test factory method"""
        from rainze.animation.frames import FrameSequence
        
        pixmaps = [QPixmap(32, 32) for _ in range(3)]
        for pm in pixmaps:
            pm.fill(QColor(100, 100, 100))
        
        seq = FrameSequence.from_pixmaps(
            pixmaps,
            duration_ms=50,
            name="factory_test",
            loop=False,
        )
        
        assert seq.name == "factory_test"
        assert seq.frame_count == 3
        assert seq.total_duration_ms == 150
        assert seq.loop is False


# ============================================================================
# FramePlayer Tests
# ============================================================================


class TestFramePlayer:
    """FramePlayer 测试类"""
    
    def test_initial_state(self, qapp: QApplication) -> None:
        """测试初始状态 / Test initial state"""
        from rainze.animation.frames import FramePlayer
        
        player = FramePlayer()
        
        assert player.is_stopped
        assert not player.is_playing
        assert not player.is_paused
        assert player.elapsed_ms == 0
    
    def test_play_sequence(self, qapp: QApplication) -> None:
        """测试播放序列 / Test playing sequence"""
        from rainze.animation.frames import FramePlayer, FrameSequence
        from rainze.animation.models import AnimationFrame
        
        player = FramePlayer()
        
        seq = FrameSequence(name="test", loop=False)
        pixmap = QPixmap(32, 32)
        seq.add_frame(AnimationFrame(pixmap=pixmap, duration_ms=100))
        seq.add_frame(AnimationFrame(pixmap=pixmap, duration_ms=100))
        
        player.set_sequence(seq, auto_play=True)
        
        assert player.is_playing
        assert player.current_frame_index == 0
    
    def test_update_advances_time(self, qapp: QApplication) -> None:
        """测试更新推进时间 / Test update advances time"""
        from rainze.animation.frames import FramePlayer, FrameSequence
        from rainze.animation.models import AnimationFrame
        
        player = FramePlayer()
        
        seq = FrameSequence(name="test", loop=False)
        pixmap = QPixmap(32, 32)
        seq.add_frame(AnimationFrame(pixmap=pixmap, duration_ms=100))
        seq.add_frame(AnimationFrame(pixmap=pixmap, duration_ms=100))
        
        player.set_sequence(seq, auto_play=True)
        
        # 更新 50ms / Update 50ms
        player.update(50)
        assert player.elapsed_ms == 50
        assert player.current_frame_index == 0
        
        # 更新 60ms，应切换到第二帧 / Update 60ms, should switch to second frame
        player.update(60)
        assert player.elapsed_ms == 110
        assert player.current_frame_index == 1
    
    def test_playback_finished_signal(self, qapp: QApplication) -> None:
        """测试播放完成信号 / Test playback finished signal"""
        from rainze.animation.frames import FramePlayer, FrameSequence
        from rainze.animation.models import AnimationFrame
        
        player = FramePlayer()
        
        seq = FrameSequence(name="test", loop=False)
        pixmap = QPixmap(32, 32)
        seq.add_frame(AnimationFrame(pixmap=pixmap, duration_ms=100))
        
        finished_called = []
        player.playback_finished.connect(lambda: finished_called.append(True))
        
        player.set_sequence(seq, auto_play=True)
        player.update(150)  # 超过总时长 / Exceed total duration
        
        assert len(finished_called) == 1
        assert player.is_stopped
    
    def test_pause_resume(self, qapp: QApplication) -> None:
        """测试暂停和恢复 / Test pause and resume"""
        from rainze.animation.frames import FramePlayer, FrameSequence
        from rainze.animation.models import AnimationFrame
        
        player = FramePlayer()
        
        seq = FrameSequence(name="test", loop=True)
        pixmap = QPixmap(32, 32)
        seq.add_frame(AnimationFrame(pixmap=pixmap, duration_ms=100))
        
        player.set_sequence(seq, auto_play=True)
        
        player.pause()
        assert player.is_paused
        
        # 暂停时更新不应改变时间 / Update while paused should not change time
        elapsed_before = player.elapsed_ms
        player.update(50)
        assert player.elapsed_ms == elapsed_before
        
        player.resume()
        assert player.is_playing
        
        player.update(50)
        assert player.elapsed_ms == elapsed_before + 50
    
    def test_playback_speed(self, qapp: QApplication) -> None:
        """测试播放速度 / Test playback speed"""
        from rainze.animation.frames import FramePlayer, FrameSequence
        from rainze.animation.models import AnimationFrame
        
        player = FramePlayer()
        player.playback_speed = 2.0  # 2x 速度 / 2x speed
        
        seq = FrameSequence(name="test", loop=False)  # 非循环避免重置
        pixmap = QPixmap(32, 32)
        seq.add_frame(AnimationFrame(pixmap=pixmap, duration_ms=200))
        
        player.set_sequence(seq, auto_play=True)
        player.update(50)  # 实际应推进 100ms / Should actually advance 100ms
        
        assert player.elapsed_ms == 100


# ============================================================================
# OverlayLayer Tests
# ============================================================================


class TestOverlayLayer:
    """OverlayLayer 测试类"""
    
    def test_initial_state(self, qapp: QApplication) -> None:
        """测试初始状态 / Test initial state"""
        from rainze.animation.layers import OverlayLayer
        
        layer = OverlayLayer(canvas_size=(256, 256))
        
        assert layer.name == "Overlay"
        assert layer.index == 2
        assert layer.visible is True
        assert len(layer.get_active_effects()) == 0
    
    def test_play_effect(self, qapp: QApplication) -> None:
        """测试播放特效 / Test playing effect"""
        from rainze.animation.layers import EffectType, OverlayLayer
        
        layer = OverlayLayer(canvas_size=(256, 256))
        
        layer.play_effect(EffectType.SPARKLE, duration_ms=1000)
        
        assert EffectType.SPARKLE in layer.get_active_effects()
    
    def test_stop_effect(self, qapp: QApplication) -> None:
        """测试停止特效 / Test stopping effect"""
        from rainze.animation.layers import EffectType, OverlayLayer
        
        layer = OverlayLayer(canvas_size=(256, 256))
        
        layer.play_effect(EffectType.SPARKLE)
        layer.play_effect(EffectType.HEART)
        
        assert len(layer.get_active_effects()) == 2
        
        layer.stop_effect(EffectType.SPARKLE)
        
        assert EffectType.SPARKLE not in layer.get_active_effects()
        assert EffectType.HEART in layer.get_active_effects()
    
    def test_stop_all_effects(self, qapp: QApplication) -> None:
        """测试停止所有特效 / Test stopping all effects"""
        from rainze.animation.layers import EffectType, OverlayLayer
        
        layer = OverlayLayer(canvas_size=(256, 256))
        
        layer.play_effect(EffectType.SPARKLE)
        layer.play_effect(EffectType.HEART)
        layer.play_effect(EffectType.TEAR_DROP)
        
        layer.stop_all_effects()
        
        assert len(layer.get_active_effects()) == 0
    
    def test_play_effect_for_emotion(self, qapp: QApplication) -> None:
        """测试根据情感播放特效 / Test playing effect for emotion"""
        from rainze.animation.layers import EffectType, OverlayLayer
        
        layer = OverlayLayer(canvas_size=(256, 256))
        
        layer.play_effect_for_emotion("happy", 0.8)
        
        # happy 映射到 SPARKLE / happy maps to SPARKLE
        assert EffectType.SPARKLE in layer.get_active_effects()
    
    def test_render_frame(self, qapp: QApplication) -> None:
        """测试渲染帧 / Test rendering frame"""
        from rainze.animation.layers import EffectType, OverlayLayer
        
        layer = OverlayLayer(canvas_size=(128, 128))
        
        layer.play_effect(EffectType.SPARKLE)
        layer.update(100)  # 推进动画 / Advance animation
        
        frame = layer.get_current_frame()
        
        assert frame is not None
        assert frame.width() == 128
        assert frame.height() == 128
    
    def test_effect_expiration(self, qapp: QApplication) -> None:
        """测试特效过期 / Test effect expiration"""
        from rainze.animation.layers import EffectType, OverlayLayer
        
        layer = OverlayLayer(canvas_size=(256, 256))
        
        # HEART 是非循环特效 / HEART is non-looping effect
        layer.play_effect(EffectType.HEART, duration_ms=100)
        
        assert EffectType.HEART in layer.get_active_effects()
        
        # 更新超过持续时间 / Update past duration
        layer.update(150)
        
        assert EffectType.HEART not in layer.get_active_effects()
    
    def test_all_effect_types_render(self, qapp: QApplication) -> None:
        """测试所有特效类型都能渲染 / Test all effect types can render"""
        from rainze.animation.layers import EffectType, OverlayLayer
        
        layer = OverlayLayer(canvas_size=(256, 256))
        
        for effect_type in EffectType:
            layer.stop_all_effects()
            layer.play_effect(effect_type, duration_ms=1000)
            layer.update(100)
            
            frame = layer.get_current_frame()
            
            assert frame is not None, f"Failed to render {effect_type.name}"
            assert not frame.isNull(), f"Rendered null frame for {effect_type.name}"
    
    def test_reset(self, qapp: QApplication) -> None:
        """测试重置 / Test reset"""
        from rainze.animation.layers import EffectType, OverlayLayer
        
        layer = OverlayLayer(canvas_size=(256, 256))
        
        layer.play_effect(EffectType.SPARKLE)
        layer.play_effect(EffectType.HEART)
        layer.update(500)
        
        layer.reset()
        
        assert len(layer.get_active_effects()) == 0


# ============================================================================
# AnimationController Integration Tests
# ============================================================================


class TestAnimationController:
    """AnimationController 集成测试"""
    
    def test_initialization(self, qapp: QApplication, animation_dir: Path) -> None:
        """测试初始化 / Test initialization"""
        from rainze.animation.controller import AnimationController
        from rainze.animation.models import AnimationState
        
        controller = AnimationController(
            resource_path=str(animation_dir),
            fps=30,
            canvas_size=(256, 256),
        )
        
        assert controller.get_current_state() == AnimationState.IDLE
    
    def test_set_animation(
        self,
        qapp: QApplication,
        sample_frames: Path,
    ) -> None:
        """测试设置动画 / Test setting animation"""
        from rainze.animation.controller import AnimationController
        
        # sample_frames 在 animations/test_anim/default 下
        # sample_frames is under animations/test_anim/default
        anim_root = sample_frames.parent.parent
        
        controller = AnimationController(
            resource_path=str(anim_root),
            fps=30,
        )
        
        controller.set_animation("test_anim")
        
        # 检查帧播放器是否设置了序列 / Check if frame player has sequence
        assert controller._frame_player.sequence is not None
        assert controller._frame_player.sequence.frame_count == 4
    
    def test_play_effect(self, qapp: QApplication, animation_dir: Path) -> None:
        """测试播放特效 / Test playing effect"""
        from rainze.animation.controller import AnimationController
        from rainze.animation.layers import EffectType
        
        controller = AnimationController(
            resource_path=str(animation_dir),
            fps=30,
        )
        
        controller.play_effect("sparkle", duration_ms=1000)
        
        # 检查叠加层是否创建并播放特效
        # Check if overlay layer was created and effect is playing
        overlay = controller._layers.get(controller.LAYER_OVERLAY)
        assert overlay is not None
        assert EffectType.SPARKLE in overlay.get_active_effects()  # type: ignore[union-attr]
    
    def test_apply_emotion_tag(self, qapp: QApplication, animation_dir: Path) -> None:
        """测试应用情感标签 / Test applying emotion tag"""
        from rainze.animation.controller import AnimationController
        from rainze.core.contracts import EmotionTag
        
        controller = AnimationController(
            resource_path=str(animation_dir),
            fps=30,
        )
        
        tag = EmotionTag(tag="happy", intensity=0.8)
        controller.apply_emotion_tag(tag)
        
        expression, intensity = controller.get_current_expression()
        assert expression == "happy"
        assert intensity == 0.8
    
    def test_parse_emotion_tag(self, qapp: QApplication, animation_dir: Path) -> None:
        """测试解析情感标签 / Test parsing emotion tag"""
        from rainze.animation.controller import AnimationController
        
        controller = AnimationController(
            resource_path=str(animation_dir),
            fps=30,
        )
        
        text = "今天天气真好呢~ [EMOTION:happy:0.8]"
        tag = controller.parse_emotion_tag(text)
        
        assert tag is not None
        assert tag.tag == "happy"
        assert tag.intensity == 0.8
    
    def test_render_loop(
        self,
        qapp: QApplication,
        sample_frames: Path,
    ) -> None:
        """测试渲染循环 / Test render loop"""
        from rainze.animation.controller import AnimationController
        
        anim_root = sample_frames.parent.parent
        
        controller = AnimationController(
            resource_path=str(anim_root),
            fps=30,
        )
        
        frames_received = []
        controller.frame_ready.connect(lambda pm: frames_received.append(pm))
        
        controller.set_animation("test_anim")
        controller.start_render_loop()
        
        # 手动触发渲染 / Manually trigger render
        controller._on_render_tick()
        
        controller.stop_render_loop()
        
        assert len(frames_received) >= 1
        assert not frames_received[0].isNull()
