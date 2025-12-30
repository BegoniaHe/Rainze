# Rainze 模块设计文档索引

> **版本**: v1.1.0
> **创建时间**: 2025-12-29
> **最后更新**: 2025-12-30
> **关联文档**: [PRD-Rainze.md](../PRD-Rainze.md) v3.1.0 | [TECH-Rainze.md](../../techstacks/TECH-Rainze.md) v1.0.1

---

## 模块架构总览

```
┌──────────────────────────────────────────────────────────────────────────┐
│                           应用层 (Application)                           │
│  ┌────────────┬────────────┬────────────┬────────────┬────────────────┐  │
│  │   GUI      │  Features  │   Plugins  │   Tools    │   Animation    │  │
│  │  图形界面  │  功能模块  │  插件系统  │  工具调用  │    动画系统    │  │
│  └────────────┴────────────┴────────────┴────────────┴────────────────┘  │
├──────────────────────────────────────────────────────────────────────────┤
│                           业务层 (Business)                              │
│  ┌────────────┬────────────┬────────────┬────────────────────────────┐   │
│  │    AI      │   Memory   │   State    │         Agent              │   │
│  │  AI服务    │  记忆系统  │  状态管理  │      自主循环系统          │   │
│  └────────────┴────────────┴────────────┴────────────────────────────┘   │
├──────────────────────────────────────────────────────────────────────────┤
│                           基础层 (Infrastructure)                        │
│  ┌────────────┬────────────┬────────────────────────────────────────┐    │
│  │   Core     │  Storage   │            RustCore                    │    │
│  │  核心基础  │  数据持久化│         Rust性能模块                   │    │
│  └────────────┴────────────┴────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 模块清单

### 基础层 (Infrastructure)

| 模块 | 文档 | 职责 | 优先级 |
|------|------|------|--------|
| **Core** | [MOD-Core.md](./MOD-Core.md) | 事件总线、配置管理、应用生命周期 | P0 |
| **Storage** | [MOD-Storage.md](./MOD-Storage.md) | SQLite、FAISS、JSON持久化 | P0 |
| **RustCore** | [MOD-RustCore.md](./MOD-RustCore.md) | Rust性能模块 (检索/监控/向量化) | P1 |

### 业务层 (Business)

| 模块 | 文档 | 职责 | 优先级 |
|------|------|------|--------|
| **AI** | [MOD-AI.md](./MOD-AI.md) | Prompt构建、LLM调用、响应策略 | P0 |
| **Memory** | [MOD-Memory.md](./MOD-Memory.md) | 3层记忆架构、检索、向量化 | P1 |
| **State** | [MOD-State.md](./MOD-State.md) | 状态机、心情、能量、好感度 | P0 |
| **Agent** | [MOD-Agent.md](./MOD-Agent.md) | 自主循环、行为计划、调度 | P1 |

### 应用层 (Application)

| 模块 | 文档 | 职责 | 优先级 |
|------|------|------|--------|
| **GUI** | [MOD-GUI.md](./MOD-GUI.md) | PySide6窗口、透明、交互 | P0 |
| **Animation** | [MOD-Animation.md](./MOD-Animation.md) | 6层动画、表情、口型 | P0 |
| **Tools** | [MOD-Tools.md](./MOD-Tools.md) | ReAct工具调用 | P1 |
| **Plugins** | [MOD-Plugins.md](./MOD-Plugins.md) | 插件加载、API、沙箱 | P2 |
| **Features** | [MOD-Features.md](./MOD-Features.md) | 26基础功能+7进阶功能 | P1-P3 |

---

## 模块依赖矩阵

| 模块 | 依赖 |
|------|------|
| Core | (无) |
| Storage | Core |
| RustCore | (无，独立Rust crate) |
| AI | Core (含contracts), Storage, RustCore |
| Memory | Core, Storage, RustCore, AI |
| State | Core (含contracts), Storage |
| Agent | Core (含contracts), AI, Memory, State |
| GUI | Core, State, Animation |
| Animation | Core, State |
| Tools | Core, AI, State |
| Plugins | Core (含contracts), AI, State, Tools |
| Features | Core (含contracts), State, AI, GUI, Agent |

---

## 跨模块契约 ⭐新增 (v1.1.0)

> **参考**: PRD §0.15 跨模块契约规范

所有模块必须遵循 `core.contracts` 中定义的统一类型：

| 契约 | 位置 | 使用模块 |
|------|------|----------|
| EmotionTag | `core.contracts.emotion` | AI, State, Animation |
| SceneType, ResponseTier | `core.contracts.scene` | AI, Agent, Features |
| InteractionRequest/Response | `core.contracts.interaction` | Agent (UCM), Features, Tools, Plugins |
| IUnifiedContextManager | `core.contracts.ucm` | Agent, Features, Tools, Plugins |
| IRustMemorySearch | `core.contracts.rust_bridge` | Memory, RustCore |
| IRustSystemMonitor | `core.contracts.rust_bridge` | State, Features (system_monitor) |
| IRustTextProcess | `core.contracts.rust_bridge` | Memory, AI |
| Tracer, TraceSpan | `core.observability` | 所有模块 |

**规则**:
- ⛔ 禁止在其他模块重复定义相同结构
- ✅ 所有模块必须从 `core.contracts` 导入公共类型
- ✅ 契约变更需同步更新所有引用模块
- ✅ 所有用户交互必须通过 UCM (IUnifiedContextManager) 处理

### 配置文件契约

| 配置文件 | 位置 | 加载模块 | 说明 |
|----------|------|----------|------|
| scene_tier_mapping.json | `config/` | `core.contracts.scene` | 场景-Tier映射 |
| api_settings.json | `config/` | AI | LLM API配置 |
| state_settings.json | `config/` | State | 状态系统配置 |
| memory_settings.json | `config/` | Memory | 记忆系统配置 |
| animation_settings.json | `config/` | Animation | 动画系统配置 |
| gui_settings.json | `config/` | GUI | GUI配置 |

### UCM 交互入口规范

所有功能模块（Features/Tools/Plugins）必须通过 UCM 处理用户交互：

```python
# ✅ 正确：通过UCM处理
from rainze.core.contracts.interaction import InteractionRequest, InteractionSource

request = InteractionRequest(
    request_id=uuid4().hex,
    source=InteractionSource.CHAT_INPUT,
    timestamp=datetime.now(),
    payload={"text": user_input}
)
response = await ucm.process_interaction(request)

# ⛔ 错误：绕过UCM直接调用
response = await ai_service.generate_response(user_input)  # 禁止！
```

---

## 开发阶段规划

### Phase 1: MVP (4-6周)

- Core, Storage, State, GUI, Animation (基础)
- AI (Tier1/2模板响应)

### Phase 2: 核心功能 (4-6周)

- AI (Tier3 LLM生成)
- Memory, Agent
- Tools
- Features (整点报时、专注、背包、好感度)

### Phase 3: 完善功能 (4-6周)

- RustCore
- Features (全部)
- Plugins

---

## 命名规范

- **模块文档**: `MOD-{ModuleName}.md`
- **Python包**: `rainze.{module_name}`
- **Rust crate**: `rainze_core`
- **配置文件**: `{feature}_settings.json`
