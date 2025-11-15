"""
Copyright (c) 2025 shark8848
MIT License

Ontology MCP Server - 电商 AI 助手系统
本体推理 + 电商业务逻辑 + 对话记忆 + 可视化 UI

Author: shark8848
Repository: https://github.com/shark8848/ontology-mcp-server
"""

"""
对话质量评分系统

评估 Agent 对话质量的多维度指标：
1. 响应效率：工具调用次数、响应时间
2. 任务完成度：是否成功完成用户请求
3. 对话流畅度：是否需要多次澄清、是否主动引导
4. 用户体验：满意度评分（可选手动标注）
"""

import time
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


class TaskOutcome(Enum):
    """任务完成状态"""
    SUCCESS = "success"           # 成功完成
    PARTIAL = "partial"           # 部分完成
    FAILED = "failed"             # 失败
    INTERRUPTED = "interrupted"   # 中断


class UserSatisfaction(Enum):
    """用户满意度（可选标注）"""
    VERY_SATISFIED = 5
    SATISFIED = 4
    NEUTRAL = 3
    DISSATISFIED = 2
    VERY_DISSATISFIED = 1


@dataclass
class TurnMetrics:
    """单轮对话的质量指标"""
    turn_id: int
    user_input: str
    agent_response: str
    
    # 效率指标
    response_time: float  # 秒
    tool_calls_count: int
    tool_calls_names: List[str] = field(default_factory=list)
    
    # 任务完成度
    task_completed: bool = False
    outcome: Optional[TaskOutcome] = None
    
    # 对话流畅度
    needs_clarification: bool = False  # 是否需要澄清
    proactive_guidance: bool = False   # 是否主动引导
    
    # 用户满意度（可选）
    user_satisfaction: Optional[UserSatisfaction] = None
    
    # 附加信息
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SessionMetrics:
    """会话级别的质量指标汇总"""
    session_id: str
    turns: List[TurnMetrics] = field(default_factory=list)
    
    # 汇总统计
    total_turns: int = 0
    total_response_time: float = 0.0
    total_tool_calls: int = 0
    
    # 成功率
    successful_tasks: int = 0
    failed_tasks: int = 0
    
    # 对话质量
    clarification_rate: float = 0.0  # 需要澄清的比例
    proactive_rate: float = 0.0      # 主动引导的比例
    
    # 平均满意度
    avg_satisfaction: Optional[float] = None
    
    def __post_init__(self):
        """初始化时计算统计"""
        if self.turns:
            self.compute_stats()
    
    def compute_stats(self):
        """计算统计指标"""
        self.total_turns = len(self.turns)
        
        if self.total_turns == 0:
            return
        
        # 计算总量
        self.total_response_time = sum(t.response_time for t in self.turns)
        self.total_tool_calls = sum(t.tool_calls_count for t in self.turns)
        
        # 计算成功率
        self.successful_tasks = sum(
            1 for t in self.turns 
            if t.task_completed and t.outcome == TaskOutcome.SUCCESS
        )
        self.failed_tasks = sum(
            1 for t in self.turns 
            if t.outcome == TaskOutcome.FAILED
        )
        
        # 计算对话质量
        clarification_count = sum(1 for t in self.turns if t.needs_clarification)
        proactive_count = sum(1 for t in self.turns if t.proactive_guidance)
        
        self.clarification_rate = clarification_count / self.total_turns
        self.proactive_rate = proactive_count / self.total_turns
        
        # 计算平均满意度
        satisfaction_scores = [
            t.user_satisfaction.value 
            for t in self.turns 
            if t.user_satisfaction is not None
        ]
        if satisfaction_scores:
            self.avg_satisfaction = sum(satisfaction_scores) / len(satisfaction_scores)
    
    def get_quality_score(self) -> float:
        """
        计算综合质量分数 (0-100)
        
        评分维度：
        - 效率分 (30分): 响应时间和工具调用效率
        - 成功率 (40分): 任务完成度
        - 流畅度 (30分): 对话流畅度和主动引导
        """
        if self.total_turns == 0:
            return 0.0
        
        # 1. 效率分 (30分)
        avg_response_time = self.total_response_time / self.total_turns
        avg_tool_calls = self.total_tool_calls / self.total_turns
        
        # 响应时间评分: <2s=15分, 2-5s=10分, >5s=5分
        if avg_response_time < 2.0:
            time_score = 15
        elif avg_response_time < 5.0:
            time_score = 10
        else:
            time_score = 5
        
        # 工具调用评分: 1-2次=15分, 3-4次=10分, >4次=5分
        if avg_tool_calls <= 2:
            tool_score = 15
        elif avg_tool_calls <= 4:
            tool_score = 10
        else:
            tool_score = 5
        
        efficiency_score = time_score + tool_score
        
        # 2. 成功率 (40分)
        if self.total_turns > 0:
            success_rate = self.successful_tasks / self.total_turns
            completion_score = success_rate * 40
        else:
            completion_score = 0
        
        # 3. 流畅度 (30分)
        # 澄清率越低越好（最多扣15分）
        clarification_penalty = self.clarification_rate * 15
        
        # 主动引导率越高越好（最多加15分）
        proactive_bonus = self.proactive_rate * 15
        
        fluency_score = 15 - clarification_penalty + proactive_bonus
        fluency_score = max(0, min(30, fluency_score))  # 限制在0-30之间
        
        # 综合分数
        total_score = efficiency_score + completion_score + fluency_score
        return round(total_score, 2)
    
    def get_summary(self) -> Dict[str, Any]:
        """获取会话质量摘要"""
        return {
            "session_id": self.session_id,
            "total_turns": self.total_turns,
            "quality_score": self.get_quality_score(),
            "efficiency": {
                "avg_response_time": round(self.total_response_time / self.total_turns, 2) if self.total_turns > 0 else 0,
                "avg_tool_calls": round(self.total_tool_calls / self.total_turns, 2) if self.total_turns > 0 else 0,
                "total_tool_calls": self.total_tool_calls,
            },
            "task_completion": {
                "successful_tasks": self.successful_tasks,
                "failed_tasks": self.failed_tasks,
                "success_rate": round(self.successful_tasks / self.total_turns, 2) if self.total_turns > 0 else 0,
            },
            "conversation_quality": {
                "clarification_rate": round(self.clarification_rate, 2),
                "proactive_rate": round(self.proactive_rate, 2),
            },
            "user_satisfaction": self.avg_satisfaction,
        }


