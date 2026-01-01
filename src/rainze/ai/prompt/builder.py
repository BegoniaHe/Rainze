"""
增量式 Prompt 构建器 / Incremental Prompt Builder

实现完整的 Prompt 构建流程，支持三层记忆架构和缓存机制。
Implements complete prompt building process with three-tier memory architecture and caching.

Reference:
    - PRD §0.5: AI提示词构建流程 (增量式 + 索引式)
    - PRD §0.5a: 统一上下文管理器

Author: Rainze Team
Created: 2026-01-01
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Optional

if TYPE_CHECKING:
    from rainze.core.contracts.interaction import InteractionRequest
    from rainze.core.contracts.scene import SceneType
    from rainze.memory.layers.identity import IdentityLayer
    from rainze.memory.layers.working import WorkingMemory

from rainze.ai.prompt.cache import ContextCache
from rainze.ai.prompt.config import DEFAULT_PROMPT_CONFIG, PromptBuilderConfig


class PromptBuilder:
    """
    增量式 Prompt 构建器 / Incremental Prompt Builder
    
    实现 PRD §0.5 定义的增量式 Prompt 构建流程：
    Implements incremental prompt building process defined in PRD §0.5:
    
    1. 静态上下文 (Static Context): 启动时加载，缓存常驻
       - Layer 1: Identity Layer (system_prompt + user_profile)
       - 触发刷新：文件变更时热重载
    
    2. 半静态上下文 (Semi-Static Context): 状态变化时刷新
       - Layer 3: Facts 摘要 (用户偏好 + 行为模式)
       - 触发刷新：记忆整合后、偏好变化时
       - TTL: 10分钟
    
    3. 动态上下文 (Dynamic Context): 每次生成时刷新
       - Layer 2: Working Memory (对话历史 + 实时状态 + 环境感知)
       - 触发刷新：每次构建前必刷新
    
    4. 缓存检索 (Cached Retrieval): 相似查询复用
       - Layer 3: Episodes (语义检索结果)
       - 缓存键: hash(event_type + context_keywords)
       - TTL: 5分钟
    
    Attributes:
        config: Prompt 构建器配置 / Prompt builder configuration
        cache: 上下文缓存管理器 / Context cache manager
        identity_layer: 身份层引用 / Identity layer reference
        working_memory: 工作记忆引用 / Working memory reference
    
    Example:
        >>> builder = PromptBuilder(config, identity_layer, working_memory)
        >>> prompt = await builder.build(
        ...     scene_type=SceneType.COMPLEX,
        ...     interaction_request=request,
        ...     memory_hints=["工作", "压力"]
        ... )
        
    Reference:
        PRD §0.5: 增量式 Prompt 构建流程
    """
    
    def __init__(
        self,
        config: Optional[PromptBuilderConfig] = None,
        identity_layer: Optional[IdentityLayer] = None,
        working_memory: Optional[WorkingMemory] = None,
    ) -> None:
        """
        初始化 Prompt 构建器 / Initialize prompt builder
        
        Args:
            config: 构建器配置，None 则使用默认配置 / Builder config, None for default
            identity_layer: 身份层实例 / Identity layer instance
            working_memory: 工作记忆实例 / Working memory instance
        """
        self.config = config or DEFAULT_PROMPT_CONFIG
        self.cache = ContextCache()
        self.identity_layer = identity_layer
        self.working_memory = working_memory
        
        # Token 计数器 (用于预算管理) / Token counter (for budget management)
        self._token_counts: Dict[str, int] = {}
    
    async def build(
        self,
        scene_type: SceneType,
        interaction_request: InteractionRequest,
        memory_hints: Optional[List[str]] = None,
    ) -> str:
        """
        构建完整 Prompt / Build complete prompt
        
        主构建流程，按照 PRD §0.5 定义的步骤组装 Prompt：
        Main building process following PRD §0.5 steps:
        
        1. Step 1: 检查静态上下文缓存 (Layer 1)
        2. Step 2: 检查状态变化，刷新半静态上下文 (Layer 3 Facts)
        3. Step 3: 刷新环境层 (必执行)
        4. Step 4: 记忆检索 (智能缓存)
        5. Step 5: 组装 Prompt
        6. Step 6: Token 预算检查与压缩
        
        Args:
            scene_type: 场景类型 (SIMPLE/MEDIUM/COMPLEX) / Scene type
            interaction_request: 交互请求 / Interaction request
            memory_hints: 记忆检索提示词 (可选) / Memory retrieval hints (optional)
        
        Returns:
            完整的 Prompt 字符串 / Complete prompt string
        
        Raises:
            RuntimeError: 当依赖的 Layer 未初始化时 / When dependent layers not initialized
        
        Example:
            >>> from rainze.core.contracts.scene import SceneType
            >>> prompt = await builder.build(
            ...     scene_type=SceneType.COMPLEX,
            ...     interaction_request=request,
            ...     memory_hints=["工作", "压力"]
            ... )
        
        Reference:
            PRD §0.5: Prompt Assembly Pipeline
        """
        # 验证依赖 / Validate dependencies
        if self.identity_layer is None:
            raise RuntimeError("IdentityLayer not initialized")
        if self.working_memory is None:
            raise RuntimeError("WorkingMemory not initialized")
        
        # 重置 Token 计数 / Reset token counts
        self._token_counts.clear()
        
        # Step 1: 加载静态上下文 (Layer 1) / Load static context
        identity_context = await self._load_static_context()
        
        # Step 2: 加载半静态上下文 (Layer 3 Facts) / Load semi-static context
        facts_summary = await self._load_semi_static_context()
        
        # Step 3: 刷新动态上下文 (Layer 2) / Refresh dynamic context
        working_context = await self._refresh_dynamic_context(interaction_request)
        
        # Step 4: 记忆检索 (Layer 3 Episodes) / Memory retrieval
        memory_context = await self._retrieve_memories(
            scene_type=scene_type,
            interaction_request=interaction_request,
            memory_hints=memory_hints,
        )
        
        # Step 5: 组装 Prompt / Assemble prompt
        prompt = self._assemble_prompt(
            identity_context=identity_context,
            working_context=working_context,
            facts_summary=facts_summary,
            memory_context=memory_context,
            interaction_request=interaction_request,
        )
        
        # Step 6: Token 预算检查 / Token budget check
        prompt = self._check_and_compress(prompt)
        
        return prompt
    
    async def _load_static_context(self) -> str:
        """
        加载静态上下文 (Layer 1: Identity Layer)
        Load static context (Layer 1: Identity Layer)
        
        从缓存或 IdentityLayer 加载角色设定和用户资料。
        Load character settings and user profile from cache or IdentityLayer.
        
        Returns:
            格式化的身份上下文 / Formatted identity context
        
        Reference:
            PRD §0.5: Step 1 - 检查静态上下文缓存
        """
        # 尝试从缓存获取 / Try to get from cache
        cached = self.cache.get_static("identity")
        if cached is not None:
            return cached
        
        # 未命中，从 IdentityLayer 加载 / Cache miss, load from IdentityLayer
        if self.identity_layer is None:
            raise RuntimeError("IdentityLayer not initialized")
        
        identity_context = self.identity_layer.get_context()
        
        # 存入缓存 (永不过期) / Cache it (never expire)
        self.cache.set_static(
            key="identity",
            content=identity_context,
            ttl=0,  # 永不过期 / Never expire
        )
        
        return identity_context
    
    async def _load_semi_static_context(self) -> str:
        """
        加载半静态上下文 (Layer 3: Facts 摘要)
        Load semi-static context (Layer 3: Facts summary)
        
        从缓存或数据库加载用户偏好和行为模式摘要。
        Load user preferences and behavior patterns summary from cache or database.
        
        Returns:
            格式化的 Facts 摘要 / Formatted facts summary
        
        Reference:
            PRD §0.5: Step 2 - 检查状态变化
        """
        # 尝试从缓存获取 / Try to get from cache
        cached = self.cache.get_semi_static("facts_summary")
        if cached is not None:
            return cached
        
        # 未命中，生成摘要 / Cache miss, generate summary
        # TODO: 从数据库查询 user_preferences 和 behavior_patterns
        # TODO: Query user_preferences and behavior_patterns from database
        
        # 占位实现 / Placeholder implementation
        facts_summary = self._generate_facts_summary([])
        
        # 存入缓存 (TTL 10分钟) / Cache it (TTL 10 minutes)
        self.cache.set_semi_static(
            key="facts_summary",
            content=facts_summary,
            ttl=self.config.semi_static_cache_ttl,
        )
        
        return facts_summary
    
    async def _refresh_dynamic_context(
        self,
        interaction_request: InteractionRequest,
    ) -> str:
        """
        刷新动态上下文 (Layer 2: Working Memory)
        Refresh dynamic context (Layer 2: Working Memory)
        
        每次必刷新，包含对话历史、实时状态、环境感知。
        Always refresh, includes conversation history, real-time state, environment.
        
        Args:
            interaction_request: 交互请求 / Interaction request
        
        Returns:
            格式化的工作记忆上下文 / Formatted working memory context
        
        Reference:
            PRD §0.5: Step 3 - 刷新环境层 (必执行)
        """
        if self.working_memory is None:
            raise RuntimeError("WorkingMemory not initialized")
        
        # 获取对话历史 / Get conversation history
        conversation_history = self.working_memory.get_recent_conversations(limit=10)
        
        # 获取实时状态 / Get real-time state
        realtime_state = self.working_memory.get_state_snapshot()
        
        # 获取环境感知 / Get environment context
        environment = await self._get_environment_context()
        
        # 格式化上下文 / Format context
        context_parts = ["{Layer 2: Working Memory}"]
        
        # 添加对话历史 / Add conversation history
        if conversation_history:
            context_parts.append("[对话历史 / Conversation History]")
            for conv in conversation_history:
                context_parts.append(f"- {conv}")
        
        # 添加实时状态 / Add real-time state
        context_parts.append(f"[实时状态 / Real-time State]\n{realtime_state}")
        
        # 添加环境感知 / Add environment
        context_parts.append(f"[环境感知 / Environment]\n{environment}")
        
        return "\n".join(context_parts)
    
    async def _retrieve_memories(
        self,
        scene_type: SceneType,
        interaction_request: InteractionRequest,
        memory_hints: Optional[List[str]] = None,
    ) -> str:
        """
        记忆检索 (Layer 3: Episodes)
        Memory retrieval (Layer 3: Episodes)
        
        根据场景类型决定是否检索长期记忆。支持智能缓存。
        Decide whether to retrieve long-term memory based on scene type. Supports smart caching.
        
        Args:
            scene_type: 场景类型 / Scene type
            interaction_request: 交互请求 / Interaction request
            memory_hints: 记忆检索提示词 / Memory retrieval hints
        
        Returns:
            格式化的记忆上下文 / Formatted memory context
        
        Reference:
            PRD §0.5: Step 4 - 记忆检索 (智能缓存)
            PRD §0.5: 记忆协调器 - 场景分类
        """
        from rainze.core.contracts.scene import SceneType as ST
        
        # 根据场景决定是否检索 / Decide whether to retrieve based on scene
        if scene_type == ST.SIMPLE:
            # SIMPLE 场景跳过检索 / Skip retrieval for SIMPLE scene
            return ""
        
        # 生成缓存键 / Generate cache key
        event_type = interaction_request.interaction_type
        context_keywords = " ".join(memory_hints or [])
        
        # 尝试从缓存获取 / Try to get from cache
        if self.config.enable_cache:
            cached = self.cache.get_retrieval(event_type, context_keywords)
            if cached is not None:
                return cached
        
        # 未命中，执行检索 / Cache miss, perform retrieval
        # TODO: 调用 HybridRetriever 进行混合检索
        # TODO: Call HybridRetriever for hybrid retrieval
        
        # 占位实现 / Placeholder implementation
        memory_context = self._generate_memory_context([])
        
        # 存入缓存 / Cache it
        if self.config.enable_cache:
            self.cache.set_retrieval(
                event_type=event_type,
                context_keywords=context_keywords,
                content=memory_context,
                ttl=300,  # 5分钟 / 5 minutes
            )
        
        return memory_context
    
    async def _get_environment_context(self) -> str:
        """
        获取环境感知上下文 / Get environment context
        
        包括时间、天气、系统状态、用户活动等。
        Includes time, weather, system status, user activity, etc.
        
        Returns:
            格式化的环境上下文 / Formatted environment context
        
        Reference:
            PRD §0.2: 环境感知 (Context Sensing)
        """
        import datetime
        
        # 获取当前时间 / Get current time
        now = datetime.datetime.now()
        time_str = now.strftime("%H:%M %A")
        
        # TODO: 获取天气 (缓存30分钟) / Get weather (cache 30min)
        # TODO: 获取系统状态 (CPU/内存) / Get system status (CPU/memory)
        # TODO: 获取用户活动 (全屏/会议检测) / Get user activity (fullscreen/meeting detection)
        
        # 占位实现 / Placeholder implementation
        environment_parts = [
            f"时间: {time_str}",
            "天气: [待实现]",
            "系统状态: [待实现]",
        ]
        
        return "\n".join(environment_parts)
    
    def _assemble_prompt(
        self,
        identity_context: str,
        working_context: str,
        facts_summary: str,
        memory_context: str,
        interaction_request: InteractionRequest,
    ) -> str:
        """
        组装完整 Prompt / Assemble complete prompt
        
        按照 PRD 定义的结构组装 Prompt。
        Assemble prompt following PRD-defined structure.
        
        Args:
            identity_context: 身份上下文 / Identity context
            working_context: 工作记忆上下文 / Working memory context
            facts_summary: Facts 摘要 / Facts summary
            memory_context: 记忆上下文 / Memory context
            interaction_request: 交互请求 / Interaction request
        
        Returns:
            完整的 Prompt 字符串 / Complete prompt string
        
        Reference:
            PRD §0.5: Prompt 注入示例
        """
        prompt_parts = []
        
        # Layer 1: Identity
        prompt_parts.append(identity_context)
        prompt_parts.append("")
        
        # Layer 2: Working Memory
        prompt_parts.append(working_context)
        prompt_parts.append("")
        
        # Layer 3: Facts Summary
        if facts_summary:
            prompt_parts.append("{Layer 3: Long-term Memory - Facts 摘要}")
            prompt_parts.append(facts_summary)
            prompt_parts.append("")
        
        # Layer 3: Memory Context (Episodes)
        if memory_context:
            prompt_parts.append(memory_context)
            prompt_parts.append("")
        
        # System Instructions
        prompt_parts.append("{系统指令 / Instructions}")
        prompt_parts.append("请根据上述信息生成合适的回复。回复应简洁、自然、符合角色设定。")
        prompt_parts.append("")
        
        # Current Event
        prompt_parts.append("{当前事件 / Current Event}")
        prompt_parts.append(f"用户输入: {interaction_request.content or '[无]'}")
        
        return "\n".join(prompt_parts)
    
    def _check_and_compress(self, prompt: str) -> str:
        """
        检查 Token 预算并压缩 / Check token budget and compress
        
        如果超出预算，按优先级压缩低优先级内容。
        If exceeding budget, compress low-priority content by priority.
        
        Args:
            prompt: 原始 Prompt / Original prompt
        
        Returns:
            可能被压缩的 Prompt / Possibly compressed prompt
        
        Reference:
            PRD §0.5: Step 5 - 组装 Prompt - Token 预算检查
        """
        if not self.config.enable_token_counting:
            return prompt  # 跳过计数 / Skip counting
        
        # 估计 Token 数量 / Estimate token count
        estimated_tokens = self.cache._estimate_tokens(prompt)
        budget = self.config.token_budget
        
        # 预留输出空间的实际预算 / Actual budget after reserving output space
        available_budget = budget.total - budget.reserved_output
        
        if estimated_tokens <= available_budget:
            return prompt  # 在预算内 / Within budget
        
        # 超出预算，需要压缩 / Exceeding budget, need compression
        if not self.config.enable_compression:
            # 不启用压缩，直接截断 / No compression, truncate directly
            return prompt[:int(len(prompt) * available_budget / estimated_tokens)]
        
        # TODO: 实现智能压缩 (优先级压缩低优先级内容)
        # TODO: Implement smart compression (compress low-priority content first)
        
        # 简单压缩：按比例缩减 / Simple compression: proportional reduction
        compression_ratio = available_budget / estimated_tokens
        compressed_length = int(len(prompt) * compression_ratio)
        
        return prompt[:compressed_length]
    
    def _generate_facts_summary(self, facts: List[Dict]) -> str:
        """
        生成 Facts 摘要 / Generate facts summary
        
        Args:
            facts: Facts 列表 / Facts list
        
        Returns:
            格式化的摘要 / Formatted summary
        """
        if not facts:
            return "[暂无用户偏好记录 / No user preferences yet]"
        
        # TODO: 实现完整的 Facts 摘要生成
        # TODO: Implement complete facts summary generation
        
        return "[用户偏好摘要占位 / User preferences summary placeholder]"
    
    def _generate_memory_context(self, memories: List[Dict]) -> str:
        """
        生成记忆上下文 / Generate memory context
        
        Args:
            memories: 检索到的记忆列表 / Retrieved memories list
        
        Returns:
            格式化的记忆上下文 / Formatted memory context
        """
        if not memories:
            return ""
        
        # TODO: 实现完整的记忆上下文生成 (索引模式)
        # TODO: Implement complete memory context generation (index mode)
        
        return "[记忆上下文占位 / Memory context placeholder]"
    
    def invalidate_identity_cache(self) -> None:
        """
        使身份缓存失效 / Invalidate identity cache
        
        当 system_prompt.txt 或 identity.json 文件变更时调用。
        Call when system_prompt.txt or identity.json file changes.
        
        Example:
            >>> builder.invalidate_identity_cache()  # 文件热重载时调用
        """
        self.cache.invalidate_static("identity")
    
    def invalidate_facts_cache(self) -> None:
        """
        使 Facts 缓存失效 / Invalidate facts cache
        
        当用户偏好或行为模式变化时调用。
        Call when user preferences or behavior patterns change.
        
        Example:
            >>> builder.invalidate_facts_cache()  # 偏好变化时调用
        """
        self.cache.invalidate_semi_static("facts_summary")


# 导出列表 / Export list
__all__ = ["PromptBuilder"]
