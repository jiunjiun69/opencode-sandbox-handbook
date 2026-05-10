#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "用法：$0 /mnt/d/path/to/your/project"
  exit 1
fi

export PROJECT_DIR="$1"

if [ ! -d "${PROJECT_DIR}" ]; then
  echo "錯誤：PROJECT_DIR 不存在：${PROJECT_DIR}"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${REPO_DIR}"
docker compose run --rm opencode
