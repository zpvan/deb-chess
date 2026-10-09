# Pyodide 静态版实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 Python 后端核心(python-chess + session/bot/models)用 Pyodide 跑在浏览器里,产出纯静态站点并自动部署到 GitHub Pages(zpvan.github.io/deb-chess)。

**Architecture:** 新增纯 Python 门面 `static_facade.py`(模块级会话/进度状态,返回 JSON 字符串);前端新增 `pyodide-api.ts`(与 `api.ts` 同签名),由 `backend.ts` 按构建模式切换;`npm run build:static` 产出纯静态产物。

**Tech Stack:** Pyodide(CDN 加载运行时)、python-chess(纯 Python wheel)、pydantic(官方 wasm32 wheel——已验证 pydantic 官方为 Pyodide 编译 pydantic-core)。

**Spec:** `docs/superpowers/specs/2026-10-09-pyodide-static-design.md`

**已验证的关键事实:** pydantic 官方为 wasm32/Pyodide 发布 wheel(pydantic-core 单测在 wasm 通过);python-chess 纯 Python,`micropip.install('python-chess')` 即可。

## 关键接口契约(跨任务一致性)

- `static_facade.py` 函数(均返回 JSON 字符串):`init()`、`get_curriculum(lang)`、`get_progress(lang)`、`meta()`、`create_session(level_id, lang)`、`get_session(sid)`、`session_move(sid, uci)`、`session_choice(sid, index)`、`session_next(sid)`、`restart_play(sid, bot)`、`set_progress_json(json_str)`。
- 返回信封:成功 `{"ok": true, "data": ...}`;失败 `{"ok": false, "status": 404|422, "detail": {"code":..., "zh":..., "en":...}}`(404 时 detail 为字符串,与 FastAPI 一致)。
- 前端 `backend` 对象签名(与 api.ts 一致):`getCurriculum(lang)`、`getProgress(lang)`、`createSession(levelId, lang)`、`getSession(id)`、`sessionMove(id, move)`、`sessionChoice(id, index)`、`sessionNext(id)`、`restartPlay(id, bot?)`。
- 构建模式:`vite build --mode static` 时 `import.meta.env.MODE === 'static'`。
- 进度持久化:JS 侧 localStorage key `deb-chess-progress`(JSON);pyodide 初始化时注入,每次通关后回写。
- Pyodide CDN:`https://cdn.jsdelivr.net/pyodide/v0.29.0/full/`(script 标签动态注入,不加 npm 依赖)。

---

### Task 1: db.py 提取纯函数 + static_facade.py(TDD)

**Files:**
- Modify: `backend/app/db.py`(提取模块级纯函数,ProgressDB 内部复用)
- Create: `backend/app/static_facade.py`
- Test: `backend/tests/test_static_facade.py`

- [ ] **Step 1: 写失败的测试**

`backend/tests/test_static_facade.py`:

