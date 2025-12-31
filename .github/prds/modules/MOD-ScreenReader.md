# MOD-ScreenReader - 屏幕内容感知模块 子PRD

> **模块版本**: v1.0.0
> **创建日期**: 2025-12-31
> **最后更新**: 2025-12-31
> **关联PRD**: PRD-Rainze.md v3.1.0 §0.0
> **关联技术栈**: TECH-Rainze.md §3.2
> **平台支持**: Windows 10/11, macOS 10.15+

---

## 1. 模块概述

### 1.1 模块定位

ScreenReader 模块是 Rainze 的**情境感知层**，负责理解用户当前正在做什么，为桌宠提供上下文感知能力。采用**双路径架构**：

- **结构路径**: UI Automation / Accessibility API → 语义化 UI 结构
- **视觉路径**: Graphics Capture / CGWindow → 截图 + OCR

**核心设计原则**: 高效、隐私、按需

```
[Screen Reader Architecture]
|
|-- 高效性:
|    |-- 触发式采集（非持续监控）
|    |-- 分层采集（按需深入）
|    |-- 变化检测（避免重复处理）
|    \-- GPU 加速截图
|
|-- 隐私性:
|    |-- 黑名单应用自动跳过
|    |-- 敏感内容过滤
|    |-- 本地处理优先
|    \-- 只存语义摘要
|
\-- 按需性:
     |-- 窗口切换 → Level 1-2
     |-- 用户空闲 → Level 3
     |-- 主动询问 → Level 3 + 截图
     \-- 异常检测 → Level 3-4
```

### 1.2 用户活动理解层次

```
[Activity Understanding Levels]
|
|-- Level 1: 应用层 (What app?) [<10ms]
|    |-- 窗口标题、进程名、应用分类
|    \-- 数据源: Win32 API / NSWorkspace
|
|-- Level 2: 任务层 (What task?) [<20ms]
|    |-- 文件类型、URL 解析、任务推断
|    \-- 数据源: 窗口标题解析 + 规则匹配
|
|-- Level 3: 内容层 (What content?) [<500ms]
|    |-- UI 元素文本、焦点内容
|    \-- 数据源: UI Automation / AX API / OCR
|
\-- Level 4: 状态层 (What state?) [异步]
     |-- 行为模式分析（卡顿、摸鱼、专注）
     \-- 数据源: 时序分析 + 启发式规则
```

### 1.3 性能目标

| 操作 | GPU 延迟 | CPU 延迟 | 说明 |
|------|----------|----------|------|
| 窗口信息获取 (L1) | <10ms | <10ms | Win32/NSWorkspace |
| 任务推断 (L2) | <20ms | <20ms | 规则匹配 |
| UI 树遍历 (L3) | <100ms | <100ms | 焦点元素为中心 |
| 窗口截图 (L3) | <50ms | <100ms | GPU: Graphics Capture |
| OCR 识别 (L3) | <300ms | <1500ms | GPU: PaddleOCR CUDA |
| 完整上下文 (L1-3) | <500ms | <2000ms | 按需组合 |

**CPU Fallback 说明**: 无 GPU 时系统自动降级到 CPU 模式，所有功能完整可用，仅延迟增加。详见 §7.4。

---

## 2. 跨平台抽象

### 2.1 平台 API 对照

| 功能 | Windows | macOS |
|------|---------|-------|
| 窗口信息 | GetForegroundWindow + GetWindowText | NSWorkspace.frontmostApplication |
| 进程信息 | GetWindowThreadProcessId + QueryFullProcessImageName | NSRunningApplication |
| UI 树 | UI Automation (IUIAutomation) | Accessibility API (AXUIElement) |
| 文本读取 | TextPattern / ValuePattern | AXValue / AXTitle |
| 屏幕截图 | Graphics Capture API / GDI | CGWindowListCreateImage |
| 事件监听 | SetWinEventHook | NSWorkspace.notificationCenter |
| 权限检查 | 无需特殊权限 | AXIsProcessTrusted + CGPreflightScreenCaptureAccess |

### 2.2 Trait 抽象

```rust
/// 跨平台屏幕读取接口
/// Cross-platform screen reader interface
pub trait PlatformScreenReader: Send + Sync {
    /// 获取前台窗口信息 / Get foreground window info
    fn get_foreground_window(&self) -> Result<WindowInfo>;
    
    /// 获取窗口 UI 树 / Get window UI tree
    fn get_ui_tree(&self, window_id: WindowId, max_depth: u32) -> Result<UINode>;
    
    /// 获取焦点元素文本 / Get focused element text
    fn get_focused_text(&self) -> Result<Option<String>>;
    
    /// 截取窗口图像 / Capture window image
    fn capture_window(&self, window_id: WindowId) -> Result<ImageData>;
    
    /// 截取屏幕区域 / Capture screen region
    fn capture_region(&self, rect: Rect) -> Result<ImageData>;
    
    /// 启动事件监听 / Start event listener
    fn start_event_listener(
        &self,
        callback: Box<dyn Fn(ScreenEvent) + Send>
    ) -> Result<EventListenerHandle>;
    
    /// 停止事件监听 / Stop event listener
    fn stop_event_listener(&self, handle: EventListenerHandle) -> Result<()>;
    
    /// 检查权限状态 / Check permission status
    fn check_permissions(&self) -> PermissionStatus;
    
    /// 请求权限 / Request permissions
    fn request_permissions(&self) -> Result<()>;
}
```

---

## 3. 数据类型定义

### 3.1 窗口信息

