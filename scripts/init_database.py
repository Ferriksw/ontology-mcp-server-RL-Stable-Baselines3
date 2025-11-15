#!/usr/bin/env python3
"""
Copyright (c) 2025 shark8848
MIT License

Ontology MCP Server - 电商 AI 助手系统
Author: shark8848
Repository: https://github.com/shark8848/ontology-mcp-server
"""

"""
数据库初始化脚本

自动创建数据库表结构
"""
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ontology_mcp_server.db_service import EcommerceService


def main():
    """初始化数据库"""
    print("🚀 开始初始化电商数据库...\n")
    
    # 创建服务实例
    service = EcommerceService(db_path="data/ecommerce.db")
    
    # 创建表
    service.init_database()
    
    print("✅ 数据库表结构已创建!")
    print(f"📁 数据库文件: data/ecommerce.db")
    print("\n📊 创建的表:")
    print("  - users (用户表)")
    print("  - products (商品表)")
    print("  - cart_items (购物车表)")
    print("  - orders (订单表)")
    print("  - order_items (订单明细表)")
    print("  - payments (支付表)")
    print("  - shipments (物流表)")
    print("  - shipment_tracks (物流轨迹表)")
    print("  - support_tickets (客服工单表)")
    print("  - support_messages (客服消息表)")
    print("  - returns (退换货表)")
    print("  - reviews (商品评价表)")
    print("\n💡 下一步: 运行 python scripts/seed_data.py 填充示例数据")


if __name__ == "__main__":
    main()
