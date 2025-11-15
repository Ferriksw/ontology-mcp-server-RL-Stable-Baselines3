from __future__ import annotations
# Copyright (c) 2025 shark8848
# MIT License
#
# Ontology MCP Server - 电商 AI 助手系统
# 本体推理 + 电商业务逻辑 + 对话记忆 + 可视化 UI
#
# Author: shark8848
# Repository: https://github.com/shark8848/ontology-mcp-server
"""配置管理：集中管理环境变量与资源路径。"""

import os
from pathlib import Path
from functools import lru_cache


class Settings:
    """读取环境变量，提供默认路径。"""

    def __init__(self) -> None:
        base = Path(
            os.getenv("ONTOLOGY_DATA_DIR", Path(__file__).resolve().parent.parent / "data")
        )
        self.data_dir = base
        self.ttl_path = Path(os.getenv("ONTOLOGY_TTL", base / "ontology_commerce.ttl"))
        self.shapes_path = Path(os.getenv("ONTOLOGY_SHAPES", base / "ontology_shapes.ttl"))
        self.synonyms_json = Path(os.getenv("ONTOLOGY_SYNONYMS_JSON", base / "product_synonyms.json"))
        self.synonyms_ttl = Path(os.getenv("ONTOLOGY_SYNONYMS_TTL", base / "product_synonyms.ttl"))
        self.capabilities_jsonld = Path(os.getenv("ONTOLOGY_CAPABILITIES_JSONLD", base / "capabilities.jsonld"))
        audit_override = os.getenv("ONTOLOGY_MCP_AUDIT", "")
        self.audit_file = Path(audit_override) if audit_override else None
        self.use_owlready2 = os.getenv("ONTOLOGY_USE_OWLREADY2", "false").lower() in {"1", "true", "yes"}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