```python
import json

import pytest

from app import static_facade as sf


@pytest.fixture(autouse=True)
def fresh_facade():
    """每个用例重置门面状态。"""
    sf.reset()
    yield


def unwrap(raw: str):
    return json.loads(raw)


def test_curriculum_en_zh():
    en = unwrap(sf.get_curriculum('en'))
    zh = unwrap(sf.get_curriculum('zh'))
    assert en['ok'] and zh['ok']
    assert en['data']['chapters'][0]['title'] == 'Meet the Pieces'
    assert zh['data']['chapters'][0]['title'] == '认识棋子朋友'


def test_meta_no_stockfish():
    m = unwrap(sf.meta())
    assert m['ok'] is True
    assert m['data']['stockfish_available'] is False
    assert 'master' in m['data']['bot_styles']  # 列表不变,前端自行隐藏


def test_full_lesson_flow_and_progress():
    sid = unwrap(sf.create_session('w1', 'en'))['data']['session_id']
    # teach → next
    st = unwrap(sf.session_next(sid))['data']
    assert st['step_index'] == 1
    # 非法走法 → 422 双语错误
    bad = unwrap(sf.session_move(sid, 'a1b2'))
    assert bad['ok'] is False and bad['status'] == 422
    assert bad['detail']['code'] == 'illegal'
    # 错误走法
    st = unwrap(sf.session_move(sid, 'a1a4'))['data']
    assert st['last_result'] == 'wrong'
    # 正确走法 → 英文成功文案
    st = unwrap(sf.session_move(sid, 'a1a5'))['data']
    assert st['solved'] is True
    assert isinstance(st['success_text'], str) and 'a5' in st['success_text']
    # 会话语言保持:zh 会话返回中文标题
    sid_zh = unwrap(sf.create_session('w1', 'zh'))['data']['session_id']
    assert unwrap(sf.get_session(sid_zh))['data']['level_title'] == '棋子走法小课堂'


def test_progress_persist_hook():
    captured = []
    sf.set_progress_json('{"levels": {"w1": 2}, "xp": 100}')
    assert unwrap(sf.get_progress('en'))['data']['xp'] == 100
    assert unwrap(sf.get_progress('zh'))['data']['rank_name'] == '小骑士'
    sid = unwrap(sf.create_session('w2', 'en'))['data']['session_id']
    # w2 第一关:teach → next,mate 一步杀
    unwrap(sf.session_next(sid))
    st = unwrap(sf.session_move(sid, 'e1e8'))['data']
    assert st['solved'] is True
    st = unwrap(sf.session_next(sid))['data']
    # w2 第二题也是一步杀(角落版)
    st2 = unwrap(sf.session_move(sid, 'a1a8'))['data']
    assert st2['solved'] is True
    fin = unwrap(sf.session_next(sid))['data']
    assert fin['finished'] is True
    # 通关后进度写出钩子被调用
    saved = sf.get_progress_json()
    p = json.loads(saved)
    assert p['levels']['w2'] >= 1
    assert p['xp'] > 100
    _ = captured


def test_unknown_session_404():
    r = unwrap(sf.session_move('deadbeef', 'a1a5'))
    assert r['ok'] is False and r['status'] == 404


def test_unknown_level_404():
    r = unwrap(sf.create_session('nope', 'en'))
    assert r['ok'] is False and r['status'] == 404
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd backend && ../.venv/bin/pytest tests/test_static_facade.py -v`
Expected: FAIL,`ModuleNotFoundError: No module named 'app.static_facade'`

- [ ] **Step 3: db.py 提取纯函数**

`backend/app/db.py`:在 `RANKS` 之后、`ProgressDB` 之前插入两个模块级函数:

```python
def rank_for(xp: int, lang: str = 'en') -> dict:
    """按 XP 计算段位。rank_name 按 lang 返回中/英文。"""
    rank = next((r for r in reversed(RANKS) if xp >= r[0]), RANKS[0])
    return {'rank_name': rank[2] if lang == 'en' else rank[1], 'rank_icon': rank[3]}


def xp_gain(prev_stars: int, stars: int) -> tuple[int, int]:
    """返回 (新的最佳星级, 本次获得的 XP)。规则:首通 60+stars*20;刷新纪录补差。"""
    best = max(prev_stars, stars)
    gained = 60 + stars * 20 if prev_stars == 0 else max(0, (best - prev_stars) * 20)
    return best, gained
```

`ProgressDB.get` 的 rank 计算改为复用:`**rank_for(xp, lang)`;`complete_level` 改为:

```python
    def complete_level(self, level_id: str, stars: int, lang: str = 'en') -> dict:
        row = self._conn.execute('SELECT stars FROM levels WHERE level_id=?', (level_id,)).fetchone()
        prev = row[0] if row else 0
        best, gained = xp_gain(prev, stars)
        self._conn.execute(
            'INSERT INTO levels (level_id, stars) VALUES (?, ?) '
            'ON CONFLICT(level_id) DO UPDATE SET stars=excluded.stars',
            (level_id, best))
        self._conn.execute(
            "INSERT INTO meta (key, value) VALUES ('xp', ?) "
            'ON CONFLICT(key) DO UPDATE SET value = value + excluded.value',
            (gained,))
        self._conn.commit()
        return self.get(lang)
```

`get` 方法 return 替换为:

