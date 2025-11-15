#!/usr/bin/env python3
"""
Copyright (c) 2025 shark8848
MIT License

Ontology MCP Server - 电商 AI 助手系统
Author: shark8848
Repository: https://github.com/shark8848/ontology-mcp-server
"""

"""
示例数据填充脚本

填充电商系统的测试数据，包括用户、商品、订单等
"""
import sys
import os
from decimal import Decimal
from datetime import datetime, timedelta

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ontology_mcp_server.db_service import EcommerceService


def seed_users(service: EcommerceService):
    """填充用户数据"""
    print("👥 创建用户...")
    
    users_data = [
        {"username": "张三", "email": "zhangsan@example.com", "phone": "13800138001", "user_level": "Regular"},
        {"username": "李四", "email": "lisi@example.com", "phone": "13800138002", "user_level": "VIP"},
        {"username": "王五", "email": "wangwu@example.com", "phone": "13800138003", "user_level": "SVIP"},
        {"username": "赵六", "email": "zhaoliu@example.com", "phone": "13800138004", "user_level": "Regular"},
        {"username": "钱七", "email": "qianqi@example.com", "phone": "13800138005", "user_level": "VIP"},
    ]
    
    created_users = []
    for data in users_data:
        user = service.users.create_user(**data)
        created_users.append(user)
        print(f"  ✓ {user.username} ({user.user_level})")
    
    # 更新部分用户的累计消费
    service.users.update_total_spent(2, Decimal('6500'))  # 李四 VIP
    service.users.update_total_spent(3, Decimal('12000'))  # 王五 SVIP
    
    return created_users


def seed_products(service: EcommerceService):
    """填充商品数据"""
    print("\n📱 创建商品...")
    
    products_data = [
        # iPhone 系列
        {
            "product_name": "iPhone 15 Pro Max",
            "category": "手机",
            "brand": "Apple",
            "model": "A3108",
            "price": Decimal("9999"),
            "stock_quantity": 50,
            "description": "6.7英寸超视网膜XDR显示屏，A17 Pro芯片，钛金属设计",
            "specs": {"color": "原色钛金属", "memory": "8GB", "storage": "256GB"},
            "image_url": "https://example.com/iphone15promax.jpg"
        },
        {
            "product_name": "iPhone 15 Pro",
            "category": "手机",
            "brand": "Apple",
            "model": "A3102",
            "price": Decimal("8999"),
            "stock_quantity": 80,
            "description": "6.1英寸超视网膜XDR显示屏，A17 Pro芯片",
            "specs": {"color": "黑色钛金属", "memory": "8GB", "storage": "256GB"},
            "image_url": "https://example.com/iphone15pro.jpg"
        },
        {
            "product_name": "iPhone 15",
            "category": "手机",
            "brand": "Apple",
            "model": "A3089",
            "price": Decimal("5999"),
            "stock_quantity": 100,
            "description": "6.1英寸超视网膜XDR显示屏，A16仿生芯片",
            "specs": {"color": "蓝色", "memory": "6GB", "storage": "128GB"},
            "image_url": "https://example.com/iphone15.jpg"
        },
        {
            "product_name": "iPhone 14 Pro",
            "category": "手机",
            "brand": "Apple",
            "model": "A2890",
            "price": Decimal("7999"),
            "stock_quantity": 60,
            "description": "6.1英寸灵动岛屏幕，A16仿生芯片",
            "specs": {"color": "深空黑色", "memory": "6GB", "storage": "256GB"},
            "image_url": "https://example.com/iphone14pro.jpg"
        },
        
        # 配件
        {
            "product_name": "AirPods Pro 2",
            "category": "配件",
            "brand": "Apple",
            "model": "MTJV3CH/A",
            "price": Decimal("1899"),
            "stock_quantity": 200,
            "description": "主动降噪，自适应通透模式，空间音频",
            "specs": {"color": "白色", "type": "入耳式"},
            "image_url": "https://example.com/airpodspro2.jpg"
        },
        {
            "product_name": "MagSafe充电器",
            "category": "配件",
            "brand": "Apple",
            "model": "MHXH3FE/A",
            "price": Decimal("329"),
            "stock_quantity": 300,
            "description": "15W无线充电，完美适配iPhone",
            "specs": {"type": "无线充电器", "power": "15W"},
            "image_url": "https://example.com/magsafe.jpg"
        },
        {
            "product_name": "iPhone硅胶保护壳",
            "category": "配件",
            "brand": "Apple",
            "model": "MT0Y3FE/A",
            "price": Decimal("399"),
            "stock_quantity": 500,
            "description": "柔滑硅胶材质，完美贴合",
            "specs": {"color": "午夜色", "model": "iPhone 15 Pro"},
            "image_url": "https://example.com/case.jpg"
        },
        
        # AppleCare+ 服务
        {
            "product_name": "AppleCare+ 服务计划",
            "category": "服务",
            "brand": "Apple",
            "model": "S6367LL/A",
            "price": Decimal("1398"),
            "stock_quantity": 9999,
            "description": "2年意外损坏保障，优先技术支持",
            "specs": {"duration": "2年", "coverage": "意外损坏"},
            "image_url": "https://example.com/applecare.jpg"
        },
    ]
    
    created_products = []
    for data in products_data:
        product = service.products.create_product(**data)
        created_products.append(product)
        print(f"  ✓ {product.product_name} - ¥{product.price}")
    
    return created_products


