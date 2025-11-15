from __future__ import annotations
# Copyright (c) 2025 shark8848
# MIT License
#
# Ontology MCP Server - 电商 AI 助手系统
# 本体推理 + 电商业务逻辑 + 对话记忆 + 可视化 UI
#
# Author: shark8848
# Repository: https://github.com/shark8848/ontology-mcp-server
"""SHACL 校验服务。"""

from typing import Tuple

from rdflib import Graph

from .config import get_settings
from .logger import get_logger


logger = get_logger(__name__)


def validate_order(data: str, fmt: str = "turtle") -> Tuple[bool, str]:
    settings = get_settings()
    data_graph = Graph()
    try:
        if fmt == "json-ld":
            data_graph.parse(data=data, format="json-ld")
        else:
            data_graph.parse(data=data, format="turtle")
    except Exception as exc:
        logger.exception("解析输入数据图失败")
        return False, f"无法解析数据图: {exc}"
    if not settings.shapes_path.exists():
        logger.info("shape 文件不存在 (%s)，视为通过", settings.shapes_path)
        return True, "shape 文件不存在，视为通过"
    try:
        from pyshacl import validate  # type: ignore
    except Exception as exc:  # pragma: no cover - 环境缺失时仍需返回
        logger.warning("pyshacl 未安装或导入失败: %s", exc)
        return True, f"pyshacl 未安装: {exc}"
    try:
        shapes_graph = Graph().parse(settings.shapes_path, format="turtle")
        data_triples_count = len(data_graph)
        logger.info("开始执行 SHACL 校验: shapes=%s format=%s data_triples=%d", 
                   settings.shapes_path, fmt, data_triples_count)
        conforms, report_graph_raw, report_text = validate(
            data_graph=data_graph,
            shacl_graph=shapes_graph,
            inference="rdfs",
            abort_on_error=False,
            meta_shacl=False,
            debug=False,
            serialize_report_graph=True,
        )
        report = report_text.decode("utf-8") if isinstance(report_text, bytes) else str(report_text)
        
        # 提取违规详情
        violations_count = 0
        violation_messages = []
        
        if not conforms:
            # 从文本报告中解析违规信息
            import re
            # 统计违规数量
            results_match = re.search(r'Results \((\d+)\):', report)
            if results_match:
                violations_count = int(results_match.group(1))
            
            # 提取所有违规消息（只取 Message: 到下一行的内容）
            message_pattern = r'Message:\s*([^\n]+)'
            msg_matches = re.findall(message_pattern, report)
            violation_messages = [msg.strip() for msg in msg_matches]
        
        if conforms:
            logger.info("✅ SHACL 校验通过: conforms=True, data_triples=%d", data_triples_count)
        else:
            logger.warning("❌ SHACL 校验失败: conforms=False, violations=%d, data_triples=%d", 
                          violations_count, data_triples_count)
            if violation_messages:
                for i, msg in enumerate(violation_messages[:5], 1):  # 最多显示前5条
                    logger.warning("  违规项 #%d: %s", i, msg)
                if len(violation_messages) > 5:
                    logger.warning("  ... 还有 %d 条违规项", len(violation_messages) - 5)
        
        return bool(conforms), report
    except Exception as exc:
        logger.exception("SHACL 校验出错: %s", exc)
        return False, f"校验失败: {exc}"
