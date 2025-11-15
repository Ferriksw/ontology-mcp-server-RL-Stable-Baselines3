from __future__ import annotations
# Copyright (c) 2025 shark8848
# MIT License
#
# Ontology MCP Server - 电商 AI 助手系统
# Author: shark8848
# Repository: https://github.com/shark8848/ontology-mcp-server

"""Pytest 全局配置与环境隔离。"""

import os
from pathlib import Path
from collections.abc import Iterator

import pytest

SRC_PATH = Path(__file__).resolve().parents[1] / "src"
if str(SRC_PATH) not in os.getenv("PYTHONPATH", ""):
    import sys

    sys.path.insert(0, str(SRC_PATH))

from ontology_mcp_server import config


@pytest.fixture(autouse=True)
def configure_data_dir(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """为测试指向项目内 data 目录，并重置缓存。"""
    config.get_settings.cache_clear()
    data_dir = Path(__file__).resolve().parents[1] / "data"
    monkeypatch.setenv("ONTOLOGY_DATA_DIR", str(data_dir))
    monkeypatch.delenv("ONTOLOGY_USE_OWLREADY2", raising=False)
    monkeypatch.delenv("ONTOLOGY_TTL", raising=False)
    monkeypatch.delenv("ONTOLOGY_SHAPES", raising=False)
    monkeypatch.delenv("ONTOLOGY_SYNONYMS_JSON", raising=False)
    try:
        yield
    finally:
        config.get_settings.cache_clear()
