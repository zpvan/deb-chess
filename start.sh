#!/usr/bin/env bash
# 本地一键启动:构建前端 → 起 FastAPI(单进程托管 API + 静态页面)
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -d node_modules ]; then npm install; fi
if [ ! -d dist ]; then npm run build; fi
if [ ! -d .venv ]; then
  python3 -m venv .venv
  .venv/bin/pip install -e 'backend[dev]'
fi

cd backend
exec ../.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
