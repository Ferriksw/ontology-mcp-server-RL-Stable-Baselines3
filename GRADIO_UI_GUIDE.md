# Gradio UI 使用指南

## 启动 UI

### 方式 1: 使用启动脚本 (推荐)

```bash
# 确保 MCP server 已在 http://localhost:8000 运行
./scripts/run_agent.sh
```

### 方式 2: 直接运行

```bash
cd /home/ontology-mcp-server
source .venv/bin/activate
GRADIO_SERVER_PORT=7870 python3 -m agent.gradio_ui
```

## 访问 UI

启动成功后,在浏览器中打开:

```
http://127.0.0.1:7870
```

## UI 组件说明

### 左侧面板 (对话区域)
- **对话历史**: 显示用户与 Agent 的完整对话记录
- **输入框**: 输入查询或请求
- **发送按钮**: 提交请求给 Agent

### 右侧面板 (调试信息)
- **Plan / Tasks**: 显示 Agent 的推理计划和任务分解
- **Tool Calls**: 展示 Agent 调用的工具及其输入输出

## 测试用例

### 示例 1: 折扣解释查询

```
我是VIP客户,订单金额是500元,能打几折?
```

**预期结果**:
- Agent 调用 `ontology_explain_discount` 工具
- 返回折扣计算结果和规则解释

### 示例 2: 产品名称规范化

```
帮我查询"iPhone 15 Pro Max"的标准产品名称
```

**预期结果**:
- Agent 调用 `ontology_normalize_product` 工具
- 返回规范化的产品名称和同义词

### 示例 3: 订单验证

```
验证订单:客户ID是customer_123,购买产品是product_456,数量3件,总价1200元
```

**预期结果**:
- Agent 调用 `ontology_validate_order` 工具
- 返回 SHACL 验证结果(是否符合业务规则)

## 环境变量配置

### MCP Server 地址

```bash
export MCP_BASE_URL=http://localhost:8000
```

### Gradio 端口

```bash
export GRADIO_SERVER_PORT=7870
```

### 公网分享 (可选)

```bash
export GRADIO_SHARE=true
```

启用后会生成公网可访问的临时链接(有效期 72 小时)

## 版本信息

- **Gradio**: 3.50.2 (降级到 3.x 解决 Pydantic V2 兼容性问题)
- **Python**: 3.12
- **OpenAI Client**: 1.30.0+
- **DeepSeek API**: https://api.deepseek.com/v1

## 故障排查

### UI 无法启动

1. 检查 MCP server 是否运行:
   ```bash
   curl http://localhost:8000/health
   ```

2. 查看日志输出,确认没有端口冲突

3. 清理 Python 缓存:
   ```bash
   find . -type d -name "__pycache__" -exec rm -rf {} +
   ```

### Tool 调用失败

1. 确认 `config.yaml` 中 API key 配置正确
2. 检查 MCP server 日志是否有错误
3. 验证网络连接(DeepSeek API 访问)

### 响应缓慢

- DeepSeek API 可能受网络延迟影响
- 考虑使用本地大模型(如 Ollama)替代

## CLI 测试替代方案

如果不想使用 Gradio UI,可以用 CLI 测试:

```bash
./scripts/start_agent_cli.sh
```

CLI 模式直接输出结构化结果,适合调试和自动化测试。
