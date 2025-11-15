#!/usr/bin/env python3
"""
Copyright (c) 2025 shark8848
MIT License

Ontology MCP Server - 电商 AI 助手系统
Author: shark8848
Repository: https://github.com/shark8848/ontology-mcp-server
"""

"""测试对话记忆功能的演示脚本"""
import sys
import os

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agent.react_agent import LangChainAgent
from agent.logger import get_logger

logger = get_logger(__name__)


def print_separator():
    print("\n" + "=" * 80 + "\n")


def demo_basic_memory():
    """演示基础记忆功能"""
    print("🧠 演示 1: 基础对话记忆")
    print_separator()
    
    # 创建启用记忆的 Agent
    agent = LangChainAgent(
        use_memory=True,
        enhanced_memory=False,
        max_history=10,
        max_summary_length=3,
    )
    
    # 第一轮对话
    print("👤 用户: 我是VIP客户,订单金额500元,能打几折?")
    result1 = agent.run("我是VIP客户,订单金额500元,能打几折?")
    print(f"🤖 Agent: {result1['final_answer']}\n")
    
    # 第二轮对话 - 引用前一轮上下文
    print("👤 用户: 那如果金额是1000元呢?")
    result2 = agent.run("那如果金额是1000元呢?")
    print(f"🤖 Agent: {result2['final_answer']}\n")
    
    # 第三轮对话 - 继续引用
    print("👤 用户: 把刚才的结果总结一下")
    result3 = agent.run("把刚才的结果总结一下")
    print(f"🤖 Agent: {result3['final_answer']}\n")
    
    # 查看记忆摘要
    print("📝 当前对话记忆摘要:")
    print(agent.get_memory_context())
    print_separator()


def demo_memory_context():
    """演示记忆上下文注入"""
    print("🧠 演示 2: 记忆上下文注入")
    print_separator()
    
    agent = LangChainAgent(
        use_memory=True,
        max_history=5,
        max_summary_length=3,
    )
    
    # 模拟多轮对话
    conversations = [
        "帮我查询iPhone 15的标准产品名称",
        "这个手机多少钱?",
        "我要买3台",
        "加上VIP折扣后总价是多少?",
        "帮我验证这个订单",
    ]
    
    for i, user_input in enumerate(conversations, 1):
        print(f"\n--- 第 {i} 轮对话 ---")
        print(f"👤 用户: {user_input}")
        
        # 显示注入的上下文
        if i > 1:
            context = agent.get_memory_context()
            print(f"\n💭 注入的历史上下文:\n{context}\n")
        
        result = agent.run(user_input)
        print(f"🤖 Agent: {result['final_answer']}")
    
    print_separator()
    
    # 查看完整历史
    print("📚 完整对话历史:")
    history = agent.get_full_history()
    for i, turn in enumerate(history, 1):
        print(f"\n第 {i} 轮:")
        print(f"  用户: {turn['user_input'][:60]}...")
        print(f"  响应: {turn['agent_response'][:60]}...")
        print(f"  摘要: {turn['summary']}")
    
    print_separator()


def demo_memory_persistence():
    """演示记忆持久化"""
    print("🧠 演示 3: 记忆持久化")
    print_separator()
    
    agent = LangChainAgent(use_memory=True)
    
    # 进行几轮对话
    print("👤 用户: 我叫小明")
    agent.run("我叫小明")
    
    print("👤 用户: 我今年25岁")
    agent.run("我今年25岁")
    
    print("👤 用户: 我喜欢编程")
    agent.run("我喜欢编程")
    
    # 保存记忆
    save_path = "/tmp/agent_memory.json"
    agent.save_memory(save_path)
    print(f"\n✅ 对话记忆已保存到: {save_path}")
    
    # 创建新的 Agent 并加载记忆
    print("\n🔄 创建新 Agent 并加载记忆...")
    new_agent = LangChainAgent(use_memory=True)
    new_agent.load_memory(save_path)
    
    print("\n📝 加载后的记忆内容:")
    print(new_agent.get_memory_context())
    
    # 继续对话
    print("\n👤 用户: 请根据你对我的了解,介绍一下我")
    result = new_agent.run("请根据你对我的了解,介绍一下我")
    print(f"🤖 Agent: {result['final_answer']}")
    
    print_separator()


def demo_memory_limits():
    """演示记忆长度限制"""
    print("🧠 演示 4: 记忆长度限制")
    print_separator()
    
    agent = LangChainAgent(
        use_memory=True,
        max_history=3,  # 只保留最近3轮
        max_summary_length=2,  # 只注入最近2轮摘要
    )
    
    # 进行5轮对话
    for i in range(1, 6):
        user_input = f"这是第{i}轮对话"
        print(f"👤 用户: {user_input}")
        agent.run(user_input)
    
    # 查看保留的历史
    history = agent.get_full_history()
    print(f"\n📝 当前保留的历史记录数: {len(history)} (最大: 3)")
    print("\n保留的记录:")
    for turn in history:
        print(f"  - {turn['summary']}")
    
    # 查看注入的上下文
    print(f"\n💭 注入的上下文 (最近 2 轮):")
    print(agent.get_memory_context())
    
    print_separator()


if __name__ == "__main__":
    print("\n🚀 对话记忆功能演示\n")
    
    try:
        demo_basic_memory()
        demo_memory_context()
        demo_memory_persistence()
        demo_memory_limits()
        
        print("\n✅ 所有演示完成!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  演示被用户中断")
    except Exception as e:
        logger.exception("演示过程中出现错误")
        print(f"\n❌ 错误: {e}")
        sys.exit(1)
