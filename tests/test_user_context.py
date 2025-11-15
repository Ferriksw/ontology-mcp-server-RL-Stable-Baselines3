#!/usr/bin/env python3
"""测试用户上下文提取功能"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agent.user_context_extractor import UserContextExtractor, UserContextManager


def test_extractor():
    """测试提取器"""
    print("=" * 60)
    print("测试用户上下文提取器")
    print("=" * 60)
    
    extractor = UserContextExtractor()
    
    # 测试1: 从用户输入提取
    print("\n【测试1】从用户输入提取信息")
    user_input = "用户ID 1购买2台iPhone 15 Pro（商品ID 2），配送地址：成都武侯区，电话：15308215756"
    context = extractor.extract_from_text(user_input)
    
    print(f"输入: {user_input}")
    print(f"提取结果:")
    print(f"  - 用户ID: {context.user_id}")
    print(f"  - 电话: {context.phone}")
    print(f"  - 地址: {context.address}")
    print(f"  - 商品ID: {context.viewed_product_ids}")
    
    # 测试2: 从工具调用提取
    print("\n【测试2】从工具调用提取信息")
    tool_calls = [
        {
            "tool": "commerce.create_order",
            "input": {
                "user_id": 1,
                "items": [{"product_id": 2, "quantity": 2}],
                "shipping_address": "成都市武侯区",
                "contact_phone": "15308215756"
            },
            "observation": "订单创建成功: ORD202511111355480001"
        }
    ]
    
    context = extractor.extract_from_tool_calls(tool_calls)
    print(f"提取结果:")
    print(f"  - 用户ID: {context.user_id}")
    print(f"  - 电话: {context.phone}")
    print(f"  - 地址: {context.address}")
    print(f"  - 订单号: {context.recent_order_id}")
    print(f"  - 商品ID: {context.viewed_product_ids}")
    
    # 测试3: 从完整对话提取
    print("\n【测试3】从完整对话提取信息")
    user_input = "我想查询订单 ORD202511111325480001 的物流信息"
    agent_response = "查询到订单信息：用户ID 1，包含商品ID 1（iPhone 15 Pro Max）×5台"
    tool_calls = [
        {
            "tool": "commerce.get_order",
            "input": {"order_id": "ORD202511111325480001"},
            "observation": "订单详情..."
        }
    ]
    
    context = extractor.extract_from_conversation(user_input, agent_response, tool_calls)
    print(f"用户输入: {user_input}")
    print(f"Agent响应: {agent_response}")
    print(f"\n提取结果:")
    print(f"  - 用户ID: {context.user_id}")
    print(f"  - 订单号: {context.recent_order_id}")
    print(f"  - 商品ID: {context.viewed_product_ids}")


def test_manager():
    """测试管理器"""
    print("\n" + "=" * 60)
    print("测试用户上下文管理器")
    print("=" * 60)
    
    manager = UserContextManager("test_session")
    
    # 模拟第一轮对话
    print("\n【第1轮对话】")
    manager.update_from_conversation(
        user_input="用户ID 1，我想买iPhone",
        agent_response="好的，为您推荐iPhone 15 Pro Max（商品ID 1）",
        tool_calls=[]
    )
    print("提示词注入内容:")
    print(manager.get_prompt_injection())
    
    # 模拟第二轮对话
    print("\n【第2轮对话】")
    manager.update_from_conversation(
        user_input="帮我下单2台，地址：成都武侯区，电话：15308215756",
        agent_response="订单创建成功",
        tool_calls=[
            {
                "tool": "commerce.create_order",
                "input": {
                    "user_id": 1,
                    "items": [{"product_id": 1, "quantity": 2}],
                    "shipping_address": "成都武侯区",
                    "contact_phone": "15308215756"
                },
                "observation": "订单号：ORD202511111425480001"
            }
        ]
    )
    print("提示词注入内容:")
    print(manager.get_prompt_injection())
    
    # 模拟第三轮对话
    print("\n【第3轮对话】")
    manager.update_from_conversation(
        user_input="查询订单状态",
        agent_response="订单ORD202511111425480001已发货",
        tool_calls=[]
    )
    print("提示词注入内容:")
    print(manager.get_prompt_injection())
    
    # 显示完整上下文
    print("\n【完整上下文】")
    ctx = manager.get_context()
    print(f"  - 用户ID: {ctx.user_id}")
    print(f"  - 电话: {ctx.phone}")
    print(f"  - 地址: {ctx.address}")
    print(f"  - 最近订单: {ctx.recent_order_id}")
    print(f"  - 所有订单: {ctx.order_ids}")
    print(f"  - 浏览商品: {ctx.viewed_product_ids}")


if __name__ == "__main__":
    test_extractor()
    test_manager()
    print("\n" + "=" * 60)
    print("✅ 所有测试完成！")
    print("=" * 60)