```rust
/// 窗口标识符 (跨平台)
/// Window identifier (cross-platform)
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub enum WindowId {
    #[cfg(windows)]
    Windows(isize),      // HWND
    #[cfg(target_os = "macos")]
    MacOS(u32),          // CGWindowID
}

/// 窗口信息
/// Window information
#[pyclass]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct WindowInfo {
    /// 窗口 ID / Window ID
    #[pyo3(get)]
    pub window_id: u64,
    
    /// 窗口标题 / Window title
    #[pyo3(get)]
    pub title: String,
    
    /// 进程名 / Process name
    #[pyo3(get)]
    pub process_name: String,
    
    /// 进程 ID / Process ID
    #[pyo3(get)]
    pub process_id: u32,
    
    /// Bundle ID (macOS) / 包标识符
    #[pyo3(get)]
    pub bundle_id: Option<String>,
    
    /// 应用分类 / App category
    #[pyo3(get)]
    pub app_category: AppCategory,
    
    /// 窗口边界 / Window bounds
    #[pyo3(get)]
    pub bounds: Rect,
    
    /// 是否全屏 / Is fullscreen
    #[pyo3(get)]
    pub is_fullscreen: bool,
    
    /// 是否最小化 / Is minimized
    #[pyo3(get)]
    pub is_minimized: bool,
    
    /// URL (浏览器窗口) / URL for browser
    #[pyo3(get)]
    pub url: Option<String>,
}

/// 应用分类
/// Application category
#[pyclass]
#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub enum AppCategory {
    /// IDE / 代码编辑器
    IDE,
    /// 浏览器
    Browser,
    /// 办公软件
    Office,
    /// 媒体播放
    Media,
    /// 游戏
    Game,
    /// 通讯软件
    Communication,
    /// 系统工具
    System,
    /// 终端
    Terminal,
    /// 隐私应用（银行、密码管理器）
    Privacy,
    /// 未知
    Unknown,
}

/// 矩形区域
/// Rectangle
#[pyclass]
#[derive(Clone, Copy, Debug, Serialize, Deserialize)]
pub struct Rect {
    #[pyo3(get)]
    pub x: i32,
    #[pyo3(get)]
    pub y: i32,
    #[pyo3(get)]
    pub width: u32,
    #[pyo3(get)]
    pub height: u32,
}
```

### 3.2 UI 元素树

```rust
/// UI 元素节点
/// UI element node
#[pyclass]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct UINode {
    /// 元素角色 / Element role
    /// Windows: "Button", "Edit", "Text", "List", etc.
    /// macOS: "AXButton", "AXTextField", "AXStaticText", etc.
    #[pyo3(get)]
    pub role: String,
    
    /// 元素名称 / Element name
    #[pyo3(get)]
    pub name: Option<String>,
    
    /// 元素值 / Element value
    #[pyo3(get)]
    pub value: Option<String>,
    
    /// 元素描述 / Element description
    #[pyo3(get)]
    pub description: Option<String>,
    
    /// 边界框 / Bounding box
    #[pyo3(get)]
    pub bounds: Rect,
    
    /// 是否有焦点 / Is focused
    #[pyo3(get)]
    pub is_focused: bool,
    
    /// 是否可用 / Is enabled
    #[pyo3(get)]
    pub is_enabled: bool,
    
    /// 是否可编辑 / Is editable
    #[pyo3(get)]
    pub is_editable: bool,
    
    /// 是否密码框 / Is password field
    #[pyo3(get)]
    pub is_password: bool,
    
    /// 子元素 / Children
    #[pyo3(get)]
    pub children: Vec<UINode>,
}

/// 焦点元素信息
/// Focused element info
#[pyclass]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct FocusedElement {
    /// 元素类型 / Element type
    #[pyo3(get)]
    pub element_type: String,
    
    /// 文本内容（截断）/ Text content (truncated)
    #[pyo3(get)]
    pub text_preview: Option<String>,
    
    /// 完整文本长度 / Full text length
    #[pyo3(get)]
    pub text_length: usize,
    
    /// 选中文本 / Selected text
    #[pyo3(get)]
    pub selected_text: Option<String>,
    
    /// 光标位置 / Cursor position
    #[pyo3(get)]
    pub cursor_position: Option<usize>,
    
    /// 父级应用 / Parent application
    #[pyo3(get)]
    pub application: String,
}
```

### 3.3 屏幕事件

```rust
/// 屏幕事件
/// Screen event
#[pyclass]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum ScreenEvent {
    /// 前台窗口变化 / Foreground window changed
    WindowFocusChanged {
        window: WindowInfo,
        previous_window_id: Option<u64>,
    },
    
    /// 窗口创建 / Window created
    WindowCreated {
        window: WindowInfo,
    },
    
    /// 窗口关闭 / Window closed
    WindowClosed {
        window_id: u64,
    },
    
    /// 窗口标题变化 / Window title changed
    WindowTitleChanged {
        window_id: u64,
        old_title: String,
        new_title: String,
    },
    
    /// 用户开始空闲 / User idle started
    UserIdleStart {
        idle_seconds: u32,
    },
    
    /// 用户结束空闲 / User idle ended
    UserIdleEnd {
        idle_duration: u32,
    },
}

/// 事件监听器句柄
/// Event listener handle
#[derive(Clone, Copy, Debug)]
pub struct EventListenerHandle(pub u64);
```

### 3.4 截图数据

```rust
/// 图像数据
/// Image data
#[pyclass]
#[derive(Clone)]
pub struct ImageData {
    /// 宽度 / Width
    #[pyo3(get)]
    pub width: u32,
    
    /// 高度 / Height
    #[pyo3(get)]
    pub height: u32,
    
    /// 像素数据 (RGBA) / Pixel data (RGBA)
    pub pixels: Vec<u8>,
    
    /// 格式 / Format
    #[pyo3(get)]
    pub format: ImageFormat,
}

#[pymethods]
impl ImageData {
    /// 转换为 PNG bytes
    /// Convert to PNG bytes
    pub fn to_png(&self) -> PyResult<Vec<u8>>;
    
    /// 转换为 JPEG bytes
    /// Convert to JPEG bytes
    pub fn to_jpeg(&self, quality: u8) -> PyResult<Vec<u8>>;
    
    /// 获取 numpy 数组
    /// Get numpy array
    pub fn to_numpy<'py>(&self, py: Python<'py>) -> PyResult<&'py PyArray3<u8>>;
    
    /// 裁剪区域
    /// Crop region
    pub fn crop(&self, rect: Rect) -> PyResult<ImageData>;
    
    /// 缩放
    /// Resize
    pub fn resize(&self, width: u32, height: u32) -> PyResult<ImageData>;
}

/// 图像格式
#[pyclass]
#[derive(Clone, Copy, Debug)]
pub enum ImageFormat {
    RGBA,
    RGB,
    BGRA,
    BGR,
}
```

### 3.5 权限状态