class QualityMetricsTracker:
    """对话质量跟踪器"""
    
    def __init__(self, session_id: str):
        self.session_metrics = SessionMetrics(session_id=session_id)
        self._current_turn_start_time: Optional[float] = None
        self._current_turn_tool_calls: List[str] = []
    
    def start_turn(self):
        """开始记录新的一轮对话"""
        self._current_turn_start_time = time.time()
        self._current_turn_tool_calls = []
    
    def record_tool_call(self, tool_name: str):
        """记录工具调用"""
        self._current_turn_tool_calls.append(tool_name)
    
    def end_turn(
        self,
        turn_id: int,
        user_input: str,
        agent_response: str,
        task_completed: bool = False,
        outcome: Optional[TaskOutcome] = None,
        needs_clarification: bool = False,
        proactive_guidance: bool = False,
        user_satisfaction: Optional[UserSatisfaction] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """结束一轮对话并记录指标"""
        if self._current_turn_start_time is None:
            raise ValueError("Must call start_turn() before end_turn()")
        
        response_time = time.time() - self._current_turn_start_time
        
        turn_metrics = TurnMetrics(
            turn_id=turn_id,
            user_input=user_input,
            agent_response=agent_response,
            response_time=response_time,
            tool_calls_count=len(self._current_turn_tool_calls),
            tool_calls_names=self._current_turn_tool_calls.copy(),
            task_completed=task_completed,
            outcome=outcome,
            needs_clarification=needs_clarification,
            proactive_guidance=proactive_guidance,
            user_satisfaction=user_satisfaction,
            metadata=metadata or {},
        )
        
        self.session_metrics.turns.append(turn_metrics)
        self.session_metrics.compute_stats()
        
        # 重置当前轮状态
        self._current_turn_start_time = None
        self._current_turn_tool_calls = []
    
    def get_metrics(self) -> SessionMetrics:
        """获取会话指标"""
        return self.session_metrics
    
    def get_summary(self) -> Dict[str, Any]:
        """获取质量摘要"""
        return self.session_metrics.get_summary()
    
    def export_to_json(self) -> Dict[str, Any]:
        """导出为 JSON 格式"""
        from dataclasses import asdict
        return {
            "session_id": self.session_metrics.session_id,
            "summary": self.get_summary(),
            "turns": [
                {
                    "turn_id": t.turn_id,
                    "user_input": t.user_input,
                    "agent_response": t.agent_response,
                    "response_time": t.response_time,
                    "tool_calls_count": t.tool_calls_count,
                    "tool_calls_names": t.tool_calls_names,
                    "task_completed": t.task_completed,
                    "outcome": t.outcome.value if t.outcome else None,
                    "needs_clarification": t.needs_clarification,
                    "proactive_guidance": t.proactive_guidance,
                    "user_satisfaction": t.user_satisfaction.value if t.user_satisfaction else None,
                    "metadata": t.metadata,
                }
                for t in self.session_metrics.turns
            ],
        }
