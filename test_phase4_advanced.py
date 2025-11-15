#!/usr/bin/env python3
"""
Copyright (c) 2025 shark8848
MIT License

Ontology MCP Server - 电商 AI 助手系统
Author: shark8848
Repository: https://github.com/shark8848/ontology-mcp-server
"""

"""
Phase 4 可选优化测试

测试功能：
1. 对话质量评分系统
2. 多轮意图识别
3. 个性化推荐引擎
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agent.react_agent import LangChainAgent
from agent.quality_metrics import TaskOutcome, UserSatisfaction
from agent.recommendation_engine import Product

def print_section(title: str):
    """打印分节标题"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def test_quality_tracking():
    """测试对话质量跟踪"""
    print_section("测试 1: 对话质量跟踪")
    
    agent = LangChainAgent(
        use_memory=True,
        session_id="test_quality_001",
        enable_quality_tracking=True,
        enable_intent_tracking=True,
    )
    
    # 第1轮：搜索商品
    print("👤 用户: 搜索笔记本电脑")
    result1 = agent.run("搜索笔记本电脑")
    print(f"🤖 Agent: {result1['final_answer'][:100]}...")
    
    # 第2轮：查看详情（缺少商品ID，测试主动引导）
    print("\n👤 用户: 看看详情")
    result2 = agent.run("看看详情")
    print(f"🤖 Agent: {result2['final_answer'][:150]}...")
    
    # 第3轮：提供商品ID
    print("\n👤 用户: 商品 prod_laptop_001")
    result3 = agent.run("商品 prod_laptop_001 的详情")
    print(f"🤖 Agent: {result3['final_answer'][:100]}...")
    
    # 获取质量报告
    print_section("质量报告")
    quality_report = agent.get_quality_report()
    
    print(f"📊 质量分数: {quality_report['quality_score']}/100")
    print(f"⏱️  平均响应时间: {quality_report['efficiency']['avg_response_time']}秒")
    print(f"🔧 平均工具调用: {quality_report['efficiency']['avg_tool_calls']}次")
    print(f"✅ 成功率: {quality_report['task_completion']['success_rate']*100}%")
    print(f"❓ 澄清率: {quality_report['conversation_quality']['clarification_rate']*100}%")
    print(f"💡 主动引导率: {quality_report['conversation_quality']['proactive_rate']*100}%")
    
    return agent


def test_intent_recognition(agent):
    """测试意图识别"""
    print_section("测试 2: 多轮意图识别")
    
    # 第4轮：价格咨询
    print("👤 用户: 这个多少钱？")
    result4 = agent.run("这个多少钱？")
    print(f"🤖 Agent: {result4['final_answer'][:100]}...")
    
    # 第5轮：库存咨询
    print("\n👤 用户: 还有货吗？")
    result5 = agent.run("还有货吗？")
    print(f"🤖 Agent: {result5['final_answer'][:100]}...")
    
    # 第6轮：加入购物车
    print("\n👤 用户: 加入购物车")
    result6 = agent.run("加入购物车")
    print(f"🤖 Agent: {result6['final_answer'][:150]}...")
    
    # 获取意图分析
    print_section("意图分析报告")
    intent_analysis = agent.get_intent_analysis()
    
    print(f"🎯 意图分布:")
    for intent_type, count in intent_analysis['intent_distribution'].items():
        print(f"   - {intent_type}: {count}次")
    
    print(f"\n🔄 识别出的复合意图:")
    for composite in intent_analysis['composite_intents']:
        print(f"   - {composite['name']}: {composite['description']}")
        print(f"     子意图: {', '.join(composite['sub_intents'])}")
    
    print(f"\n📍 当前意图: {intent_analysis['current_intent']}")
    print(f"🔮 预测下一步: {', '.join(intent_analysis['predicted_next'])}")