```rust
/// 权限状态
/// Permission status
#[pyclass]
#[derive(Clone, Debug)]
pub struct PermissionStatus {
    /// 辅助功能权限 (macOS)
    /// Accessibility permission
    #[pyo3(get)]
    pub accessibility: bool,
    
    /// 屏幕录制权限 (macOS)
    /// Screen capture permission
    #[pyo3(get)]
    pub screen_capture: bool,
    
    /// 是否所有权限就绪
    /// All permissions ready
    #[pyo3(get)]
    pub all_granted: bool,
    
    /// 缺失权限说明
    /// Missing permission descriptions
    #[pyo3(get)]
    pub missing_descriptions: Vec<String>,
}
```

---

## 4. 采集策略

### 4.1 触发器设计

```
[Trigger System]
|
|-- Trigger 1: 窗口切换 (WindowFocusChanged)
|    |-- 检测: SetWinEventHook / NSWorkspace.notification
|    |-- 去抖: 300ms
|    |-- 采集: Level 1-2
|    \-- 用途: 实时感知应用切换
|
|-- Trigger 2: 用户空闲 (UserIdle)
|    |-- 检测: GetLastInputInfo / CGEventSourceSecondsSinceLastEventType
|    |-- 阈值: 30 秒
|    |-- 采集: Level 3 (内容快照)
|    \-- 用途: 理解用户停在哪里
|
|-- Trigger 3: 主动询问 (UserQuery)
|    |-- 检测: 用户输入包含 "看看" / "帮我" / "这是什么"
|    |-- 采集: Level 3 + 截图 + OCR
|    \-- 用途: 精确理解当前上下文
|
|-- Trigger 4: 定时心跳 (Heartbeat)
|    |-- 间隔: 5 分钟
|    |-- 采集: Level 1-2 + 时间统计
|    \-- 用途: 构建使用习惯画像
|
\-- Trigger 5: 异常检测 (Anomaly)
     |-- 条件:
     |    |-- 同一窗口停留 >1 小时
     |    |-- 频繁 Ctrl+Z (>10 次/分钟)
     |    |-- 深夜工作 (23:00-06:00)
     |-- 采集: Level 3-4
     \-- 用途: 主动关怀触发
```

### 4.2 分层采集接口

```rust
/// 屏幕上下文
/// Screen context
#[pyclass]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct ScreenContext {
    /// 时间戳 / Timestamp
    #[pyo3(get)]
    pub timestamp: i64,
    
    /// 窗口信息 / Window info
    #[pyo3(get)]
    pub window: WindowInfo,
    
    /// 焦点元素 (Level 3) / Focused element
    #[pyo3(get)]
    pub focus_element: Option<FocusedElement>,
    
    /// 活动提示 / Activity hint
    #[pyo3(get)]
    pub activity_hint: String,
    
    /// 采集级别 / Collection level
    #[pyo3(get)]
    pub level: u8,
}

#[pymethods]
impl ScreenReader {
    /// 快速采集 (Level 1-2)
    /// Quick collection
    /// 
    /// 只获取窗口信息和任务推断，<20ms
    pub fn collect_quick(&self) -> PyResult<ScreenContext>;
    
    /// 标准采集 (Level 1-3)
    /// Standard collection
    /// 
    /// 包含 UI 树和焦点文本，<200ms
    pub fn collect_standard(&self) -> PyResult<ScreenContext>;
    
    /// 完整采集 (Level 1-3 + 截图)
    /// Full collection with screenshot
    /// 
    /// 包含截图，<500ms
    pub fn collect_full(&self) -> PyResult<(ScreenContext, ImageData)>;
    
    /// 仅截图
    /// Capture only
    pub fn capture_foreground(&self) -> PyResult<ImageData>;
}
```

---

## 5. 应用分类器

### 5.1 分类规则

```rust
/// 应用分类器
/// Application classifier
pub struct AppClassifier {
    /// 进程名 -> 分类 映射
    process_rules: HashMap<String, AppCategory>,
    
    /// Bundle ID -> 分类 映射 (macOS)
    bundle_rules: HashMap<String, AppCategory>,
    
    /// URL 域名 -> 分类 映射
    url_rules: HashMap<String, AppCategory>,
    
    /// 隐私应用列表
    privacy_apps: HashSet<String>,
}
```

### 5.2 预设分类规则

```json
{
  "process_rules": {
    "code.exe": "IDE",
    "Code.exe": "IDE",
    "idea64.exe": "IDE",
    "pycharm64.exe": "IDE",
    "devenv.exe": "IDE",
    "webstorm64.exe": "IDE",
    
    "chrome.exe": "Browser",
    "firefox.exe": "Browser",
    "msedge.exe": "Browser",
    "Safari": "Browser",
    
    "WINWORD.EXE": "Office",
    "EXCEL.EXE": "Office",
    "POWERPNT.EXE": "Office",
    "Notion.exe": "Office",
    "Obsidian.exe": "Office",
    
    "vlc.exe": "Media",
    "PotPlayerMini64.exe": "Media",
    "Spotify.exe": "Media",
    
    "WeChat.exe": "Communication",
    "QQ.exe": "Communication",
    "Telegram.exe": "Communication",
    "Slack.exe": "Communication",
    "Teams.exe": "Communication",
    "Discord.exe": "Communication",
    
    "WindowsTerminal.exe": "Terminal",
    "cmd.exe": "Terminal",
    "powershell.exe": "Terminal",
    "Terminal": "Terminal",
    "iTerm2": "Terminal",
    
    "explorer.exe": "System",
    "Finder": "System",
    "SystemPreferences": "System"
  },
  
  "url_rules": {
    "github.com": "IDE",
    "gitlab.com": "IDE",
    "stackoverflow.com": "IDE",
    
    "bilibili.com": "Media",
    "youtube.com": "Media",
    "netflix.com": "Media",
    
    "docs.google.com": "Office",
    "notion.so": "Office",
    "figma.com": "Office",
    
    "twitter.com": "Communication",
    "weibo.com": "Communication",
    "discord.com": "Communication"
  },
  
  "privacy_apps": [
    "1Password.exe",
    "Bitwarden.exe",
    "KeePass.exe",
    "LastPass.exe",
    "银行",
    "Bank",
    "Alipay",
    "支付宝"
  ]
}
```

### 5.3 桌宠行为响应映射

