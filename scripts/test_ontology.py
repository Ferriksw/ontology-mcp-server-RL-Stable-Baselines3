#!/usr/bin/env python3
"""
Copyright (c) 2025 shark8848
MIT License

Ontology MCP Server - 电商 AI 助手系统
Author: shark8848
Repository: https://github.com/shark8848/ontology-mcp-server
"""

"""
测试电商本体推理功能
"""
import sys
import os
from decimal import Decimal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ontology_mcp_server.ecommerce_ontology import EcommerceOntologyService


def test_user_level_inference():
    """测试用户等级推理"""
    print("=" * 60)
    print("🧠 测试用户等级推理")
    print("=" * 60)
    
    service = EcommerceOntologyService()
    
    test_cases = [
        (Decimal('3000'), 'Regular'),
        (Decimal('5000'), 'VIP'),
        (Decimal('8500'), 'VIP'),
        (Decimal('10000'), 'SVIP'),
        (Decimal('15000'), 'SVIP'),
    ]
    
    for spent, expected in test_cases:
        result = service.infer_user_level(spent)
        status = "✅" if result == expected else "❌"
        print(f"{status} 累计消费 ¥{spent} -> {result} (期望: {expected})")
    
    print()


def test_discount_inference():
    """测试折扣推理"""
    print("=" * 60)
    print("💰 测试折扣推理")
    print("=" * 60)
    
    service = EcommerceOntologyService()
    
    test_cases = [
        ("Regular", Decimal('3000'), False),
        ("VIP", Decimal('3000'), False),
        ("SVIP", Decimal('3000'), False),
        ("Regular", Decimal('6000'), False),
        ("VIP", Decimal('6000'), False),
        ("Regular", Decimal('12000'), False),
        ("SVIP", Decimal('12000'), False),
    ]
    
    for user_level, amount, is_first in test_cases:
        result = service.infer_discount(user_level, amount, is_first)
        print(f"\n用户等级: {user_level}, 订单金额: ¥{amount}")
        print(f"  折扣类型: {result['discount_type']}")
        print(f"  折扣率: {float(result['discount_rate']):.2f}")
        print(f"  折扣金额: ¥{result['discount_amount']:.2f}")
        print(f"  最终金额: ¥{result['final_amount']:.2f}")
        print(f"  理由: {result['reason']}")
    
    print()


def test_shipping_inference():
    """测试物流推理"""
    print("=" * 60)
    print("🚚 测试物流推理")
    print("=" * 60)
    
    service = EcommerceOntologyService()
    
    test_cases = [
        ("Regular", Decimal('300'), False),
        ("Regular", Decimal('600'), False),
        ("VIP", Decimal('300'), False),
        ("SVIP", Decimal('300'), False),
        ("Regular", Decimal('600'), True),  # 偏远地区
        ("SVIP", Decimal('300'), True),
    ]
    
    for user_level, amount, is_remote in test_cases:
        result = service.infer_shipping(user_level, amount, is_remote)
        area_str = "(偏远地区)" if is_remote else ""
        print(f"\n用户等级: {user_level}, 订单金额: ¥{amount} {area_str}")
        print(f"  运费: ¥{result['shipping_cost']}")
        print(f"  配送类型: {result['shipping_type']}")
        print(f"  包邮: {'是' if result['free_shipping'] else '否'}")
        print(f"  预计天数: {result['estimated_days']}天")
        print(f"  理由: {result['reason']}")
    
    print()


def test_return_policy():
    """测试退换货推理"""
    print("=" * 60)
    print("🔄 测试退换货推理")
    print("=" * 60)
    
    service = EcommerceOntologyService()
    
    test_cases = [
        ("Regular", "手机", False),
        ("Regular", "手机", True),
        ("VIP", "手机", False),
        ("Regular", "配件", False),
        ("Regular", "服务", False),
    ]
    
    for user_level, category, activated in test_cases:
        result = service.infer_return_policy(user_level, category, activated)
        activated_str = "(已激活)" if activated else "(未激活)"
        print(f"\n用户等级: {user_level}, 商品: {category} {activated_str if category == '手机' else ''}")
        print(f"  可退货: {'是' if result['returnable'] else '否'}")
        print(f"  退货期限: {result['return_period_days']}天")
        if result['conditions']:
            print(f"  退货条件: {', '.join(result['conditions'])}")
        print(f"  理由: {result['reason']}")
    
    print()


def test_comprehensive_inference():
    """测试综合推理"""
    print("=" * 60)
    print("🎯 测试综合订单推理")
    print("=" * 60)
    
    service = EcommerceOntologyService()
    
    # 模拟用户数据
    user_data = {
        'user_id': 1,
        'user_level': 'Regular',
        'total_spent': Decimal('8500'),  # 应该升级到VIP
        'order_count': 3
    }
    
    # 模拟订单数据
    order_data = {
        'order_amount': Decimal('6999'),
        'products': [
            {'product_id': 1, 'name': 'iPhone 15 Pro', 'price': 6999}
        ],
        'shipping_address': '北京市朝阳区xxx路xxx号'
    }
    
    result = service.infer_order_details(user_data, order_data)
    
    print(f"\n用户信息:")
    print(f"  原等级: {result['user_level_inference']['original_level']}")
    print(f"  推理等级: {result['user_level_inference']['inferred_level']}")
    print(f"  应升级: {'是' if result['user_level_inference']['should_upgrade'] else '否'}")
    
    print(f"\n折扣信息:")
    disc = result['discount_inference']
    print(f"  折扣类型: {disc['discount_type']}")
    print(f"  折扣率: {float(disc['discount_rate']):.2f}")
    print(f"  折扣金额: ¥{disc['discount_amount']:.2f}")
    
    print(f"\n物流信息:")
    ship = result['shipping_inference']
    print(f"  运费: ¥{ship['shipping_cost']}")
    print(f"  配送类型: {ship['shipping_type']}")
    print(f"  包邮: {'是' if ship['free_shipping'] else '否'}")
    
    print(f"\n订单汇总:")
    summary = result['final_summary']
    print(f"  原始金额: ¥{summary['original_amount']}")
    print(f"  折扣金额: ¥{summary['discount_amount']:.2f}")
    print(f"  小计: ¥{summary['subtotal']:.2f}")
    print(f"  运费: ¥{summary['shipping_cost']}")
    print(f"  应付总额: ¥{summary['total_payable']:.2f}")
    
    print()


def main():
    """主测试函数"""
    print("\n🧪 开始测试电商本体推理功能\n")
    
    try:
        test_user_level_inference()
        test_discount_inference()
        test_shipping_inference()
        test_return_policy()
        test_comprehensive_inference()
        
        print("=" * 60)
        print("✅ 所有测试完成!")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
