from __future__ import annotations
# Copyright (c) 2025 shark8848
# MIT License
#
# Ontology MCP Server - 电商 AI 助手系统
# 本体推理 + 电商业务逻辑 + 对话记忆 + 可视化 UI
#
# Author: shark8848
# Repository: https://github.com/shark8848/ontology-mcp-server
"""Agent 专用日志初始化与获取封装。"""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

_initialized = False
_LOGGER_NAME = "agent"


def _log_dir() -> Path:
    env_dir = os.getenv("AGENT_LOG_DIR")
    if env_dir:
        return Path(env_dir)
    pkg_dir = Path(__file__).resolve().parent / "logs"
    if pkg_dir.exists():
        return pkg_dir
    try:
        pkg_dir.mkdir(parents=True, exist_ok=True)
        return pkg_dir
    except Exception:
        pass
    # 回退到当前工作目录下的 logs/agent，避免写入只读的 site-packages
    return Path.cwd() / "logs" / "agent"


def _base_logger() -> logging.Logger:
    return logging.getLogger(_LOGGER_NAME)


def init_logging(level_name: Optional[str] = None) -> None:
    """初始化 Agent 作用域日志：控制台 + logs/agent/agent.log。"""
    global _initialized
    if _initialized:
        return

    log_dir = _log_dir()
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

    level_str = (level_name or os.getenv("AGENT_LOG_LEVEL", "INFO")).upper()
    level = getattr(logging, level_str, logging.INFO)

    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")

    logger = _base_logger()
    logger.setLevel(level)
    logger.propagate = False
    logger.handlers.clear()

    console = logging.StreamHandler()
    console.setLevel(level)
    console.setFormatter(formatter)
    logger.addHandler(console)

    try:
        file_handler = RotatingFileHandler(str(log_dir / "agent.log"), maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception:
        pass

    _initialized = True


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """获得 Agent 专用 logger（带层级）。"""
    init_logging()
    base = _base_logger()
    if not name or name == _LOGGER_NAME:
        return base
    if name.startswith(f"{_LOGGER_NAME}."):
        suffix = name[len(_LOGGER_NAME) + 1 :]
        return base.getChild(suffix)
    return base.getChild(name)