def seed_orders_and_related(service: EcommerceService, users, products):
    """填充订单及相关数据"""
    print("\n📦 创建订单...")
    
    # 订单1: 李四购买iPhone 15 Pro Max
    order1_items = [
        {
            "product_id": products[0].product_id,
            "product_name": products[0].product_name,
            "quantity": 1,
            "unit_price": products[0].price
        },
        {
            "product_id": products[4].product_id,  # AirPods Pro 2
            "product_name": products[4].product_name,
            "quantity": 1,
            "unit_price": products[4].price
        }
    ]
    
    order1 = service.orders.create_order(
        user_id=users[1].user_id,  # 李四
        items=order1_items,
        shipping_address="北京市朝阳区xxx路xxx号",
        contact_phone="13800138002",
        discount_amount=Decimal("500")  # VIP折扣
    )
    print(f"  ✓ 订单 {order1.order_no} - 李四 - ¥{order1.final_amount}")
    
    # 创建支付记录
    payment1 = service.payments.create_payment(
        order_id=order1.order_id,
        payment_method="alipay",
        payment_amount=order1.final_amount
    )
    service.payments.update_payment_status(payment1.payment_id, "success")
    service.orders.update_payment_status(order1.order_id, "paid")
    service.orders.update_order_status(order1.order_id, "paid")
    print(f"    💳 支付成功 - 支付宝")
    
    # 创建物流记录
    shipment1 = service.shipments.create_shipment(
        order_id=order1.order_id,
        carrier="顺丰速运",
        estimated_delivery=datetime.now() + timedelta(days=2)
    )
    service.shipments.add_track(shipment1.shipment_id, "已揽收", "北京分拨中心", "快件已被揽收")
    service.shipments.add_track(shipment1.shipment_id, "运输中", "上海转运中心", "快件正在运输途中")
    service.orders.update_order_status(order1.order_id, "shipped")
    print(f"    🚚 物流单号: {shipment1.tracking_no}")
    
    # 订单2: 王五购买iPhone 15 Pro
    order2_items = [
        {
            "product_id": products[1].product_id,
            "product_name": products[1].product_name,
            "quantity": 1,
            "unit_price": products[1].price
        },
        {
            "product_id": products[7].product_id,  # AppleCare+
            "product_name": products[7].product_name,
            "quantity": 1,
            "unit_price": products[7].price
        }
    ]
    
    order2 = service.orders.create_order(
        user_id=users[2].user_id,  # 王五
        items=order2_items,
        shipping_address="上海市浦东新区xxx街xxx号",
        contact_phone="13800138003",
        discount_amount=Decimal("1000")  # SVIP折扣
    )
    print(f"  ✓ 订单 {order2.order_no} - 王五 - ¥{order2.final_amount}")
    
    # 支付并发货
    payment2 = service.payments.create_payment(
        order_id=order2.order_id,
        payment_method="wechat",
        payment_amount=order2.final_amount
    )
    service.payments.update_payment_status(payment2.payment_id, "success")
    service.orders.update_payment_status(order2.order_id, "paid")
    service.orders.update_order_status(order2.order_id, "paid")
    print(f"    💳 支付成功 - 微信支付")
    
    shipment2 = service.shipments.create_shipment(
        order_id=order2.order_id,
        carrier="京东物流",
        estimated_delivery=datetime.now() + timedelta(days=1)
    )
    service.shipments.add_track(shipment2.shipment_id, "已揽收", "上海仓库", "快件已出库")
    service.shipments.add_track(shipment2.shipment_id, "派送中", "上海浦东新区", "快件正在派送中")
    service.shipments.add_track(shipment2.shipment_id, "已签收", "上海浦东新区", "快件已签收")
    service.orders.update_order_status(order2.order_id, "delivered")
    print(f"    🚚 物流单号: {shipment2.tracking_no} (已签收)")
    
    # 订单3: 张三购买iPhone 15
    order3_items = [
        {
            "product_id": products[2].product_id,
            "product_name": products[2].product_name,
            "quantity": 1,
            "unit_price": products[2].price
        },
        {
            "product_id": products[6].product_id,  # 保护壳
            "product_name": products[6].product_name,
            "quantity": 1,
            "unit_price": products[6].price
        }
    ]
    
    order3 = service.orders.create_order(
        user_id=users[0].user_id,  # 张三
        items=order3_items,
        shipping_address="广州市天河区xxx路xxx号",
        contact_phone="13800138001",
        discount_amount=Decimal("0")  # 普通用户无折扣
    )
    print(f"  ✓ 订单 {order3.order_no} - 张三 - ¥{order3.final_amount} (待支付)")
    
    return [order1, order2, order3]


