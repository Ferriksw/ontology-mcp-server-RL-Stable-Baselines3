# Agent 使用指南

## 快速启动

### 方式 1: 命令行测试（推荐）

```bash
# 启动 CLI 测试
./scripts/start_agent_cli.sh

# 或直接运行
source .venv/bin/activate
python3 test_agent_cli.py
```

### 方式 2: Python API 集成

```python
from agent.react_agent import LangChainAgent

# 初始化 agent
agent = LangChainAgent()

# 运行查询
result = agent.run("我是VIP客户，订单金额是500元，请解释折扣规则")

# 获取结果
print("回答:", result["final_answer"])
print("计划:", result["plan"])
print("工具调用:", result["tool_log"])
```

## 配置

Agent 配置位于 `src/agent/config.yaml`:

```yaml
OPENAI_API_URL: https://api.deepseek.com/v1
OPENAI_API_KEY: your-api-key-here
OPENAI_MODEL: deepseek-chat
MCP_BASE_URL: http://localhost:8000
```

也可通过环境变量覆盖:

```bash
export OPENAI_API_KEY="sk-xxxxx"
export OPENAI_API_URL="https://api.deepseek.com/v1"
export MCP_BASE_URL="http://localhost:8000"
```

## 可用工具

Agent 自动连接到 MCP 服务器并加载以下工具:

1. **ontology_explain_discount** - 解释订单折扣规则
2. **ontology_normalize_product** - 商品名称归一化
3. **ontology_validate_order** - SHACL 数据校验

## 架构说明

```
┌─────────────────┐
│  Gradio UI      │  (可选，当前有兼容性问题)
│  (暂不可用)      │
└────────┬────────┘
         │
┌────────▼────────────────────────────┐
│     LangChainAgent                  │
│  - 自定义 OpenAI function-calling   │
│  - 工具调用循环                      │
│  - 对话历史管理                      │
└────────┬────────────────────────────┘
         │
    ┌────┴────┐
    │         │
┌───▼──┐  ┌──▼───────┐
│ LLM  │  │ MCP Tools│
│Model │  │ Adapter  │
└──────┘  └──────────┘
   │          │
   │      ┌───▼──────────┐
   │      │ MCP Server   │
   │      │ (HTTP API)   │
   │      └──────────────┘
   │
   └─► OpenAI/DeepSeek API
```

## 已移除的依赖

✅ 成功移除 `langchain-openai` 和相关 LangChain 组件
✅ 使用原生 `openai>=1.30.0` 客户端
✅ 自定义工具抽象层 (`ToolDefinition`)

## 已知问题

- **Gradio UI**: 当前版本 (4.x) 与 Pydantic V2 JSON schema 存在兼容性问题
  - 临时方案: 使用 CLI 或 Python API
  - 或降级到 Gradio 3.x

## 测试示例

```bash
# 测试折扣解释
./scripts/start_agent_cli.sh

# 自定义 MCP 服务器地址
MCP_BASE_URL=http://custom-server:8080 ./scripts/start_agent_cli.sh
```

## 日志

Agent 运行日志保存在:
- `src/agent/logs/agent.log`

查看实时日志:
```bash
tail -f src/agent/logs/agent.log
```
