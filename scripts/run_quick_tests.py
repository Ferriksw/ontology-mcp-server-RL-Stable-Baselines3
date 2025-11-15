#!/usr/bin/env python3
"""
Copyright (c) 2025 shark8848
MIT License

Ontology MCP Server - 电商 AI 助手系统
Author: shark8848
Repository: https://github.com/shark8848/ontology-mcp-server
"""

"""快速运行关键断言，代替 pytest 环境（用于 CI/本地验证）。"""
import sys

from ontology_mcp_server.ontology_service import OntologyService
from ontology_mcp_server.shacl_service import validate_order


def fail(msg: str):
    print("FAIL:", msg)
    sys.exit(2)


def main():
    svc = OntologyService()

    # test_explain_discount_infers_rule
    hit, rate, rule = svc.explain_discount(is_vip=True, amount=1200)
    if not (hit is True and rate == 0.1 and "discount" in rule):
        fail("explain_discount inference failed")
    miss, miss_rate, _ = svc.explain_discount(is_vip=False, amount=800)
    if not (miss is False and miss_rate == 0.0):
        fail("explain_discount miss case failed")

    # test_normalize_product_uses_synonyms
    info = svc.normalize_product("客户想要最新的苹果智能手机并要求加急")
    if not (info.get("canonical_name") == "Smartphone"):
        fail("normalize_product canonical_name mismatch")

    # test_shacl_validation_detects_violations (basic)
    valid_ttl = """
        @prefix : <http://example.com/commerce#> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

        :order1 a :Order ;
            :hasCustomer :cust1 ;
            :hasItem :item1 ;
            :totalAmount "1200"^^xsd:decimal ;
            :discountRate "0.1"^^xsd:decimal .

        :cust1 a :VIPCustomer .

        :item1 a :OrderItem ;
            :hasProduct :product1 .

        :product1 a :Product .
    """
    conforms, report = validate_order(valid_ttl)
    if not conforms:
        fail("shacl valid case did not conform")

    print("ALL QUICK CHECKS PASSED")


if __name__ == "__main__":
    main()