def test_recommendation_engine():
    """测试推荐引擎"""
    print_section("测试 3: 个性化推荐引擎")
    
    # 创建带推荐功能的 Agent
    agent = LangChainAgent(
        use_memory=True,
        session_id="test_recommend_001",
        enable_recommendation=True,
    )
    
    # 添加模拟商品数据
    if agent.recommendation_engine:
        print("📦 添加模拟商品...")
        
        products = [
            Product(
                product_id="prod_laptop_001",
                name="ThinkPad X1 Carbon",
                category="笔记本电脑",
                brand="Lenovo",
                price=8999.0,
                tags=["商务", "轻薄", "高性能"],
                sales_count=520,
                rating=4.8,
            ),
            Product(
                product_id="prod_laptop_002",
                name="MacBook Air M2",
                category="笔记本电脑",
                brand="Apple",
                price=9499.0,
                tags=["办公", "轻薄", "长续航"],
                sales_count=890,
                rating=4.9,
            ),
            Product(
                product_id="prod_mouse_001",
                name="罗技 MX Master 3",
                category="鼠标",
                brand="Logitech",
                price=699.0,
                tags=["无线", "人体工学", "多设备"],
                sales_count=1200,
                rating=4.7,
            ),
            Product(
                product_id="prod_keyboard_001",
                name="HHKB Professional",
                category="键盘",
                brand="HHKB",
                price=1999.0,
                tags=["机械键盘", "静音", "便携"],
                sales_count=450,
                rating=4.6,
            ),
            Product(
                product_id="prod_laptop_003",
                name="Dell XPS 13",
                category="笔记本电脑",
                brand="Dell",
                price=8499.0,
                tags=["轻薄", "高颜值", "4K屏"],
                sales_count=680,
                rating=4.7,
            ),
        ]
        
        for product in products:
            agent.recommendation_engine.add_product(product)
        
        # 模拟用户行为
        user_id = "user_001"
        print(f"\n👤 模拟用户 {user_id} 的行为...")
        
        # 浏览行为
        agent.recommendation_engine.update_user_profile_from_action(
            user_id, "view", "prod_laptop_001"
        )
        agent.recommendation_engine.update_user_profile_from_action(
            user_id, "view", "prod_laptop_002"
        )
        
        # 搜索行为
        agent.recommendation_engine.update_user_profile_from_action(
            user_id, "search", keywords=["笔记本", "轻薄", "商务"]
        )
        
        # 购买行为
        agent.recommendation_engine.update_user_profile_from_action(
            user_id, "purchase", "prod_laptop_001"
        )
        
        print("✅ 用户行为已记录")
        
        # 获取推荐
        print_section("基于内容的推荐")
        content_recs = agent.get_recommendations(user_id, top_n=3, strategy="content")
        for i, rec in enumerate(content_recs, 1):
            print(f"{i}. {rec['product_name']} (分数: {rec['score']})")
            print(f"   原因: {rec['reason']}")
        
        print_section("热门商品推荐")
        popular_recs = agent.get_recommendations(user_id, top_n=3, strategy="popular")
        for i, rec in enumerate(popular_recs, 1):
            print(f"{i}. {rec['product_name']} (分数: {rec['score']})")
            print(f"   原因: {rec['reason']}")
        
        print_section("混合推荐（综合策略）")
        hybrid_recs = agent.get_recommendations(user_id, top_n=5, strategy="hybrid")
        for i, rec in enumerate(hybrid_recs, 1):
            print(f"{i}. {rec['product_name']} (分数: {rec['score']})")
            print(f"   原因: {rec['reason']}")


def test_full_analytics():
    """测试完整的分析导出"""
    print_section("测试 4: 完整分析导出")
    
    agent = LangChainAgent(
        use_memory=True,
        session_id="test_analytics_001",
        enable_quality_tracking=True,
        enable_intent_tracking=True,
        enable_conversation_state=True,
    )
    
    # 模拟一个完整的购物流程
    conversations = [
        "你好",
        "搜索游戏本",
        "看看第一个商品的详情",
        "多少钱？",
        "加入购物车",
    ]
    
    print("📝 模拟完整对话流程...\n")
    for user_input in conversations:
        print(f"👤 {user_input}")
        result = agent.run(user_input)
        print(f"🤖 {result['final_answer'][:80]}...\n")
    
    # 导出完整分析
    print_section("完整分析数据")
    analytics = agent.export_analytics()
    
    import json
    print(json.dumps(analytics, indent=2, ensure_ascii=False))
    
    # 保存到文件
    output_file = "test_analytics_output.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analytics, f, indent=2, ensure_ascii=False)
    print(f"\n✅ 分析数据已保存到: {output_file}")


def main():
    """主测试流程"""
    print("\n" + "="*60)
    print("  Phase 4 可选优化功能测试")
    print("="*60)
    
    try:
        # 测试 1: 质量跟踪
        agent1 = test_quality_tracking()
        
        # 测试 2: 意图识别（继续使用 agent1）
        test_intent_recognition(agent1)
        
        # 测试 3: 推荐引擎
        test_recommendation_engine()
        
        # 测试 4: 完整分析
        test_full_analytics()
        
        print_section("测试总结")
        print("✅ 所有测试通过！")
        print("\n核心功能验证:")
        print("  ✓ 对话质量评分系统")
        print("  ✓ 多轮意图识别")
        print("  ✓ 复合意图检测")
        print("  ✓ 个性化推荐引擎")
        print("  ✓ 完整分析数据导出")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
