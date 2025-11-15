# 对话记忆配置指南

## 概述

对话记忆系统支持通过 `config.yaml` 文件灵活配置存储策略和使用策略,无需修改代码即可调整记忆行为。

## 配置文件位置

配置文件位于: `src/agent/config.yaml`

参考示例: `src/agent/config.example.yaml`

## 配置层级

配置加载优先级:

1. **环境变量** (最高优先级)
2. **YAML 配置文件**
3. **代码默认值** (最低优先级)

## 核心配置项

### 1. 启用/禁用记忆

```yaml
memory:
  enabled: true  # true/false
```

环境变量: `MEMORY_ENABLED=true`

### 2. 后端选择

```yaml
memory:
  backend: "chromadb"  # "chromadb" 或 "basic"
```

- **chromadb**: 持久化向量存储,支持语义检索 (推荐)
- **basic**: 简单内存存储,仅支持最近N条检索

环境变量: `MEMORY_BACKEND=chromadb`

### 3. ChromaDB 配置

```yaml
memory:
  chromadb:
    persist_directory: "data/chroma_memory"  # 存储目录
    collection_name: "conversation_memory"   # Collection 名称
    embedding_model: "all-MiniLM-L6-v2"      # 嵌入模型
```

环境变量: `CHROMA_PERSIST_DIR=/path/to/storage`

## 检索策略配置

### 1. 检索模式

```yaml
memory:
  strategy:
    retrieval_mode: "recent"  # "recent" 或 "similarity"
```

- **recent**: 返回最近的 N 条对话 (速度快)
- **similarity**: 基于语义相似度检索 (智能但稍慢)

环境变量: `MEMORY_RETRIEVAL_MODE=recent`

### 2. 最近模式配置

```yaml
memory:
  strategy:
    max_recent_turns: 10  # 返回最近的 10 条对话
```

适用场景:
- 短期客服对话
- FAQ 问答
- 简单任务协助

环境变量: `MEMORY_MAX_TURNS=10`

### 3. 相似度模式配置

```yaml
memory:
  strategy:
    max_similarity_results: 5      # 返回最相似的 5 条
    similarity_threshold: 0.5       # 相似度阈值 (0-1)
```

适用场景:
- 长期项目协作
- 知识库问答
- 个人助理

相似度阈值说明:
- `0.3-0.5`: 宽松匹配,返回更多结果
- `0.5-0.7`: 中等匹配 (推荐)
- `0.7-1.0`: 严格匹配,仅返回高度相关

## 摘要生成配置

### 1. 启用 LLM 摘要

```yaml
memory:
  strategy:
    enable_llm_summary: true  # 是否使用 LLM 生成摘要
```

注意: 启用后每次生成摘要会额外调用 LLM API,增加成本和延迟。

### 2. 摘要触发策略

```yaml
memory:
  summary:
    trigger: "threshold"  # "always", "threshold", "manual"
    turns_threshold: 5               # 对话轮数超过 5 轮时生成
    text_length_threshold: 500       # 文本长度超过 500 字符时生成
    max_summary_length: 200          # 摘要最大长度
```

触发模式:
- **always**: 每轮对话都生成摘要
- **threshold**: 超过阈值时生成 (推荐)
- **manual**: 仅手动调用生成

## 会话管理配置

```yaml
memory:
  session:
    default_session_prefix: "session"  # 会话ID前缀
    timeout: 0                         # 超时时间(秒), 0=永不超时
    auto_cleanup: false                # 是否自动清理过期会话
```

## 性能优化配置

```yaml
memory:
  performance:
    enable_cache: true   # 启用内存缓存
    cache_size: 100      # 缓存最大条目数
    batch_size: 10       # 批量操作大小
```

## 使用场景示例

### 场景 1: 短期客服对话

```yaml
memory:
  enabled: true
  backend: "chromadb"
  strategy:
    retrieval_mode: "recent"
    max_recent_turns: 5
    enable_llm_summary: false
```

特点: 快速响应,低成本

### 场景 2: 长期项目协作

```yaml
memory:
  enabled: true
  backend: "chromadb"
  strategy:
    retrieval_mode: "similarity"
    max_similarity_results: 10
    similarity_threshold: 0.6
    enable_llm_summary: true
  summary:
    trigger: "threshold"
    turns_threshold: 10
```

