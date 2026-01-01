# Rainze Makefile
# AI 桌面宠物应用构建脚本 / AI Desktop Pet Build Script
#
# Usage / 使用方式:
#   make help       - 显示帮助 / Show help
#   make setup      - 初始化环境 / Initialize environment
#   make build      - 构建项目 / Build project
#   make run        - 运行应用 / Run application
#   make test       - 运行测试 / Run tests
#   make clean      - 清理构建 / Clean build artifacts
#
# Requirements / 依赖:
#   - Python 3.12+
#   - Rust 1.92+
#   - uv (Python package manager)
#   - MinGW (for Rust GNU target on Windows)

# ============================================================================
# 平台检测 / Platform Detection
# ============================================================================

# 检测操作系统 / Detect operating system
ifeq ($(OS),Windows_NT)
    PLATFORM := windows
    SHELL := powershell.exe
    .SHELLFLAGS := -NoProfile -Command
    # Windows 路径 / Windows paths
    VENV := .venv
    PYTHON := $(VENV)\Scripts\python.exe
    MATURIN := $(VENV)\Scripts\maturin.exe
    RUFF := $(VENV)\Scripts\ruff.exe
    MYPY := $(VENV)\Scripts\mypy.exe
    PYTEST := $(VENV)\Scripts\pytest.exe
    # MinGW 路径 / MinGW path
    MINGW_PATH := C:\msys64\mingw64\bin
    # Wheel 文件名 / Wheel filename (abi3 支持 Python 3.9+)
    RUST_WHEEL_PATTERN := rainze_core-*-cp39-abi3-win_amd64.whl
else
    UNAME_S := $(shell uname -s)
    ifeq ($(UNAME_S),Darwin)
        PLATFORM := macos
        # macOS wheel 架构检测 / macOS wheel architecture detection
        UNAME_M := $(shell uname -m)
        ifeq ($(UNAME_M),arm64)
            RUST_WHEEL_PATTERN := rainze_core-*-cp39-abi3-macosx_*_arm64.whl
        else
            RUST_WHEEL_PATTERN := rainze_core-*-cp39-abi3-macosx_*_x86_64.whl
        endif
    else
        PLATFORM := linux
        RUST_WHEEL_PATTERN := rainze_core-*-cp39-abi3-manylinux*.whl
    endif
    SHELL := /bin/bash
    .SHELLFLAGS := -c
    # Unix 路径 / Unix paths
    VENV := .venv
    PYTHON := $(VENV)/bin/python
    MATURIN := $(VENV)/bin/maturin
    RUFF := $(VENV)/bin/ruff
    MYPY := $(VENV)/bin/mypy
    PYTEST := $(VENV)/bin/pytest
    MINGW_PATH :=
endif

# ============================================================================
# 配置 / Configuration
# ============================================================================

UV := uv

# Rust 配置 / Rust configuration
RUST_TARGET := rainze_core
RUST_WHEEL_DIR := $(RUST_TARGET)/target/wheels

# ============================================================================
# 跨平台辅助函数 / Cross-platform Helper Functions
# ============================================================================

# 定义颜色输出 (Unix 使用 ANSI, Windows 使用 Write-Host)
# Define colored output (Unix uses ANSI, Windows uses Write-Host)
ifeq ($(PLATFORM),windows)
    define log_info
		@Write-Host "$(1)" -ForegroundColor Cyan
    endef
    define log_success
		@Write-Host "$(1)" -ForegroundColor Green
    endef
    define log_warn
		@Write-Host "$(1)" -ForegroundColor Yellow
    endef