```
[App Category -> Pet Behavior]
|
|-- IDE:
|    |-- 模式: "专注模式"
|    |-- 行为: 安静陪伴，减少主动打扰
|    |-- 触发: 连续 1 小时后提醒休息
|
|-- Browser:
|    |-- 根据 URL 细分
|    |-- 编程网站 → 同 IDE
|    |-- 视频网站 → "休息模式"
|    |-- 社交网站 → "社交模式"
|
|-- Office:
|    |-- 模式: "工作模式"
|    |-- 行为: 适度互动
|    |-- 触发: 文档编辑 30 分钟后提醒保存
|
|-- Media:
|    |-- 模式: "休息模式"
|    |-- 行为: 放松表情，减少打扰
|    |-- 触发: 视频结束时轻声问候
|
|-- Game:
|    |-- 模式: "娱乐模式"
|    |-- 行为: 兴奋表情，"玩得开心！"
|    |-- 触发: 游戏结束时关心战绩
|
|-- Communication:
|    |-- 模式: "社交模式"
|    |-- 行为: 正常互动
|    |-- 触发: 会议应用 → 静音/最小化
|
|-- Privacy:
|    |-- 模式: "静默模式"
|    |-- 行为: 完全不读取、不打扰
|    |-- 触发: 无
|
\-- Unknown:
     |-- 行为: 询问用户 "你在用什么呀？"
     |-- 学习: 用户回答后记录分类
```

---

## 6. 隐私保护

### 6.1 隐私配置

```rust
/// 隐私配置
/// Privacy configuration
#[pyclass]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct PrivacyConfig {
    /// 黑名单进程 / Blocked processes
    #[pyo3(get, set)]
    pub blocked_processes: Vec<String>,
    
    /// 黑名单窗口标题关键词 / Blocked title keywords
    #[pyo3(get, set)]
    pub blocked_title_keywords: Vec<String>,
    
    /// 黑名单 URL 域名 / Blocked URL domains
    #[pyo3(get, set)]
    pub blocked_domains: Vec<String>,
    
    /// 是否读取密码框 / Read password fields
    #[pyo3(get, set)]
    pub read_password_fields: bool,
    
    /// 文本预览最大长度 / Max text preview length
    #[pyo3(get, set)]
    pub max_text_preview_length: usize,
    
    /// 是否保存截图 / Save screenshots
    #[pyo3(get, set)]
    pub save_screenshots: bool,
    
    /// 截图保留时间 (秒) / Screenshot retention (seconds)
    #[pyo3(get, set)]
    pub screenshot_retention_seconds: u64,
    
    /// 是否启用 OCR / Enable OCR
    #[pyo3(get, set)]
    pub enable_ocr: bool,
    
    /// 敏感信息正则 / Sensitive info patterns
    #[pyo3(get, set)]
    pub sensitive_patterns: Vec<String>,
}

impl Default for PrivacyConfig {
    fn default() -> Self {
        Self {
            blocked_processes: vec![
                "1Password.exe".into(),
                "Bitwarden.exe".into(),
                "KeePass.exe".into(),
            ],
            blocked_title_keywords: vec![
                "银行".into(),
                "Bank".into(),
                "密码".into(),
                "Password".into(),
                "支付".into(),
                "Payment".into(),
            ],
            blocked_domains: vec![
                "bank".into(),
                "alipay.com".into(),
                "paypal.com".into(),
            ],
            read_password_fields: false,
            max_text_preview_length: 200,
            save_screenshots: false,
            screenshot_retention_seconds: 60,
            enable_ocr: true,
            sensitive_patterns: vec![
                r"\d{16,19}".into(),        // 信用卡号
                r"\d{6}(19|20)\d{9}".into(), // 身份证号
                r"\d{11}".into(),            // 手机号
            ],
        }
    }
}
```

### 6.2 隐私过滤器

```rust
/// 隐私过滤器
/// Privacy filter
#[pyclass]
pub struct PrivacyFilter {
    config: PrivacyConfig,
    sensitive_regex: Vec<Regex>,
}

#[pymethods]
impl PrivacyFilter {
    /// 检查窗口是否在黑名单
    /// Check if window is blocked
    pub fn is_blocked(&self, window: &WindowInfo) -> bool;
    
    /// 过滤敏感文本
    /// Filter sensitive text
    pub fn filter_text(&self, text: &str) -> String;
    
    /// 检查是否应跳过 UI 元素
    /// Check if UI element should be skipped
    pub fn should_skip_element(&self, node: &UINode) -> bool;
    
    /// 模糊化窗口标题
    /// Obfuscate window title
    pub fn obfuscate_title(&self, title: &str) -> String;
}
```

### 6.3 数据生命周期

```
[Data Lifecycle]
|
|-- 原始截图:
|    |-- 处理后立即删除
|    |-- 最长保留: 60 秒
|    \-- 不上传云端
|
|-- UI 文本:
|    |-- 会话结束后删除
|    |-- 敏感信息过滤后存储
|    \-- 只保留预览 (max 200 字符)
|
|-- 活动摘要:
|    |-- 保留: 7 天
|    |-- 格式: "用户在 VS Code 编写 Python"
|    \-- 用于: 桌宠上下文理解
|
\-- 使用统计:
     |-- 长期保留
     |-- 完全脱敏
     \-- 格式: {"IDE": 3600, "Browser": 1800} (秒)
```

---

## 7. OCR 集成 (PaddleOCR)

### 7.1 OCR 配置

```python
# src/rainze/screen/ocr.py

class OCRConfig:
    """OCR 配置"""
    
    # 模型路径
    det_model_dir: str = "./models/paddleocr/det"
    rec_model_dir: str = "./models/paddleocr/rec"
    cls_model_dir: str = "./models/paddleocr/cls"
    
    # 语言
    lang: str = "ch"  # 中英文混合
    
    # 性能优化
    use_gpu: bool = True
    gpu_mem: int = 500  # MB
    use_tensorrt: bool = False
    
    # 推理参数
    det_db_thresh: float = 0.3
    det_db_box_thresh: float = 0.5
    rec_batch_num: int = 6
    max_text_length: int = 25
    
    # 并发控制
    enable_mkldnn: bool = True
    cpu_threads: int = 4
```

### 7.2 OCR 接口

