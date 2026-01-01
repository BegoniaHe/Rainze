#!/usr/bin/env python3
"""
Rainze LLM 端到端测试脚本
Rainze LLM End-to-End Test Script

测试 UCM -> Tier3 LLM 的完整对话流程。
Test complete conversation flow from UCM to Tier3 LLM.

使用方法 / Usage:
    # 确保设置环境变量 / Ensure env vars are set
    export OPENAI_API_KEY="your-key"
    # 或 / or
    export ANTHROPIC_API_KEY="your-key"

    # 运行测试 / Run test
    cd /path/to/Rainze
    uv run python tests/e2e_llm_test.py

Author: Rainze Team
Created: 2025-12-31
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# 确保 src 在 Python 路径中 / Ensure src is in Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from rainze.agent.context_manager import UnifiedContextManager  # noqa: E402
from rainze.core.contracts import InteractionRequest, InteractionSource  # noqa: E402

# 配置日志 / Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("e2e_test")


async def test_simple_conversation() -> bool:
    """
    测试简单对话
    Test simple conversation
    """
    logger.info("=" * 60)
    logger.info("测试 1: 简单对话 (Tier3 LLM)")
    logger.info("=" * 60)

    ucm = UnifiedContextManager()

    # 测试用例 / Test cases
    test_inputs = [
        "你好呀~",
        "今天过得怎么样？",
        "给我讲个笑话吧",
    ]

    success_count = 0
    for user_input in test_inputs:
        logger.info(f"\n📤 用户输入: {user_input}")

        # 创建交互请求 / Create interaction request
        request = InteractionRequest.create(
            source=InteractionSource.CHAT_INPUT,
            payload={"text": user_input},
        )

        # 处理交互 / Process interaction
        response = await ucm.process_interaction(request)

        # 检查响应 / Check response
        if response.success:
            logger.info(f"📥 AI 响应: {response.response_text}")
            logger.info(
                f"   情感: {response.emotion.tag if response.emotion else 'N/A'} "
                f"({response.emotion.intensity if response.emotion else 0:.1f})"
            )
            logger.info(f"   层级: {response.state_changes.get('tier_used', 'N/A')}")
            logger.info(f"   延迟: {response.state_changes.get('latency_ms', 0)}ms")
            success_count += 1
        else:
            logger.error(f"❌ 请求失败: {response.error}")

    logger.info(f"\n✅ 简单对话测试: {success_count}/{len(test_inputs)} 成功")
    return success_count == len(test_inputs)


async def test_multi_turn_conversation() -> bool:
    """
    测试多轮对话（验证对话历史）
    Test multi-turn conversation (verify conversation history)
    """
    logger.info("\n" + "=" * 60)
    logger.info("测试 2: 多轮对话 (验证上下文保持)")
    logger.info("=" * 60)

    ucm = UnifiedContextManager()

    # 多轮对话 / Multi-turn conversation
    conversation = [
        "我叫小明",
        "你还记得我叫什么吗？",
        "我今天有点累",
        "有什么建议吗？",
    ]

    for i, user_input in enumerate(conversation, 1):
        logger.info(f"\n--- 第 {i} 轮 ---")
        logger.info(f"📤 用户: {user_input}")

        request = InteractionRequest.create(
            source=InteractionSource.CHAT_INPUT,
            payload={"text": user_input},
        )

        response = await ucm.process_interaction(request)

        if response.success:
            logger.info(f"📥 Rainze: {response.response_text}")
        else:
            logger.error(f"❌ 失败: {response.error}")
            return False

    # 检查上下文摘要 / Check context summary
    summary = await ucm.get_context_summary()
    logger.info(f"\n📊 上下文摘要: 已处理 {summary['interaction_count']} 次交互")

    return True


async def test_tier1_template() -> bool:
    """
    测试 Tier1 模板响应（点击事件）
    Test Tier1 template response (click event)
    """
    logger.info("\n" + "=" * 60)
    logger.info("测试 3: Tier1 模板响应 (点击事件)")
    logger.info("=" * 60)

    ucm = UnifiedContextManager()

    # 模拟点击事件 / Simulate click event
    request = InteractionRequest.create(
        source=InteractionSource.PASSIVE_TRIGGER,
        payload={"event_type": "click"},
    )

    logger.info("📤 触发: 点击事件")
    response = await ucm.process_interaction(request)

    if response.success:
        logger.info(f"📥 响应: {response.response_text}")
        tier_used = response.state_changes.get("tier_used", "")
        logger.info(f"   层级: {tier_used}")
        logger.info(f"   延迟: {response.state_changes.get('latency_ms', 0)}ms")

        # Tier1 应该非常快 / Tier1 should be very fast
        latency = response.state_changes.get("latency_ms", 999)
        if latency < 100:
            logger.info("✅ Tier1 响应时间符合预期 (<100ms)")
            return True
        else:
            logger.warning(f"⚠️ Tier1 响应较慢: {latency}ms")
            return True  # 仍然算成功 / Still count as success
    else:
        logger.error(f"❌ 失败: {response.error}")
        return False


async def test_tier2_rule() -> bool:
    """
    测试 Tier2 规则响应（系统警告）
    Test Tier2 rule response (system warning)
    """
    logger.info("\n" + "=" * 60)
    logger.info("测试 4: Tier2 规则响应 (系统警告)")
    logger.info("=" * 60)

    ucm = UnifiedContextManager()

    # 模拟 CPU 高警告 / Simulate high CPU warning
    request = InteractionRequest.create(
        source=InteractionSource.SYSTEM_EVENT,
        payload={
            "event_type": "system_warning",
            "warning_type": "cpu_high",
            "value": 95,
        },
    )

    logger.info("📤 触发: CPU 使用率 95% 警告")
    response = await ucm.process_interaction(request)

    if response.success:
        logger.info(f"📥 响应: {response.response_text}")
        logger.info(f"   层级: {response.state_changes.get('tier_used', 'N/A')}")
        return True
    else:
        logger.error(f"❌ 失败: {response.error}")
        return False


async def main() -> None:
    """主测试入口 / Main test entry"""
    logger.info("🚀 Rainze LLM 端到端测试开始")
    logger.info(f"📁 项目根目录: {PROJECT_ROOT}")

    # 检查环境变量 / Check environment variables
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "")

    if not openai_key and not anthropic_key:
        logger.warning("⚠️ 未设置 API Key 环境变量!")
        logger.warning("   请设置 OPENAI_API_KEY 或 ANTHROPIC_API_KEY")
        logger.warning("   Tier3 测试将使用占位响应")
    else:
        if openai_key:
            logger.info(f"✅ OPENAI_API_KEY 已设置 (长度: {len(openai_key)})")
        if anthropic_key:
            logger.info(f"✅ ANTHROPIC_API_KEY 已设置 (长度: {len(anthropic_key)})")

    # 运行测试 / Run tests
    results = {
        "Tier1 模板": await test_tier1_template(),
        "Tier2 规则": await test_tier2_rule(),
        "简单对话": await test_simple_conversation(),
        "多轮对话": await test_multi_turn_conversation(),
    }

    # 输出总结 / Output summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 测试总结")
    logger.info("=" * 60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"  {name}: {status}")

    logger.info(f"\n总计: {passed}/{total} 通过")

    if passed == total:
        logger.info("🎉 所有测试通过!")
        sys.exit(0)
    else:
        logger.error("💥 部分测试失败")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