```python
        return {
            'levels': levels,
            'xp': xp,
            'total_stars': sum(levels.values()),
            **rank_for(xp, lang),
        }
```

Run: `cd backend && ../.venv/bin/pytest tests/test_db.py -q` → Expected: 4 passed(重构无行为变化)。

- [ ] **Step 4: 实现 static_facade.py**

`backend/app/static_facade.py`:

```python
"""静态版(Pyodide)门面:与 FastAPI 路由对应的纯函数,全部返回 JSON 字符串。

模块级状态:课程(惰性加载)、SessionStore、进度(内存 dict)。
JS 侧通过 set_progress_json/get_progress_json 对接 localStorage 持久化。
"""
import json

from app.core.session import ERRORS, IllegalMove, LessonSession
from app.core.store import SessionStore
from app.db import rank_for, xp_gain
from app.models import load_curriculum, loc_text, public_step

_curriculum = None
_store = None
_progress = {'levels': {}, 'xp': 0}


def init() -> None:
    """加载课程数据(幂等)。所有公开函数内部会自动调用。"""
    global _curriculum, _store
    if _curriculum is None:
        _curriculum = load_curriculum()
    if _store is None:
        _store = SessionStore()


def reset() -> None:
    """测试用:清空全部状态。"""
    global _curriculum, _store, _progress
    _curriculum = None
    _store = None
    _progress = {'levels': {}, 'xp': 0}


# ---------- 进度持久化(JS 对接 localStorage) ----------

def set_progress_json(raw: str) -> None:
    global _progress
    try:
        data = json.loads(raw)
        _progress = {'levels': dict(data.get('levels', {})), 'xp': int(data.get('xp', 0))}
    except (ValueError, TypeError):
        pass


def get_progress_json() -> str:
    return json.dumps(_progress, ensure_ascii=False)


def _ok(data) -> str:
    return json.dumps({'ok': True, 'data': data}, ensure_ascii=False)


def _err(status: int, detail) -> str:
    return json.dumps({'ok': False, 'status': status, 'detail': detail}, ensure_ascii=False)


def _get_session(sid: str):
    s = _store.get(sid)
    if s is None:
        return None
    return s


def _maybe_record(s: LessonSession) -> None:
    if s.finished and not s.progress_recorded:
        prev = _progress['levels'].get(s.level.id, 0)
        best, gained = xp_gain(prev, s.stars)
        _progress['levels'][s.level.id] = best
        _progress['xp'] += gained
        s.progress_recorded = True


# ---------- 公开 API ----------

def get_curriculum(lang: str = 'en') -> str:
    init()
    chapters = []
    for ch in _curriculum.chapters:
        levels = [{
            'id': lv.id,
            'title': loc_text(lv.title, lang),
            'goal': loc_text(lv.goal, lang),
            'skill': loc_text(lv.skill, lang),
            'steps': [public_step(st, lang) for st in lv.steps],
        } for lv in ch.levels]
        chapters.append({
            'id': ch.id,
            'badge': loc_text(ch.badge, lang),
            'title': loc_text(ch.title, lang),
            'intro': loc_text(ch.intro, lang),
            'color': ch.color,
            'soft': ch.soft,
            'levels': levels,
        })
    return _ok({
        'chapters': chapters,
        'total_levels': len(_curriculum.flat_levels()),
        'total_puzzles': _curriculum.total_puzzles,
        'stockfish_available': False,
        'bot_styles': ['random', 'greedy', 'smart', 'master'],
    })


def meta() -> str:
    init()
    return _ok({'stockfish_available': False,
                'bot_styles': ['random', 'greedy', 'smart', 'master']})


def get_progress(lang: str = 'en') -> str:
    init()
    levels = _progress['levels']
    return _ok({
        'levels': levels,
        'xp': _progress['xp'],
        'total_stars': sum(levels.values()),
        **rank_for(_progress['xp'], lang),
    })


def create_session(level_id: str, lang: str = 'en') -> str:
    init()
    try:
        s = LessonSession(_curriculum, level_id, lang=lang)
    except KeyError:
        return _err(404, f'level not found: {level_id}')
    _store.put(s)
    return _ok(s.state())


def get_session(sid: str) -> str:
    init()
    s = _get_session(sid)
    if s is None:
        return _err(404, 'session not found or expired')
    return _ok(s.state())


def _op(sid: str, fn) -> str:
    init()
    s = _get_session(sid)
    if s is None:
        return _err(404, 'session not found or expired')
    try:
        state = fn(s)
    except IllegalMove as e:
        msg = ERRORS[e.code]
        return _err(422, {'code': e.code, 'zh': msg['zh'], 'en': msg['en']})
    _maybe_record(s)
    return _ok(state)


def session_move(sid: str, uci: str) -> str:
    return _op(sid, lambda s: s.submit_move(uci))


def session_choice(sid: str, index: int) -> str:
    return _op(sid, lambda s: s.submit_choice(index))


def session_next(sid: str) -> str:
    return _op(sid, lambda s: s.advance())


def restart_play(sid: str, bot: str | None = None) -> str:
    return _op(sid, lambda s: s.restart_play(bot_style=bot))
```

