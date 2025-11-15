# Agent 对话记忆功能使用指南

## 功能概述

对话记忆功能为 Agent 提供了上下文保持能力,使其能够:

1. **记录完整对话历史** - 保存用户输入、Agent 响应和工具调用
2. **自动生成摘要** - 为每轮对话生成简洁摘要
3. **注入历史上下文** - 在新的推理中自动包含最近的对话摘要
4. **持久化存储** - 支持保存和加载对话历史

## 快速开始

### 1. 启用基础记忆

```python
from agent.react_agent import LangChainAgent

# 创建启用记忆的 Agent
agent = LangChainAgent(
    use_memory=True,           # 启用记忆
    max_history=10,            # 保留最近10轮对话
    max_summary_length=5,      # 注入最近5轮摘要
)

# 多轮对话会自动保持上下文
result1 = agent.run("我是VIP客户,订单500元")
result2 = agent.run("那1000元呢?")  # Agent 会记住你是VIP客户
```

### 2. 启用增强版记忆 (LLM 生成摘要)

```python
agent = LangChainAgent(
    use_memory=True,
    enhanced_memory=True,      # 使用 LLM 生成更智能的摘要
    max_history=10,
    max_summary_length=5,
)
```

**注意**: 增强版记忆会为每轮对话额外调用一次 LLM 生成摘要,会增加响应延迟和 API 调用成本。

### 3. Gradio UI 中使用

Gradio UI 已默认启用记忆功能:

```bash
# 启动 UI
./scripts/run_agent.sh

# 或直接运行
python3 -m agent.gradio_ui
```

UI 特性:
- **对话历史面板**: 显示完整对话
- **对话记忆面板**: 显示摘要(右下角)
- **清空对话按钮**: 清除所有历史记录

## API 使用

### 查看记忆状态

```python
# 获取当前上下文摘要
context = agent.get_memory_context()
print(context)
# 输出:
# # 对话历史摘要
# 1. 用户: 我是VIP客户,订单金额500元, 调用工具: ontology_explain_discount → VIP客户订单...
# 2. 用户: 那如果金额是1000元呢?, 调用工具: ontology_explain_discount → 1000元订单...

# 获取完整历史
history = agent.get_full_history()
for turn in history:
    print(f"用户: {turn['user_input']}")
    print(f"Agent: {turn['agent_response']}")
    print(f"摘要: {turn['summary']}")
```

### 清空记忆

```python
# 清空所有对话历史
agent.clear_memory()
```

### 保存和加载记忆

```python
# 保存到文件
agent.save_memory("conversation_history.json")

# 加载历史
new_agent = LangChainAgent(use_memory=True)
new_agent.load_memory("conversation_history.json")
```

## 配置参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `use_memory` | bool | True | 是否启用记忆功能 |
| `enhanced_memory` | bool | False | 是否使用 LLM 生成摘要 |
| `max_history` | int | 10 | 保留的最大对话轮数 |
| `max_summary_length` | int | 5 | 注入上下文时使用的最大摘要数 |

### 参数调优建议

**短对话场景** (快速问答):
```python
agent = LangChainAgent(
    use_memory=True,
    max_history=5,
    max_summary_length=3,
)
```

**长对话场景** (复杂任务):
```python
agent = LangChainAgent(
    use_memory=True,
    max_history=20,
    max_summary_length=10,
)
```

**高质量摘要场景**:
```python
agent = LangChainAgent(
    use_memory=True,
    enhanced_memory=True,  # 使用 LLM 生成摘要
    max_history=10,
    max_summary_length=5,
)
```

## 工作原理

### 1. 对话流程

```
用户输入 
  ↓
注入历史摘要到 prompt
  ↓
LLM 推理 + 工具调用
  ↓
生成响应
  ↓
保存对话记录 + 生成摘要
  ↓
更新记忆
```

### 2. 摘要生成

**基础模式** (规则提取):
- 截取用户输入前100字符
- 记录使用的工具名称
- 截取响应前50字符
- 格式: `用户: {input}, 调用工具: {tools} → {response}`

**增强模式** (LLM 生成):
- 将完整对话发送给 LLM
- 生成不超过50字的智能摘要
- 捕获关键信息和意图

### 3. 上下文注入

在每次用户提问时,会自动构造增强提示:

