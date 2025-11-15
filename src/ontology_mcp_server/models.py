"""
Copyright (c) 2025 shark8848
MIT License

Ontology MCP Server - 电商 AI 助手系统
本体推理 + 电商业务逻辑 + 对话记忆 + 可视化 UI

Author: shark8848
Repository: https://github.com/shark8848/ontology-mcp-server
"""

"""
SQLAlchemy ORM 模型定义 - 电商数据库表结构

采用面向对象设计，每个类对应一张数据库表，封装原子级操作。
"""
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
import json

from sqlalchemy import (
    Column, Integer, String, DateTime, Numeric,
    Boolean, Text, ForeignKey, JSON, create_engine
)
from sqlalchemy.orm import declarative_base, relationship, Session
from sqlalchemy.pool import StaticPool

Base = declarative_base()


# ============ 用户相关模型 ============

class User(Base):
    """用户模型"""
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100))
    phone = Column(String(20))
    user_level = Column(String(20), default='Regular')  # Regular/VIP/SVIP
    registration_date = Column(DateTime, default=datetime.now)
    total_spent = Column(Numeric(10, 2), default=0)
    credit_score = Column(Integer, default=100)
    
    # 关联关系
    orders = relationship("Order", back_populates="user")
    cart_items = relationship("CartItem", back_populates="user")
    support_tickets = relationship("SupportTicket", back_populates="user")
    returns = relationship("Return", back_populates="user")
    reviews = relationship("Review", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.user_id}, username='{self.username}', level='{self.user_level}')>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'phone': self.phone,
            'user_level': self.user_level,
            'registration_date': self.registration_date.isoformat() if self.registration_date else None,
            'total_spent': float(self.total_spent) if self.total_spent else 0,
            'credit_score': self.credit_score
        }


# ============ 商品相关模型 ============

class Product(Base):
    """商品模型"""
    __tablename__ = 'products'
    
    product_id = Column(Integer, primary_key=True, autoincrement=True)
    product_name = Column(String(200), nullable=False)
    category = Column(String(50), index=True)  # 手机/配件/服务
    brand = Column(String(50))
    model = Column(String(100))
    price = Column(Numeric(10, 2), nullable=False)
    stock_quantity = Column(Integer, default=0)
    description = Column(Text)
    specs = Column(JSON)  # 规格参数 {"color": "黑色", "memory": "256GB"}
    image_url = Column(String(500))
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    
    # 关联关系
    order_items = relationship("OrderItem", back_populates="product")
    cart_items = relationship("CartItem", back_populates="product")
    reviews = relationship("Review", back_populates="product")
    
    def __repr__(self):
        return f"<Product(id={self.product_id}, name='{self.product_name}', price={self.price})>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            'product_id': self.product_id,
            'product_name': self.product_name,
            'category': self.category,
            'brand': self.brand,
            'model': self.model,
            'price': float(self.price) if self.price else 0,
            'stock_quantity': self.stock_quantity,
            'description': self.description,
            'specs': self.specs,
            'image_url': self.image_url,
            'is_available': self.is_available,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# ============ 购物车模型 ============

class CartItem(Base):
    """购物车项模型"""
    __tablename__ = 'cart_items'
    
    cart_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.product_id'), nullable=False)
    quantity = Column(Integer, default=1)
    added_at = Column(DateTime, default=datetime.now)
    
    # 关联关系
    user = relationship("User", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items")
    
    def __repr__(self):
        return f"<CartItem(user_id={self.user_id}, product_id={self.product_id}, qty={self.quantity})>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            'cart_id': self.cart_id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'added_at': self.added_at.isoformat() if self.added_at else None,
            'product': self.product.to_dict() if self.product else None
        }


# ============ 订单相关模型 ============

