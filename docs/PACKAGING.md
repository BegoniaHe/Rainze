# Rainze 打包指南 / Packaging Guide

本文档说明如何使用 PyInstaller 打包 Rainze。

## 快速开始 / Quick Start

```bash
# 1. 基础打包 (推荐)
make package

# 2. 单文件打包
make package-onefile

# 3. 创建分发包
make package-all
```

## 可用命令 / Available Commands

| 命令 | 说明 | 输出 |
|------|------|------|
| `make package` | 目录模式打包 | `dist/Rainze/` or `.app` |
| `make package-onefile` | 单文件打包 | `dist/Rainze` or `.exe` |
| `make package-zip` | 创建 ZIP | `dist/Rainze-{platform}.zip` |
| `make package-dmg` | 创建 DMG (仅 macOS) | `dist/Rainze-macos.dmg` |
| `make package-all` | 创建所有格式 | 平台相关 |
| `make clean-dist` | 清理打包产物 | - |

## 配置文件 / Configuration

- `rainze.spec`: PyInstaller 配置
- `assets/ui/icons/`: 应用图标目录

## 更多信息 / More Info

参见: <https://pyinstaller.org/en/stable/>
