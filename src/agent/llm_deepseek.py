from __future__ import annotations
# Copyright (c) 2025 shark8848
# MIT License
#
# Ontology MCP Server - 电商 AI 助手系统
# 本体推理 + 电商业务逻辑 + 对话记忆 + 可视化 UI
#
# Author: shark8848
# Repository: https://github.com/shark8848/ontology-mcp-server
"""OpenAI/DeepSeek 聊天模型工厂。"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from openai import OpenAI
except ImportError as exc:  # pragma: no cover - import guarded for informative error
    raise ImportError(
        "openai package is required for chat model support. "
        "Please install it with `pip install openai`."
    ) from exc

from .logger import get_logger

logger = get_logger(__name__)

DEFAULT_API_URL = "https://api.deepseek.com/v1"
DEFAULT_MODEL = "deepseek-chat"


def _load_yaml_config() -> dict:
    try:
        import yaml
    except Exception:
        return {}

    candidates = [
        Path(__file__).resolve().parent / "config.yaml",
        Path(__file__).resolve().parents[1] / "agent" / "config.yaml",
    ]

    for cfg_path in candidates:
        if not cfg_path.exists():
            continue
        try:
            with cfg_path.open("r", encoding="utf-8") as fh:
                data = yaml.safe_load(fh) or {}
        except Exception:
            continue
        if isinstance(data, dict):
            return data

    return {}


def _first_non_empty(*values: Any) -> Optional[Any]:
    for value in values:
        if value is None:
            continue
        if isinstance(value, str) and value.strip() == "":
            continue
        return value
    return None


def _coerce_float(value: Optional[Any]) -> Optional[float]:
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value))
    except (TypeError, ValueError):
        return None


def _coerce_int(value: Optional[Any]) -> Optional[int]:
    if value is None or value == "":
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return None


class DeepseekChatModel:
    """为 OpenAI 兼容接口提供简易的聊天封装。"""

    def __init__(
        self,
        *,
        api_url: str,
        api_key: str,
        model: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        request_timeout: Optional[float] = None,
    ) -> None:
        client_kwargs: Dict[str, Any] = {}
        if request_timeout is not None:
            client_kwargs["timeout"] = request_timeout

        self.client = OpenAI(base_url=api_url, api_key=api_key, **client_kwargs)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def generate(
        self,
        messages: List[Dict[str, Any]],
        *,
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        kwargs: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
        }
        if tools:
            kwargs["tools"] = tools
        if self.temperature is not None:
            kwargs["temperature"] = self.temperature
        if self.max_tokens is not None:
            kwargs["max_tokens"] = self.max_tokens

        try:
            response = self.client.chat.completions.create(**kwargs)
        except Exception as e:
            logger.error(
                f"LLM API 调用失败: {type(e).__name__}: {str(e)}\n"
                f"API URL: {self.client.base_url}\n"
                f"Model: {self.model}\n"
                f"Messages count: {len(messages)}\n"
                f"Tools count: {len(tools) if tools else 0}",
                exc_info=True
            )
            raise
        
        if not response.choices:
            return {"content": "", "tool_calls": [], "raw_response": response}

        choice = response.choices[0]
        message = choice.message

        content_text = ""
        if isinstance(message.content, list):
            for part in message.content:
                if isinstance(part, dict) and "text" in part:
                    content_text += str(part.get("text", ""))
        elif message.content:
            content_text = str(message.content)

        tool_calls: List[Dict[str, Any]] = []
        if getattr(message, "tool_calls", None):
            for call in message.tool_calls:  # type: ignore[attr-defined]
                arguments: Dict[str, Any]
                raw_arguments = getattr(call.function, "arguments", "")
                try:
                    arguments = json.loads(raw_arguments) if raw_arguments else {}
                except json.JSONDecodeError:
                    arguments = {"_raw": raw_arguments}
                tool_calls.append(
                    {
                        "id": call.id,
                        "name": call.function.name,
                        "arguments": arguments,
                    }
                )

        return {
            "content": content_text,
            "tool_calls": tool_calls,
            "raw_response": response,
        }


def build_chat_model(
    api_url: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    *,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    request_timeout: Optional[float] = None,
) -> DeepseekChatModel:
    """创建 OpenAI 兼容的聊天模型实例。"""

    cfg = _load_yaml_config()

    resolved_api_url = _first_non_empty(
        api_url,
        os.getenv("OPENAI_API_URL"),
        cfg.get("OPENAI_API_URL"),
        os.getenv("DEEPSEEK_API_URL"),
        cfg.get("DEEPSEEK_API_URL"),
        DEFAULT_API_URL,
    )
    resolved_api_url = resolved_api_url or DEFAULT_API_URL

    resolved_api_key = _first_non_empty(
        api_key,
        os.getenv("OPENAI_API_KEY"),
        cfg.get("OPENAI_API_KEY"),
        os.getenv("DEEPSEEK_API_KEY"),
        cfg.get("DEEPSEEK_API_KEY"),
    )

    if not resolved_api_key:
        raise RuntimeError(
            "未找到 OpenAI/DeepSeek API Key，请设置 OPENAI_API_KEY 或 DEEPSEEK_API_KEY"
        )

    resolved_model = _first_non_empty(
        model,
        os.getenv("OPENAI_MODEL"),
        cfg.get("OPENAI_MODEL"),
        os.getenv("DEEPSEEK_MODEL"),
        cfg.get("DEEPSEEK_MODEL"),
        DEFAULT_MODEL,
    )
    resolved_model = resolved_model or DEFAULT_MODEL

    resolved_temperature = (
        temperature
        if temperature is not None
        else _coerce_float(
            _first_non_empty(
                os.getenv("OPENAI_TEMPERATURE"),
                cfg.get("OPENAI_TEMPERATURE"),
                os.getenv("DEEPSEEK_TEMPERATURE"),
                cfg.get("DEEPSEEK_TEMPERATURE"),
            )
        )
    )

    resolved_max_tokens = (
        max_tokens
        if max_tokens is not None
        else _coerce_int(
            _first_non_empty(
                os.getenv("OPENAI_MAX_TOKENS"),
                cfg.get("OPENAI_MAX_TOKENS"),
                os.getenv("DEEPSEEK_MAX_TOKENS"),
                cfg.get("DEEPSEEK_MAX_TOKENS"),
            )
        )
    )

    logger.info(
        "Initializing DeepSeek chat model=%s base=%s",
        resolved_model,
        resolved_api_url,
    )

    return DeepseekChatModel(
        api_url=resolved_api_url,
        api_key=resolved_api_key,
        model=resolved_model,
        temperature=resolved_temperature,
        max_tokens=resolved_max_tokens,
        request_timeout=request_timeout,
    )


def get_default_chat_model() -> DeepseekChatModel:
    """便捷函数：按默认配置创建一个聊天模型。"""

    return build_chat_model()


# 为向后兼容保留旧名称
OpenAICompatibleLLM = build_chat_model
DeepseekLLM = build_chat_model

