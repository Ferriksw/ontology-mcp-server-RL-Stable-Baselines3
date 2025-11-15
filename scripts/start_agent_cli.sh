#!/usr/bin/env bash
# Agent CLI 交互式启动脚本

set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(cd "${SCRIPT_DIR}/.." && pwd)
cd "${REPO_ROOT}"

: "${MCP_BASE_URL:=http://localhost:8000}"
export MCP_BASE_URL

echo "========================================"
echo "   Ontology MCP Agent - CLI 模式"
echo "========================================"
echo ""
echo "MCP 服务器: $MCP_BASE_URL"
echo "配置文件: src/agent/config.yaml"
echo ""

# 激活虚拟环境
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "✓ 虚拟环境已激活"
else
    echo "⚠️  未找到虚拟环境，请先运行: python3 -m venv .venv"
    exit 1
fi

# 运行测试脚本
python3 test_agent_cli.py "$@"
