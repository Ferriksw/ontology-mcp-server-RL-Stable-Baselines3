# 记忆配置快速参考

## 配置文件位置
```
src/agent/config.yaml
```

## 快速配置示例

### 使用最近模式 (快速)
```yaml
memory:
  backend: "chromadb"
  strategy:
    retrieval_mode: "recent"
    max_recent_turns: 10
    enable_llm_summary: false
```

### 使用相似度模式 (智能)
```yaml
memory:
  backend: "chromadb"
  strategy:
    retrieval_mode: "similarity"
    max_similarity_results: 5
    similarity_threshold: 0.6
    enable_llm_summary: true
```

### 禁用记忆
```yaml
memory:
  enabled: false
```

## 环境变量覆盖

```bash
# 切换检索模式
export MEMORY_RETRIEVAL_MODE=similarity

# 修改最大记录数
export MEMORY_MAX_TURNS=20

# 自定义存储目录
export CHROMA_PERSIST_DIR=/custom/path
```

## 代码中使用

### 自动使用配置
```python
from agent.react_agent import LangChainAgent

agent = LangChainAgent()  # 自动读取配置
```

### 覆盖配置
```python
agent = LangChainAgent(
    use_similarity_search=True,
    max_results=20,
)
```

### 读取配置
```python
from agent.memory_config import get_memory_config

config = get_memory_config()
print(config.strategy.retrieval_mode)
```

## 常用配置项

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `memory.enabled` | `true` | 启用/禁用记忆 |
| `memory.backend` | `chromadb` | 后端类型 |
| `strategy.retrieval_mode` | `recent` | 检索模式 |
| `strategy.max_recent_turns` | `10` | 最近模式记录数 |
| `strategy.enable_llm_summary` | `false` | 启用 LLM 摘要 |
| `performance.enable_cache` | `true` | 启用缓存 |

## 场景推荐

| 场景 | 配置 |
|------|------|
| 客服对话 | `recent` + `max_turns: 5` |
| 项目协作 | `similarity` + `threshold: 0.6` |
| 知识问答 | `similarity` + `llm_summary: true` |
| 高性能 | `backend: basic` + `cache: true` |

## 测试配置

```bash
# 运行配置测试
python3 test_memory_config.py

# 查看配置
python3 -c "from agent.memory_config import get_memory_config; print(get_memory_config())"
```

## 更多信息

- 完整指南: `docs/MEMORY_CONFIG_GUIDE.md`
- 实现文档: `docs/MEMORY_CONFIG_IMPLEMENTATION.md`
- 示例配置: `src/agent/config.example.yaml`