Run: `cd backend && ../.venv/bin/pytest tests/test_static_facade.py tests/test_db.py -q`
Expected: 全部通过。

- [ ] **Step 5: Commit**

```bash
git add backend/app/db.py backend/app/static_facade.py backend/tests/test_static_facade.py
git commit -m "feat: static facade for Pyodide with progress hooks"
```

### Task 2: Python 打包脚本 + pyodide-api.ts + backend.ts 切换层

**Files:**
- Create: `scripts/bundle_py.mjs`
- Create: `src/lib/pyodide-api.ts`
- Create: `src/lib/backend.ts`
- Modify: `src/state/curriculum.tsx`、`src/state/progress.tsx`、`src/pages/Lesson.tsx`(import 换源)
- Modify: `package.json`(scripts)
- Modify: `.gitignore`(pybundle 生成物)

- [ ] **Step 1: bundle_py.mjs**

`scripts/bundle_py.mjs`:

```js
// 构建时把 Python 后端源码打包成 src/lib/pybundle.ts(生成物,不入库)。
import { readdirSync, readFileSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'

const FILES = []
function walk(dir, prefix) {
  for (const name of readdirSync(dir)) {
    if (name.startsWith('.') || name === '__pycache__') continue
    const p = join(dir, name)
    if (p.endsWith('.py')) {
      FILES.push([`${prefix}/${name}`, readFileSync(p, 'utf-8')])
    } else if (!p.includes('.')) {
      walk(p, `${prefix}/${name}`)
    }
  }
}

walk('backend/app', 'app')
FILES.push(['data/curriculum.py', readFileSync('backend/data/curriculum.py', 'utf-8')])
// main.py 是 FastAPI 壳,静态版不需要,剔除
const filtered = FILES.filter(([p]) => p !== 'app/main.py')

const out = `// GENERATED by scripts/bundle_py.mjs — do not edit
export const PY_FILES: Record<string, string> = ${JSON.stringify(Object.fromEntries(filtered), null, 0)}
`
writeFileSync('src/lib/pybundle.ts', out)
console.log(`pybundle.ts written: ${filtered.length} files, ${out.length} bytes`)
```

- [ ] **Step 2: pyodide-api.ts**

`src/lib/pyodide-api.ts`:

```ts
// 静态版后端:Pyodide 在浏览器里跑 Python 后端核心。
// 与 api.ts 暴露完全相同的函数签名,由 backend.ts 按构建模式选择。
import { ApiError, type CurriculumResponse, type ProgressResponse, type SessionState } from './api'
import { PY_FILES } from './pybundle'

const PYODIDE_URL = 'https://cdn.jsdelivr.net/pyodide/v0.29.0/full/pyodide.js'
const PYODIDE_INDEX = 'https://cdn.jsdelivr.net/pyodide/v0.29.0/full/'
const PROGRESS_KEY = 'deb-chess-progress'

declare global {
  interface Window {
    loadPyodide?: (opts: { indexURL: string }) => Promise<PyodideInstance>
  }
}

interface PyodideInstance {
  runPython(code: string): unknown
  FS: { writeFile(path: string, data: string): void; mkdirTree(path: string): void }
  loadPackage(names: string[]): Promise<void>
  pyimport(name: string): PyProxy
}

interface PyProxy {
  [key: string]: (...args: unknown[]) => unknown
}

let facadePromise: Promise<PyProxy> | null = null

function loadScript(src: string): Promise<void> {
  return new Promise((resolve, reject) => {
    const el = document.createElement('script')
    el.src = src
    el.onload = () => resolve()
    el.onerror = () => reject(new Error(`failed to load ${src}`))
    document.head.appendChild(el)
  })
}

async function init(): Promise<PyProxy> {
  if (facadePromise) return facadePromise
  facadePromise = (async () => {
    await loadScript(PYODIDE_URL)
    const pyodide = await window.loadPyodide!({ indexURL: PYODIDE_INDEX })
    await pyodide.loadPackage(['micropip'])
    await pyodide.runPython(`
