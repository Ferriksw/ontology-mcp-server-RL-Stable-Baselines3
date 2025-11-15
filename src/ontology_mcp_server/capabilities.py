from __future__ import annotations
# Copyright (c) 2025 shark8848
# MIT License
#
# Ontology MCP Server - 电商 AI 助手系统
# 本体推理 + 电商业务逻辑 + 对话记忆 + 可视化 UI
#
# Author: shark8848
# Repository: https://github.com/shark8848/ontology-mcp-server
"""MCP 能力描述与辅助函数。"""

import json
from pathlib import Path

from .config import get_settings
from .logger import get_logger


def capability_list():
    logger = get_logger(__name__)
    settings = get_settings()
    # 从 data 目录读取 capabilities.jsonld（仅数据）
    cfg_path: Path = settings.data_dir / "capabilities.jsonld"
    logger.debug("加载能力配置文件: %s", cfg_path)
    try:
        with cfg_path.open("r", encoding="utf-8") as fh:
            cfg = json.load(fh)
        logger.info("已加载 %d 个能力项", len(cfg.get("capabilities", [])))
    except FileNotFoundError:
        logger.warning("能力配置文件未找到: %s，使用空默认配置", cfg_path)
        cfg = {"version": "1.0", "capabilities": []}
    except Exception as exc:
        logger.exception("解析能力配置文件失败: %s", exc)
        cfg = {"version": "1.0", "capabilities": []}

    # 确保返回的结构包含 metadata
    return {
        "version": cfg.get("version", "1.0"),
        "capabilities": cfg.get("capabilities", []),
        "metadata": {
            "data_dir": str(settings.data_dir),
            "use_owlready2": getattr(settings, "use_owlready2", False),
        },
    }


def capability_names() -> list[str]:
    return [cap["name"] for cap in capability_list()["capabilities"]]
