#!/usr/bin/env bash
# 一次性脚本:把课程数据导出为 Python 模块 backend/data/curriculum.py。
# 利用项目已有的 esbuild(vite 依赖)打包 TS,再经 python 转写为 Python 字面量。
set -euo pipefail
cd "$(dirname "$0")/../.."   # 仓库根目录

npx esbuild src/data/curriculum.ts --bundle --platform=node --format=cjs \
  --outfile=/tmp/deb-chess-curriculum.cjs --log-level=warning

node -e "
const { chapters } = require('/tmp/deb-chess-curriculum.cjs');
process.stdout.write(JSON.stringify(chapters));
" | python3 -c "
import json, pprint, sys
data = json.load(sys.stdin)
header = '''# 课程数据:教学方法源自《鲍比·菲舍尔教你下国际象棋》(Bobby Fischer Teaches Chess)
# 菲舍尔核心理念:程序化练习 —— 看局面、自己想、对答案,反复识别杀王模式形成直觉。
# 所有棋题均经过 python-chess 引擎逐一校验(见 backend/scripts/validate_curriculum.py)。
#
# 本文件由 backend/scripts/convert_curriculum.sh 生成;修改请直接编辑本文件,
# 改完必须跑校验:.venv/bin/python backend/scripts/validate_curriculum.py

CHAPTERS = '''
out = header + pprint.pformat(data, width=100, sort_dicts=False) + '\n'
open('backend/data/curriculum.py', 'w', encoding='utf-8').write(out)
levels = sum(len(c['levels']) for c in data)
steps = sum(len(l['steps']) for c in data for l in c['levels'])
print('chapters:', len(data), 'levels:', levels, 'steps:', steps)
"
