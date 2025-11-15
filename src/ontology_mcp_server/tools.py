from __future__ import annotations
# Copyright (c) 2025 shark8848
# MIT License
#
# Ontology MCP Server - 电商 AI 助手系统
# 本体推理 + 电商业务逻辑 + 对话记忆 + 可视化 UI
#
# Author: shark8848
# Repository: https://github.com/shark8848/ontology-mcp-server
"""将 MCP 能力包装为可被 agent 调用的工具，并记录每次调用的输入/输出以便 UI 展示。"""

import json
import traceback
from decimal import Decimal
import re
from typing import Any, Dict, List, Tuple

from .capabilities import capability_names
from .commerce_service import CommerceService
from .ontology_service import get_ontology_service
from .shacl_service import validate_order
from .logger import get_logger

logger = get_logger(__name__)

# 全局调用日志（内存），每次调用会 append 一条记录。UI 可以读取此列表展示工具调用细节。
tool_call_log: List[Dict[str, Any]] = []

_commerce_service: CommerceService | None = None


def get_commerce_service() -> CommerceService:
    global _commerce_service
    if _commerce_service is None:
        _commerce_service = CommerceService()
    return _commerce_service


def _log_tool_call(name: str, input_data: Any, output_data: Any, err: str | None = None) -> None:
    entry = {
        "tool": name,
        "input": input_data,
        "output": output_data,
        "error": err,
    }
    tool_call_log.append(entry)
    logger.info("工具调用: %s input=%s error=%s", name, str(input_data)[:200], bool(err))


_MAX_SQLITE_INT = 2**63 - 1
_ORDER_NUM_PATTERN = re.compile(r"(\d+)")


def _parse_order_id(raw: Any) -> int:
    """Normalize order id strings (e.g., ORD123...) and guard against overflow."""
    if raw is None:
        raise ValueError("order_id 不能为空")

    raw_str = str(raw).strip().upper()
    match = _ORDER_NUM_PATTERN.search(raw_str)
    if not match:
        raise ValueError("order_id 格式无效，请提供有效的数字编号或 ORD 前缀编号")

    digits = match.group(1)
    if len(digits) > 19 or (len(digits) == 19 and digits > str(_MAX_SQLITE_INT)):
        raise ValueError(
            "order_id 超出系统支持范围，请确认订单号是否正确后再试"
        )

    order_id = int(digits)
    if order_id <= 0:
        raise ValueError("order_id 必须是正整数")

    return order_id