```
# 对话历史摘要
1. 用户: 我是VIP客户...
2. 用户: 订单金额1000元...
3. 用户: 帮我查询折扣...

# 当前用户问题
那如果金额是2000元呢?
```

## 测试和演示

### 运行演示脚本

```bash
cd /home/ontology-mcp-server
source .venv/bin/activate
python3 test_memory_demo.py
```

演示内容:
1. ✅ 基础对话记忆
2. ✅ 记忆上下文注入
3. ✅ 记忆持久化
4. ✅ 记忆长度限制

### 交互式测试

```bash
# 启动 Gradio UI
./scripts/run_agent.sh

# 访问 http://127.0.0.1:7870
# 进行多轮对话,观察右下角的"对话记忆"面板
```

### CLI 测试

```python
from agent.react_agent import LangChainAgent

agent = LangChainAgent(use_memory=True)

# 第一轮
agent.run("我想买iPhone 15")

# 第二轮 - 会记住上下文
agent.run("这个手机多少钱?")

# 查看记忆
print(agent.get_memory_context())
```

## 性能考虑

### Token 消耗

- **基础记忆**: 每轮对话额外消耗约 50-200 tokens (取决于摘要数量)
- **增强记忆**: 每轮额外调用1次 LLM,增加约 200-500 tokens

### 响应延迟

- **基础记忆**: 几乎无延迟增加(规则生成摘要)
- **增强记忆**: 每轮增加约 1-2 秒(LLM 生成摘要)

### 建议

- 生产环境使用**基础记忆** (速度快,成本低)
- 关键场景使用**增强记忆** (质量高,上下文理解更准确)
- 根据对话长度调整 `max_history` 和 `max_summary_length`

## 故障排查

### 记忆未生效

检查 Agent 初始化:
```python
# 确保启用记忆
agent = LangChainAgent(use_memory=True)

# 验证记忆状态
print(f"记忆启用: {agent.use_memory}")
print(f"历史记录数: {len(agent.get_full_history())}")
```

### 上下文丢失

- 检查 `max_history` 设置是否过小
- 检查 `max_summary_length` 是否足够
- 查看日志确认摘要生成是否正常

### 增强记忆失败

- 检查 LLM API 是否正常
- 查看日志中的错误信息
- 会自动降级到基础记忆模式

## 最佳实践

### 1. 根据场景选择模式

```python
# 快速客服 - 基础记忆
customer_service_agent = LangChainAgent(
    use_memory=True,
    max_history=5,
    max_summary_length=3,
)

# 复杂咨询 - 增强记忆
consulting_agent = LangChainAgent(
    use_memory=True,
    enhanced_memory=True,
    max_history=15,
    max_summary_length=8,
)
```

### 2. 定期清理记忆

```python
# 在会话结束时清空
agent.clear_memory()

# 或保存后清空
agent.save_memory(f"session_{session_id}.json")
agent.clear_memory()
```

### 3. 监控记忆使用

```python
# 定期检查
if len(agent.get_full_history()) > 50:
    logger.warning("对话历史过长,考虑清理")
    agent.clear_memory()
```

### 4. 结合持久化

```python
# 会话开始时加载
if os.path.exists(history_file):
    agent.load_memory(history_file)

# 定期保存
agent.save_memory(history_file)

# 会话结束时保存
agent.save_memory(f"sessions/{user_id}_{timestamp}.json")
```

## 扩展开发

### 自定义摘要生成

继承 `ConversationMemory` 并重写 `_generate_summary`:

```python
from agent.memory import ConversationMemory

class CustomMemory(ConversationMemory):
    def _generate_summary(self, turn):
        # 自定义摘要逻辑
        summary = f"意图: {extract_intent(turn.user_input)}"
        return summary
```

### 集成外部存储

```python
class DatabaseMemory(ConversationMemory):
    def save_to_file(self, filepath):
        # 保存到数据库
        db.save_conversation(self.get_full_history())
    
    def load_from_file(self, filepath):
        # 从数据库加载
        data = db.load_conversation(session_id)
        # ...
```

## 参考链接

- [Agent 实现代码](../src/agent/react_agent.py)
- [记忆模块代码](../src/agent/memory.py)
- [Gradio UI 代码](../src/agent/gradio_ui.py)
- [演示脚本](../test_memory_demo.py)