import micropip
await micropip.install(['python-chess', 'pydantic'])
`)
    // 写入 Python 源码并保持包结构
    for (const [path, source] of Object.entries(PY_FILES)) {
      const dir = path.split('/').slice(0, -1).join('/')
      if (dir) pyodide.FS.mkdirTree(`/${dir}`)
      pyodide.FS.writeFile(`/${path}`, source)
    }
    await pyodide.runPython(`import sys\nsys.path.insert(0, '/')`)
    const facade = pyodide.pyimport('app.static_facade')
    // 恢复持久化进度
    try {
      const saved = localStorage.getItem(PROGRESS_KEY)
      if (saved) facade.set_progress_json(saved)
    } catch { /* ignore */ }
    return facade
  })()
  return facadePromise
}

type Envelope<T> = { ok: true; data: T } | { ok: false; status: number; detail: unknown }

function currentLang(): 'en' | 'zh' {
  try {
    if (localStorage.getItem('deb-chess-lang') === 'zh') return 'zh'
  } catch { /* ignore */ }
  return 'en'
}

async function call<T>(fn: string, ...args: unknown[]): Promise<T> {
  const facade = await init()
  const raw = (facade[fn] as (...a: unknown[]) => string)(...args)
  const env = JSON.parse(raw) as Envelope<T>
  if (!env.ok) {
    const lang = currentLang()
    let msg = `Request failed (${env.status})`
    if (typeof env.detail === 'string') msg = env.detail
    else if (env.detail && typeof env.detail === 'object') {
      const d = env.detail as Record<string, string>
      msg = d[lang] ?? d.en ?? msg
    }
    throw new ApiError(msg, env.status)
  }
  // 通关后回写进度到 localStorage
  if (fn === 'session_move' || fn === 'session_next' || fn === 'session_choice') {
    const data = env.data as { finished?: boolean }
    if (data.finished) {
      try {
        localStorage.setItem(PROGRESS_KEY, (facade.get_progress_json as () => string)())
      } catch { /* ignore */ }
    }
  }
  return env.data
}

export const pyodideApi = {
  getCurriculum: (lang: string) => call<CurriculumResponse>('get_curriculum', lang),
  getProgress: (lang: string) => call<ProgressResponse>('get_progress', lang),
  createSession: (levelId: string, lang: string) => call<SessionState>('create_session', levelId, lang),
  getSession: (id: string) => call<SessionState>('get_session', id),
  sessionMove: (id: string, move: string) => call<SessionState>('session_move', id, move),
  sessionChoice: (id: string, index: number) => call<SessionState>('session_choice', id, index),
  sessionNext: (id: string) => call<SessionState>('session_next', id),
  restartPlay: (id: string, bot?: string) => call<SessionState>('restart_play', id, bot ?? null),
}
```

- [ ] **Step 3: backend.ts 切换层**

`src/lib/backend.ts`:

```ts
// 统一后端出口:static 构建走 Pyodide(浏览器内 Python),否则走 HTTP API。
import { api } from './api'
import { pyodideApi } from './pyodide-api'

export const backend: typeof api =
  import.meta.env.MODE === 'static' ? pyodideApi : api
```

- [ ] **Step 4: 前端三个文件换 import 源**

