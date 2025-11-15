#!/usr/bin/env python3
"""
Copyright (c) 2025 shark8848
MIT License

Ontology MCP Server - 电商 AI 助手系统
Author: shark8848
Repository: https://github.com/shark8848/ontology-mcp-server
"""

"""
测试执行日志功能
展示运行日志的完整内容和格式
"""

from agent.react_agent import LangChainAgent
from agent.gradio_ui import format_execution_log
import json


def main():
    print("=" * 80)
    print("🔍 测试增强的执行日志功能")
    print("=" * 80)
    print()
    
    # 初始化 agent
    print("📦 初始化 Agent...")
    agent = LangChainAgent()
    print("✅ Agent 初始化完成")
    print()
    
    # 测试查询
    test_query = "我是VIP客户，订单金额1000元能打几折？"
    print(f"💬 测试查询: {test_query}")
    print()
    
    # 执行 agent
    print("🚀 执行 Agent...")
    result = agent.run(test_query)
    print("✅ Agent 执行完成")
    print()
    
    # 显示执行结果统计
    print("=" * 80)
    print("📊 执行结果统计")
    print("=" * 80)
    print(f"最终答案长度: {len(result['final_answer'])} 字符")
    print(f"工具调用次数: {len(result['tool_log'])}")
    print(f"执行日志条目: {len(result['execution_log'])}")
    print()
    
    # 统计日志类型
    log_types = {}
    for log in result['execution_log']:
        step_type = log.get('step_type')
        log_types[step_type] = log_types.get(step_type, 0) + 1
    
    print("日志步骤类型分布:")
    for step_type, count in sorted(log_types.items()):
        print(f"  • {step_type:20s}: {count:2d} 条")
    print()
    
    # 显示最终答案
    print("=" * 80)
    print("🎯 最终答案")
    print("=" * 80)
    print(result['final_answer'])
    print()
    
    # 显示格式化的执行日志
    print("=" * 80)
    print("📋 格式化的执行日志 (UI 显示效果)")
    print("=" * 80)
    formatted_log = format_execution_log(result['execution_log'])
    print(formatted_log)
    print()
    
    # 显示详细的执行日志 JSON
    print("=" * 80)
    print("📝 详细执行日志 (JSON 格式)")
    print("=" * 80)
    print(json.dumps(result['execution_log'], ensure_ascii=False, indent=2))
    print()
    
    print("=" * 80)
    print("✅ 测试完成!")
    print("=" * 80)


if __name__ == "__main__":
    main()
