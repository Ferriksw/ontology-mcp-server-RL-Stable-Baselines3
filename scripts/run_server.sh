#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(cd "${SCRIPT_DIR}/.." && pwd)
cd "${REPO_ROOT}"

: "${ONTOLOGY_DATA_DIR:=${REPO_ROOT}/data}"
export ONTOLOGY_DATA_DIR

APP_HOST=${APP_HOST:-0.0.0.0}
APP_PORT=${APP_PORT:-8000}

uvicorn ontology_mcp_server.server:app --host "${APP_HOST}" --port "${APP_PORT}" "$@"