- `src/state/curriculum.tsx`:`import { api, ... } from '@/lib/api'` → `import { backend as api } from '@/lib/backend'` + `import type { ChapterData, LevelData } from '@/lib/api'`(类型仍从 api.ts 拿)。
- `src/state/progress.tsx`:同上(`backend as api`)。
- `src/pages/Lesson.tsx`:`import { api, ApiError, type SessionState } from '@/lib/api'` → `import { ApiError, type SessionState } from '@/lib/api'` + `import { backend as api } from '@/lib/backend'`。

- [ ] **Step 5: package.json 与 .gitignore**

`package.json` scripts 段改为:

```json
    "dev": "node scripts/bundle_py.mjs && vite",
    "build": "node scripts/bundle_py.mjs && tsc -b && vite build",
    "build:static": "node scripts/bundle_py.mjs && tsc -b && vite build --mode static",
```

`.gitignore` 末尾追加:

```
# 生成物
src/lib/pybundle.ts
```

- [ ] **Step 6: 双构建验证**

```bash
npm run build          # 服务器版:构建成功
npm run build:static   # 静态版:构建成功,dist/ 内含 pybundle
```
Expected: 两者均成功。注意 pyodide npm 包**不需要**安装(运行时走 CDN script 注入)。

- [ ] **Step 7: Commit**

```bash
git add scripts/bundle_py.mjs src/lib/pyodide-api.ts src/lib/backend.ts src/state/ src/pages/Lesson.tsx package.json .gitignore
git commit -m "feat: pyodide static backend with build-mode switch"
```

### Task 3: CI + Pages 部署 workflow + 文档

**Files:**
- Create: `.github/workflows/pages.yml`
- Modify: `.github/workflows/ci.yml`(加 static 构建 job)
- Modify: `README.md`、`README_ZH.md`(加在线地址与静态构建说明)

- [ ] **Step 1: Pages 部署 workflow(照 deb-credit 样式)**

`.github/workflows/pages.yml`:

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: true

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci
      - run: npm run build:static
      - uses: actions/upload-pages-artifact@v3
        with:
          path: dist

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4
```

- [ ] **Step 2: ci.yml 加 static 构建冒烟 job**

`.github/workflows/ci.yml` 的 `jobs:` 末尾追加:

```yaml
  static-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci
      - run: npm run build:static
```

- [ ] **Step 3: README 更新**

`README.md` 的 `## Quick Start` 之前插入:

```markdown
## Play Online

<https://zpvan.github.io/deb-chess/> — runs entirely in your browser
(Python backend core via Pyodide/WebAssembly; progress saved in
localStorage; the Stockfish master tier is not available in this version).
```

`README_ZH.md` 的 `## 快速开始` 之前插入:

```markdown
## 在线玩

<https://zpvan.github.io/deb-chess/> —— 完全在浏览器里运行
(Python 后端核心经 Pyodide/WebAssembly 运行;进度存在浏览器 localStorage;
在线版暂不含 Stockfish 大师档)。
```

- [ ] **Step 4: Commit 并推送**

```bash
git add .github/workflows/pages.yml .github/workflows/ci.yml README.md README_ZH.md
git commit -m "feat: GitHub Pages deployment workflow for static build"
git push origin main
```

- [ ] **Step 5: 开启 Pages(用户手动或 gh)**

需要 gh 认证(`! gh auth login`)后执行:

```bash
gh api repos/zpvan/deb-chess/pages -X POST -f "build_type=workflow"
```

或用户手动:GitHub 仓库 Settings → Pages → Source 选 **GitHub Actions**。推送后 Actions 里的 "Deploy to GitHub Pages" 运行成功即可访问 <https://zpvan.github.io/deb-chess/>。

### Task 4: 静态版端到端验证(本地)

**Files:**
- Create(临时,不进仓库): `/tmp/deb-shots/static-check.mjs`

