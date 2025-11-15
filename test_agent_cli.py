#!/usr/bin/env python3
"""
Copyright (c) 2025 shark8848
MIT License

Ontology MCP Server - 电商 AI 助手系统
Author: shark8848
Repository: https://github.com/shark8848/ontology-mcp-server
"""

"""命令行测试脚本：直接调用 agent API 验证功能"""
import sys
import os

# 确保导入路径正确
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agent.react_agent import LangChainAgent
from agent.logger import get_logger

logger = get_logger(__name__)


def test_agent():
    """测试 agent 基本功能"""
    print("=" * 60)
    print("初始化 Agent...")
    print("=" * 60)

    try:
        agent = LangChainAgent()
    except Exception as exc:  # pragma: no cover - defensive logging
        print(f"✗ Agent 初始化失败: {exc}")
        import traceback

        traceback.print_exc()
        raise

    print(f"✓ Agent 初始化成功，加载了 {len(agent.tools)} 个工具")
    print(f"  工具列表: {[tool.name for tool in agent.tools]}")
    assert agent.tools, "Agent 未加载任何工具"

    print("\n" + "=" * 60)
    print("测试查询: 解释 VIP 客户 500 元订单的折扣")
    print("=" * 60)

    result = agent.run("我是VIP客户，订单金额是500元，请解释折扣规则")

    print("\n📋 执行计划:")
    print(result.get("plan", "(无计划)"))

    print("\n🔧 工具调用记录:")
    for i, log_entry in enumerate(result.get("tool_log", []), 1):
        print(f"\n  {i}. 工具: {log_entry.get('tool')}")
        print(f"     输入: {log_entry.get('input')}")
        obs = log_entry.get('observation', '')
        if isinstance(obs, str) and len(obs) > 200:
            obs = obs[:200] + "..."
        print(f"     观察: {obs}")

    print("\n💬 最终回答:")
    final_answer = result.get("final_answer", "")
    print(final_answer or "(无回答)")

    assert isinstance(result, dict), "返回结果必须为字典"
    assert final_answer, "Agent 未返回最终回答"
    assert "discount" in final_answer or "折扣" in final_answer, "回答中缺少折扣说明"


if __name__ == "__main__":
    print("Agent CLI 测试工具")
    print(f"MCP 服务器地址: {os.getenv('MCP_BASE_URL', 'http://localhost:8000')}")
    print()
    
    # 检查环境变量
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("DEEPSEEK_API_KEY"):
        print("⚠️  警告: 未设置 OPENAI_API_KEY 或 DEEPSEEK_API_KEY 环境变量")
        print("   Agent 需要 API key 才能调用 LLM")
        print()
    
    success = test_agent()
    
    print("\n" + "=" * 60)
    if success:
        print("✓ 测试完成")
        sys.exit(0)
    else:
        print("✗ 测试失败")
        sys.exit(1)
