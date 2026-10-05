#!/usr/bin/env bash
# 一次性脚本:把 src/data/curriculum.ts 的 chapters 数据导出为 JSON。
# 利用项目已有的 esbuild(vite 依赖)打包 TS,无需新增依赖。
set -euo pipefail
cd "$(dirname "$0")/../.."   # 仓库根目录

npx esbuild src/data/curriculum.ts --bundle --platform=node --format=cjs \
  --outfile=/tmp/deb-chess-curriculum.cjs --log-level=warning

node -e "
const { chapters } = require('/tmp/deb-chess-curriculum.cjs');
const fs = require('fs');
fs.mkdirSync('backend/data', { recursive: true });
fs.writeFileSync('backend/data/curriculum.json', JSON.stringify(chapters, null, 2));
const levels = chapters.reduce((n, c) => n + c.levels.length, 0);
const steps = chapters.reduce((n, c) => n + c.levels.reduce((m, l) => m + l.steps.length, 0), 0);
console.log('chapters:', chapters.length, 'levels:', levels, 'steps:', steps);
"
