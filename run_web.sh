#!/usr/bin/env bash
set -e
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR/build/web"
PORT="${PORT:-8000}"
python -m http.server "$PORT"