class Order(Base):
    """订单模型"""
    __tablename__ = 'orders'
    
    order_id = Column(Integer, primary_key=True, autoincrement=True)
    order_no = Column(String(50), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    total_amount = Column(Numeric(10, 2))
    discount_amount = Column(Numeric(10, 2), default=0)
    final_amount = Column(Numeric(10, 2))
    order_status = Column(String(20), default='pending')  # pending/paid/shipped/delivered/cancelled
    payment_status = Column(String(20), default='unpaid')  # unpaid/paid/refunded
    shipping_address = Column(Text)
    contact_phone = Column(String(20))
    created_at = Column(DateTime, default=datetime.now)
    paid_at = Column(DateTime)
    shipped_at = Column(DateTime)
    delivered_at = Column(DateTime)
    
    # 关联关系
    user = relationship("User", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="order")
    shipments = relationship("Shipment", back_populates="order")
    support_tickets = relationship("SupportTicket", back_populates="order")
    returns = relationship("Return", back_populates="order")
    
    def __repr__(self):
        return f"<Order(no='{self.order_no}', user_id={self.user_id}, status='{self.order_status}')>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            'order_id': self.order_id,
            'order_no': self.order_no,
            'user_id': self.user_id,
            'total_amount': float(self.total_amount) if self.total_amount else 0,
            'discount_amount': float(self.discount_amount) if self.discount_amount else 0,
            'final_amount': float(self.final_amount) if self.final_amount else 0,
            'order_status': self.order_status,
            'payment_status': self.payment_status,
            'shipping_address': self.shipping_address,
            'contact_phone': self.contact_phone,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'paid_at': self.paid_at.isoformat() if self.paid_at else None,
            'shipped_at': self.shipped_at.isoformat() if self.shipped_at else None,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None,
            'items': [item.to_dict() for item in self.order_items] if self.order_items else []
        }


class OrderItem(Base):
    """订单明细模型"""
    __tablename__ = 'order_items'
    
    item_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.order_id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.product_id'), nullable=False)
    product_name = Column(String(200))
    quantity = Column(Integer)
    unit_price = Column(Numeric(10, 2))
    subtotal = Column(Numeric(10, 2))
    
    # 关联关系
    order = relationship("Order", back_populates="order_items")
    product = relationship("Product", back_populates="order_items")
    
    def __repr__(self):
        return f"<OrderItem(order_id={self.order_id}, product='{self.product_name}', qty={self.quantity})>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            'item_id': self.item_id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'product_name': self.product_name,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price) if self.unit_price else 0,
            'subtotal': float(self.subtotal) if self.subtotal else 0
        }


# ============ 支付模型 ============

class Payment(Base):
    """支付模型"""
    __tablename__ = 'payments'
    
    payment_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.order_id'), nullable=False)
    payment_method = Column(String(20))  # alipay/wechat/credit_card/apple_pay
    payment_amount = Column(Numeric(10, 2))
    payment_status = Column(String(20), default='pending')  # pending/success/failed
    transaction_id = Column(String(100), unique=True)
    payment_time = Column(DateTime)
    
    # 关联关系
    order = relationship("Order", back_populates="payments")
    
    def __repr__(self):
        return f"<Payment(order_id={self.order_id}, method='{self.payment_method}', status='{self.payment_status}')>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            'payment_id': self.payment_id,
            'order_id': self.order_id,
            'payment_method': self.payment_method,
            'payment_amount': float(self.payment_amount) if self.payment_amount else 0,
            'payment_status': self.payment_status,
            'transaction_id': self.transaction_id,
            'payment_time': self.payment_time.isoformat() if self.payment_time else None
        }


# ============ 物流模型 ============

class Shipment(Base):
    """物流模型"""
    __tablename__ = 'shipments'
    
    shipment_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.order_id'), nullable=False)
    tracking_no = Column(String(50), unique=True)
    carrier = Column(String(50))  # 顺丰/京东/圆通
    current_status = Column(String(50))
    current_location = Column(String(200))
    estimated_delivery = Column(DateTime)
    shipped_at = Column(DateTime)
    delivered_at = Column(DateTime)
    
    # 关联关系
    order = relationship("Order", back_populates="shipments")
    tracks = relationship("ShipmentTrack", back_populates="shipment", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Shipment(tracking='{self.tracking_no}', status='{self.current_status}')>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            'shipment_id': self.shipment_id,
            'order_id': self.order_id,
            'tracking_no': self.tracking_no,
            'carrier': self.carrier,
            'current_status': self.current_status,
            'current_location': self.current_location,
            'estimated_delivery': self.estimated_delivery.isoformat() if self.estimated_delivery else None,
            'shipped_at': self.shipped_at.isoformat() if self.shipped_at else None,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None,
            'tracks': [track.to_dict() for track in self.tracks] if self.tracks else []
        }


