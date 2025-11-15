from __future__ import annotations
# Copyright (c) 2025 shark8848
# MIT License
#
# Ontology MCP Server - 电商 AI 助手系统
# Author: shark8848
# Repository: https://github.com/shark8848/ontology-mcp-server

"""涵盖本体推理、同义词归一与 SHACL 校验的核心测试。"""

from ontology_mcp_server.ontology_service import OntologyService
from ontology_mcp_server.shacl_service import validate_order


def test_explain_discount_infers_rule() -> None:
    service = OntologyService()

    hit, rate, rule = service.explain_discount(is_vip=True, amount=1200)

    assert hit is True
    assert rate == 0.1
    assert "discount" in rule

    miss, miss_rate, _ = service.explain_discount(is_vip=False, amount=800)

    assert miss is False
    assert miss_rate == 0.0


def test_normalize_product_uses_synonyms() -> None:
    service = OntologyService()

    info = service.normalize_product("客户想要最新的苹果智能手机并要求加急")

    assert info["canonical_name"] == "Smartphone"
    assert info["uri"] == "http://example.com/commerce#Smartphone"
    assert info["matched_synonym"] in {"智能手机", "手机", "smartphone", "phone", "mobile phone", "cellphone"}


def test_shacl_validation_detects_violations() -> None:
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
    assert conforms is True
    assert "Validation Report" in report

    invalid_ttl = """
        @prefix : <http://example.com/commerce#> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

        :order_bad a :Order ;
            :hasCustomer :cust_bad ;
            :hasItem :item_bad ;
            :totalAmount "500"^^xsd:decimal ;
            :discountRate "1.5"^^xsd:decimal .

        :cust_bad a :Customer .

        :item_bad a :OrderItem .
    """
    invalid_conforms, invalid_report = validate_order(invalid_ttl)
    assert invalid_conforms is False
    assert "1.5" in invalid_report or "maxInclusive" in invalid_report