def call_tool(name: str, payload: Dict[str, Any]) -> Tuple[bool, Any]:
    """通用工具调用入口。

    返回 (ok, result_or_error_message)
    """
    name = str(name)
    if name not in capability_names():
        err = f"未知工具: {name}"
        _log_tool_call(name, payload, None, err)
        return False, err

    try:
        if name.startswith("ontology."):
            svc = get_ontology_service()
            if name == "ontology.explain_discount":
                is_vip = bool(payload.get("is_vip"))
                amount = float(payload.get("amount", 0.0))
                hit, rate, source = svc.explain_discount(is_vip, amount)
                result = {
                    "discount_applied": hit,
                    "discount_rate": rate,
                    "rule_source": source,
                }
                _log_tool_call(name, payload, result)
                return True, result

            if name == "ontology.normalize_product":
                text = str(payload.get("text", ""))
                result = svc.normalize_product(text)
                _log_tool_call(name, payload, result)
                return True, result

            if name == "ontology.validate_order":
                data = payload.get("data")
                fmt = str(payload.get("format", "turtle")).lower()
                ok, report = validate_order(data, fmt)
                response = {"conforms": ok, "report": report}
                _log_tool_call(name, payload, response)
                return True, response

            err = f"工具未实现: {name}"
            _log_tool_call(name, payload, None, err)
            return False, err

        commerce = get_commerce_service()

        if name == "commerce.search_products":
            min_price = payload.get("min_price")
            max_price = payload.get("max_price")
            min_price_val = float(min_price) if min_price is not None else None
            max_price_val = float(max_price) if max_price is not None else None
            result = commerce.search_products(
                keyword=payload.get("keyword"),
                category=payload.get("category"),
                brand=payload.get("brand"),
                min_price=min_price_val,
                max_price=max_price_val,
                available_only=bool(payload.get("available_only", True)),
                limit=int(payload.get("limit", 20)),
            )
            _log_tool_call(name, payload, result)
            return True, result

        if name == "commerce.get_product_detail":
            product_id = int(payload.get("product_id"))
            result = commerce.get_product_detail(product_id)
            _log_tool_call(name, payload, result)
            return True, result

        if name == "commerce.check_stock":
            product_id = int(payload.get("product_id"))
            quantity = int(payload.get("quantity", 1))
            result = commerce.check_stock(product_id, quantity)
            _log_tool_call(name, payload, result)
            return True, result

        if name == "commerce.get_product_recommendations":
            result = commerce.get_product_recommendations(
                product_id=(int(payload["product_id"]) if payload.get("product_id") is not None else None),
                category=payload.get("category"),
                limit=int(payload.get("limit", 5)),
            )
            _log_tool_call(name, payload, result)
            return True, result

        if name == "commerce.get_product_reviews":
            product_id = int(payload.get("product_id"))
            limit = int(payload.get("limit", 10))
            result = commerce.get_product_reviews(product_id, limit)
            _log_tool_call(name, payload, result)
            return True, result

        if name == "commerce.add_to_cart":
            result = commerce.add_to_cart(
                user_id=int(payload.get("user_id")),
                product_id=int(payload.get("product_id")),
                quantity=int(payload.get("quantity", 1)),
            )
            _log_tool_call(name, payload, result)
            return True, result

        if name == "commerce.view_cart":
            result = commerce.view_cart(int(payload.get("user_id")))
            _log_tool_call(name, payload, result)
            return True, result

        if name == "commerce.remove_from_cart":
            result = commerce.remove_from_cart(
                user_id=int(payload.get("user_id")),
                product_id=int(payload.get("product_id")),
            )
            _log_tool_call(name, payload, result)
            return True, result

        if name == "commerce.create_order":
            result = commerce.create_order(
                user_id=int(payload.get("user_id")),
                items=list(payload.get("items", [])),
                shipping_address=str(payload.get("shipping_address", "")),
                contact_phone=str(payload.get("contact_phone", "")),
            )
            _log_tool_call(name, payload, result)
            return True, result

        if name == "commerce.get_order_detail":
            result = commerce.get_order_detail(_parse_order_id(payload.get("order_id")))
            _log_tool_call(name, payload, result)
            return True, result

        if name == "commerce.cancel_order":
            result = commerce.cancel_order(_parse_order_id(payload.get("order_id")))
            _log_tool_call(name, payload, result)
            return True, result

        if name == "commerce.get_user_orders":
            result = commerce.get_user_orders(
                user_id=int(payload.get("user_id")),
                status=payload.get("status"),
            )
            _log_tool_call(name, payload, result)
            return True, result

        if name == "commerce.process_payment":
            result = commerce.process_payment(
                order_id=_parse_order_id(payload.get("order_id")),
                payment_method=str(payload.get("payment_method", "")),
                amount=Decimal(str(payload.get("amount", 0))),
            )
            _log_tool_call(name, payload, result)
            return True, result

        if name == "commerce.track_shipment":
            result = commerce.track_shipment(str(payload.get("tracking_no", "")))
            _log_tool_call(name, payload, result)
            return True, result

        if name == "commerce.get_shipment_status":
            result = commerce.get_shipment_status(_parse_order_id(payload.get("order_id")))
            _log_tool_call(name, payload, result)
            return True, result

        if name == "commerce.create_support_ticket":
            result = commerce.create_support_ticket(
                user_id=int(payload.get("user_id")),
                subject=str(payload.get("subject", "")),
                description=str(payload.get("description", "")),
                order_id=(
                    _parse_order_id(payload.get("order_id"))
                    if payload.get("order_id") is not None
                    else None
                ),
                category=str(payload.get("category", "售后")),
                priority=str(payload.get("priority", "medium")),
                initial_message=payload.get("initial_message"),
            )
            _log_tool_call(name, payload, result)
            return True, result

        if name == "commerce.process_return":
            result = commerce.process_return(
                order_id=_parse_order_id(payload.get("order_id")),
                user_id=int(payload.get("user_id")),
                return_type=str(payload.get("return_type", "return")),
                reason=str(payload.get("reason", "")),
                product_category=str(payload.get("product_category", "手机")),
                is_activated=bool(payload.get("is_activated", False)),
            )
            _log_tool_call(name, payload, result)
            return True, result

        if name == "commerce.get_user_profile":
            result = commerce.get_user_profile(int(payload.get("user_id")))
            _log_tool_call(name, payload, result)
            return True, result

        err = f"工具未实现: {name}"
        _log_tool_call(name, payload, None, err)
        return False, err
    except Exception:  # 捕获异常并记录
        tb = traceback.format_exc()
        _log_tool_call(name, payload, None, tb)
        return False, tb


def get_tool_log() -> List[Dict[str, Any]]:
    return list(tool_call_log)
