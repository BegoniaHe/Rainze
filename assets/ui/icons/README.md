# Rainze 图标目录 / Icons Directory

此目录存放应用图标文件。
This directory contains application icon files.

## 需要的图标文件 / Required Icon Files

### macOS

- `rainze.icns` - macOS 应用图标 (1024x1024 及多分辨率)

### Windows

- `rainze.ico` - Windows 应用图标 (256x256 及多分辨率)

## 创建图标 / Creating Icons

### 从 PNG 创建 ICNS (macOS)

```bash
mkdir rainze.iconset
# 创建不同尺寸的 PNG (16, 32, 128, 256, 512, 1024)
sips -z 16 16     icon.png --out rainze.iconset/icon_16x16.png
sips -z 32 32     icon.png --out rainze.iconset/icon_16x16@2x.png
sips -z 32 32     icon.png --out rainze.iconset/icon_32x32.png
sips -z 64 64     icon.png --out rainze.iconset/icon_32x32@2x.png
sips -z 128 128   icon.png --out rainze.iconset/icon_128x128.png
sips -z 256 256   icon.png --out rainze.iconset/icon_128x128@2x.png
sips -z 256 256   icon.png --out rainze.iconset/icon_256x256.png
sips -z 512 512   icon.png --out rainze.iconset/icon_256x256@2x.png
sips -z 512 512   icon.png --out rainze.iconset/icon_512x512.png
sips -z 1024 1024 icon.png --out rainze.iconset/icon_512x512@2x.png
iconutil -c icns rainze.iconset
```

### 从 PNG 创建 ICO (Windows)

使用在线工具或 ImageMagick:

```bash
convert icon.png -define icon:auto-resize=256,128,64,48,32,16 rainze.ico
```

## 临时占位 / Temporary Placeholder

当前使用系统默认图标。请替换为正式设计的图标。
Currently using system default icons. Please replace with official designed icons.