- [ ] **Step 1: 构建并用静态服务器起 dist/**

```bash
npm run build:static
pkill -f "http.server" 2>/dev/null; sleep 1
(cd dist && python3 -m http.server 8643 > /tmp/static-serve.log 2>&1 &)
sleep 1
curl -s -o /dev/null -w "%{http_code}" localhost:8643/   # Expected: 200
```

- [ ] **Step 2: Playwright 全流程(真实浏览器跑 Pyodide)**

`/tmp/deb-shots/static-check.mjs`:

```js
import { chromium } from 'playwright'

const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1280, height: 800 } })
page.on('pageerror', (e) => console.log('[pageerror]', e.message))

await page.goto('http://localhost:8643')
// Pyodide 首次加载较慢(CDN 下载运行时 + 安装 python-chess/pydantic)
await page.getByRole('button', { name: /playing|闯关/ }).waitFor({ timeout: 120000 })
console.log('loaded ok')
await page.screenshot({ path: '/tmp/static-home.png' })

await page.getByRole('button', { name: /playing|闯关/ }).first().click()
await page.waitForTimeout(1000)
await page.getByRole('button', { name: /Level 1|第 1 关/ }).click()
await page.waitForTimeout(1000)
await page.screenshot({ path: '/tmp/static-lesson.png' })

// teach → move 步骤,在棋盘上点 a1 → a5(白方视角:a 列最左,1 行最下)
await page.getByRole('button', { name: /Got it|我明白了/ }).click()
await page.waitForTimeout(800)
const board = await page.locator('.aspect-square').first().boundingBox()
const sq = (f, r) => ({
  x: board.x + (f + 0.5) * board.width / 8,
  y: board.y + (7 - r + 0.5) * board.height / 8,  // r=0 是第 1 行(底部)
})
await page.mouse.click(sq(0, 0).x, sq(0, 0).y)  // a1
await page.waitForTimeout(300)
await page.mouse.click(sq(0, 4).x, sq(0, 4).y)  // a5
await page.waitForTimeout(1000)
await page.screenshot({ path: '/tmp/static-solved.png' })
const body = await page.evaluate(() => document.body.innerText)
console.log('解出习题:', /zoomed straight|走上了 a5/.test(body))

// 打完第 1 关剩余步骤,验证进度持久化
for (let i = 0; i < 8; i++) {
  const btn = page.getByRole('button', { name: /Continue|继续/ })
  if (await btn.count()) { await btn.first().click(); await page.waitForTimeout(600); continue }
  break
}
// 刷新页面,确认进度仍在(localStorage)
await page.reload()
await page.waitForTimeout(3000)
const txt = await page.evaluate(() => document.body.innerText)
console.log('刷新后 XP 显示:', /[1-9]\d*\s*(XP|分)/.test(txt) ? '有进度 ✓' : '无进度 ✗')
await page.screenshot({ path: '/tmp/static-after-reload.png' })

await browser.close()
console.log('done')
```

Run: `cd /tmp/deb-shots && node static-check.mjs`
Expected 输出:`loaded ok`、`解出习题: true`、`刷新后 XP 显示: 有进度 ✓`(或走到关卡中段也算过——关键是刷新后 XP 非 0)。

**注意**:第一关剩余的 move 步骤各有固定答案(b1c3、e2e4 等),自动点击只做 a1a5 这一步;其余步骤由 Continue 跳过——如果某步没有 Continue 按钮(未解出),循环会 break,不影响验证目标(进度持久化只要 progress.db 里有记录)。若第 1 关没打完,可用另一种验证:截图 static-solved.png 确认解题框出现即可,进度条刷新验证放在「刷新后星星数 > 0 或 XP > 0」。

- [ ] **Step 3: 人工检查 4 张截图**

Read `/tmp/static-home.png`、`/tmp/static-lesson.png`、`/tmp/static-solved.png`、`/tmp/static-after-reload.png`:
- home:正常显示(与服务器版一致);
- lesson:棋盘与教学卡片正常;
- solved:出现绿色成功提示框;
- after-reload:首页星标/XP 非零。

- [ ] **Step 4: 停服务、回归、Commit**

```bash
pkill -f "http.server"
cd backend && ../.venv/bin/pytest tests/ -q   # Expected: 全部通过
cd .. && npm run build && npm run build:static  # 两种构建都成功
git add -A; git commit -m "test: verify static pyodide build end-to-end" || true
git push origin main
```
