#!/usr/bin/env python3
"""
Copyright (c) 2025 shark8848
MIT License

Ontology MCP Server - 电商 AI 助手系统
Author: shark8848
Repository: https://github.com/shark8848/ontology-mcp-server
"""

"""测试 ChromaDB 记忆功能"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agent.react_agent import LangChainAgent

def test_chroma_memory():
    print("🧠 测试 ChromaDB 记忆功能\n")
    
    # 创建启用 ChromaDB 的 Agent
    session_id = "test_session_001"
    agent = LangChainAgent(
        use_memory=True,
        session_id=session_id,
        max_results=5,
    )
    
    # 查看记忆统计
    stats = agent.get_memory_stats()
    print("=" * 60)
    print("记忆统计信息:")
    print(f"  后端: {stats.get('backend')}")
    print(f"  会话ID: {stats.get('session_id')}")
    print(f"  存储目录: {stats.get('persist_directory', 'N/A')}")
    print(f"  记录数: {stats.get('total_turns', 0)}")
    print("=" * 60)
    print()
    
    # 第一轮对话
    print("=" * 60)
    print("第 1 轮对话")
    print("=" * 60)
    print("👤 用户: 我是VIP客户")
    result1 = agent.run("我是VIP客户")
    print(f"🤖 Agent: {result1['final_answer'][:100]}...\n")
    
    # 第二轮对话 - 应该记住VIP身份
    print("=" * 60)
    print("第 2 轮对话")
    print("=" * 60)
    print("👤 用户: 我的订单金额是1000元,能打几折?")
    
    print("\n💭 注入的历史上下文:")
    print(agent.get_memory_context())
    print()
    
    result2 = agent.run("我的订单金额是1000元,能打几折?")
    print(f"🤖 Agent: {result2['final_answer'][:100]}...\n")
    
    # 第三轮对话
    print("=" * 60)
    print("第 3 轮对话")
    print("=" * 60)
    print("👤 用户: 那500元呢?")
    
    print("\n💭 注入的历史上下文:")
    print(agent.get_memory_context())
    print()
    
    result3 = agent.run("那500元呢?")
    print(f"🤖 Agent: {result3['final_answer'][:100]}...\n")
    
    # 查看完整历史
    print("=" * 60)
    print("完整对话历史 (存储在 ChromaDB)")
    print("=" * 60)
    history = agent.get_full_history()
    for i, turn in enumerate(history, 1):
        print(f"\n第 {i} 轮:")
        print(f"  📝 摘要: {turn['summary'][:80]}...")
        print(f"  ⏰ 时间: {turn['timestamp']}")
        if turn['tool_calls']:
            tools = [tc['tool'] for tc in turn['tool_calls']]
            print(f"  🔧 工具: {', '.join(tools)}")
    
    # 更新统计
    print("\n" + "=" * 60)
    print("最终统计:")
    stats = agent.get_memory_stats()
    print(f"  会话ID: {stats.get('session_id')}")
    print(f"  总记录数: {stats.get('total_turns', 0)}")
    print(f"  存储位置: {stats.get('persist_directory', 'N/A')}")
    print("=" * 60)
    
    # 测试语义检索
    print("\n" + "=" * 60)
    print("测试语义相似度检索")
    print("=" * 60)
    query = "折扣信息"
    print(f"查询: {query}")
    similar = agent.search_similar_conversations(query, n_results=3)
    print(f"\n找到 {len(similar)} 条相似对话:")
    for i, turn in enumerate(similar, 1):
        print(f"\n{i}. 相似度: {turn.get('metadata', {}).get('similarity_distance', 'N/A')}")
        print(f"   摘要: {turn['summary'][:80]}...")
    
    print("\n" + "=" * 60)
    print("✅ ChromaDB 测试完成!")
    print("\n💡 提示: 对话已持久化到磁盘,重启后仍然可用")
    print(f"   存储位置: {stats.get('persist_directory', 'N/A')}")
    print("=" * 60)


def test_persistence():
    """测试持久化: 关闭后重新打开会话"""
    print("\n\n" + "=" * 60)
    print("测试持久化: 重新打开会话")
    print("=" * 60)
    
    session_id = "test_session_001"
    
    # 创建新的 Agent 实例(模拟程序重启)
    new_agent = LangChainAgent(
        use_memory=True,
        session_id=session_id,
    )
    
    print(f"\n✅ 重新加载会话: {session_id}")
    
    # 查看历史
    history = new_agent.get_full_history()
    print(f"📚 自动从 ChromaDB 加载了 {len(history)} 条历史记录\n")
    
    if history:
        print("最近的对话:")
        for turn in history[-3:]:
            print(f"  - {turn['summary'][:80]}...")
    
    # 继续对话
    print("\n👤 用户: 帮我总结一下我们的对话")
    print("\n💭 Agent 可以看到之前的所有对话:")
    print(new_agent.get_memory_context())
    print()
    
    result = new_agent.run("帮我总结一下我们的对话")
    print(f"🤖 Agent: {result['final_answer'][:150]}...")
    
    print("\n" + "=" * 60)
    print("✅ 持久化测试完成!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_chroma_memory()
        test_persistence()
        
        print("\n\n🎉 所有测试通过!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
    except Exception as e:
        import traceback
        print(f"\n❌ 错误: {e}")
        traceback.print_exc()
        sys.exit(1)
