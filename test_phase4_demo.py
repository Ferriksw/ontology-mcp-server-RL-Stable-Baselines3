#!/usr/bin/env python3
"""
Copyright (c) 2025 shark8848
MIT License

Ontology MCP Server - 电商 AI 助手系统
Author: shark8848
Repository: https://github.com/shark8848/ontology-mcp-server
"""

"""Phase 4 快速体验 - 感受优化后的对话体验"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agent.react_agent import LangChainAgent


def demo_phase4_improvements():
    """展示 Phase 4 的关键改进"""
    
    print("=" * 70)
    print("  Phase 4: Agent 对话优化 - 快速演示")
    print("=" * 70)
    print()
    print("🎯 Phase 4 核心改进:")
    print("  1. 电商专用系统提示 - 更自然友好的对话风格")
    print("  2. 对话状态跟踪 - 自动识别购物阶段")
    print("  3. 主动引导机制 - 询问而非拒绝")
    print()
    
    # 创建 Agent（启用 Phase 4 所有功能）
    agent = LangChainAgent(
        use_memory=True,
        enable_conversation_state=True,
        enable_system_prompt=True,
    )
    
    print("✅ Agent 已启动（Phase 4 完整功能）\n")
    
    # === 示例1: 友好的问候 ===
    print("-" * 70)
    print("示例 1: 友好的问候")
    print("-" * 70)
    print("👤 用户: 你好\n")
    
    result1 = agent.run("你好")
    print(f"🤖 Agent: {result1['final_answer'][:200]}...\n")
    print(f"📊 对话阶段: {agent.get_current_stage()}")
    print()
    
    # === 示例2: 主动引导 ===
    print("-" * 70)
    print("示例 2: 主动引导（询问而非拒绝）")
    print("-" * 70)
    print("👤 用户: 我想买东西\n")
    
    result2 = agent.run("我想买东西")
    print(f"🤖 Agent: {result2['final_answer'][:300]}...\n")
    print(f"📊 对话阶段: {agent.get_current_stage()}")
    print()
    
    # === 示例3: 记住上下文 ===
    print("-" * 70)
    print("示例 3: 上下文记忆（记住之前的对话）")
    print("-" * 70)
    print("👤 用户: 推荐一款吧\n")
    
    result3 = agent.run("推荐一款吧")
    print(f"🤖 Agent: {result3['final_answer'][:250]}...\n")
    print(f"📊 对话阶段: {agent.get_current_stage()}")
    print()
    
    # === 总结 ===
    print("=" * 70)
    print("  Phase 4 体验总结")
    print("=" * 70)
    
    state = agent.get_conversation_state()
    if state:
        print(f"\n📊 会话统计:")
        print(f"  - 会话ID: {state['session_id']}")
        print(f"  - 当前阶段: {state['stage']}")
        print(f"  - 意图历史: {len(state['intent_history'])}条")
    
    history = agent.get_full_history()
    print(f"\n💬 对话轮次: {len(history)}轮")
    
    print("\n✨ Phase 4 优化点:")
    print("  ✅ Agent 语气更友好自然")
    print("  ✅ 主动询问补充信息")
    print("  ✅ 自动跟踪对话阶段")
    print("  ✅ 记住完整对话上下文")
    print()


if __name__ == "__main__":
    try:
        demo_phase4_improvements()
        print("🎉 Phase 4 功能演示完成！\n")
    except Exception as e:
        print(f"\n❌ 演示失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