```python
class ScreenOCR:
    """
    屏幕 OCR 识别器
    Screen OCR recognizer
    
    基于 PaddleOCR，优化桌面应用场景。
    Based on PaddleOCR, optimized for desktop scenarios.
    """
    
    def __init__(self, config: OCRConfig = None):
        """初始化 OCR（延迟加载模型）"""
        self._ocr = None
        self._config = config or OCRConfig()
        
    async def recognize(
        self,
        image: ImageData,
        *,
        region: Rect = None,
        language: str = None,
    ) -> OCRResult:
        """
        识别图像中的文字
        Recognize text in image
        
        Args:
            image: 图像数据
            region: 识别区域（可选）
            language: 语言（可选，默认中英混合）
            
        Returns:
            OCRResult: 识别结果
        """
        ...
    
    async def recognize_focused_area(
        self,
        image: ImageData,
        focus_point: tuple[int, int],
        expand_ratio: float = 1.5,
    ) -> OCRResult:
        """
        识别焦点区域周围的文字
        Recognize text around focus point
        
        优化策略：只识别焦点周围区域，提升速度
        """
        ...
    
    def preload_model(self) -> None:
        """预加载模型到 GPU"""
        ...
    
    def unload_model(self) -> None:
        """卸载模型释放显存"""
        ...


@dataclass
class OCRResult:
    """OCR 识别结果"""
    
    # 识别的文本块
    text_blocks: list[TextBlock]
    
    # 完整文本（按阅读顺序拼接）
    full_text: str
    
    # 识别耗时 (ms)
    latency_ms: int
    
    # 置信度
    confidence: float


@dataclass  
class TextBlock:
    """文本块"""
    
    # 文本内容
    text: str
    
    # 边界框
    bbox: tuple[int, int, int, int]
    
    # 置信度
    confidence: float
```

### 7.3 性能优化策略

```
[OCR Performance Optimization]
|
|-- 1. 延迟加载:
|    |-- 首次使用时才加载模型
|    |-- 空闲 5 分钟后自动卸载
|    \-- 预计节省 ~500MB 显存
|
|-- 2. 区域裁剪:
|    |-- 只识别焦点窗口
|    |-- 进一步裁剪到焦点元素周围
|    \-- 减少 60-80% 像素处理
|
|-- 3. 分辨率优化:
|    |-- 最大宽度: 1920px
|    |-- 超过时等比缩放
|    \-- 平衡精度与速度
|
|-- 4. 批处理:
|    |-- 多个小区域合并识别
|    |-- rec_batch_num = 6
|    \-- 提升 GPU 利用率
|
|-- 5. 缓存:
|    |-- 相同图像 hash 复用结果
|    |-- 缓存 TTL: 5 秒
|    \-- 避免重复识别
|
\-- 6. 异步:
     |-- 识别在后台线程
     |-- 不阻塞主线程
     \-- 结果通过回调返回
```

### 7.4 无 GPU 完整降级方案

当设备没有 GPU 或 GPU 不可用时，系统提供完整的 CPU fallback 方案：

```
[No-GPU Fallback Strategy]
|
|-- 检测优先级:
|    |-- 1. CUDA GPU (NVIDIA)
|    |-- 2. DirectML (Windows, AMD/Intel GPU)
|    |-- 3. CoreML (macOS, Apple Silicon)
|    |-- 4. OpenVINO (Intel CPU 优化)
|    |-- 5. ONNX Runtime CPU
|    \-- 6. PaddlePaddle CPU (最终兜底)
|
|-- 降级触发条件:
|    |-- GPU 内存不足 (<500MB 可用)
|    |-- CUDA 初始化失败
|    |-- GPU 驱动版本过低
|    |-- 用户配置强制 CPU
|    \-- 移动设备/虚拟机环境
|
|-- CPU 模式优化:
|    |-- 启用 MKL-DNN (Intel CPU)
|    |-- 启用 OpenBLAS (通用)
|    |-- 多线程推理 (cpu_threads=4)
|    |-- 使用轻量模型 (PP-OCRv4-mobile)
|    \-- 更激进的图像缩放
|
\-- 功能完整性:
     |-- ✅ 所有功能可用
     |-- ⚠️ 延迟增加 3-5x
     \-- ⚠️ 建议降低采集频率
```

#### 7.4.1 降级配置

```python
class OCRConfig:
    """OCR 配置 - 支持完整 CPU fallback"""
    
    # GPU 设置
    use_gpu: bool = True              # 优先使用 GPU
    gpu_mem: int = 500                # GPU 显存限制 (MB)
    
    # CPU Fallback 设置
    enable_cpu_fallback: bool = True  # 启用 CPU 降级
    cpu_threads: int = 4              # CPU 线程数
    enable_mkldnn: bool = True        # Intel MKL-DNN 加速
    
    # 降级时使用轻量模型
    use_mobile_model_on_cpu: bool = True
    
    # 降级时的性能调整
    cpu_max_image_width: int = 1280   # CPU 模式最大宽度 (vs GPU 1920)
    cpu_rec_batch_num: int = 2        # CPU 模式批处理数 (vs GPU 6)
    
    # 超时设置
    gpu_init_timeout_seconds: int = 10
    cpu_inference_timeout_seconds: int = 30


class OCRBackend(Enum):
    """OCR 后端类型"""
    CUDA = "cuda"           # NVIDIA GPU
    DIRECTML = "directml"   # Windows DirectML (AMD/Intel)
    COREML = "coreml"       # macOS CoreML
    OPENVINO = "openvino"   # Intel OpenVINO
    ONNX_CPU = "onnx_cpu"   # ONNX Runtime CPU
    PADDLE_CPU = "paddle_cpu"  # PaddlePaddle CPU
```

#### 7.4.2 自动检测与降级

