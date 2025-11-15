#!/usr/bin/env python3
"""
Copyright (c) 2025 shark8848
MIT License

Ontology MCP Server - 电商 AI 助手系统
Author: shark8848
Repository: https://github.com/shark8848/ontology-mcp-server
"""

"""Phase 4: 完整购物对话流程测试"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agent.react_agent import LangChainAgent


def print_section(title: str):
    """打印章节分隔"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_response(agent_result: dict, show_tools: bool = True):
    """打印 Agent 响应"""
    print(f"\n🤖 Agent: {agent_result['final_answer']}")
    
    if show_tools and agent_result.get('tool_log'):
        print(f"\n🔧 调用工具: {len(agent_result['tool_log'])}个")
        for i, tool in enumerate(agent_result['tool_log'], 1):
            print(f"   {i}. {tool['tool']}")


def test_complete_shopping_conversation():
    """测试完整购物对话流程"""
    
    print_section("Phase 4: 完整购物会话测试")
    
    # 创建启用所有Phase 4功能的 Agent
    agent = LangChainAgent(
        use_memory=True,
        enable_conversation_state=True,
        enable_system_prompt=True,
        session_id="test_shopping_session",
    )
    
    print("\n✅ Agent 初始化完成")
    print(f"   - 对话记忆: 已启用")
    print(f"   - 状态跟踪: 已启用")
    print(f"   - 系统提示: 已启用")
    print(f"   - 工具数量: {len(agent.tools)}")
    
    # === 第1轮: 初次问候 ===
    print_section("第 1 轮: 用户初次问候")
    print("👤 用户: 你好")
    
    result1 = agent.run("你好")
    print_response(result1, show_tools=False)
    
    stage1 = agent.get_current_stage()
    print(f"\n📊 当前阶段: {stage1}")
    
    # === 第2轮: 搜索商品 ===
    print_section("第 2 轮: 搜索商品")
    print("👤 用户: 我想买手机")
    
    result2 = agent.run("我想买手机")
    print_response(result2)
    
    stage2 = agent.get_current_stage()
    print(f"\n📊 当前阶段: {stage2}")
    
    # === 第3轮: 查看商品详情 ===
    print_section("第 3 轮: 查看具体商品")
    print("👤 用户: 第一个商品怎么样？")
    
    result3 = agent.run("第一个商品怎么样？")
    print_response(result3)
    
    stage3 = agent.get_current_stage()
    print(f"\n📊 当前阶段: {stage3}")
    
    # === 第4轮: 加入购物车 ===
    print_section("第 4 轮: 加入购物车")
    print("👤 用户: 帮我加入购物车")
    
    result4 = agent.run("帮我加入购物车")
    print_response(result4)
    
    stage4 = agent.get_current_stage()
    state4 = agent.get_conversation_state()
    print(f"\n📊 当前阶段: {stage4}")
    if state4 and state4.get('user_context'):
        cart_count = state4['user_context'].get('cart_item_count', 0)
        print(f"📊 购物车: {cart_count}件商品")
    
    # === 第5轮: 查看购物车 ===
    print_section("第 5 轮: 查看购物车")
    print("👤 用户: 我的购物车里有什么？")
    
    result5 = agent.run("我的购物车里有什么？")
    print_response(result5)
    
    # === 第6轮: 下单 ===
    print_section("第 6 轮: 创建订单")
    print("👤 用户: 帮我下单，收货地址是北京市朝阳区，电话18888888888")
    
    result6 = agent.run("帮我下单，收货地址是北京市朝阳区，电话18888888888")
    print_response(result6)
    
    stage6 = agent.get_current_stage()
    state6 = agent.get_conversation_state()
    print(f"\n📊 当前阶段: {stage6}")
    if state6 and state6.get('current_order_id'):
        print(f"📊 订单ID: {state6['current_order_id']}")
    
    # === 第7轮: 查询订单 ===
    print_section("第 7 轮: 查询订单状态")
    print("👤 用户: 我的订单状态怎么样？")
    
    result7 = agent.run("我的订单状态怎么样？")
    print_response(result7)
    
    stage7 = agent.get_current_stage()
    print(f"\n📊 当前阶段: {stage7}")
    
    # === 总结 ===
    print_section("测试总结")
    
    history = agent.get_full_history()
    print(f"\n📋 对话历史: 共 {len(history)} 轮")
    
    state_final = agent.get_conversation_state()
    if state_final:
        print(f"\n📊 最终状态:")
        print(f"   - 会话ID: {state_final['session_id']}")
        print(f"   - 当前阶段: {state_final['stage']}")
        print(f"   - VIP客户: {state_final['user_context'].get('is_vip', False)}")
        print(f"   - 购物车: {state_final['user_context'].get('cart_item_count', 0)}件")
        print(f"   - 浏览商品: {len(state_final['user_context'].get('last_viewed_products', []))}个")
        if state_final.get('current_order_id'):
            print(f"   - 当前订单: #{state_final['current_order_id']}")
    
    memory_stats = agent.get_memory_stats()
    if memory_stats.get('enabled'):
        print(f"\n💾 记忆统计:")
        print(f"   - 后端: {memory_stats.get('backend', 'Unknown')}")
        if 'total_turns' in memory_stats:
            print(f"   - 总轮次: {memory_stats['total_turns']}")
        if 'session_id' in memory_stats:
            print(f"   - 会话ID: {memory_stats['session_id']}")
    
    print("\n" + "=" * 70)
    print("  ✅ 完整购物会话测试完成！")
    print("=" * 70)
    
    return agent


if __name__ == "__main__":
    try:
        agent = test_complete_shopping_conversation()
        print("\n✨ Phase 4 优化功能正常工作！")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
