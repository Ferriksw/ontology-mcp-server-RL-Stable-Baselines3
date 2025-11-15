#!/usr/bin/env python3
from __future__ import annotations
# Copyright (c) 2025 shark8848
# MIT License
#
# Ontology MCP Server - 电商 AI 助手系统
# 本体推理 + 电商业务逻辑 + 对话记忆 + 可视化 UI
#
# Author: shark8848
# Repository: https://github.com/shark8848/ontology-mcp-server
"""对话记忆管理模块，支持历史会话和摘要提取。
功能：
1. 保存完整对话历史
2. 对每轮对话生成摘要
3. 在推理时注入最近的对话摘要
4. 避免上下文丢失
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json

from agent.logger import get_logger

LOGGER = get_logger(__name__)


@dataclass
class ConversationTurn:
    """单轮对话记录"""
    user_input: str
    agent_response: str
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    summary: Optional[str] = None


class ConversationMemory:
    """对话记忆管理器
    
    管理对话历史、生成摘要、提供上下文注入功能。
    """
    
    def __init__(self, max_history: int = 10, max_summary_length: int = 5):
        """初始化对话记忆
        
        Args:
            max_history: 保留的最大完整对话轮数
            max_summary_length: 注入上下文时使用的最大摘要数量
        """
        self.max_history = max_history
        self.max_summary_length = max_summary_length
        self.history: List[ConversationTurn] = []
        LOGGER.info("对话记忆初始化: max_history=%d, max_summary_length=%d", 
                   max_history, max_summary_length)
    
    def add_turn(
        self, 
        user_input: str, 
        agent_response: str, 
        tool_calls: List[Dict[str, Any]] = None
    ) -> ConversationTurn:
        """添加一轮对话
        
        Args:
            user_input: 用户输入
            agent_response: Agent 响应
            tool_calls: 使用的工具调用列表
            
        Returns:
            ConversationTurn: 新增的对话记录
        """
        turn = ConversationTurn(
            user_input=user_input,
            agent_response=agent_response,
            tool_calls=tool_calls or [],
        )
        
        # 生成摘要
        turn.summary = self._generate_summary(turn)
        
        self.history.append(turn)
        
        # 限制历史长度
        if len(self.history) > self.max_history:
            removed = self.history.pop(0)
            LOGGER.debug("移除最早对话记录: %s...", removed.user_input[:50])
        
        LOGGER.info("新增对话记录 #%d: 用户输入长度=%d, 响应长度=%d, 工具调用=%d", 
                   len(self.history), len(user_input), len(agent_response), 
                   len(tool_calls or []))
        
        return turn
    
    def _generate_summary(self, turn: ConversationTurn) -> str:
        """生成单轮对话摘要
        
        使用简单的规则提取关键信息，避免依赖额外的 LLM 调用。
        实际生产环境可以调用 LLM 生成更智能的摘要。
        
        Args:
            turn: 对话轮次
            
        Returns:
            str: 摘要文本
        """
        # 提取用户意图关键词
        user_summary = turn.user_input[:100]  # 截取前100字符
        
        # 工具使用情况
        tool_summary = ""
        if turn.tool_calls:
            tool_names = [tc.get("tool", "unknown") for tc in turn.tool_calls]
            tool_summary = f", 调用工具: {', '.join(tool_names)}"
        
        # 响应摘要(提取前50字符)
        response_summary = turn.agent_response[:50]
        if len(turn.agent_response) > 50:
            response_summary += "..."
        
        summary = f"用户: {user_summary}{tool_summary} → {response_summary}"
        
        LOGGER.debug("生成摘要: %s", summary[:150])
        return summary
    
    def get_context_for_prompt(self) -> str:
        """获取用于注入 prompt 的上下文
        
        返回最近几轮对话的摘要，作为上下文信息。
        
        Returns:
            str: 格式化的上下文字符串
        """
        if not self.history:
            return ""
        
        # 获取最近的 N 轮摘要
        recent_turns = self.history[-self.max_summary_length:]
        
        context_lines = ["# 对话历史摘要"]
        for i, turn in enumerate(recent_turns, 1):
            context_lines.append(f"{i}. {turn.summary}")
        
        context = "\n".join(context_lines)
        LOGGER.debug("生成上下文提示: %d 轮摘要", len(recent_turns))
        
        return context
    
    def get_full_history(self) -> List[Dict[str, Any]]:
        """获取完整对话历史(用于调试或日志)
        
        Returns:
            List[Dict]: 历史记录列表
        """
        return [
            {
                "user_input": turn.user_input,
                "agent_response": turn.agent_response,
                "tool_calls": turn.tool_calls,
                "timestamp": turn.timestamp,
                "summary": turn.summary,
            }
            for turn in self.history
        ]
    
    def clear(self):
        """清空对话历史"""
        count = len(self.history)
        self.history.clear()
        LOGGER.info("清空对话历史: 移除 %d 条记录", count)
    
    def save_to_file(self, filepath: str):
        """保存对话历史到文件
        
        Args:
            filepath: 保存路径
        """
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(self.get_full_history(), f, ensure_ascii=False, indent=2)
            LOGGER.info("对话历史已保存至: %s (%d 条记录)", filepath, len(self.history))
        except Exception as e:
            LOGGER.error("保存对话历史失败: %s", e)
    
    def load_from_file(self, filepath: str):
        """从文件加载对话历史
        
        Args:
            filepath: 文件路径
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            self.history.clear()
            for item in data:
                turn = ConversationTurn(
                    user_input=item["user_input"],
                    agent_response=item["agent_response"],
                    tool_calls=item.get("tool_calls", []),
                    timestamp=item.get("timestamp", ""),
                    summary=item.get("summary"),
                )
                self.history.append(turn)
            
            LOGGER.info("从文件加载对话历史: %s (%d 条记录)", filepath, len(self.history))
        except Exception as e:
            LOGGER.error("加载对话历史失败: %s", e)