```python
class ScreenOCR:
    """支持自动 GPU/CPU 切换的 OCR"""
    
    def __init__(self, config: OCRConfig = None):
        self._config = config or OCRConfig()
        self._backend: OCRBackend = None
        self._ocr = None
        
    async def _detect_backend(self) -> OCRBackend:
        """
        自动检测最佳后端
        Auto-detect best backend
        
        按优先级尝试，返回第一个可用的后端
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # 1. 尝试 CUDA
        if self._config.use_gpu:
            try:
                import paddle
                if paddle.is_compiled_with_cuda():
                    gpu_available = paddle.device.cuda.device_count() > 0
                    if gpu_available:
                        # 检查显存
                        free_mem = self._get_gpu_free_memory()
                        if free_mem >= self._config.gpu_mem:
                            logger.info(f"使用 CUDA 后端，可用显存: {free_mem}MB")
                            return OCRBackend.CUDA
                        else:
                            logger.warning(f"GPU 显存不足: {free_mem}MB < {self._config.gpu_mem}MB")
            except Exception as e:
                logger.warning(f"CUDA 检测失败: {e}")
        
        # 2. Windows: 尝试 DirectML
        if sys.platform == "win32":
            try:
                # DirectML 支持检测
                if self._check_directml_available():
                    logger.info("使用 DirectML 后端")
                    return OCRBackend.DIRECTML
            except Exception as e:
                logger.debug(f"DirectML 不可用: {e}")
        
        # 3. macOS: 尝试 CoreML
        if sys.platform == "darwin":
            try:
                if self._check_coreml_available():
                    logger.info("使用 CoreML 后端")
                    return OCRBackend.COREML
            except Exception as e:
                logger.debug(f"CoreML 不可用: {e}")
        
        # 4. 尝试 OpenVINO (Intel CPU 优化)
        try:
            import openvino
            logger.info("使用 OpenVINO 后端")
            return OCRBackend.OPENVINO
        except ImportError:
            pass
        
        # 5. 尝试 ONNX Runtime CPU
        try:
            import onnxruntime
            logger.info("使用 ONNX Runtime CPU 后端")
            return OCRBackend.ONNX_CPU
        except ImportError:
            pass
        
        # 6. 最终兜底: PaddlePaddle CPU
        logger.info("使用 PaddlePaddle CPU 后端")
        return OCRBackend.PADDLE_CPU
    
    async def _init_backend(self, backend: OCRBackend):
        """初始化指定后端"""
        from paddleocr import PaddleOCR
        
        # 根据后端选择配置
        if backend == OCRBackend.CUDA:
            self._ocr = PaddleOCR(
                use_gpu=True,
                gpu_mem=self._config.gpu_mem,
                lang=self._config.lang,
            )
        elif backend in (OCRBackend.PADDLE_CPU, OCRBackend.ONNX_CPU):
            # CPU 模式：使用轻量模型 + 优化参数
            model_type = "mobile" if self._config.use_mobile_model_on_cpu else "server"
            self._ocr = PaddleOCR(
                use_gpu=False,
                enable_mkldnn=self._config.enable_mkldnn,
                cpu_threads=self._config.cpu_threads,
                lang=self._config.lang,
                det_model_dir=f"./models/paddleocr/{model_type}/det",
                rec_model_dir=f"./models/paddleocr/{model_type}/rec",
            )
        # ... 其他后端初始化
        
        self._backend = backend
    
    def get_current_backend(self) -> OCRBackend:
        """获取当前使用的后端"""
        return self._backend
    
    def is_using_gpu(self) -> bool:
        """是否正在使用 GPU"""
        return self._backend in (OCRBackend.CUDA, OCRBackend.DIRECTML, OCRBackend.COREML)
```

#### 7.4.3 CPU 模式性能对比

| 后端 | 设备 | 1080p 延迟 | 内存占用 | 精度 |
|------|------|-----------|---------|------|
| **CUDA** | NVIDIA GPU | ~200ms | ~500MB VRAM | 100% |
| **DirectML** | AMD/Intel GPU | ~300ms | ~400MB VRAM | 100% |
| **CoreML** | Apple Silicon | ~250ms | ~300MB | 100% |
| **OpenVINO** | Intel CPU | ~800ms | ~200MB RAM | 99% |
| **ONNX CPU** | Any CPU | ~1200ms | ~300MB RAM | 99% |
| **Paddle CPU** | Any CPU | ~1500ms | ~400MB RAM | 99% |

#### 7.4.4 CPU 模式自适应策略

```python
class AdaptiveOCR:
    """
    自适应 OCR - 根据设备性能动态调整
    Adaptive OCR - Dynamically adjust based on device performance
    """
    
    def __init__(self):
        self._ocr = ScreenOCR()
        self._performance_profile: str = "auto"
        
    async def initialize(self):
        """初始化并检测设备性能"""
        await self._ocr._detect_backend()
        
        # 根据后端自动调整策略
        if not self._ocr.is_using_gpu():
            self._apply_cpu_optimizations()
    
    def _apply_cpu_optimizations(self):
        """应用 CPU 模式优化"""
        # 1. 降低采集频率
        self._collection_interval_multiplier = 2.0  # 2x 间隔
        
        # 2. 更激进的图像缩放
        self._max_image_width = 1280  # vs 1920
        
        # 3. 减少 OCR 触发场景
        self._ocr_trigger_threshold = "high"  # 只在必要时触发
        
        # 4. 增加缓存时间
        self._cache_ttl_seconds = 15  # vs 5
        
        # 5. 异步预热
        self._enable_async_preload = True
    
    async def recognize_adaptive(
        self,
        image: ImageData,
        urgency: str = "normal",  # "low" | "normal" | "high"
    ) -> OCRResult:
        """
        自适应识别
        
        Args:
            image: 图像数据
            urgency: 紧急程度
                - "low": 可延迟，优先省资源
                - "normal": 平衡
                - "high": 用户主动请求，优先速度
        """
        # CPU 模式下，低紧急度请求延迟处理
        if not self._ocr.is_using_gpu() and urgency == "low":
            # 加入队列，批量处理
            return await self._queue_for_batch(image)
        
        # 正常处理
        return await self._ocr.recognize(image)
```

#### 7.4.5 无 GPU 时的功能调整建议

```
[CPU-Only Mode Recommendations]
|
|-- UI Automation 优先:
|    |-- CPU 模式下优先使用 UI Automation 获取文本
|    |-- 只在 UI Automation 失败时才启用 OCR
|    \-- 减少 80% 的 OCR 调用
|
|-- 降低采集频率:
|    |-- 窗口切换: 保持实时
|    |-- 空闲检测: 60秒 → 120秒
|    |-- 心跳: 5分钟 → 10分钟
|    \-- 异常检测: 保持
|
|-- 智能触发:
|    |-- 只在用户主动询问时进行完整 OCR
|    |-- 自动检测场景：浏览器/非原生应用 才启用 OCR
|    \-- 原生应用优先 UI Automation
|
|-- 用户提示:
|    |-- 首次启动时提示 "检测到 CPU 模式，部分功能响应较慢"
|    |-- 设置中显示当前后端
|    \-- 提供 "GPU 加速" 安装引导
|
\-- 降级保证:
     |-- 所有核心功能可用
     |-- 不影响桌宠基本交互
     \-- 只是响应速度下降
```