def seed_cart_items(service: EcommerceService, users, products):
    """填充购物车数据"""
    print("\n🛒 创建购物车...")
    
    # 赵六的购物车
    service.cart.add_to_cart(users[3].user_id, products[3].product_id, 1)  # iPhone 14 Pro
    service.cart.add_to_cart(users[3].user_id, products[4].product_id, 1)  # AirPods Pro 2
    print(f"  ✓ 赵六的购物车: 2件商品")
    
    # 钱七的购物车
    service.cart.add_to_cart(users[4].user_id, products[0].product_id, 1)  # iPhone 15 Pro Max
    service.cart.add_to_cart(users[4].user_id, products[5].product_id, 2)  # MagSafe充电器 x2
    service.cart.add_to_cart(users[4].user_id, products[6].product_id, 1)  # 保护壳
    print(f"  ✓ 钱七的购物车: 3种商品")


def main():
    """主函数"""
    print("🌱 开始填充电商示例数据...\n")
    
    # 创建服务实例
    service = EcommerceService(db_path="data/ecommerce.db")
    
    # 填充数据
    users = seed_users(service)
    products = seed_products(service)
    orders = seed_orders_and_related(service, users, products)
    seed_cart_items(service, users, products)
    
    print("\n" + "="*60)
    print("✅ 示例数据填充完成!")
    print("="*60)
    print(f"\n📊 数据统计:")
    print(f"  👥 用户: {len(users)} 个")
    print(f"  📱 商品: {len(products)} 个")
    print(f"  📦 订单: {len(orders)} 个")
    print(f"  🛒 购物车: 2个用户有商品")
    
    print(f"\n💡 测试建议:")
    print(f"  - 用户 '李四' (user_id=2) 是VIP，有1个已发货订单")
    print(f"  - 用户 '王五' (user_id=3) 是SVIP，有1个已签收订单")
    print(f"  - 用户 '张三' (user_id=1) 是普通用户，有1个待支付订单")
    print(f"  - 用户 '赵六' (user_id=4) 的购物车有2件商品")
    print(f"\n🚀 现在可以启动Agent进行对话测试!")


if __name__ == "__main__":
    main()
