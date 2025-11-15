#!/usr/bin/env python3
"""
Copyright (c) 2025 shark8848
MIT License

Ontology MCP Server - 电商 AI 助手系统
Author: shark8848
Repository: https://github.com/shark8848/ontology-mcp-server
"""

"""快速测试对话记忆功能"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agent.react_agent import LangChainAgent

def test_memory():
    print("🧠 测试对话记忆功能\n")
    
    # 创建启用记忆的 Agent
    agent = LangChainAgent(
        use_memory=True,
        max_history=5,
        max_summary_length=3,
    )
    
    # 第一轮对话
    print("=" * 60)
    print("第 1 轮对话")
    print("=" * 60)
    print("👤 用户: 我是VIP客户")
    result1 = agent.run("我是VIP客户")
    print(f"🤖 Agent: {result1['final_answer']}\n")
    
    # 第二轮对话 - 应该记住VIP身份
    print("=" * 60)
    print("第 2 轮对话")
    print("=" * 60)
    print("👤 用户: 我的订单金额是1000元,能打几折?")
    
    # 显示注入的上下文
    print("\n💭 注入的历史上下文:")
    print(agent.get_memory_context())
    print()
    
    result2 = agent.run("我的订单金额是1000元,能打几折?")
    print(f"🤖 Agent: {result2['final_answer']}\n")
    
    # 第三轮对话 - 引用前面的结果
    print("=" * 60)
    print("第 3 轮对话")
    print("=" * 60)
    print("👤 用户: 那500元呢?")
    
    print("\n💭 注入的历史上下文:")
    print(agent.get_memory_context())
    print()
    
    result3 = agent.run("那500元呢?")
    print(f"🤖 Agent: {result3['final_answer']}\n")
    
    # 查看完整历史
    print("=" * 60)
    print("完整对话历史")
    print("=" * 60)
    history = agent.get_full_history()
    for i, turn in enumerate(history, 1):
        print(f"\n第 {i} 轮:")
        print(f"  📝 摘要: {turn['summary']}")
        print(f"  👤 用户: {turn['user_input']}")
        print(f"  🤖 响应: {turn['agent_response'][:100]}...")
        if turn['tool_calls']:
            tools = [tc['tool'] for tc in turn['tool_calls']]
            print(f"  🔧 工具: {', '.join(tools)}")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成!")
    print("=" * 60)

if __name__ == "__main__":
    test_memory()
