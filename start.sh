#!/usr/bin/env bash
# 用法:
#   ./start.sh         生产模式:构建前端,起 FastAPI 托管 API + 静态页面 → http://localhost:8642
#   ./start.sh --dev   开发模式:后端热更新(uvicorn --reload)+ 前端 HMR(vite)→ http://localhost:3000
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -d node_modules ]; then npm install; fi
if [ ! -d .venv ]; then
  python3 -m venv .venv
  .venv/bin/pip install -e 'backend[dev]'
fi

if [ "${1:-}" = "--dev" ]; then
  (cd backend && exec ../.venv/bin/uvicorn app.main:app --reload --port 8642) &
  BACK_PID=$!
  trap 'kill $BACK_PID 2>/dev/null || true' EXIT
  npm run dev
  exit 0
fi

if [ ! -d dist ]; then npm run build; fi
cd backend
exec ../.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8642