class ShipmentTrack(Base):
    """物流轨迹模型"""
    __tablename__ = 'shipment_tracks'
    
    track_id = Column(Integer, primary_key=True, autoincrement=True)
    shipment_id = Column(Integer, ForeignKey('shipments.shipment_id'), nullable=False)
    status = Column(String(50))
    location = Column(String(200))
    description = Column(Text)
    track_time = Column(DateTime, default=datetime.now)
    
    # 关联关系
    shipment = relationship("Shipment", back_populates="tracks")
    
    def __repr__(self):
        return f"<ShipmentTrack(shipment_id={self.shipment_id}, status='{self.status}')>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            'track_id': self.track_id,
            'shipment_id': self.shipment_id,
            'status': self.status,
            'location': self.location,
            'description': self.description,
            'track_time': self.track_time.isoformat() if self.track_time else None
        }


# ============ 客服模型 ============

class SupportTicket(Base):
    """客服工单模型"""
    __tablename__ = 'support_tickets'
    
    ticket_id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_no = Column(String(50), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    order_id = Column(Integer, ForeignKey('orders.order_id'))
    category = Column(String(50))  # 售前/售后/投诉/退换货
    priority = Column(String(20), default='medium')  # low/medium/high/urgent
    status = Column(String(20), default='open')  # open/processing/resolved/closed
    subject = Column(String(200))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    resolved_at = Column(DateTime)
    
    # 关联关系
    user = relationship("User", back_populates="support_tickets")
    order = relationship("Order", back_populates="support_tickets")
    messages = relationship("SupportMessage", back_populates="ticket", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<SupportTicket(no='{self.ticket_no}', status='{self.status}')>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            'ticket_id': self.ticket_id,
            'ticket_no': self.ticket_no,
            'user_id': self.user_id,
            'order_id': self.order_id,
            'category': self.category,
            'priority': self.priority,
            'status': self.status,
            'subject': self.subject,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'messages': [msg.to_dict() for msg in self.messages] if self.messages else []
        }


class SupportMessage(Base):
    """客服消息模型"""
    __tablename__ = 'support_messages'
    
    message_id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(Integer, ForeignKey('support_tickets.ticket_id'), nullable=False)
    sender_type = Column(String(20))  # customer/agent/system
    sender_id = Column(Integer)
    message_content = Column(Text)
    sent_at = Column(DateTime, default=datetime.now)
    
    # 关联关系
    ticket = relationship("SupportTicket", back_populates="messages")
    
    def __repr__(self):
        return f"<SupportMessage(ticket_id={self.ticket_id}, sender='{self.sender_type}')>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            'message_id': self.message_id,
            'ticket_id': self.ticket_id,
            'sender_type': self.sender_type,
            'sender_id': self.sender_id,
            'message_content': self.message_content,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None
        }


# ============ 退换货模型 ============

class Return(Base):
    """退换货模型"""
    __tablename__ = 'returns'
    
    return_id = Column(Integer, primary_key=True, autoincrement=True)
    return_no = Column(String(50), unique=True, nullable=False)
    order_id = Column(Integer, ForeignKey('orders.order_id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    return_type = Column(String(20))  # return/exchange
    reason = Column(String(200))
    status = Column(String(20), default='pending')  # pending/approved/rejected/completed
    refund_amount = Column(Numeric(10, 2))
    created_at = Column(DateTime, default=datetime.now)
    processed_at = Column(DateTime)
    
    # 关联关系
    user = relationship("User", back_populates="returns")
    order = relationship("Order", back_populates="returns")
    
    def __repr__(self):
        return f"<Return(no='{self.return_no}', type='{self.return_type}', status='{self.status}')>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            'return_id': self.return_id,
            'return_no': self.return_no,
            'order_id': self.order_id,
            'user_id': self.user_id,
            'return_type': self.return_type,
            'reason': self.reason,
            'status': self.status,
            'refund_amount': float(self.refund_amount) if self.refund_amount else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None
        }


# ============ 商品评价模型 ============

class Review(Base):
    """商品评价模型"""
    __tablename__ = 'reviews'
    
    review_id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.product_id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    order_id = Column(Integer, ForeignKey('orders.order_id'))
    rating = Column(Integer)  # 1-5星
    content = Column(Text)
    images = Column(JSON)  # 评价图片列表
    created_at = Column(DateTime, default=datetime.now)
    
    # 关联关系
    product = relationship("Product", back_populates="reviews")
    user = relationship("User", back_populates="reviews")
    
    def __repr__(self):
        return f"<Review(product_id={self.product_id}, rating={self.rating})>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            'review_id': self.review_id,
            'product_id': self.product_id,
            'user_id': self.user_id,
            'order_id': self.order_id,
            'rating': self.rating,
            'content': self.content,
            'images': self.images,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
