from __future__ import annotations
# Copyright (c) 2025 shark8848
# MIT License
#
# Ontology MCP Server - 电商 AI 助手系统
# 本体推理 + 电商业务逻辑 + 对话记忆 + 可视化 UI
#
# Author: shark8848
# Repository: https://github.com/shark8848/ontology-mcp-server
"""FastAPI 实现的 MCP 风格服务器。"""

from datetime import datetime
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .capabilities import capability_list, capability_names
from .config import get_settings
from .logger import get_logger, init_logging
from .tools import call_tool as dispatch_tool

# 在应用启动时初始化日志（避免按需延迟初始化）
init_logging()
logger = get_logger(__name__)

app = FastAPI(title="Ontology MCP Server", version="0.1.0")


@app.on_event("startup")
def _on_startup() -> None:
    # 确保在 FastAPI 启动生命周期里也执行一次（冗余安全）
    init_logging()
    logger.info("Ontology MCP Server 启动完成，日志已初始化")


class InvokeRequest(BaseModel):
    tool: str = Field(..., description="能力名称，如 ontology.explain_discount")
    payload: Dict[str, Any] = Field(default_factory=dict)


@app.get("/health")
def health() -> Dict[str, Any]:
    settings = get_settings()
    logger.debug("health check 请求")
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "use_owlready2": settings.use_owlready2,
        "ttl_path": str(settings.ttl_path),
        "shapes_path": str(settings.shapes_path),
    }


@app.get("/capabilities")
def capabilities() -> Dict[str, Any]:
    logger.debug("返回能力列表请求")
    return capability_list()


@app.post("/invoke")
def invoke(req: InvokeRequest) -> Dict[str, Any]:
    logger.info("/invoke 请求: tool=%s payload keys=%s", req.tool, list(req.payload.keys()))
    if req.tool not in capability_names():
        logger.warning("未知工具被请求: %s", req.tool)
        raise HTTPException(status_code=404, detail=f"未知工具: {req.tool}")
    ok, result = dispatch_tool(req.tool, req.payload)
    if not ok:
        logger.warning("工具执行失败: %s -> %s", req.tool, result)
        raise HTTPException(status_code=400, detail=str(result))
    logger.info("工具执行成功: %s", req.tool)
    if isinstance(result, dict):
        return result
    return {"result": result}