---

## 8. 目录结构

### 8.1 Rust 模块

```
rainze_core/src/
├── lib.rs                      # PyO3 模块入口
├── screen_reader/
│   ├── mod.rs                  # 模块入口 + ScreenReader PyO3 类
│   ├── traits.rs               # PlatformScreenReader trait
│   ├── types.rs                # 跨平台数据类型
│   ├── app_classifier.rs       # 应用分类器
│   ├── privacy_filter.rs       # 隐私过滤器
│   │
│   ├── windows/                # Windows 实现
│   │   ├── mod.rs              # Windows 入口
│   │   ├── window_info.rs      # GetForegroundWindow 等
│   │   ├── automation.rs       # UI Automation
│   │   ├── capture.rs          # Graphics Capture API
│   │   └── hooks.rs            # SetWinEventHook
│   │
│   └── macos/                  # macOS 实现
│       ├── mod.rs              # macOS 入口
│       ├── window_info.rs      # NSWorkspace
│       ├── accessibility.rs    # AXUIElement
│       ├── capture.rs          # CGWindowListCreateImage
│       └── observer.rs         # NSWorkspace.notification
│
└── utils/
    └── image.rs                # 图像处理工具
```

### 8.2 Python 模块

```
src/rainze/screen/
├── __init__.py
├── reader.py                   # ScreenReader Python 封装
├── context.py                  # ScreenContext 数据类
├── triggers.py                 # 采集触发器
├── analyzer.py                 # 内容分析器
├── ocr.py                      # PaddleOCR 集成
└── privacy.py                  # 隐私配置管理
```

---

## 9. 配置文件

### 9.1 screen_reader_settings.json

```json
{
  "$schema": "screen_reader_settings.schema.json",
  "version": "1.0.0",
  
  "collection": {
    "window_change_debounce_ms": 300,
    "idle_threshold_seconds": 30,
    "heartbeat_interval_seconds": 300,
    "max_ui_tree_depth": 5,
    "text_preview_max_length": 200
  },
  
  "triggers": {
    "window_change": {
      "enabled": true,
      "collect_level": 2
    },
    "user_idle": {
      "enabled": true,
      "threshold_seconds": 30,
      "collect_level": 3
    },
    "heartbeat": {
      "enabled": true,
      "interval_seconds": 300,
      "collect_level": 2
    },
    "anomaly": {
      "enabled": true,
      "same_window_threshold_minutes": 60,
      "frequent_undo_threshold": 10
    }
  },
  
  "app_classifier": {
    "rules_file": "./config/app_rules.json",
    "learn_from_user": true
  },
  
  "ocr": {
    "enabled": true,
    "provider": "paddleocr",
    "lang": "ch",
    
    "gpu": {
      "use_gpu": true,
      "gpu_mem_mb": 500,
      "use_tensorrt": false
    },
    
    "cpu_fallback": {
      "enabled": true,
      "use_mobile_model": true,
      "cpu_threads": 4,
      "enable_mkldnn": true,
      "max_image_width": 1280
    },
    
    "backend_priority": [
      "cuda",
      "directml",
      "coreml",
      "openvino",
      "onnx_cpu",
      "paddle_cpu"
    ],
    
    "lazy_load": true,
    "unload_after_idle_seconds": 300,
    "max_image_width_gpu": 1920,
    "cache_ttl_seconds": 5,
    "cache_ttl_seconds_cpu": 15
  },
  
  "cpu_mode_adjustments": {
    "collection_interval_multiplier": 2.0,
    "idle_threshold_multiplier": 2.0,
    "heartbeat_interval_multiplier": 2.0,
    "prefer_ui_automation": true,
    "ocr_trigger_threshold": "high"
  },
  
  "privacy": {
    "blocked_processes": [
      "1Password.exe",
      "Bitwarden.exe",
      "KeePass.exe"
    ],
    "blocked_title_keywords": [
      "银行", "Bank", "密码", "Password"
    ],
    "blocked_domains": [
      "bank", "alipay.com", "paypal.com"
    ],
    "read_password_fields": false,
    "save_screenshots": false,
    "screenshot_retention_seconds": 60,
    "filter_sensitive_info": true
  },
  
  "performance": {
    "capture_method": "graphics_capture",
    "capture_fallback": "gdi",
    "ui_automation_timeout_ms": 100,
    "cache_window_info_ms": 500
  }
}
```

---

## 10. 使用示例

### 10.1 基础使用

```python
from rainze_core import ScreenReader
from rainze.screen import ScreenContext, ScreenOCR

# 创建屏幕读取器
reader = ScreenReader()

# 检查权限 (macOS)
permissions = reader.check_permissions()
if not permissions.all_granted:
    reader.request_permissions()

# 快速采集
context = reader.collect_quick()
print(f"当前应用: {context.window.process_name}")
print(f"应用分类: {context.window.app_category}")
print(f"活动提示: {context.activity_hint}")

# 标准采集 (含 UI 树)
context = reader.collect_standard()
if context.focus_element:
    print(f"焦点元素: {context.focus_element.element_type}")
    print(f"文本预览: {context.focus_element.text_preview}")

# 完整采集 (含截图)
context, image = reader.collect_full()

# OCR 识别
ocr = ScreenOCR()
result = await ocr.recognize(image)
print(f"识别文本: {result.full_text[:100]}...")
```

### 10.2 事件监听

```python
from rainze_core import ScreenReader, ScreenEvent

reader = ScreenReader()

def on_screen_event(event: ScreenEvent):
    if event.type == "WindowFocusChanged":
        print(f"切换到: {event.window.process_name}")
        if event.window.app_category == "Privacy":
            print("检测到隐私应用，暂停监控")
    
    elif event.type == "UserIdleStart":
        print(f"用户空闲 {event.idle_seconds} 秒")
    
    elif event.type == "UserIdleEnd":
        print(f"用户恢复活动，空闲了 {event.idle_duration} 秒")

# 开始监听
handle = reader.start_event_listener(on_screen_event)

# ... 应用运行 ...

# 停止监听
reader.stop_event_listener(handle)
```