else
    # ANSI 颜色代码 / ANSI color codes
    CYAN := \033[36m
    GREEN := \033[32m
    YELLOW := \033[33m
    RESET := \033[0m
    define log_info
		@echo "$(CYAN)$(1)$(RESET)"
    endef
    define log_success
		@echo "$(GREEN)$(1)$(RESET)"
    endef
    define log_warn
		@echo "$(YELLOW)$(1)$(RESET)"
    endef
endif

# ============================================================================
# 默认目标 / Default target
# ============================================================================

.PHONY: help
help:
ifeq ($(PLATFORM),windows)
	@Write-Host "Rainze Makefile - AI Desktop Pet" -ForegroundColor Cyan
	@Write-Host "=================================" -ForegroundColor Cyan
	@Write-Host ""
	@Write-Host "Setup / 环境配置:" -ForegroundColor Yellow
	@Write-Host "  make setup      - 完整环境初始化 / Full environment setup"
	@Write-Host "  make venv       - 创建虚拟环境 / Create virtual environment"
	@Write-Host "  make deps       - 安装 Python 依赖 / Install Python dependencies"
	@Write-Host ""
	@Write-Host "Build / 构建:" -ForegroundColor Yellow
	@Write-Host "  make build      - 构建所有组件 / Build all components"
	@Write-Host "  make build-rust - 构建 Rust 模块 / Build Rust module"
	@Write-Host "  make build-dev  - 开发模式构建 / Development build"
	@Write-Host ""
	@Write-Host "Run / 运行:" -ForegroundColor Yellow
	@Write-Host "  make run        - 运行应用 / Run application"
	@Write-Host "  make verify     - 验证环境 / Verify environment"
	@Write-Host ""
	@Write-Host "Quality / 质量:" -ForegroundColor Yellow
	@Write-Host "  make test       - 运行测试 / Run tests"
	@Write-Host "  make lint       - 代码检查 / Lint code"
	@Write-Host "  make format     - 格式化代码 / Format code"
	@Write-Host "  make typecheck  - 类型检查 / Type check"
	@Write-Host "  make check      - 运行所有检查 / Run all checks"
	@Write-Host ""
	@Write-Host "Packaging / 打包:" -ForegroundColor Yellow
	@Write-Host "  make package           - 打包应用 (目录模式) / Package app (directory mode)"
	@Write-Host "  make package-onefile   - 打包单文件应用 / Package as single file"
	@Write-Host "  make package-zip       - 创建 ZIP 分发包 / Create ZIP distribution"
	@Write-Host "  make package-dmg       - 创建 DMG 镜像 (仅 macOS) / Create DMG (macOS only)"
	@Write-Host "  make package-all       - 创建所有打包格式 / Create all package formats"
	@Write-Host "  make clean-dist        - 清理打包产物 / Clean dist artifacts"
	@Write-Host ""
else
	@printf "\033[36mRainze Makefile - AI Desktop Pet\033[0m\n"
	@printf "\033[36m=================================\033[0m\n"
	@printf "\n"
	@printf "\033[33mSetup / 环境配置:\033[0m\n"
	@printf "  make setup      - 完整环境初始化 / Full environment setup\n"
	@printf "  make venv       - 创建虚拟环境 / Create virtual environment\n"
	@printf "  make deps       - 安装 Python 依赖 / Install Python dependencies\n"
	@printf "\n"
	@printf "\033[33mBuild / 构建:\033[0m\n"
	@printf "  make build      - 构建所有组件 / Build all components\n"
	@printf "  make build-rust - 构建 Rust 模块 / Build Rust module\n"
	@printf "  make build-dev  - 开发模式构建 / Development build\n"
	@printf "\n"
	@printf "\033[33mRun / 运行:\033[0m\n"
	@printf "  make run        - 运行应用 / Run application\n"
	@printf "  make verify     - 验证环境 / Verify environment\n"
	@printf "\n"
	@printf "\033[33mQuality / 质量:\033[0m\n"
	@printf "  make test       - 运行测试 / Run tests\n"
	@printf "  make lint       - 代码检查 / Lint code\n"
	@printf "  make format     - 格式化代码 / Format code\n"
	@printf "  make typecheck  - 类型检查 / Type check\n"
	@printf "  make check      - 运行所有检查 / Run all checks\n"
	@printf "\n"
	@printf "\033[33mPackaging / 打包:\033[0m\n"
	@printf "  make package           - 打包应用 (目录模式) / Package app (directory mode)\n"
	@printf "  make package-onefile   - 打包单文件应用 / Package as single file\n"
	@printf "  make package-zip       - 创建 ZIP 分发包 / Create ZIP distribution\n"
	@printf "  make package-dmg       - 创建 DMG 镜像 (仅 macOS) / Create DMG (macOS only)\n"
	@printf "  make package-all       - 创建所有打包格式 / Create all package formats\n"
	@printf "  make clean-dist        - 清理打包产物 / Clean dist artifacts\n"
	@printf "\n"
endif

# ============================================================================
# 环境配置 / Environment Setup
# ============================================================================

.PHONY: setup
setup: venv deps build-dev
ifeq ($(PLATFORM),windows)
	@Write-Host " 环境配置完成 / Setup complete!" -ForegroundColor Green
else
	@printf "\033[32m 环境配置完成 / Setup complete!\033[0m\n"
endif

.PHONY: venv
venv:
ifeq ($(PLATFORM),windows)
	@Write-Host " 创建虚拟环境 / Creating virtual environment..." -ForegroundColor Cyan
else
	@printf "\033[36m 创建虚拟环境 / Creating virtual environment...\033[0m\n"
endif
	@$(UV) venv

.PHONY: deps
deps:
ifeq ($(PLATFORM),windows)
	@Write-Host "📥 安装依赖 / Installing dependencies..." -ForegroundColor Cyan
else
	@printf "\033[36m📥 安装依赖 / Installing dependencies...\033[0m\n"
endif
	@$(UV) sync --all-extras

# ============================================================================
# 构建 / Build
# ============================================================================

.PHONY: build
build: build-rust install-rust
ifeq ($(PLATFORM),windows)
	@Write-Host " 构建完成 / Build complete!" -ForegroundColor Green
else
	@printf "\033[32m 构建完成 / Build complete!\033[0m\n"
endif

.PHONY: build-rust
build-rust:
ifeq ($(PLATFORM),windows)
	@Write-Host " 构建 Rust 模块 / Building Rust module..." -ForegroundColor Cyan
	@$$env:PATH = "$(MINGW_PATH);$$env:PATH"; $$env:PYO3_PYTHON = (Resolve-Path "$(PYTHON)").Path; $$maturin = (Resolve-Path "$(MATURIN)").Path; Push-Location $(RUST_TARGET); & $$maturin build --release; Pop-Location
else
	@printf "\033[36m 构建 Rust 模块 / Building Rust module...\033[0m\n"
	@cd $(RUST_TARGET) && PYO3_PYTHON=$(CURDIR)/$(PYTHON) $(CURDIR)/$(MATURIN) build --release
endif

.PHONY: build-dev
build-dev:
ifeq ($(PLATFORM),windows)
	@Write-Host " 开发模式构建 / Development build..." -ForegroundColor Cyan
	@$$env:PATH = "$(MINGW_PATH);$$env:PATH"; $$env:PYO3_PYTHON = (Resolve-Path "$(PYTHON)").Path; $$maturin = (Resolve-Path "$(MATURIN)").Path; Push-Location $(RUST_TARGET); & $$maturin develop; Pop-Location
else
	@printf "\033[36m 开发模式构建 / Development build...\033[0m\n"
	@cd $(RUST_TARGET) && PYO3_PYTHON=$(CURDIR)/$(PYTHON) $(CURDIR)/$(MATURIN) develop
endif

.PHONY: install-rust
install-rust:
ifeq ($(PLATFORM),windows)
	@Write-Host " 安装 Rust wheel / Installing Rust wheel..." -ForegroundColor Cyan
	@$(UV) pip install (Get-ChildItem "$(RUST_WHEEL_DIR)\$(RUST_WHEEL_PATTERN)" | Select-Object -First 1).FullName --force-reinstall
else
	@printf "\033[36m 安装 Rust wheel / Installing Rust wheel...\033[0m\n"
	@$(UV) pip install $$(ls $(RUST_WHEEL_DIR)/$(RUST_WHEEL_PATTERN) | head -1) --force-reinstall
endif

# ============================================================================
# 运行 / Run
# ============================================================================

.PHONY: run
run:
ifeq ($(PLATFORM),windows)
	@Write-Host " 启动 Rainze / Starting Rainze..." -ForegroundColor Cyan
	@& "$(PYTHON)" -m rainze.main
else
	@printf "\033[36m 启动 Rainze / Starting Rainze...\033[0m\n"
	@$(PYTHON) -m rainze.main
endif

.PHONY: verify
verify:
ifeq ($(PLATFORM),windows)
	@Write-Host " 验证环境 / Verifying environment..." -ForegroundColor Cyan
	@& "$(PYTHON)" -c "import rainze_core; import rainze; print('rainze:', rainze.__version__); m = rainze_core.SystemMonitor(); print('rainze_core: OK'); print(f'CPU: {m.get_cpu_usage():.1f}%%'); print(f'Memory: {m.get_memory_usage():.1f}%%')"
else
	@printf "\033[36m 验证环境 / Verifying environment...\033[0m\n"
	@$(PYTHON) -c "import rainze_core; import rainze; print('rainze:', rainze.__version__); m = rainze_core.SystemMonitor(); print('rainze_core: OK'); print(f'CPU: {m.get_cpu_usage():.1f}%'); print(f'Memory: {m.get_memory_usage():.1f}%')"
endif

# ============================================================================
# 质量检查 / Quality Checks
# ============================================================================

.PHONY: test
test:
ifeq ($(PLATFORM),windows)
	@Write-Host " 运行测试 / Running tests..." -ForegroundColor Cyan
	@& "$(PYTEST)" tests/ -v
else
	@printf "\033[36m 运行测试 / Running tests...\033[0m\n"
	@$(PYTEST) tests/ -v
endif

.PHONY: test-unit
test-unit:
ifeq ($(PLATFORM),windows)
	@Write-Host " 运行单元测试 / Running unit tests..." -ForegroundColor Cyan
	@& "$(PYTEST)" tests/unit/ -v
else
	@printf "\033[36m 运行单元测试 / Running unit tests...\033[0m\n"
	@$(PYTEST) tests/unit/ -v
endif

.PHONY: test-cov
test-cov:
ifeq ($(PLATFORM),windows)
	@Write-Host " 运行测试 (覆盖率) / Running tests with coverage..." -ForegroundColor Cyan
	@& "$(PYTEST)" tests/ -v --cov=src/rainze --cov-report=term-missing
else
	@printf "\033[36m 运行测试 (覆盖率) / Running tests with coverage...\033[0m\n"
	@$(PYTEST) tests/ -v --cov=src/rainze --cov-report=term-missing
endif

.PHONY: lint
lint:
ifeq ($(PLATFORM),windows)
	@Write-Host "🔎 代码检查 / Linting..." -ForegroundColor Cyan
	@& "$(RUFF)" check src/ tests/
else
	@printf "\033[36m🔎 代码检查 / Linting...\033[0m\n"
	@$(RUFF) check src/ tests/
endif

.PHONY: format
format:
ifeq ($(PLATFORM),windows)
	@Write-Host "✨ 格式化代码 / Formatting..." -ForegroundColor Cyan
	@& "$(RUFF)" format src/ tests/
	@& "$(RUFF)" check src/ tests/ --fix
else
	@printf "\033[36m✨ 格式化代码 / Formatting...\033[0m\n"
	@$(RUFF) format src/ tests/
	@$(RUFF) check src/ tests/ --fix
endif

.PHONY: typecheck
typecheck:
ifeq ($(PLATFORM),windows)
	@Write-Host " 类型检查 / Type checking..." -ForegroundColor Cyan
	@& "$(MYPY)" src/rainze --ignore-missing-imports
else
	@printf "\033[36m 类型检查 / Type checking...\033[0m\n"
	@$(MYPY) src/rainze --ignore-missing-imports
endif

.PHONY: check
check: lint typecheck test
ifeq ($(PLATFORM),windows)
	@Write-Host " 所有检查通过 / All checks passed!" -ForegroundColor Green
else
	@printf "\033[32m 所有检查通过 / All checks passed!\033[0m\n"
endif

.PHONY: rust-check
rust-check:
ifeq ($(PLATFORM),windows)
	@Write-Host " Rust 检查 / Rust check..." -ForegroundColor Cyan
	@$$env:PATH = "$(MINGW_PATH);$$env:PATH"; $$env:PYO3_PYTHON = (Resolve-Path "$(PYTHON)").Path; Push-Location $(RUST_TARGET); cargo check; cargo clippy; Pop-Location
else
	@printf "\033[36m Rust 检查 / Rust check...\033[0m\n"
	@cd $(RUST_TARGET) && cargo check && cargo clippy
endif

# ============================================================================
# 清理 / Clean
# ============================================================================

.PHONY: clean
clean:
ifeq ($(PLATFORM),windows)
	@Write-Host "🧹 清理构建产物 / Cleaning build artifacts..." -ForegroundColor Cyan
	@Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $(RUST_TARGET)\target, dist, build, *.egg-info, .pytest_cache, .mypy_cache, .ruff_cache, __pycache__
	@Get-ChildItem -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
	@Write-Host " 清理完成 / Clean complete!" -ForegroundColor Green
else
	@printf "\033[36m🧹 清理构建产物 / Cleaning build artifacts...\033[0m\n"
	@rm -rf $(RUST_TARGET)/target dist build *.egg-info .pytest_cache .mypy_cache .ruff_cache
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@printf "\033[32m 清理完成 / Clean complete!\033[0m\n"
endif

.PHONY: clean-all
clean-all: clean
ifeq ($(PLATFORM),windows)
	@Write-Host "🧹 完全清理 / Full clean..." -ForegroundColor Cyan
	@Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $(VENV)
	@Write-Host " 完全清理完成 / Full clean complete!" -ForegroundColor Green
else
	@printf "\033[36m🧹 完全清理 / Full clean...\033[0m\n"
	@rm -rf $(VENV)
	@printf "\033[32m 完全清理完成 / Full clean complete!\033[0m\n"
endif

# ============================================================================
# 开发辅助 / Development Helpers
# ============================================================================

.PHONY: pre-commit
pre-commit:
ifeq ($(PLATFORM),windows)
	@Write-Host " 安装 pre-commit hooks / Installing pre-commit hooks..." -ForegroundColor Cyan
	@& "$(VENV)\Scripts\pre-commit.exe" install
else
	@printf "\033[36m 安装 pre-commit hooks / Installing pre-commit hooks...\033[0m\n"
	@$(VENV)/bin/pre-commit install
endif

.PHONY: update
update:
ifeq ($(PLATFORM),windows)
	@Write-Host " 更新依赖 / Updating dependencies..." -ForegroundColor Cyan
else
	@printf "\033[36m 更新依赖 / Updating dependencies...\033[0m\n"
endif
	@$(UV) lock --upgrade
	@$(UV) sync --all-extras

# ============================================================================
# 打包 / Packaging
# ============================================================================

.PHONY: package
package: build
ifeq ($(PLATFORM),windows)
	@Write-Host "📦 打包应用 / Packaging application..." -ForegroundColor Cyan
	@& "$(PYTHON)" -m PyInstaller rainze.spec --clean --noconfirm
	@Write-Host " 打包完成！/ Package complete!" -ForegroundColor Green
	@Write-Host "  输出目录 / Output: dist\Rainze\" -ForegroundColor Yellow
else
	@printf "\033[36m📦 打包应用 / Packaging application...\033[0m\n"
	@$(PYTHON) -m PyInstaller rainze.spec --clean --noconfirm
	@printf "\033[32m 打包完成！/ Package complete!\033[0m\n"
ifeq ($(PLATFORM),macos)
	@printf "\033[33m  输出目录 / Output: dist/Rainze.app\033[0m\n"
else
	@printf "\033[33m  输出目录 / Output: dist/Rainze/\033[0m\n"
endif
endif

.PHONY: package-onefile
package-onefile: build
ifeq ($(PLATFORM),windows)
	@Write-Host "📦 打包单文件应用 / Packaging as single file..." -ForegroundColor Cyan
	@& "$(PYTHON)" -m PyInstaller src/rainze/main.py --name Rainze --onefile --windowed --clean --noconfirm --icon assets/ui/icons/rainze.ico
	@Write-Host " 单文件打包完成！/ Single-file package complete!" -ForegroundColor Green
	@Write-Host "  输出文件 / Output: dist\Rainze.exe" -ForegroundColor Yellow
else
	@printf "\033[36m📦 打包单文件应用 / Packaging as single file...\033[0m\n"
ifeq ($(PLATFORM),macos)
	@$(PYTHON) -m PyInstaller src/rainze/main.py --name Rainze --onefile --windowed --clean --noconfirm --icon assets/ui/icons/rainze.icns
else
	@$(PYTHON) -m PyInstaller src/rainze/main.py --name Rainze --onefile --windowed --clean --noconfirm
endif
	@printf "\033[32m 单文件打包完成！/ Single-file package complete!\033[0m\n"
	@printf "\033[33m  输出文件 / Output: dist/Rainze\033[0m\n"
endif

.PHONY: package-dir
package-dir: package
ifeq ($(PLATFORM),windows)
	@Write-Host "📦 创建分发目录 / Creating distribution directory..." -ForegroundColor Cyan
	@New-Item -ItemType Directory -Force -Path "dist\Rainze-$(PLATFORM)" | Out-Null
	@Copy-Item -Recurse -Force "dist\Rainze\*" "dist\Rainze-$(PLATFORM)\"
	@Copy-Item -Force "README.md", "LICENSE" "dist\Rainze-$(PLATFORM)\" -ErrorAction SilentlyContinue
	@Write-Host " 分发目录创建完成！/ Distribution directory created!" -ForegroundColor Green
	@Write-Host "  位置 / Location: dist\Rainze-$(PLATFORM)\" -ForegroundColor Yellow
else
	@printf "\033[36m📦 创建分发目录 / Creating distribution directory...\033[0m\n"
	@mkdir -p "dist/Rainze-$(PLATFORM)"
ifeq ($(PLATFORM),macos)
	@cp -R dist/Rainze.app "dist/Rainze-$(PLATFORM)/"
else
	@cp -R dist/Rainze/* "dist/Rainze-$(PLATFORM)/"
endif
	@cp README.md LICENSE "dist/Rainze-$(PLATFORM)/" 2>/dev/null || true
	@printf "\033[32m 分发目录创建完成！/ Distribution directory created!\033[0m\n"
	@printf "\033[33m  位置 / Location: dist/Rainze-$(PLATFORM)/\033[0m\n"
endif

.PHONY: package-zip
package-zip: package-dir
ifeq ($(PLATFORM),windows)
	@Write-Host "📦 创建 ZIP 压缩包 / Creating ZIP archive..." -ForegroundColor Cyan
	@Push-Location dist; Compress-Archive -Force -Path "Rainze-$(PLATFORM)" -DestinationPath "Rainze-$(PLATFORM).zip"; Pop-Location
	@Write-Host " ZIP 创建完成！/ ZIP created!" -ForegroundColor Green
	@Write-Host "  文件 / File: dist\Rainze-$(PLATFORM).zip" -ForegroundColor Yellow
else
	@printf "\033[36m📦 创建 ZIP 压缩包 / Creating ZIP archive...\033[0m\n"
	@cd dist && zip -r "Rainze-$(PLATFORM).zip" "Rainze-$(PLATFORM)"
	@printf "\033[32m ZIP 创建完成！/ ZIP created!\033[0m\n"
	@printf "\033[33m  文件 / File: dist/Rainze-$(PLATFORM).zip\033[0m\n"
endif

.PHONY: package-dmg
package-dmg: package
ifeq ($(PLATFORM),macos)
	@printf "\033[36m📦 创建 DMG 镜像 / Creating DMG image...\033[0m\n"
	@hdiutil create -volname "Rainze" -srcfolder dist/Rainze.app -ov -format UDZO dist/Rainze-macos.dmg
	@printf "\033[32m DMG 创建完成！/ DMG created!\033[0m\n"
	@printf "\033[33m  文件 / File: dist/Rainze-macos.dmg\033[0m\n"
else
	@printf "\033[31m⚠️  DMG 仅支持 macOS / DMG only available on macOS\033[0m\n"
endif

.PHONY: package-installer
package-installer: package-dir
ifeq ($(PLATFORM),windows)
	@Write-Host "📦 创建安装程序 / Creating installer..." -ForegroundColor Cyan
	@Write-Host "⚠️  需要 Inno Setup / Requires Inno Setup" -ForegroundColor Yellow
	@Write-Host "  TODO: 实现 Inno Setup 脚本 / TODO: Implement Inno Setup script" -ForegroundColor Yellow
else
	@printf "\033[33m⚠️  安装程序创建仅支持 Windows / Installer creation only for Windows\033[0m\n"
endif

.PHONY: package-all
package-all: package-zip
ifeq ($(PLATFORM),macos)
	@$(MAKE) package-dmg
endif
ifeq ($(PLATFORM),windows)
	@Write-Host " 所有打包完成！/ All packages created!" -ForegroundColor Green
else
	@printf "\033[32m 所有打包完成！/ All packages created!\033[0m\n"
endif

.PHONY: clean-dist
clean-dist:
ifeq ($(PLATFORM),windows)
	@Write-Host "🧹 清理打包产物 / Cleaning dist..." -ForegroundColor Cyan
	@Remove-Item -Recurse -Force -ErrorAction SilentlyContinue dist, build, *.spec
	@Write-Host " 打包产物清理完成！/ Dist cleaned!" -ForegroundColor Green
else
	@printf "\033[36m🧹 清理打包产物 / Cleaning dist...\033[0m\n"
	@rm -rf dist build *.spec
	@printf "\033[32m 打包产物清理完成！/ Dist cleaned!\033[0m\n"
endif
