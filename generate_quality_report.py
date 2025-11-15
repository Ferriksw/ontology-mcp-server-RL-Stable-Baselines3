#!/usr/bin/env python3
"""
对话质量报告生成工具

功能：
1. 生成对话质量 Markdown 报告
2. 生成意图分布饼图
3. 生成质量评分趋势图
4. 生成推荐效果分析
"""

import json
from typing import Dict, Any, List
from datetime import datetime
import os


def generate_markdown_report(analytics: Dict[str, Any], output_file: str = "quality_report.md"):
    """生成 Markdown 格式的质量报告"""
    
    report_lines = []
    
    # 标题
    report_lines.append("# 对话质量分析报告")
    report_lines.append(f"\n**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"\n**会话ID**: {analytics.get('session_id', 'N/A')}")
    report_lines.append("\n---\n")
    
    # 1. 质量指标总览
    quality = analytics.get('quality_metrics', {})
    if quality:
        report_lines.append("## 📊 质量指标总览\n")
        report_lines.append(f"### 综合评分: **{quality.get('quality_score', 0)}/100**\n")
        
        score = quality.get('quality_score', 0)
        if score >= 80:
            grade = "🏆 优秀"
            comment = "对话质量非常出色！"
        elif score >= 60:
            grade = "✅ 良好"
            comment = "对话质量较好，还有提升空间。"
        elif score >= 40:
            grade = "⚠️ 及格"
            comment = "对话质量尚可，需要改进。"
        else:
            grade = "❌ 较差"
            comment = "对话质量需要大幅优化。"
        
        report_lines.append(f"**评级**: {grade}\n")
        report_lines.append(f"**评价**: {comment}\n")
        
        # 效率指标
        efficiency = quality.get('efficiency', {})
        report_lines.append("\n### 效率指标\n")
        report_lines.append(f"- **平均响应时间**: {efficiency.get('avg_response_time', 0)}秒")
        report_lines.append(f"- **平均工具调用**: {efficiency.get('avg_tool_calls', 0)}次")
        report_lines.append(f"- **总工具调用**: {efficiency.get('total_tool_calls', 0)}次\n")
        
        # 任务完成度
        completion = quality.get('task_completion', {})
        report_lines.append("\n### 任务完成度\n")
        report_lines.append(f"- **成功任务**: {completion.get('successful_tasks', 0)}个")
        report_lines.append(f"- **失败任务**: {completion.get('failed_tasks', 0)}个")
        report_lines.append(f"- **成功率**: {completion.get('success_rate', 0)*100:.1f}%\n")
        
        # 对话质量
        conv_quality = quality.get('conversation_quality', {})
        report_lines.append("\n### 对话流畅度\n")
        report_lines.append(f"- **澄清率**: {conv_quality.get('clarification_rate', 0)*100:.1f}%")
        report_lines.append(f"  - ✅ 越低越好（表示对话清晰明确）")
        report_lines.append(f"- **主动引导率**: {conv_quality.get('proactive_rate', 0)*100:.1f}%")
        report_lines.append(f"  - ✅ 越高越好（表示Agent主动帮助用户）\n")
    
    # 2. 意图分析
    intent = analytics.get('intent_analysis', {})
    if intent:
        report_lines.append("\n## 🎯 意图分析\n")
        report_lines.append(f"**总对话轮次**: {intent.get('total_turns', 0)}\n")
        
        # 意图分布
        intent_dist = intent.get('intent_distribution', {})
        if intent_dist:
            report_lines.append("\n### 意图分布\n")
            report_lines.append("| 意图类型 | 出现次数 | 占比 |")
            report_lines.append("|---------|---------|------|")
            
            total_intents = sum(intent_dist.values())
            for intent_type, count in sorted(intent_dist.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total_intents * 100) if total_intents > 0 else 0
                report_lines.append(f"| {intent_type} | {count} | {percentage:.1f}% |")
            report_lines.append("")
        
        # 复合意图
        composite = intent.get('composite_intents', [])
        if composite:
            report_lines.append("\n### 🔄 复合意图检测\n")
            for comp in composite:
                report_lines.append(f"**{comp.get('name', 'Unknown')}**")
                report_lines.append(f"- 描述: {comp.get('description', 'N/A')}")
                report_lines.append(f"- 置信度: {comp.get('confidence', 0):.2f}")
                report_lines.append(f"- 子意图: {', '.join(comp.get('sub_intents', []))}\n")
        
        # 当前状态和预测
        report_lines.append("\n### 当前状态\n")
        report_lines.append(f"- **当前意图**: {intent.get('current_intent', 'N/A')}")
        predicted = intent.get('predicted_next', [])
        if predicted:
            report_lines.append(f"- **预测下一步**: {', '.join(predicted)}\n")
    
    # 3. 对话状态
    conv_state = analytics.get('conversation_state', {})
    if conv_state:
        report_lines.append("\n## 🛒 对话状态\n")
        report_lines.append(f"**当前阶段**: {conv_state.get('current_stage', 'N/A')}\n")
        
        # 用户上下文
        user_ctx = conv_state.get('user_context', {})
        if user_ctx:
            report_lines.append("\n### 用户上下文\n")
            report_lines.append(f"- **用户ID**: {user_ctx.get('user_id', '未登录')}")
            report_lines.append(f"- **VIP状态**: {'是' if user_ctx.get('is_vip') else '否'}")
            report_lines.append(f"- **购物车商品**: {user_ctx.get('cart_item_count', 0)}件")
            
            viewed = user_ctx.get('last_viewed_products', [])
            if viewed:
                report_lines.append(f"- **最近浏览**: {', '.join(map(str, viewed[:5]))}")
            
            order_id = user_ctx.get('recent_order_id')
            if order_id:
                report_lines.append(f"- **最近订单**: {order_id}\n")
    
    # 4. 改进建议
    report_lines.append("\n## 💡 改进建议\n")
    
    if quality:
        score = quality.get('quality_score', 0)
        efficiency = quality.get('efficiency', {})
        conv_quality = quality.get('conversation_quality', {})
        
        if efficiency.get('avg_response_time', 0) > 5:
            report_lines.append("- ⚠️ **响应时间较长**：建议优化工具调用逻辑，减少不必要的API请求")
        
        if efficiency.get('avg_tool_calls', 0) > 3:
            report_lines.append("- ⚠️ **工具调用过多**：建议优化推理链，合并相关工具调用")
        
        if conv_quality.get('clarification_rate', 0) > 0.5:
            report_lines.append("- ⚠️ **澄清率较高**：建议改进意图识别，减少反复询问")
        
        if conv_quality.get('proactive_rate', 0) < 0.3:
            report_lines.append("- ⚠️ **主动引导不足**：建议增强主动服务意识，提供更多建议")
        
        completion = quality.get('task_completion', {})
        if completion.get('success_rate', 0) < 0.6:
            report_lines.append("- ⚠️ **任务完成率低**：建议检查工具实现，提升任务成功率")
        
        if not any("⚠️" in line for line in report_lines[-5:]):
            report_lines.append("- ✅ **表现良好**：继续保持当前质量水平！")
    
    # 写入文件
    report_content = "\n".join(report_lines)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    return output_file


def generate_ascii_chart(data: Dict[str, int], title: str = "分布图") -> str:
    """生成简单的 ASCII 柱状图"""
    lines = []
    lines.append(f"\n{title}")
    lines.append("=" * 50)
    
    if not data:
        lines.append("(无数据)")
        return "\n".join(lines)
    
    max_value = max(data.values()) if data else 1
    max_label_len = max(len(str(k)) for k in data.keys()) if data else 0
    
    for label, value in sorted(data.items(), key=lambda x: x[1], reverse=True):
        bar_length = int((value / max_value) * 30) if max_value > 0 else 0
        bar = "█" * bar_length
        lines.append(f"{label:>{max_label_len}} | {bar} {value}")
    
    lines.append("=" * 50)
    return "\n".join(lines)


def generate_text_report(analytics: Dict[str, Any]) -> str:
    """生成纯文本报告（用于终端输出）"""
    lines = []
    
    lines.append("\n" + "="*60)
    lines.append("  对话质量分析报告")
    lines.append("="*60)
    
    # 质量指标
    quality = analytics.get('quality_metrics', {})
    if quality:
        lines.append(f"\n📊 综合评分: {quality.get('quality_score', 0)}/100")
        lines.append(f"⏱️  平均响应: {quality.get('efficiency', {}).get('avg_response_time', 0):.2f}秒")
        lines.append(f"🔧 平均工具: {quality.get('efficiency', {}).get('avg_tool_calls', 0):.2f}次")
        lines.append(f"✅ 成功率: {quality.get('task_completion', {}).get('success_rate', 0)*100:.1f}%")
    
    # 意图分布图
    intent = analytics.get('intent_analysis', {})
    if intent and intent.get('intent_distribution'):
        lines.append(generate_ascii_chart(
            intent['intent_distribution'],
            "\n🎯 意图分布"
        ))
    
    # 复合意图
    if intent and intent.get('composite_intents'):
        lines.append("\n🔄 复合意图:")
        for comp in intent['composite_intents']:
            lines.append(f"  - {comp.get('name')}: {comp.get('description')}")
    
    lines.append("\n" + "="*60)
    return "\n".join(lines)


def main():
    """主函数：读取测试输出并生成报告"""
    
    # 读取测试输出
    test_output_file = "test_analytics_output.json"
    
    if not os.path.exists(test_output_file):
        print(f"❌ 找不到测试输出文件: {test_output_file}")
        print("请先运行 test_phase4_advanced.py")
        return 1
    
    with open(test_output_file, 'r', encoding='utf-8') as f:
        analytics = json.load(f)
    
    # 生成文本报告（终端输出）
    print(generate_text_report(analytics))
    
    # 生成 Markdown 报告
    md_file = generate_markdown_report(analytics, "quality_report.md")
    print(f"\n✅ Markdown 报告已生成: {md_file}")
    
    # 生成详细的 JSON 报告
    detailed_file = "quality_report_detailed.json"
    with open(detailed_file, 'w', encoding='utf-8') as f:
        json.dump(analytics, f, indent=2, ensure_ascii=False)
    print(f"✅ 详细 JSON 报告已生成: {detailed_file}")
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
