# -*- mode: python ; coding: utf-8 -*-
"""
Rainze PyInstaller Configuration (Simplified)
AI 桌面宠物应用打包配置（简化版）

Author: Rainze Team
Created: 2026-01-01
"""

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# ============================================================================
# 基本配置 / Basic Configuration
# ============================================================================

APP_NAME = 'Rainze'
APP_VERSION = '0.1.0'
MAIN_SCRIPT = 'src/rainze/main.py'

IS_MACOS = sys.platform == 'darwin'
IS_WINDOWS = sys.platform == 'win32'

# ============================================================================
# 数据文件收集 / Data Files Collection
# ============================================================================

datas = []

# 配置文件 / Config files
import glob
for pattern, dest in [
    ('config/*.json', 'config'),
    ('config/*.txt', 'config'),
    ('config/database/*.sql', 'config/database'),
]:
    matched = glob.glob(pattern)
    if matched:
        datas.append((pattern, dest))

# Assets 资源文件 / Assets
# 包括所有图片、字体等静态资源
for src_dir, dest_dir in [
    ('assets', 'assets'),  # 直接打包整个 assets 目录
]:
    if os.path.exists(src_dir):
        datas.append((src_dir, dest_dir))

# ============================================================================
# 隐藏导入 / Hidden Imports
# ============================================================================

hiddenimports = [
    # PySide6 核心
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    
    # Rainze 模块
    'rainze',
    'rainze.core',
    'rainze.gui',
    'rainze.ai',
    'rainze.memory',
    'rainze.animation',
    'rainze.state',
    'rainze.agent',
    
    # Rust 核心
    'rainze_core',
    
    # AI 库
    'openai',
    'anthropic',
    'tiktoken',
    
    # 向量搜索
    'faiss',
    'numpy',
    
    # 数据库
    'sqlite3',
    'aiosqlite',
    
    # HTTP
    'httpx',
    'aiohttp',
]

# 收集所有 rainze 子模块
try:
    hiddenimports += collect_submodules('rainze')
except Exception:
    pass

# ============================================================================
# 排除模块 / Excludes
# ============================================================================

excludes = [
    'pytest', 'unittest', 'nose',
    'IPython', 'jupyter', 'notebook',
    'sphinx', 'pydoc',
    'mypy', 'pyright',
    'pylint', 'flake8', 'black', 'ruff',
    'setuptools', 'pip', 'wheel',
    'tkinter', 'gtk', 'wx',
    'tensorflow', 'torch', 'keras',
    # 排除大型 Qt 模块
    'PySide6.QtCharts',
    'PySide6.QtDataVisualization',
    'PySide6.Qt3DCore',
    'PySide6.QtQuick',
    'PySide6.QtWebEngine',
    'PySide6.QtMultimedia',
]

# ============================================================================
# 二进制文件 / Binaries
# ============================================================================

binaries = []

# rainze_core Rust 扩展
if IS_MACOS:
    import glob as g
    rust_libs = g.glob('.venv/lib/python*/site-packages/rainze_core*.so')
    if rust_libs:
        binaries.append((rust_libs[0], '.'))
elif IS_WINDOWS:
    import glob as g
    rust_libs = g.glob('.venv/Lib/site-packages/rainze_core*.pyd')
    if rust_libs:
        binaries.append((rust_libs[0], '.'))

# ============================================================================
# Analysis
# ============================================================================

a = Analysis(
    [MAIN_SCRIPT],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

# ============================================================================
# EXE
# ============================================================================

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # GUI 应用
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# ============================================================================
# COLLECT
# ============================================================================

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=APP_NAME,
)

# ============================================================================
# macOS App Bundle
# ============================================================================

if IS_MACOS:
    app = BUNDLE(
        coll,
        name=f'{APP_NAME}.app',
        bundle_identifier='com.rainze.app',
        version=APP_VERSION,
        info_plist={
            'CFBundleName': APP_NAME,
            'CFBundleDisplayName': 'Rainze',
            'CFBundleVersion': APP_VERSION,
            'CFBundleShortVersionString': APP_VERSION,
            'NSHighResolutionCapable': 'True',
            'LSMinimumSystemVersion': '10.15.0',
        },
    )
