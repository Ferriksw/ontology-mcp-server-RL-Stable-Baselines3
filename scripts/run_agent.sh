#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(cd "${SCRIPT_DIR}/.." && pwd)
cd "${REPO_ROOT}"

: "${MCP_BASE_URL:=http://localhost:8000}"
export MCP_BASE_URL

python3 -m agent.gradio_ui "$@"
