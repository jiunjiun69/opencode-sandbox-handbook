#!/usr/bin/env bash
set -euo pipefail

# Set this to a WSL path before running the script, for example:
# export PROJECT_DIR="/mnt/d/path/to/your/project"
if [ -z "${PROJECT_DIR:-}" ]; then
  echo "Error: PROJECT_DIR is not set."
  echo "Example: export PROJECT_DIR=\"/mnt/d/path/to/your/project\""
  exit 1
fi

if [ ! -d "${PROJECT_DIR}" ]; then
  echo "Error: PROJECT_DIR does not exist: ${PROJECT_DIR}"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${REPO_DIR}"
docker compose run --service-ports --rm opencode
