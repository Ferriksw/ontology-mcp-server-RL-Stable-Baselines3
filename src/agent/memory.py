#!/usr/bin/env python3
from __future__ import annotations
from typing import List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
import json

from agent.logger import get_logger

LOGGER = get_logger(__name__)


@dataclass
class ConversationTurn:
    """单轮对话记录，仅保留摘要"""
    summary: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class ConversationMemory:
    """对话记忆管理器
    
    管理对话摘要历史、生成摘要、提供上下文注入功能。
    """
    
    def __init__(self, max_history: int = 10, max_summary_length: int = 5):
        """初始化对话记忆
        
        Args:
            max_history: 保留的最大摘要轮数
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
            ConversationTurn: 新增的摘要记录
        """
        # 生成摘要
        summary = self._generate_summary(user_input, agent_response, tool_calls)
        turn = ConversationTurn(summary=summary)
        
        self.history.append(turn)
        
        # 限制历史长度
        self._truncate_history()
        
        LOGGER.info("新增摘要记录 #%d: 摘要长度=%d", len(self.history), len(summary))
        
        return turn
    
    def _generate_summary(self, user_input: str, agent_response: str, tool_calls: List[Dict[str, Any]] = None) -> str:
        """生成单轮对话摘要
        
        使用简单的规则提取关键信息，避免依赖额外的 LLM 调用。
        
        Args:
            user_input: 用户输入
            agent_response: Agent 响应
            tool_calls: 工具调用列表
            
        Returns:
            str: 摘要文本
        """
        # 提取用户意图关键词
        user_summary = user_input[:100]  # 截取前100字符
        
        # 工具使用情况
        tool_summary = ""
        if tool_calls:
            tool_names = [tc.get("tool", "unknown") for tc in tool_calls]
            tool_summary = f", 调用工具: {', '.join(tool_names)}"
        
        # 响应摘要(提取前50字符)
        response_summary = agent_response[:50]
        if len(agent_response) > 50:
            response_summary += "..."
        
        summary = f"用户: {user_summary}{tool_summary} → {response_summary}"
        
        LOGGER.debug("生成摘要: %s", summary[:150])
        return summary
    
    def _truncate_history(self):
        """清理历史记录，确保不超过最大保存轮数"""
        if len(self.history) > self.max_history:
            # 合并旧的摘要
            merged_summary = " | ".join(turn.summary for turn in self.history[:-self.max_history])
            self.history = self.history[-self.max_history:]
            self.history.insert(0, ConversationTurn(summary=merged_summary))
            LOGGER.debug("合并并移除旧摘要: %s...", merged_summary[:50])
    
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
        """获取完整摘要历史(用于调试或日志)
        
        Returns:
            List[Dict]: 摘要记录列表
        """
        return [
            {
                "summary": turn.summary,
                "timestamp": turn.timestamp,
            }
            for turn in self.history
        ]
    
    def clear(self):
        """清空摘要历史"""
        count = len(self.history)
        self.history.clear()
        LOGGER.info("清空摘要历史: 移除 %d 条记录", count)
    
    def save_to_file(self, filepath: str):
        """保存摘要历史到文件
        
        Args:
            filepath: 保存路径
        """
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(self.get_full_history(), f, ensure_ascii=False, indent=2)
            LOGGER.info("摘要历史已保存至: %s (%d 条记录)", filepath, len(self.history))
        except Exception as e:
            LOGGER.error("保存摘要历史失败: %s", e)
    
    def load_from_file(self, filepath: str):
        """从文件加载摘要历史
        
        Args:
            filepath: 文件路径
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            self.history.clear()
            for item in data:
                turn = ConversationTurn(
                    summary=item["summary"],
                    timestamp=item.get("timestamp", ""),
                )
                self.history.append(turn)
            
            self._truncate_history()  # 确保加载后历史记录不超限
            LOGGER.info("从文件加载摘要历史: %s (%d 条记录)", filepath, len(self.history))
        except Exception as e:
            LOGGER.error("加载摘要历史失败: %s", e)