特点: 智能检索,自动压缩长对话

### 场景 3: 高性能需求

```yaml
memory:
  enabled: true
  backend: "basic"
  strategy:
    max_recent_turns: 3
    enable_llm_summary: false
  performance:
    enable_cache: true
    cache_size: 50
```

特点: 极速响应,内存占用小

### 场景 4: 离线或低资源环境

```yaml
memory:
  enabled: true
  backend: "basic"
  strategy:
    retrieval_mode: "recent"
    max_recent_turns: 5
    enable_llm_summary: false
```

特点: 无需向量模型,最小依赖

## 环境变量覆盖

常用环境变量:

```bash
# 启用/禁用记忆
export MEMORY_ENABLED=true

# 选择后端
export MEMORY_BACKEND=chromadb

# 存储目录
export CHROMA_PERSIST_DIR=/custom/path

# 检索模式
export MEMORY_RETRIEVAL_MODE=similarity

# 最大记录数
export MEMORY_MAX_TURNS=15
```

## 代码中使用配置

### 1. 自动使用配置

```python
from agent.react_agent import LangChainAgent

# Agent 自动读取配置
agent = LangChainAgent()
```

### 2. 手动覆盖配置

```python
from agent.react_agent import LangChainAgent

# 参数优先级高于配置文件
agent = LangChainAgent(
    use_memory=True,
    session_id="custom_session",
    use_similarity_search=True,
    max_results=20,
)
```

### 3. 读取配置信息

```python
from agent.memory_config import get_memory_config

config = get_memory_config()
print(f"后端: {config.backend}")
print(f"检索模式: {config.strategy.retrieval_mode}")
print(f"存储路径: {config.chromadb.persist_directory}")
```

## 配置验证

启动 Agent 时会在日志中看到配置信息:

```
INFO agent.memory_config: 记忆配置加载完成: backend=chromadb, mode=recent
INFO agent.chroma_memory: ChromaDB 记忆初始化: session=session_abc123, mode=recent
INFO agent.react_agent: Initialized agent with ChromaDB memory: session=session_abc123, mode=recent
```

## 故障排查

### 问题 1: ChromaDB 初始化失败

**症状**: 看到 "Failed to initialize ChromaDB memory" 错误

**解决方案**:
1. 检查 `chromadb` 包是否已安装: `pip install chromadb`
2. 检查存储目录权限: `data/chroma_memory/` 需要写权限
3. 查看详细错误日志

### 问题 2: 配置不生效

**症状**: 修改配置后行为未改变

**解决方案**:
1. 确认配置文件路径正确: `src/agent/config.yaml`
2. 检查 YAML 语法是否正确 (缩进、冒号)
3. 清理缓存后重启: `rm -rf **/__pycache__`
4. 检查是否被环境变量覆盖

### 问题 3: 相似度检索效果不佳

**症状**: 返回的历史记录不相关

**解决方案**:
1. 调整 `similarity_threshold` (尝试 0.4-0.7)
2. 增加 `max_similarity_results` 数量
3. 检查嵌入模型是否正确加载
4. 考虑使用 "recent" 模式作为备选

## 最佳实践

1. **开发环境**: 使用 `recent` 模式快速迭代
2. **生产环境**: 根据实际需求选择 `similarity` 或 `recent`
3. **成本控制**: 禁用 `enable_llm_summary` 除非必要
4. **性能优化**: 启用 `enable_cache` 并调整 `cache_size`
5. **存储管理**: 定期备份 `persist_directory` 目录
6. **会话隔离**: 为不同用户/场景使用不同 `session_id`

## 高级配置

### 动态切换检索模式

```python
from agent.memory_config import get_memory_config

config = get_memory_config()

# 根据对话长度动态切换
if turn_count > 20:
    config.strategy.retrieval_mode = "similarity"
else:
    config.strategy.retrieval_mode = "recent"
```

### 自定义嵌入模型

```yaml
memory:
  chromadb:
    embedding_model: "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
```

支持所有 Sentence Transformers 模型。

## 参考资源

- [ChromaDB 文档](https://docs.trychroma.com/)
- [Sentence Transformers 模型列表](https://www.sbert.net/docs/pretrained_models.html)
- [配置示例文件](./config.example.yaml)
