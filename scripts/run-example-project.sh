#!/usr/bin/env bash
set -euo pipefail

# 請將此路徑改成你的 WSL 專案路徑。
export PROJECT_DIR="/mnt/d/path/to/your/project"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${REPO_DIR}"
docker compose run --rm opencode