### 10.3 与 UCM 集成

```python
# src/rainze/agent/context_manager.py

class UnifiedContextManager:
    def __init__(self):
        self._screen_reader = ScreenReader()
        self._screen_ocr = ScreenOCR()
        
    async def _get_screen_context(
        self,
        level: int = 2,
        include_screenshot: bool = False,
    ) -> dict:
        """
        获取屏幕上下文，注入到 LLM prompt
        """
        if level <= 2:
            context = self._screen_reader.collect_quick()
        else:
            if include_screenshot:
                context, image = self._screen_reader.collect_full()
                ocr_result = await self._screen_ocr.recognize(image)
                context.ocr_text = ocr_result.full_text
            else:
                context = self._screen_reader.collect_standard()
        
        return {
            "current_app": context.window.process_name,
            "app_category": context.window.app_category.name,
            "window_title": context.window.title,
            "activity_hint": context.activity_hint,
            "focus_text": context.focus_element.text_preview if context.focus_element else None,
            "ocr_text": getattr(context, "ocr_text", None),
        }
    
    async def process_interaction(self, request: InteractionRequest):
        # 获取屏幕上下文
        screen_context = await self._get_screen_context(level=2)
        
        # 注入到处理流程
        context = {
            "screen": screen_context,
            **other_context,
        }
        
        # ... 继续处理
```

---

## 11. 测试要点

### 11.1 单元测试

| 测试项 | 测试内容 | 预期结果 |
|--------|----------|----------|
| 窗口信息获取 | 获取前台窗口标题、进程名 | 信息正确 |
| 应用分类 | 各类应用正确分类 | IDE/Browser/Office 等 |
| UI 树遍历 | 获取焦点元素及其父级 | 树结构正确 |
| 截图功能 | 截取前台窗口 | 图像尺寸正确 |
| 隐私过滤 | 银行应用检测 | 正确跳过 |
| 敏感信息过滤 | 信用卡号、手机号 | 正确遮蔽 |
| OCR 识别 | 中英文混合文本 | 准确率 >95% |
| 事件监听 | 窗口切换事件 | 正确触发 |

### 11.2 性能测试

| 测试项 | 目标 | 测试方法 |
|--------|------|----------|
| L1 采集延迟 | <10ms | 连续 1000 次采集取平均 |
| L2 采集延迟 | <20ms | 连续 1000 次采集取平均 |
| L3 采集延迟 | <200ms | 含 UI 树遍历 |
| 截图延迟 | <50ms | Graphics Capture |
| OCR 延迟 | <300ms | 1080p 窗口，GPU |
| 内存占用 | <100MB | 不含 OCR 模型 |
| OCR 显存 | <500MB | PaddleOCR |

### 11.3 跨平台测试

| 平台 | 测试项 | 验收标准 |
|------|--------|----------|
| Windows 10 | 全功能 | 所有功能正常 |
| Windows 11 | 全功能 | 所有功能正常 |
| macOS 12+ | 全功能 | 权限引导正确 |
| macOS (无权限) | 降级 | 优雅提示用户 |

---

## 12. 依赖关系

### 12.1 外部依赖 (Rust)

| 依赖 | 版本 | 用途 | 平台 |
|------|------|------|------|
| windows | 0.58 | Windows API | Windows |
| objc2 | 0.5 | Objective-C 绑定 | macOS |
| objc2-app-kit | 0.2 | AppKit 绑定 | macOS |
| core-graphics | 0.24 | Core Graphics | macOS |
| image | 0.25 | 图像处理 | 跨平台 |
| png | 0.17 | PNG 编解码 | 跨平台 |

### 12.2 外部依赖 (Python)

| 依赖 | 版本 | 用途 |
|------|------|------|
| paddlepaddle-gpu | 2.6+ | PaddlePaddle GPU |
| paddleocr | 2.7+ | OCR 引擎 |
| numpy | 1.24+ | 数组处理 |
| pillow | 10.0+ | 图像处理 |

### 12.3 内部依赖

```
ScreenReader
├── 被依赖:
│   ├── MOD-Agent (UCM 上下文增强)
│   ├── MOD-State (用户活动状态)
│   └── MOD-Features (主动关怀触发)
│
└── 依赖:
    └── MOD-RustCore (基础设施)
```

---

## 13. 版本历史

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| v1.0.0 | 2025-12-31 | 初始版本：跨平台屏幕读取、OCR 集成、隐私保护 |

---

## 附录

### A. Windows Graphics Capture 参考

```rust
// 使用 windows-rs 的 Graphics Capture API
use windows::{
    Graphics::Capture::*,
    Graphics::DirectX::Direct3D11::*,
    Win32::Graphics::Direct3D11::*,
};

// 关键步骤:
// 1. 创建 D3D11 设备
// 2. 创建 Direct3D11CaptureFramePool
// 3. 创建 GraphicsCaptureSession
// 4. 开始捕获，获取帧
// 5. 从 GPU 纹理复制到 CPU
```

### B. macOS Accessibility API 参考

```rust
// 使用 objc2 的 Accessibility API
use objc2_foundation::*;

// 关键函数:
// - AXIsProcessTrusted() - 检查权限
// - AXUIElementCreateSystemWide() - 创建系统级元素
// - AXUIElementCopyAttributeValue() - 获取属性值
// - kAXFocusedUIElementAttribute - 获取焦点元素
```

### C. PaddleOCR 模型下载

```bash
# 下载检测模型
wget https://paddleocr.bj.bcebos.com/PP-OCRv4/chinese/ch_PP-OCRv4_det_infer.tar

# 下载识别模型  
wget https://paddleocr.bj.bcebos.com/PP-OCRv4/chinese/ch_PP-OCRv4_rec_infer.tar

# 下载方向分类模型
wget https://paddleocr.bj.bcebos.com/dygraph_v2.0/ch/ch_ppocr_mobile_v2.0_cls_infer.tar
```

---

> **文档生成**: Claude Sonnet 4
> **审核状态**: 待技术审核
> **下次更新**: 随实现进度同步更新