class EnhancedConversationMemory(ConversationMemory):
    """增强版对话记忆，支持使用 LLM 生成智能摘要"""
    
    def __init__(
        self, 
        llm_model=None,
        max_history: int = 10, 
        max_summary_length: int = 5
    ):
        """初始化增强版记忆
        
        Args:
            llm_model: 用于生成摘要的 LLM 实例(如 DeepseekChatModel)
            max_history: 保留的最大完整对话轮数
            max_summary_length: 注入上下文时使用的最大摘要数量
        """
        super().__init__(max_history, max_summary_length)
        self.llm_model = llm_model
        LOGGER.info("增强版对话记忆初始化: 使用 LLM 生成摘要=%s", llm_model is not None)
    
    def _generate_summary(self, turn: ConversationTurn) -> str:
        """使用 LLM 生成智能摘要
        
        Args:
            turn: 对话轮次
            
        Returns:
            str: 摘要文本
        """
        if not self.llm_model:
            # 回退到基础摘要生成
            return super()._generate_summary(turn)
        
        try:
            # 构造摘要提示
            summary_prompt = f"""请为以下对话生成简洁摘要(不超过50字):

用户: {turn.user_input}
Agent: {turn.agent_response}

摘要:"""
            
            # 调用 LLM 生成摘要
            messages = [{"role": "user", "content": summary_prompt}]
            response = self.llm_model.generate(messages, tools=[])
            
            summary = response.get("content", "").strip()
            if not summary:
                # LLM 响应为空，回退到基础方法
                LOGGER.warning("LLM 生成摘要为空，使用基础方法")
                return super()._generate_summary(turn)
            
            LOGGER.debug("使用 LLM 生成摘要: %s", summary[:100])
            return summary
            
        except Exception as e:
            LOGGER.error("LLM 摘要生成失败: %s, 回退到基础方法", e)
            return super()._generate_summary(turn)
