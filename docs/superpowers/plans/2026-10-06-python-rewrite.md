# deb-chess Python 改写实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 deb-chess(React 纯前端国际象棋教学应用)改写为 FastAPI + python-chess 后端权威架构,前端收缩为纯展示层。

**Architecture:** FastAPI 后端用 python-chess 维护局面/校验走法/判定将杀,课程数据存 JSON,进度存 SQLite,bot 为手写三档 + Stockfish 大师档(UCI);React 前端保留 UI,删除 chess.js,全部改调 `/api`。

**Tech Stack:** Python ≥3.10, FastAPI, python-chess, pydantic v2, pytest, SQLite(stdlib sqlite3), React 19 + Vite(既有前端)。

**Spec:** `docs/superpowers/specs/2026-10-06-python-rewrite-design.md`

## 对 spec 的细化(实现层面简化,方向不变)

1. **无独立 `/hint` 端点**:hint 不是答案,随公开步骤数据下发,前端本地控制显示。
2. **无 `POST /api/progress/complete`**:后端在会话通关时自动写入进度(单一数据源)。
3. **新增端点**:`POST /api/sessions/{id}/next`(推进 teach/已解步骤)、`/choice`(选择题作答)、`/restart-play`(对弈重开/换档)、`GET /api/sessions/{id}`(刷新恢复)。
4. **session 过期(404)处理**:前端重建会话从第 0 步重来(TTL 2 小时,避免复杂的步骤回放)。
5. **路由集中在 `app/main.py`**;课程模型集中在 `app/models.py`。

## 文件结构

```
deb-chess/
├── backend/
│   ├── pyproject.toml              # 依赖与打包
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI 入口:全部路由 + 静态托管 + create_app 工厂
│   │   ├── models.py               # Pydantic 课程模型 + public_step() 答案剥离
│   │   ├── db.py                   # ProgressDB:SQLite 进度 + XP 规则 + 段位
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── session.py          # LessonSession 状态机(6 种步骤类型)
│   │   │   └── store.py            # SessionStore:内存会话 + TTL
│   │   └── engine/
│   │       ├── __init__.py
│   │       ├── bot.py              # random/greedy/smart 三档(平移自 src/lib/bot.ts)
│   │       └── stockfish_bot.py    # master 档,UCI 协议,优雅降级
│   ├── data/curriculum.json        # Task 2 由 curriculum.ts 转换生成
│   ├── scripts/
│   │   ├── convert_curriculum.sh   # 一次性转换脚本(esbuild + node)
│   │   └── validate_curriculum.py  # python-chess 逐题校验(脚本兼 pytest 用例)
│   └── tests/
│       ├── conftest.py             # make_curriculum 工厂 fixture
│       ├── test_models.py
│       ├── test_validate_curriculum.py
│       ├── test_bot.py
│       ├── test_db.py
│       ├── test_session.py         # teach/mate/move/line/choice
│       ├── test_play.py            # play 步骤 + bot + restart
│       └── test_api.py             # TestClient 集成
├── src/                            # 前端(改造)
│   ├── lib/api.ts                  # 新增:API client
│   ├── lib/fen.ts                  # 新增:FEN 解析(替代 chess.js 的渲染用途)
│   ├── state/curriculum.tsx        # 新增:课程数据 context(来自 API)
│   ├── state/progress.tsx          # 重写:进度 context(来自 API)
│   ├── components/ChessBoard.tsx   # 重写:去 chess.js
│   ├── pages/Lesson.tsx            # 重写:session 驱动
│   ├── pages/Home.tsx              # 改:数据来自 context
│   ├── pages/Map.tsx               # 改:数据来自 context
│   └── App.tsx                     # 改:Provider 嵌套 + Lesson 传 levelId
├── start.sh                        # 新增:本地一键启动
├── Dockerfile                      # 新增:多阶段构建
├── docker-compose.yml              # 新增
├── .dockerignore                   # 新增
└── vite.config.ts                  # 改:dev proxy /api → :8000
```

## 关键接口契约(跨任务一致性)

**SessionState(JSON,所有 session 端点的返回):**

```json
{
  "session_id": "hex", "level_id": "w1", "level_title": "...", "level_skill": "...",
  "chapter_title": "...", "chapter_badge": "...", "chapter_color": "#...", "chapter_soft": "#...",
  "step_index": 0, "step_count": 8,
  "step": { "type": "move", "fen": "...", "prompt": "...", "hint": "..." },
  "fen": "...(展示用,有 reply 时为用户走完的中间局面)",
  "legal_moves": ["e2e4"], "check_square": null,
  "last_move": ["e2", "e4"], "solved": false, "fast_mate": false,
  "line_prompt": null, "play_status": null, "my_moves": 0, "bot_style": null,
  "mistakes": 0, "finished": false, "stars": 0,
  "success_text": null, "end_text": null, "last_result": null,
  "reply": { "move": ["e7", "e5"], "fen": "..." }
}
```

- `last_result`: `'correct' | 'wrong' | null`(本次提交结果)
- `end_text`: play 步骤 lost/draw 时的 failText/drawText
- `reply`: line 剧本对手应对或 play 的 bot 回应;前端延迟 700ms 展示 `reply.fen`
- 公开 step 剥离字段:`accepted, script, answer, explain, successText, failText, drawText`

**Python 命名:** `pick_bot_move(board, style, rng)`、`black_queen_gone(board)`、`ProgressDB.get()/complete_level(level_id, stars)`、`LessonSession(curriculum, level_id, stockfish=None, rng=None)` 及其方法 `.state()/.advance()/.submit_move(uci)/.submit_choice(index)/.restart_play(bot_style=None)`、`SessionStore.put(session)/get(session_id)`、`StockfishBot.available()/pick(board)`、`load_curriculum(path)`、`public_step(step)`、`create_app(...)`。

---

### Task 1: 后端骨架

**Files:**
- Create: `backend/pyproject.toml`
- Create: `backend/app/__init__.py`
- Create: `backend/app/main.py`
- Create: `backend/tests/test_api.py`

- [ ] **Step 1: 确认 Python 版本 ≥ 3.10**

Run: `python3 --version`
Expected: `Python 3.10.x` 或更高。若低于 3.10:`brew install python@3.12` 并用 `python3.12` 替代后续命令中的 `python3`。

- [ ] **Step 2: 写 pyproject.toml 与包骨架**

`backend/pyproject.toml`:

```toml
[project]
name = "deb-chess-backend"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
  "fastapi>=0.115",
  "uvicorn>=0.30",
  "python-chess>=1.11",
]

[project.optional-dependencies]
dev = ["pytest>=8", "httpx>=0.27"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["app"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
```

`backend/app/__init__.py`:空文件。

- [ ] **Step 3: 写失败的测试**

`backend/tests/test_api.py`:

```python
from fastapi.testclient import TestClient

from app.main import create_app


def test_health():
    client = TestClient(create_app())
    r = client.get('/api/health')
    assert r.status_code == 200
    assert r.json() == {'ok': True}
```

- [ ] **Step 4: 建 venv、装依赖、跑测试确认失败**

```bash
python3 -m venv .venv
.venv/bin/pip install -e 'backend[dev]'
cd backend && ../.venv/bin/pytest tests/test_api.py -v
```
Expected: FAIL,`ImportError: cannot import name 'create_app' from 'app.main'`(main.py 尚不存在)。

- [ ] **Step 5: 最小实现**

`backend/app/main.py`:

```python
from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI(title='deb-chess')

    @app.get('/api/health')
    def health():
        return {'ok': True}

    return app


app = create_app()
```

- [ ] **Step 6: 跑测试确认通过**

Run: `cd backend && ../.venv/bin/pytest tests/test_api.py -v`
Expected: 1 passed

- [ ] **Step 7: .gitignore 追加 Python 条目**

先 `cat .gitignore` 确认已包含 `node_modules` 与 `dist`(vite 模板自带;若缺失一并补上),然后追加:

```
# Python
.venv/
__pycache__/
*.pyc
.pytest_cache/

# 后端运行时数据
backend/data/progress.db
```

- [ ] **Step 8: Commit**

```bash
git add backend/ .gitignore
git commit -m "feat: FastAPI backend skeleton with health endpoint"
```

### Task 2: 课程数据转换(curriculum.ts → curriculum.json)

**Files:**
- Create: `backend/scripts/convert_curriculum.sh`
- Create: `backend/data/curriculum.json`(生成物)

- [ ] **Step 1: 写转换脚本**

`backend/scripts/convert_curriculum.sh`:

```bash
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
```

`chmod +x backend/scripts/convert_curriculum.sh`

- [ ] **Step 2: 运行转换**

Run: `npm install`(若 node_modules 不存在)然后 `bash backend/scripts/convert_curriculum.sh`
Expected: 输出 `chapters: 5 levels: 20 steps: 82`。确认 `backend/data/curriculum.json` 已生成且开头为 `[ { "id": "warmup", ...`。

- [ ] **Step 3: 抽查数据完整性**

Run: `python3 -c "import json; d=json.load(open('backend/data/curriculum.json')); print(d[0]['levels'][0]['steps'][1])"`
Expected: 打印出第一关第二个步骤(move 类型,含 `accepted: ['a1a5']`),与 `src/data/curriculum.ts` 中一致。

- [ ] **Step 4: Commit**

```bash
git add backend/scripts/convert_curriculum.sh backend/data/curriculum.json
git commit -m "feat: convert curriculum data to JSON"
```

### Task 3: 课程模型与加载器

**Files:**
- Create: `backend/app/models.py`
- Test: `backend/tests/test_models.py`

- [ ] **Step 1: 写失败的测试**

`backend/tests/test_models.py`:

```python
from pathlib import Path

from app.models import load_curriculum, public_step

DATA = Path(__file__).resolve().parents[1] / 'data' / 'curriculum.json'


def test_load_real_curriculum():
    cur = load_curriculum(DATA)
    flats = cur.flat_levels()
    assert len(flats) > 0
    ids = [lv.id for _, lv, _ in flats]
    assert len(ids) == len(set(ids)), '关卡 id 必须唯一'
    assert cur.find_level('w1') is not None
    assert cur.find_level('no-such') is None
    assert cur.total_puzzles > 0


def test_public_step_strips_answers():
    cur = load_curriculum(DATA)
    _, level, _ = cur.find_level('w1')
    move_step = next(s for s in level.steps if s.type == 'move')
    pub = public_step(move_step)
    assert 'accepted' not in pub
    assert 'successText' not in pub
    assert pub['type'] == 'move'
    assert pub['fen'] == move_step.fen
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd backend && ../.venv/bin/pytest tests/test_models.py -v`
Expected: FAIL,`ModuleNotFoundError: No module named 'app.models'`

- [ ] **Step 3: 实现 models.py**

`backend/app/models.py`:

```python
import json
from pathlib import Path
from typing import Annotated, Literal, Optional, Union

from pydantic import BaseModel, Field


class TeachStep(BaseModel):
    type: Literal['teach']
    title: str
    text: list[str]
    fen: Optional[str] = None
    highlight: Optional[list[str]] = None
    arrows: Optional[list[tuple[str, str]]] = None


class MateStep(BaseModel):
    type: Literal['mate']
    fen: str
    prompt: str
    hint: Optional[str] = None
    successText: str
    orientation: Optional[Literal['white', 'black']] = None


class MoveStep(BaseModel):
    type: Literal['move']
    fen: str
    prompt: str
    accepted: list[str]
    hint: Optional[str] = None
    successText: str
    orientation: Optional[Literal['white', 'black']] = None


class LineStep(BaseModel):
    type: Literal['line']
    fen: str
    script: list[str]
    endsWithMate: bool = True
    prompts: list[str]
    hint: Optional[str] = None
    successText: str


class ChoiceStep(BaseModel):
    type: Literal['choice']
    fen: str
    sideLabel: str
    question: str
    options: list[str]
    answer: int
    explain: str
    orientation: Optional[Literal['white', 'black']] = None


class PlayStep(BaseModel):
    type: Literal['play']
    fen: str
    bot: Literal['random', 'greedy', 'smart']
    win: Literal['mate', 'mateOrQueen']
    prompt: str
    hint: Optional[str] = None
    successText: str
    failText: str
    drawText: str


Step = Annotated[
    Union[TeachStep, MateStep, MoveStep, LineStep, ChoiceStep, PlayStep],
    Field(discriminator='type'),
]


class Level(BaseModel):
    id: str
    title: str
    goal: str
    skill: str
    steps: list[Step]


class Chapter(BaseModel):
    id: str
    badge: str
    title: str
    intro: str
    color: str
    soft: str
    levels: list[Level]


class Curriculum(BaseModel):
    chapters: list[Chapter]

    def flat_levels(self) -> list[tuple[Chapter, Level, int]]:
        out: list[tuple[Chapter, Level, int]] = []
        for ch in self.chapters:
            for lv in ch.levels:
                out.append((ch, lv, len(out)))
        return out

    def find_level(self, level_id: str) -> Optional[tuple[Chapter, Level, int]]:
        for ch, lv, idx in self.flat_levels():
            if lv.id == level_id:
                return ch, lv, idx
        return None

    @property
    def total_puzzles(self) -> int:
        return sum(1 for _, lv, _ in self.flat_levels() for s in lv.steps if s.type != 'teach')


# 答案字段:绝不下发给前端
ANSWER_FIELDS = {'accepted', 'script', 'answer', 'explain', 'successText', 'failText', 'drawText'}


def public_step(step: Step) -> dict:
    return {
        k: v
        for k, v in step.model_dump(mode='json').items()
        if k not in ANSWER_FIELDS and v is not None
    }


def load_curriculum(path: Union[str, Path]) -> Curriculum:
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    return Curriculum.model_validate({'chapters': data})
```

- [ ] **Step 4: 跑测试确认通过**

Run: `cd backend && ../.venv/bin/pytest tests/test_models.py -v`
Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add backend/app/models.py backend/tests/test_models.py
git commit -m "feat: curriculum pydantic models and loader"
```

### Task 4: 课程校验器

**Files:**
- Create: `backend/scripts/validate_curriculum.py`
- Test: `backend/tests/test_validate_curriculum.py`

- [ ] **Step 1: 写失败的测试**

`backend/tests/test_validate_curriculum.py`:

```python
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from validate_curriculum import validate_all

DATA = Path(__file__).resolve().parents[1] / 'data' / 'curriculum.json'


def test_real_curriculum_is_valid():
    chapters = json.loads(DATA.read_text(encoding='utf-8'))
    errors = validate_all(chapters)
    assert errors == [], '\n'.join(errors)


def test_validator_catches_bad_fen():
    bad = [{'id': 'c', 'levels': [{'id': 'L', 'steps': [
        {'type': 'mate', 'fen': 'not-a-fen', 'prompt': 'x', 'successText': 'y'}]}]}]
    errors = validate_all(bad)
    assert any('FEN' in e for e in errors)


def test_validator_catches_illegal_accepted_move():
    bad = [{'id': 'c', 'levels': [{'id': 'L', 'steps': [
        {'type': 'move', 'fen': '4k3/8/8/8/8/8/8/R3K3 w - - 0 1',
         'prompt': 'x', 'accepted': ['a1a9'], 'successText': 'y'}]}]}]
    errors = validate_all(bad)
    assert any('a1a9' in e for e in errors)
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd backend && ../.venv/bin/pytest tests/test_validate_curriculum.py -v`
Expected: FAIL,`ModuleNotFoundError: No module named 'validate_curriculum'`

- [ ] **Step 3: 实现校验器**

`backend/scripts/validate_curriculum.py`:

```python
"""用 python-chess 校验 curriculum.json 中的所有棋题。

用法:
  python scripts/validate_curriculum.py   # 校验 backend/data/curriculum.json
也被 tests/test_validate_curriculum.py 作为用例调用。
"""
import json
import sys
from pathlib import Path

import chess

DATA = Path(__file__).resolve().parents[1] / 'data' / 'curriculum.json'


def _legal(board: chess.Board) -> set[str]:
    s = {m.uci() for m in board.legal_moves}
    return s | {u[:4] for u in s}


def _push(board: chess.Board, uci: str) -> chess.Move:
    move = chess.Move.from_uci(uci)
    if move not in board.legal_moves and len(uci) == 5:
        move = chess.Move.from_uci(uci[:4])
    board.push(move)
    return move


def validate_all(chapters: list[dict]) -> list[str]:
    errors: list[str] = []
    for ch in chapters:
        for lv in ch['levels']:
            for i, st in enumerate(lv['steps']):
                where = f"{lv['id']}[{i}]({st['type']})"
                fen = st.get('fen')
                if fen is None:
                    continue
                try:
                    board = chess.Board(fen)
                except ValueError:
                    errors.append(f'{where}: FEN 无法解析')
                    continue
                if not board.is_valid():
                    errors.append(f'{where}: FEN 局面不合法')

                t = st['type']
                if t == 'move':
                    legal = _legal(board)
                    for a in st['accepted']:
                        if a not in legal:
                            errors.append(f'{where}: accepted 走法不合法: {a}')
                elif t == 'mate':
                    if not any(board.gives_check(m) and _mates(board, m) for m in board.legal_moves):
                        errors.append(f'{where}: 不存在一步杀')
                elif t == 'line':
                    ok = True
                    for j, u in enumerate(st['script']):
                        try:
                            if u not in _legal(board):
                                raise ValueError(u)
                            _push(board, u)
                        except ValueError:
                            errors.append(f'{where}: script[{j}] 走法不合法: {u}')
                            ok = False
                            break
                    if ok and st.get('endsWithMate', True) and not board.is_checkmate():
                        errors.append(f'{where}: script 走完未将杀(endsWithMate 默认为 true)')
                elif t == 'play':
                    if st['bot'] not in ('random', 'greedy', 'smart'):
                        errors.append(f'{where}: 未知 bot: {st["bot"]}')
                    if st['win'] not in ('mate', 'mateOrQueen'):
                        errors.append(f'{where}: 未知 win: {st["win"]}')
    return errors


def _mates(board: chess.Board, move: chess.Move) -> bool:
    board.push(move)
    mated = board.is_checkmate()
    board.pop()
    return mated


def main() -> int:
    chapters = json.loads(DATA.read_text(encoding='utf-8'))
    errors = validate_all(chapters)
    if errors:
        print(f'发现 {len(errors)} 个问题:')
        for e in errors:
            print(' -', e)
        return 1
    print('全部棋题校验通过 ✓')
    return 0


if __name__ == '__main__':
    sys.exit(main())
```

- [ ] **Step 4: 跑测试确认通过**

Run: `cd backend && ../.venv/bin/pytest tests/test_validate_curriculum.py -v`
Expected: 3 passed。**若 `test_real_curriculum_is_valid` 失败**,说明转换数据或原数据有真问题——逐个检查报错,优先怀疑 `arrows` 等无关字段;只有确认原数据棋题本身有误才可修数据,并在 commit message 中说明。

- [ ] **Step 5: Commit**

```bash
git add backend/scripts/validate_curriculum.py backend/tests/test_validate_curriculum.py
git commit -m "feat: curriculum validator powered by python-chess"
```

### Task 5: Bot 三档(random/greedy/smart)

**Files:**
- Create: `backend/app/engine/__init__.py`
- Create: `backend/app/engine/bot.py`
- Test: `backend/tests/test_bot.py`

- [ ] **Step 1: 写失败的测试**

`backend/tests/test_bot.py`:

```python
import random

import chess

from app.engine.bot import black_queen_gone, pick_bot_move, score_moves

# 白车 a1、白王 e1;黑后 a8、黑王 e8。白方可 Rxa8+ 白吃皇后。
GREEDY_FEN = 'q3k3/8/8/8/8/8/8/R3K3 w - - 0 1'
# 底线杀:Ra1a8 一步将杀。
MATE_FEN = '6k1/5ppp/8/8/8/8/8/R5K1 w - - 0 1'
# 白后 d1 走到 d5 会被 e6 黑兵白吃(无保护);d2 是安全着法。
SMART_FEN = '4k3/8/4p3/8/8/8/8/3QK3 w - - 0 1'


def test_random_returns_legal_move():
    board = chess.Board()
    rng = random.Random(42)
    assert pick_bot_move(board, 'random', rng) in list(board.legal_moves)


def test_no_moves_returns_none():
    board = chess.Board('7k/5Q2/6K1/8/8/8/8/8 b - - 0 1')  # 黑方逼和
    assert pick_bot_move(board, 'greedy', random.Random(1)) is None


def test_greedy_scores_queen_capture_highest():
    board = chess.Board(GREEDY_FEN)
    scored = score_moves(board, 'greedy', random.Random(42))
    assert scored[0][1].uci() == 'a1a8'  # 吃后 180 分,远超噪声 ±2


def test_greedy_prefers_mate():
    board = chess.Board(MATE_FEN)
    scored = score_moves(board, 'greedy', random.Random(42))
    assert scored[0][1].uci() == 'a1a8'  # +10000 将杀分


def test_smart_avoids_hanging_queen():
    board = chess.Board(SMART_FEN)
    scored = dict((m.uci(), s) for s, m in score_moves(board, 'smart', random.Random(42)))
    assert scored['d1d5'] < scored['d1d2']  # 送后 -135,噪声 ±2 无法翻盘


def test_pick_is_deterministic_with_seed():
    board = chess.Board(GREEDY_FEN)
    a = pick_bot_move(board, 'greedy', random.Random(7))
    b = pick_bot_move(board, 'greedy', random.Random(7))
    assert a == b


def test_black_queen_gone():
    assert not black_queen_gone(chess.Board(GREEDY_FEN))
    assert black_queen_gone(chess.Board(MATE_FEN))
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd backend && ../.venv/bin/pytest tests/test_bot.py -v`
Expected: FAIL,`ModuleNotFoundError: No module named 'app.engine'`

- [ ] **Step 3: 实现 bot.py(平移自 src/lib/bot.ts)**

`backend/app/engine/__init__.py`:空文件。

`backend/app/engine/bot.py`:

```python
"""电脑对手:random 随便走 / greedy 贪吃+爱将军 / smart 还会避免送子。
逻辑平移自原前端 src/lib/bot.ts,行为保持一致。"""
import random

import chess

VAL = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0}


def score_moves(board: chess.Board, style: str, rng: random.Random) -> list[tuple[float, chess.Move]]:
    """给所有合法走法打分,按分数降序返回 (score, move) 列表。"""
    scored: list[tuple[float, chess.Move]] = []
    for m in board.legal_moves:
        s = rng.random() * 2
        captured = board.piece_type_at(m.to_square) if board.is_capture(m) else None
        board.push(m)
        if board.is_checkmate():
            s += 10000
        if captured is not None:
            s += VAL[captured] * 20
        if board.is_check():
            s += 8
        if style == 'smart':
            # 走完若会被对方白白吃掉,扣分(对方攻击者多于我方保护者且棋子比兵贵)
            enemy = board.turn
            piece = board.piece_type_at(m.to_square)  # push 之后,棋子在落点格
            attackers = len(board.attackers(enemy, m.to_square))
            defenders = len(board.attackers(not enemy, m.to_square))
            if attackers > defenders and VAL[piece] > 1:
                s -= VAL[piece] * 15
        board.pop()
        scored.append((s, m))
    scored.sort(key=lambda t: t[0], reverse=True)
    return scored


def pick_bot_move(board: chess.Board, style: str, rng: random.Random) -> chess.Move | None:
    moves = list(board.legal_moves)
    if not moves:
        return None
    if style == 'random':
        return rng.choice(moves)
    scored = score_moves(board, style, rng)
    # 在前 30% 里随机,保留一点变化
    top_n = max(1, int(len(scored) * 0.3))
    return rng.choice(scored[:top_n])[1]


def black_queen_gone(board: chess.Board) -> bool:
    """判断黑方是否还有皇后(用于"吃掉皇后也算赢")。"""
    return not any(
        p.piece_type == chess.QUEEN and p.color == chess.BLACK
        for p in board.piece_map().values()
    )
```

- [ ] **Step 4: 跑测试确认通过**

Run: `cd backend && ../.venv/bin/pytest tests/test_bot.py -v`
Expected: 7 passed

- [ ] **Step 5: Commit**

```bash
git add backend/app/engine/ backend/tests/test_bot.py
git commit -m "feat: port three-tier chess bot to python-chess"
```

### Task 6: 进度存储(SQLite)

**Files:**
- Create: `backend/app/db.py`
- Test: `backend/tests/test_db.py`

- [ ] **Step 1: 写失败的测试**

`backend/tests/test_db.py`:

```python
from app.db import ProgressDB


def test_empty_progress(tmp_path):
    db = ProgressDB(tmp_path / 'p.db')
    p = db.get()
    assert p == {'levels': {}, 'xp': 0, 'total_stars': 0, 'rank_name': '小士兵', 'rank_icon': '♟'}
    db.close()


def test_complete_level_first_time(tmp_path):
    db = ProgressDB(tmp_path / 'p.db')
    p = db.complete_level('w1', 2)
    assert p['levels'] == {'w1': 2}
    assert p['xp'] == 60 + 2 * 20  # 首通 60 + stars*20
    assert p['rank_name'] == '小骑士'  # xp >= 100
    db.close()


def test_replay_keeps_best_and_grants_diff(tmp_path):
    db = ProgressDB(tmp_path / 'p.db')
    db.complete_level('w1', 3)   # xp: 60+60=120
    p = db.complete_level('w1', 1)  # 更差:不加分,星级不降
    assert p['levels']['w1'] == 3
    assert p['xp'] == 120
    p = db.complete_level('w1', 3)  # 持平:不加分
    assert p['xp'] == 120
    db.close()


def test_persistence_across_instances(tmp_path):
    path = tmp_path / 'p.db'
    ProgressDB(path).complete_level('w1', 1)
    db = ProgressDB(path)
    assert db.get()['levels'] == {'w1': 1}
    db.close()
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd backend && ../.venv/bin/pytest tests/test_db.py -v`
Expected: FAIL,`ModuleNotFoundError: No module named 'app.db'`

- [ ] **Step 3: 实现 db.py**

`backend/app/db.py`:

```python
"""进度存储:SQLite。规则平移自原前端 src/state/progress.tsx:
- 首通:xp += 60 + stars*20;刷新纪录:xp += (新 best - 旧 best)*20;持平或更差:不加。
- 星级只升不降。"""
import sqlite3
from pathlib import Path
from typing import Union

RANKS = [
    (0, '小士兵', '♟'),
    (100, '小骑士', '♞'),
    (250, '小主教', '♝'),
    (450, '小城堡', '♜'),
    (700, '小皇后', '♛'),
    (1000, '小棋王', '♚'),
]


class ProgressDB:
    def __init__(self, path: Union[str, Path]):
        path = str(path)
        if path != ':memory:':
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._conn.execute(
            'CREATE TABLE IF NOT EXISTS levels (level_id TEXT PRIMARY KEY, stars INTEGER NOT NULL)')
        self._conn.execute(
            'CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value INTEGER NOT NULL)')
        self._conn.commit()

    def get(self) -> dict:
        levels = {r[0]: r[1] for r in self._conn.execute('SELECT level_id, stars FROM levels')}
        row = self._conn.execute("SELECT value FROM meta WHERE key='xp'").fetchone()
        xp = row[0] if row else 0
        rank = next((r for r in reversed(RANKS) if xp >= r[0]), RANKS[0])
        return {
            'levels': levels,
            'xp': xp,
            'total_stars': sum(levels.values()),
            'rank_name': rank[1],
            'rank_icon': rank[2],
        }

    def complete_level(self, level_id: str, stars: int) -> dict:
        row = self._conn.execute('SELECT stars FROM levels WHERE level_id=?', (level_id,)).fetchone()
        prev = row[0] if row else 0
        best = max(prev, stars)
        gained = 60 + stars * 20 if prev == 0 else max(0, (best - prev) * 20)
        self._conn.execute(
            'INSERT INTO levels (level_id, stars) VALUES (?, ?) '
            'ON CONFLICT(level_id) DO UPDATE SET stars=excluded.stars',
            (level_id, best))
        self._conn.execute(
            "INSERT INTO meta (key, value) VALUES ('xp', ?) "
            'ON CONFLICT(key) DO UPDATE SET value = value + excluded.value',
            (gained,))
        self._conn.commit()
        return self.get()

    def close(self) -> None:
        self._conn.close()
```

- [ ] **Step 4: 跑测试确认通过**

Run: `cd backend && ../.venv/bin/pytest tests/test_db.py -v`
Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
git add backend/app/db.py backend/tests/test_db.py
git commit -m "feat: SQLite progress store with XP and ranks"
```

### Task 7: Stockfish 大师档

**Files:**
- Create: `backend/app/engine/stockfish_bot.py`
- Test: `backend/tests/test_stockfish.py`

- [ ] **Step 1: 写测试(本机无 stockfish 时自动跳过)**

`backend/tests/test_stockfish.py`:

```python
import shutil

import chess
import pytest

from app.engine.stockfish_bot import StockfishBot

pytestmark = pytest.mark.skipif(shutil.which('stockfish') is None, reason='stockfish 未安装')


def test_available_and_pick():
    bot = StockfishBot()
    assert bot.available()
    board = chess.Board('6k1/5ppp/8/8/8/8/8/R5K1 w - - 0 1')
    move = bot.pick(board)
    assert move is not None and move in list(board.legal_moves)
    bot.close()


def test_bad_path_unavailable():
    bot = StockfishBot(path='/nonexistent/stockfish')
    assert not bot.available()
    assert bot.pick(chess.Board()) is None
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd backend && ../.venv/bin/pytest tests/test_stockfish.py -v`
Expected: FAIL,`ModuleNotFoundError`(若 stockfish 未安装则 SKIP,先 `brew install stockfish` 或接受 skip——Docker 镜像内会自带)

- [ ] **Step 3: 实现 stockfish_bot.py**

`backend/app/engine/stockfish_bot.py`:

```python
"""Stockfish 大师档:UCI 协议调用本机 stockfish 二进制。
未安装时优雅降级:available() 返回 False,pick() 返回 None。"""
import os
import shutil
from typing import Optional

import chess
import chess.engine


class StockfishBot:
    def __init__(self, path: Optional[str] = None, skill: int = 10, time_limit: float = 0.2):
        self._path = path or os.environ.get('STOCKFISH_PATH', 'stockfish')
        self._skill = skill
        self._limit = chess.engine.Limit(time=time_limit)
        self._engine: Optional[chess.engine.SimpleEngine] = None

    def available(self) -> bool:
        if self._engine is not None:
            return True
        if shutil.which(self._path) is None and not os.path.exists(self._path):
            return False
        try:
            self._engine = chess.engine.SimpleEngine.popen_uci(self._path)
            self._engine.configure({'Skill Level': self._skill})
            return True
        except Exception:
            self._engine = None
            return False

    def pick(self, board: chess.Board) -> Optional[chess.Move]:
        if not self.available():
            return None
        try:
            return self._engine.play(board, self._limit).move
        except Exception:
            return None

    def close(self) -> None:
        if self._engine is not None:
            self._engine.quit()
            self._engine = None
```

- [ ] **Step 4: 跑测试确认通过(或合理 skip)**

Run: `cd backend && ../.venv/bin/pytest tests/test_stockfish.py -v`
Expected: 2 passed(有 stockfish)或 2 skipped(无)

- [ ] **Step 5: Commit**

```bash
git add backend/app/engine/stockfish_bot.py backend/tests/test_stockfish.py
git commit -m "feat: Stockfish master bot via UCI with graceful fallback"
```

### Task 8: 会话状态机(puzzle 步骤:teach/mate/move/line/choice)

**Files:**
- Create: `backend/app/core/__init__.py`
- Create: `backend/app/core/session.py`
- Create: `backend/tests/conftest.py`
- Test: `backend/tests/test_session.py`

- [ ] **Step 1: 写 conftest 与失败的测试**

`backend/tests/conftest.py`:

```python
import pytest

from app.models import Curriculum


def make_curriculum(steps: list[dict]) -> Curriculum:
    return Curriculum.model_validate({'chapters': [{
        'id': 'c1', 'badge': '测试', 'title': '测试章', 'intro': '', 'color': '#000000',
        'soft': '#ffffff',
        'levels': [{'id': 't1', 'title': '测试关', 'goal': 'g', 'skill': 's', 'steps': steps}],
    }]})


@pytest.fixture
def curriculum_factory():
    return make_curriculum
```

`backend/tests/test_session.py`:

```python
import random

import pytest

from app.core.session import IllegalMove, LessonSession

ROOK_FEN = '4k3/8/8/8/8/8/8/R3K3 w - - 0 1'      # 白车 a1,可 a1a5
MATE_FEN = '6k1/5ppp/8/8/8/8/8/R5K1 w - - 0 1'  # a1a8 一步杀
PAWN_FEN = '4k3/8/8/8/8/8/4P3/4K3 w - - 0 1'   # 白兵 e2


def mk(factory, steps):
    return LessonSession(factory(steps), 't1', rng=random.Random(42))


def test_teach_then_advance(curriculum_factory):
    s = mk(curriculum_factory, [
        {'type': 'teach', 'title': 't', 'text': ['x']},
        {'type': 'teach', 'title': 't2', 'text': ['y']},
    ])
    assert s.state()['step_index'] == 0
    st = s.advance()
    assert st['step_index'] == 1
    st = s.advance()  # 最后一步再推进 → 通关
    assert st['finished'] is True
    assert st['stars'] == 3  # 零失误


def test_advance_blocked_on_unsolved_puzzle(curriculum_factory):
    s = mk(curriculum_factory, [
        {'type': 'move', 'fen': ROOK_FEN, 'prompt': 'p', 'accepted': ['a1a5'], 'successText': 'ok'},
    ])
    with pytest.raises(IllegalMove):
        s.advance()


def test_mate_step_right_and_wrong(curriculum_factory):
    s = mk(curriculum_factory, [
        {'type': 'mate', 'fen': MATE_FEN, 'prompt': 'p', 'successText': '将杀!'},
    ])
    st = s.submit_move('a1a2')  # 合法但不是将杀
    assert st['last_result'] == 'wrong'
    assert st['mistakes'] == 1
    assert st['fen'] == MATE_FEN  # 局面回滚
    st = s.submit_move('a1a8')
    assert st['last_result'] == 'correct'
    assert st['solved'] is True
    assert st['success_text'] == '将杀!'
    assert st['last_move'] == ['a1', 'a8']


def test_move_step_accepted(curriculum_factory):
    s = mk(curriculum_factory, [
        {'type': 'move', 'fen': ROOK_FEN, 'prompt': 'p', 'accepted': ['a1a5'], 'successText': 'ok'},
    ])
    st = s.submit_move('a1a4')  # 合法但非答案
    assert st['last_result'] == 'wrong'
    st = s.submit_move('a1a5')
    assert st['solved'] is True


def test_illegal_move_raises(curriculum_factory):
    s = mk(curriculum_factory, [
        {'type': 'move', 'fen': ROOK_FEN, 'prompt': 'p', 'accepted': ['a1a5'], 'successText': 'ok'},
    ])
    with pytest.raises(IllegalMove):
        s.submit_move('a1b2')  # 车不能斜走
    with pytest.raises(IllegalMove):
        s.submit_move('xxxx')  # 格式错误


def test_extra_promotion_char_tolerated(curriculum_factory):
    # 旧版前端对非升变走法也附带 'q'(chess.js 会忽略),后端须容忍
    s = mk(curriculum_factory, [
        {'type': 'move', 'fen': ROOK_FEN, 'prompt': 'p', 'accepted': ['a1a5'], 'successText': 'ok'},
    ])
    st = s.submit_move('a1a5q')
    assert st['solved'] is True


def test_line_step_script_with_reply(curriculum_factory):
    s = mk(curriculum_factory, [
        {'type': 'line', 'fen': PAWN_FEN, 'script': ['e2e4', 'e8e7', 'e4e5'],
         'endsWithMate': False, 'prompts': ['冲兵!', '再冲!'], 'successText': 'ok'},
    ])
    st = s.submit_move('e2e3')  # 不按剧本
    assert st['last_result'] == 'wrong'
    assert st['line_prompt'] == '冲兵!'
    st = s.submit_move('e2e4')
    assert st['last_result'] == 'correct'
    assert st['solved'] is False
    assert st['reply'] is not None and st['reply']['move'] == ['e8', 'e7']  # 对手自动应对
    assert st['line_prompt'] == '再冲!'
    st = s.submit_move('e4e5')  # 最后一步
    assert st['solved'] is True


def test_line_step_fast_mate(curriculum_factory):
    # 剧本更长,但直接一步将死 → 算成功且 fast_mate
    s = mk(curriculum_factory, [
        {'type': 'line', 'fen': MATE_FEN, 'script': ['a1a7', 'g7g6', 'a7a8'],
         'prompts': ['p1', 'p2'], 'successText': 'ok'},
    ])
    st = s.submit_move('a1a8')
    assert st['solved'] is True
    assert st['fast_mate'] is True
    assert '更快将死' in st['success_text']


def test_choice_step(curriculum_factory):
    s = mk(curriculum_factory, [
        {'type': 'choice', 'fen': ROOK_FEN, 'sideLabel': '白方', 'question': 'q?',
         'options': ['甲', '乙'], 'answer': 1, 'explain': '因为乙对'},
    ])
    st = s.submit_choice(0)
    assert st['last_result'] == 'wrong'
    assert st['mistakes'] == 1
    st = s.submit_choice(1)
    assert st['solved'] is True
    assert st['success_text'] == '因为乙对'


def test_stars_by_mistakes(curriculum_factory):
    steps = [
        {'type': 'move', 'fen': ROOK_FEN, 'prompt': 'p', 'accepted': ['a1a5'], 'successText': 'ok'},
        {'type': 'teach', 'title': 't', 'text': ['x']},
    ]
    s = mk(curriculum_factory, steps)
    s.submit_move('a1a4')  # 错 1 次
    s.submit_move('a1a5')
    s.advance()
    st = s.advance()
    assert st['finished'] is True
    assert st['stars'] == 2  # 1-2 次失误 → 2 星


def test_state_has_no_answers(curriculum_factory):
    s = mk(curriculum_factory, [
        {'type': 'move', 'fen': ROOK_FEN, 'prompt': 'p', 'accepted': ['a1a5'], 'successText': 'ok'},
    ])
    assert 'accepted' not in s.state()['step']
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd backend && ../.venv/bin/pytest tests/test_session.py -v`
Expected: FAIL,`ModuleNotFoundError: No module named 'app.core'`

- [ ] **Step 3: 实现 session.py**

`backend/app/core/__init__.py`:空文件。

`backend/app/core/session.py`:

```python
"""课程会话状态机。每个关卡一个 LessonSession,持有 python-chess Board,
覆盖 6 种步骤类型。逻辑平移自原前端 src/pages/Lesson.tsx。"""
import random
import uuid
from typing import Optional

import chess

from app.engine.bot import black_queen_gone, pick_bot_move
from app.engine.stockfish_bot import StockfishBot
from app.models import Curriculum, public_step

BOT_STYLES = ('random', 'greedy', 'smart', 'master')
PUZZLE_TYPES = ('mate', 'move', 'line')


class IllegalMove(ValueError):
    pass


def is_draw(board: chess.Board) -> bool:
    """对齐 chess.js 的 isDraw():逼和/子力不足/三次重复/五十回合。"""
    return (board.is_stalemate() or board.is_insufficient_material()
            or board.can_claim_threefold_repetition() or board.can_claim_fifty_moves())


def parse_move(board: chess.Board, uci: str) -> chess.Move:
    uci = uci.strip().lower()
    try:
        move = chess.Move.from_uci(uci)
    except ValueError:
        raise IllegalMove(f'走法格式不对:{uci}(应为如 e2e4 的格式)')
    if move in board.legal_moves:
        return move
    # 前端对非升变走法也可能附带 'q'(旧版 chess.js 行为),容忍之
    if len(uci) == 5:
        alt = chess.Move.from_uci(uci[:4])
        if alt in board.legal_moves:
            return alt
    raise IllegalMove('这步棋不符合规则哦!')


class LessonSession:
    def __init__(self, curriculum: Curriculum, level_id: str,
                 stockfish: Optional[StockfishBot] = None, rng: Optional[random.Random] = None):
        found = curriculum.find_level(level_id)
        if found is None:
            raise KeyError(f'未知关卡:{level_id}')
        self.chapter, self.level, self.level_index = found
        self.id = uuid.uuid4().hex
        self.rng = rng or random.Random()
        self.stockfish = stockfish
        self.idx = 0
        self.mistakes = 0
        self.finished = False
        self.stars = 0
        self.progress_recorded = False
        self._reset_step_state()

    @property
    def step(self):
        return self.level.steps[self.idx]

    def _reset_step_state(self) -> None:
        self.solved = False
        self.fast_mate = False
        self.line_pos = 0
        self.last_move: Optional[list[str]] = None
        self.play_status: Optional[str] = None
        self.my_moves = 0
        self.bot_style: Optional[str] = self.step.bot if self.step.type == 'play' else None
        self.success_text: Optional[str] = None
        self.end_text: Optional[str] = None
        self.last_result: Optional[str] = None
        self.reply: Optional[dict] = None
        self._display_fen: Optional[str] = None
        self.board: Optional[chess.Board] = (
            chess.Board(self.step.fen) if getattr(self.step, 'fen', None) else None)
        if self.step.type == 'play':
            self.play_status = 'playing'

    # ---------- 公开状态 ----------
    def state(self) -> dict:
        step = self.step
        interactive = ((step.type in PUZZLE_TYPES and not self.solved)
                       or (step.type == 'play' and self.play_status == 'playing'))
        check_square = None
        if self.board is not None and self.board.is_check():
            check_square = chess.square_name(self.board.king(self.board.turn))
        line_prompt = None
        if step.type == 'line':
            i = min(self.line_pos // 2, len(step.prompts) - 1)
            line_prompt = step.prompts[i]
        return {
            'session_id': self.id,
            'level_id': self.level.id,
            'level_title': self.level.title,
            'level_skill': self.level.skill,
            'chapter_title': self.chapter.title,
            'chapter_badge': self.chapter.badge,
            'chapter_color': self.chapter.color,
            'chapter_soft': self.chapter.soft,
            'step_index': self.idx,
            'step_count': len(self.level.steps),
            'step': public_step(step),
            # 有 reply 时展示用户走完的中间局面,前端延迟后再展示 reply.fen
            'fen': self._display_fen or (self.board.fen() if self.board else None),
            'legal_moves': [m.uci() for m in self.board.legal_moves]
                           if (interactive and self.board) else [],
            'check_square': check_square,
            'last_move': self.last_move,
            'solved': self.solved,
            'fast_mate': self.fast_mate,
            'line_prompt': line_prompt,
            'play_status': self.play_status,
            'my_moves': self.my_moves,
            'bot_style': self.bot_style,
            'mistakes': self.mistakes,
            'finished': self.finished,
            'stars': self.stars,
            'success_text': self.success_text,
            'end_text': self.end_text,
            'last_result': self.last_result,
            'reply': self.reply,
        }

    # ---------- 推进 ----------
    def advance(self) -> dict:
        if self.finished:
            return self.state()
        step = self.step
        if step.type in PUZZLE_TYPES + ('choice', 'play') and not self.solved:
            raise IllegalMove('先完成这一步再走哦!')
        if self.idx + 1 >= len(self.level.steps):
            self.stars = 3 if self.mistakes == 0 else 2 if self.mistakes <= 2 else 1
            self.finished = True
        else:
            self.idx += 1
            self._reset_step_state()
        return self.state()

    # ---------- 走子 ----------
    def submit_move(self, uci: str) -> dict:
        if self.finished or self.board is None:
            raise IllegalMove('当前步骤不能走子')
        if self.step.type == 'play':
            return self._play_move(uci)
        if self.step.type not in PUZZLE_TYPES or self.solved:
            raise IllegalMove('当前步骤不能走子')
        self.reply = None
        self._display_fen = None
        move = parse_move(self.board, uci)
        handler = {'mate': self._handle_mate, 'move': self._handle_move,
                   'line': self._handle_line}[self.step.type]
        handler(move)
        return self.state()

    def _wrong(self) -> None:
        self.mistakes += 1
        self.last_result = 'wrong'

    def _handle_mate(self, move: chess.Move) -> None:
        self.board.push(move)
        if self.board.is_checkmate():
            self.solved = True
            self.last_move = [move.uci()[:2], move.uci()[2:4]]
            self.last_result = 'correct'
            self.success_text = self.step.successText
        else:
            self.board.pop()
            self._wrong()

    def _handle_move(self, move: chess.Move) -> None:
        bare = move.uci()[:4]
        if bare in self.step.accepted or move.uci() in self.step.accepted:
            self.board.push(move)
            self.solved = True
            self.last_move = [bare[:2], bare[2:]]
            self.last_result = 'correct'
            self.success_text = self.step.successText
        else:
            self._wrong()

    def _handle_line(self, move: chess.Move) -> None:
        step = self.step
        script = step.script
        bare = move.uci()[:4]
        self.board.push(move)
        mated = self.board.is_checkmate()
        hit = script[self.line_pos] in (bare, move.uci())
        if not (mated or hit):
            self.board.pop()
            self._wrong()
            return
        self.last_move = [bare[:2], bare[2:]]
        is_last = self.line_pos == len(script) - 1
        # 任何时候直接将死都算成功(更快杀法同样算挑战成功)
        if mated or is_last or self.line_pos + 1 >= len(script):
            self.fast_mate = mated and not is_last
            self.solved = True
            self.last_result = 'correct'
            self.success_text = ('更快将死!比参考答案还少用了步数,太厉害了!'
                                 if self.fast_mate else step.successText)
            return
        # 自动走出对手的应对
        user_fen = self.board.fen()
        self.line_pos += 1
        reply_uci = script[self.line_pos]
        reply_move = parse_move(self.board, reply_uci)
        self.board.push(reply_move)
        self.line_pos += 1
        self.last_result = 'correct'
        self._display_fen = user_fen
        self.reply = {'move': [reply_move.uci()[:2], reply_move.uci()[2:4]],
                      'fen': self.board.fen()}

    # ---------- 选择题 ----------
    def submit_choice(self, index: int) -> dict:
        if self.step.type != 'choice' or self.solved:
            raise IllegalMove('当前步骤不能作答')
        if index == self.step.answer:
            self.solved = True
            self.last_result = 'correct'
            self.success_text = self.step.explain
        else:
            self._wrong()
        return self.state()
```

- [ ] **Step 4: 跑测试确认通过**

Run: `cd backend && ../.venv/bin/pytest tests/test_session.py -v`
Expected: 11 passed

- [ ] **Step 5: Commit**

```bash
git add backend/app/core/ backend/tests/conftest.py backend/tests/test_session.py
git commit -m "feat: lesson session state machine for puzzle steps"
```

### Task 9: 会话 play 步骤(实战对弈 + bot + 重开)

**Files:**
- Modify: `backend/app/core/session.py`(追加 `_play_move`、`_pick_bot`、`restart_play`)
- Test: `backend/tests/test_play.py`

- [ ] **Step 1: 写失败的测试**

`backend/tests/test_play.py`:

```python
import random

import pytest

from app.core.session import IllegalMove, LessonSession

MATE_FEN = '6k1/5ppp/8/8/8/8/8/R5K1 w - - 0 1'       # a1a8 一步杀
QUEEN_FEN = '4k3/8/8/8/8/8/q7/R3K3 w - - 0 1'       # a1a2 吃掉黑后
ROOK_ENDGAME = '6k1/8/8/8/8/8/8/R5K1 w - - 0 1'     # 车王对单王

PLAY = {'type': 'play', 'fen': MATE_FEN, 'bot': 'random', 'win': 'mate',
        'prompt': 'p', 'successText': '赢了', 'failText': '输了', 'drawText': '和了'}


def mk(factory, step):
    return LessonSession(factory([step]), 't1', rng=random.Random(42))


def test_play_win_by_mate(curriculum_factory):
    s = mk(curriculum_factory, PLAY)
    st = s.submit_move('a1a8')
    assert st['play_status'] == 'won'
    assert st['solved'] is True
    assert '赢了' in st['success_text']
    assert st['my_moves'] == 1


def test_play_win_by_queen_capture(curriculum_factory):
    s = mk(curriculum_factory, {**PLAY, 'fen': QUEEN_FEN, 'win': 'mateOrQueen'})
    st = s.submit_move('a1a2')
    assert st['play_status'] == 'won'


def test_play_bot_replies(curriculum_factory):
    s = mk(curriculum_factory, {**PLAY, 'fen': ROOK_ENDGAME, 'bot': 'smart'})
    st = s.submit_move('a1a2')  # 未分胜负 → bot 回应
    assert st['play_status'] == 'playing'
    assert st['my_moves'] == 1
    assert st['reply'] is not None
    assert st['reply']['fen'] != st['fen']  # reply.fen 是 bot 走完之后
    assert len(st['legal_moves']) > 0


def test_play_move_after_game_over_raises(curriculum_factory):
    s = mk(curriculum_factory, PLAY)
    s.submit_move('a1a8')
    with pytest.raises(IllegalMove):
        s.submit_move('a8a1')


def test_restart_play(curriculum_factory):
    s = mk(curriculum_factory, {**PLAY, 'fen': ROOK_ENDGAME, 'bot': 'smart'})
    s.submit_move('a1a2')
    st = s.restart_play()
    assert st['fen'] == ROOK_ENDGAME
    assert st['my_moves'] == 0
    assert st['play_status'] == 'playing'
    assert st['mistakes'] == 1  # 对局中途重开算一次小失误
    assert st['reply'] is None


def test_restart_play_switch_bot(curriculum_factory):
    s = mk(curriculum_factory, {**PLAY, 'fen': ROOK_ENDGAME})
    st = s.restart_play(bot_style='greedy')
    assert st['bot_style'] == 'greedy'
    assert st['mistakes'] == 0  # 尚未走子,换档不算失误
    with pytest.raises(IllegalMove):
        s.restart_play(bot_style='terminator')
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd backend && ../.venv/bin/pytest tests/test_play.py -v`
Expected: FAIL,`AttributeError: 'LessonSession' object has no attribute '_play_move'`(submit_move 走到 play 分支报错)

- [ ] **Step 3: 实现 play 逻辑**

在 `backend/app/core/session.py` 的 `submit_choice` 方法之后追加:

```python
    # ---------- 实战对弈 ----------
    def _pick_bot(self) -> Optional[chess.Move]:
        if self.bot_style == 'master':
            if self.stockfish is not None:
                m = self.stockfish.pick(self.board)
                if m is not None:
                    return m
            return pick_bot_move(self.board, 'smart', self.rng)  # 无 stockfish 时兜底
        return pick_bot_move(self.board, self.bot_style or 'random', self.rng)

    def _play_move(self, uci: str) -> dict:
        step = self.step
        if self.play_status != 'playing':
            raise IllegalMove('本局已结束,请点击"再来一盘"')
        self.reply = None
        self._display_fen = None
        move = parse_move(self.board, uci)
        self.board.push(move)
        self.my_moves += 1
        self.last_move = [move.uci()[:2], move.uci()[2:4]]

        if self.board.is_checkmate():
            self.play_status = 'won'
            self.solved = True
            self.success_text = f'{step.successText}(用了 {self.my_moves} 步)'
            self.last_result = 'correct'
            return self.state()
        if step.win == 'mateOrQueen' and black_queen_gone(self.board):
            self.play_status = 'won'
            self.solved = True
            self.success_text = f'{step.successText}(用了 {self.my_moves} 步)'
            self.last_result = 'correct'
            return self.state()
        if is_draw(self.board):
            self.play_status = 'draw'
            self.end_text = step.drawText
            return self.state()

        # 电脑应对(同步返回,前端延迟动画展示)
        user_fen = self.board.fen()
        bm = self._pick_bot()
        if bm is not None:
            self.board.push(bm)
            self._display_fen = user_fen
            self.reply = {'move': [bm.uci()[:2], bm.uci()[2:4]], 'fen': self.board.fen()}
            if self.board.is_checkmate():
                self.play_status = 'lost'
                self.end_text = step.failText
            elif is_draw(self.board):
                self.play_status = 'draw'
                self.end_text = step.drawText
        return self.state()

    def restart_play(self, bot_style: Optional[str] = None) -> dict:
        step = self.step
        if step.type != 'play':
            raise IllegalMove('当前不是对弈步骤')
        if bot_style is not None:
            if bot_style not in BOT_STYLES:
                raise IllegalMove(f'未知对手档位:{bot_style}')
            self.bot_style = bot_style
        # 尚未走子的换档/重开不算失误;对局中途重开算一次小失误(影响星级)
        fresh = self.play_status == 'playing' and self.my_moves == 0
        if not fresh:
            self.mistakes += 1
        self.board = chess.Board(step.fen)
        self.last_move = None
        self.reply = None
        self._display_fen = None
        self.play_status = 'playing'
        self.my_moves = 0
        self.solved = False
        self.success_text = None
        self.end_text = None
        self.last_result = None
        return self.state()
```

- [ ] **Step 4: 跑测试确认通过**

Run: `cd backend && ../.venv/bin/pytest tests/test_play.py tests/test_session.py -v`
Expected: 6 + 11 passed

- [ ] **Step 5: Commit**

```bash
git add backend/app/core/session.py backend/tests/test_play.py
git commit -m "feat: play step with bot replies and restart"
```

### Task 10: API 路由 + 会话存储 + 静态托管

**Files:**
- Create: `backend/app/core/store.py`
- Modify: `backend/app/main.py`(全量替换)
- Test: `backend/tests/test_api.py`(追加集成测试)

- [ ] **Step 1: 写失败的测试**

`backend/tests/test_api.py` 全量替换为:

```python
import json

import pytest
from fastapi.testclient import TestClient

from app.main import create_app

TINY_CURRICULUM = [{
    'id': 'c1', 'badge': '测试', 'title': '测试章', 'intro': '', 'color': '#000', 'soft': '#fff',
    'levels': [{
        'id': 't1', 'title': '测试关', 'goal': 'g', 'skill': 's',
        'steps': [
            {'type': 'teach', 'title': 't', 'text': ['x']},
            {'type': 'move', 'fen': '4k3/8/8/8/8/8/8/R3K3 w - - 0 1',
             'prompt': 'p', 'accepted': ['a1a5'], 'successText': 'ok'},
        ],
    }],
}]


@pytest.fixture
def client(tmp_path):
    cur = tmp_path / 'cur.json'
    cur.write_text(json.dumps(TINY_CURRICULUM), encoding='utf-8')
    app = create_app(curriculum_path=cur, db_path=tmp_path / 'p.db', dist_dir=tmp_path / 'no-dist')
    return TestClient(app)


def test_health():
    from app.main import create_app as ca
    r = TestClient(ca(dist_dir='/nonexistent')).get('/api/health')
    assert r.status_code == 200 and r.json() == {'ok': True}


def test_curriculum_has_no_answers(client):
    r = client.get('/api/curriculum')
    assert r.status_code == 200
    assert 'accepted' not in r.text and 'successText' not in r.text
    body = r.json()
    assert body['total_levels'] == 1
    assert 'stockfish_available' in body


def test_full_lesson_flow(client):
    # 创建会话
    r = client.post('/api/sessions', json={'level_id': 't1'})
    assert r.status_code == 201
    sid = r.json()['session_id']
    # 未知关卡 404
    assert client.post('/api/sessions', json={'level_id': 'nope'}).status_code == 404
    # GET 恢复状态
    assert client.get(f'/api/sessions/{sid}').json()['step_index'] == 0
    # teach → next
    st = client.post(f'/api/sessions/{sid}/next').json()
    assert st['step_index'] == 1
    # 非法走法 422
    r = client.post(f'/api/sessions/{sid}/move', json={'move': 'a1b2'})
    assert r.status_code == 422
    # 合法但错误
    st = client.post(f'/api/sessions/{sid}/move', json={'move': 'a1a4'}).json()
    assert st['last_result'] == 'wrong'
    # 正确
    st = client.post(f'/api/sessions/{sid}/move', json={'move': 'a1a5'}).json()
    assert st['solved'] is True
    # 通关 → 自动写进度(1 次失误 → 2 星 → xp = 60 + 2*20)
    st = client.post(f'/api/sessions/{sid}/next').json()
    assert st['finished'] is True and st['stars'] == 2
    p = client.get('/api/progress').json()
    assert p['levels'] == {'t1': 2}
    assert p['xp'] == 100
    # 未知会话 404
    assert client.post('/api/sessions/deadbeef/move', json={'move': 'a1a5'}).status_code == 404


def test_progress_initially_empty(client):
    p = client.get('/api/progress').json()
    assert p['xp'] == 0 and p['levels'] == {}
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd backend && ../.venv/bin/pytest tests/test_api.py -v`
Expected: FAIL,`TypeError: create_app() got an unexpected keyword argument 'curriculum_path'`

- [ ] **Step 3: 实现 store.py**

`backend/app/core/store.py`:

```python
"""内存会话存储,带 TTL(默认 2 小时)。本地单用户应用足够。"""
import time
from typing import Optional

from app.core.session import LessonSession


class SessionStore:
    def __init__(self, ttl_seconds: int = 7200):
        self._sessions: dict[str, tuple[float, LessonSession]] = {}
        self._ttl = ttl_seconds

    def put(self, session: LessonSession) -> None:
        self._purge()
        self._sessions[session.id] = (time.time(), session)

    def get(self, session_id: str) -> Optional[LessonSession]:
        self._purge()
        item = self._sessions.get(session_id)
        if item is None:
            return None
        self._sessions[session_id] = (time.time(), item[1])  # 续期
        return item[1]

    def _purge(self) -> None:
        now = time.time()
        for k in [k for k, (t, _) in self._sessions.items() if now - t > self._ttl]:
            del self._sessions[k]
```

- [ ] **Step 4: 全量替换 main.py**

`backend/app/main.py`:

```python
import os
from pathlib import Path
from typing import Optional, Union

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.core.session import BOT_STYLES, IllegalMove, LessonSession
from app.core.store import SessionStore
from app.db import ProgressDB
from app.engine.stockfish_bot import StockfishBot
from app.models import load_curriculum, public_step

BACKEND_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_DIR.parent
DEFAULT_CURRICULUM = BACKEND_DIR / 'data' / 'curriculum.json'
DEFAULT_DB = BACKEND_DIR / 'data' / 'progress.db'


class NewSession(BaseModel):
    level_id: str


class MoveIn(BaseModel):
    move: str


class ChoiceIn(BaseModel):
    index: int


class RestartIn(BaseModel):
    bot: Optional[str] = None


def create_app(curriculum_path: Union[str, Path] = DEFAULT_CURRICULUM,
               db_path: Optional[Union[str, Path]] = None,
               dist_dir: Optional[Union[str, Path]] = None) -> FastAPI:
    curriculum = load_curriculum(curriculum_path)
    db = ProgressDB(db_path or os.environ.get('DB_PATH', str(DEFAULT_DB)))
    stockfish = StockfishBot()
    store = SessionStore()
    app = FastAPI(title='deb-chess')

    def get_session(session_id: str) -> LessonSession:
        s = store.get(session_id)
        if s is None:
            raise HTTPException(404, '课程会话不存在或已过期,请重新开始本关')
        return s

    def maybe_record(s: LessonSession) -> None:
        if s.finished and not s.progress_recorded:
            db.complete_level(s.level.id, s.stars)
            s.progress_recorded = True

    @app.get('/api/health')
    def health():
        return {'ok': True}

    @app.get('/api/curriculum')
    def get_curriculum():
        return {
            'chapters': [
                {**ch.model_dump(mode='json', exclude={'levels'}),
                 'levels': [
                     {**lv.model_dump(mode='json', exclude={'steps'}),
                      'steps': [public_step(st) for st in lv.steps]}
                     for lv in ch.levels
                 ]}
                for ch in curriculum.chapters
            ],
            'total_levels': len(curriculum.flat_levels()),
            'total_puzzles': curriculum.total_puzzles,
            'stockfish_available': stockfish.available(),
            'bot_styles': list(BOT_STYLES),
        }

    @app.get('/api/progress')
    def get_progress():
        return db.get()

    @app.post('/api/sessions', status_code=201)
    def new_session(body: NewSession):
        try:
            s = LessonSession(curriculum, body.level_id, stockfish=stockfish)
        except KeyError:
            raise HTTPException(404, f'关卡不存在:{body.level_id}')
        store.put(s)
        return s.state()

    @app.get('/api/sessions/{sid}')
    def session_state(sid: str):
        return get_session(sid).state()

    @app.post('/api/sessions/{sid}/move')
    def move(sid: str, body: MoveIn):
        s = get_session(sid)
        try:
            state = s.submit_move(body.move)
        except IllegalMove as e:
            raise HTTPException(422, str(e))
        maybe_record(s)
        return state

    @app.post('/api/sessions/{sid}/choice')
    def choice(sid: str, body: ChoiceIn):
        s = get_session(sid)
        try:
            state = s.submit_choice(body.index)
        except IllegalMove as e:
            raise HTTPException(422, str(e))
        maybe_record(s)
        return state

    @app.post('/api/sessions/{sid}/next')
    def nxt(sid: str):
        s = get_session(sid)
        try:
            state = s.advance()
        except IllegalMove as e:
            raise HTTPException(422, str(e))
        maybe_record(s)
        return state

    @app.post('/api/sessions/{sid}/restart-play')
    def restart(sid: str, body: RestartIn):
        s = get_session(sid)
        try:
            return s.restart_play(bot_style=body.bot)
        except IllegalMove as e:
            raise HTTPException(422, str(e))

    dist = Path(dist_dir or os.environ.get('DIST_DIR', str(REPO_ROOT / 'dist')))
    if dist.is_dir():
        app.mount('/', StaticFiles(directory=dist, html=True), name='static')

    return app


app = create_app()
```

- [ ] **Step 5: 跑测试确认通过**

Run: `cd backend && ../.venv/bin/pytest tests/ -v`
Expected: 全部通过(test_health 用 `/nonexistent` dist 避免依赖前端构建产物)

- [ ] **Step 6: Commit**

```bash
git add backend/app/main.py backend/app/core/store.py backend/tests/test_api.py
git commit -m "feat: full REST API with session store and static hosting"
```

### Task 11: 前端基础设施(api.ts、fen.ts、两个 context、dev proxy)

**Files:**
- Create: `src/lib/api.ts`
- Create: `src/lib/fen.ts`
- Create: `src/state/curriculum.tsx`
- Modify: `src/state/progress.tsx`(全量替换)
- Modify: `vite.config.ts`(加 proxy)

- [ ] **Step 1: 写 api.ts**

`src/lib/api.ts`:

```ts
const BASE = '/api'

export class ApiError extends Error {
  status: number

  constructor(message: string, status: number) {
    super(message)
    this.status = status
  }
}

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(BASE + path, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
  if (!res.ok) {
    let msg = `请求失败(${res.status})`
    try {
      const d = await res.json()
      if (typeof d.detail === 'string') msg = d.detail
    } catch { /* ignore */ }
    throw new ApiError(msg, res.status)
  }
  return res.json()
}

export interface PublicStep {
  type: 'teach' | 'mate' | 'move' | 'line' | 'choice' | 'play'
  fen?: string
  title?: string
  text?: string[]
  highlight?: string[]
  arrows?: [string, string][]
  prompt?: string
  prompts?: string[]
  hint?: string
  sideLabel?: string
  question?: string
  options?: string[]
  bot?: 'random' | 'greedy' | 'smart'
  win?: 'mate' | 'mateOrQueen'
  orientation?: 'white' | 'black'
}

export interface SessionState {
  session_id: string
  level_id: string
  level_title: string
  level_skill: string
  chapter_title: string
  chapter_badge: string
  chapter_color: string
  chapter_soft: string
  step_index: number
  step_count: number
  step: PublicStep
  fen: string | null
  legal_moves: string[]
  check_square: string | null
  last_move: [string, string] | null
  solved: boolean
  fast_mate: boolean
  line_prompt: string | null
  play_status: 'playing' | 'won' | 'lost' | 'draw' | null
  my_moves: number
  bot_style: string | null
  mistakes: number
  finished: boolean
  stars: number
  success_text: string | null
  end_text: string | null
  last_result: 'correct' | 'wrong' | null
  reply: { move: [string, string]; fen: string } | null
}

export interface LevelData {
  id: string
  title: string
  goal: string
  skill: string
  steps: PublicStep[]
}

export interface ChapterData {
  id: string
  badge: string
  title: string
  intro: string
  color: string
  soft: string
  levels: LevelData[]
}

export interface CurriculumResponse {
  chapters: ChapterData[]
  total_levels: number
  total_puzzles: number
  stockfish_available: boolean
  bot_styles: string[]
}

export interface ProgressResponse {
  levels: Record<string, number>
  xp: number
  total_stars: number
  rank_name: string
  rank_icon: string
}

export const api = {
  getCurriculum: () => req<CurriculumResponse>('/curriculum'),
  getProgress: () => req<ProgressResponse>('/progress'),
  createSession: (levelId: string) =>
    req<SessionState>('/sessions', { method: 'POST', body: JSON.stringify({ level_id: levelId }) }),
  getSession: (id: string) => req<SessionState>(`/sessions/${id}`),
  sessionMove: (id: string, move: string) =>
    req<SessionState>(`/sessions/${id}/move`, { method: 'POST', body: JSON.stringify({ move }) }),
  sessionChoice: (id: string, index: number) =>
    req<SessionState>(`/sessions/${id}/choice`, { method: 'POST', body: JSON.stringify({ index }) }),
  sessionNext: (id: string) =>
    req<SessionState>(`/sessions/${id}/next`, { method: 'POST', body: '{}' }),
  restartPlay: (id: string, bot?: string) =>
    req<SessionState>(`/sessions/${id}/restart-play`, {
      method: 'POST',
      body: JSON.stringify({ bot: bot ?? null }),
    }),
}
```

- [ ] **Step 2: 写 fen.ts(替代 chess.js 的渲染/解析用途)**

`src/lib/fen.ts`:

```ts
// 轻量 FEN 解析:只提取渲染所需的棋盘数组与行棋方。
// 返回结构与旧版 chess.js board() 兼容:[rank8..rank1][file a..h],格子含 square 字段。
export interface BoardPiece {
  type: string // 'p' | 'n' | 'b' | 'r' | 'q' | 'k'
  color: 'w' | 'b'
  square: string
}

const FILES = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']

export function parseFen(fen: string): { board: (BoardPiece | null)[][]; turn: 'w' | 'b' } {
  const [placement, turn] = fen.split(' ')
  const board = placement.split('/').map((row, r) => {
    const out: (BoardPiece | null)[] = []
    let f = 0
    for (const ch of row) {
      if (/\d/.test(ch)) {
        for (let i = 0; i < parseInt(ch, 10); i++) {
          out.push(null)
          f++
        }
      } else {
        out.push({
          type: ch.toLowerCase(),
          color: ch === ch.toUpperCase() ? 'w' : 'b',
          square: `${FILES[f]}${8 - r}`,
        })
        f++
      }
    }
    return out
  })
  return { board, turn: turn === 'b' ? 'b' : 'w' }
}
```

- [ ] **Step 3: 写 curriculum context**

`src/state/curriculum.tsx`:

```tsx
import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
import { api, type ChapterData, type LevelData } from '@/lib/api'

export interface FlatLevel {
  chapter: ChapterData
  level: LevelData
  index: number
}

interface CurriculumCtx {
  chapters: ChapterData[]
  flatLevels: FlatLevel[]
  totalLevels: number
  totalPuzzles: number
  stockfishAvailable: boolean
  loading: boolean
}

const Ctx = createContext<CurriculumCtx | null>(null)

const EMPTY: CurriculumCtx = {
  chapters: [],
  flatLevels: [],
  totalLevels: 0,
  totalPuzzles: 0,
  stockfishAvailable: false,
  loading: true,
}

export function CurriculumProvider({ children }: { children: ReactNode }) {
  const [data, setData] = useState<CurriculumCtx>(EMPTY)

  useEffect(() => {
    api
      .getCurriculum()
      .then((res) => {
        const flatLevels: FlatLevel[] = res.chapters.flatMap((chapter) =>
          chapter.levels.map((level) => ({ chapter, level, index: -1 })),
        )
        flatLevels.forEach((f, i) => (f.index = i))
        setData({
          chapters: res.chapters,
          flatLevels,
          totalLevels: res.total_levels,
          totalPuzzles: res.total_puzzles,
          stockfishAvailable: res.stockfish_available,
          loading: false,
        })
      })
      .catch(() => setData({ ...EMPTY, loading: false }))
  }, [])

  return <Ctx.Provider value={data}>{children}</Ctx.Provider>
}

export function useCurriculum(): CurriculumCtx {
  const ctx = useContext(Ctx)
  if (!ctx) throw new Error('useCurriculum must be used within CurriculumProvider')
  return ctx
}
```

- [ ] **Step 4: 重写 progress context(全量替换)**

`src/state/progress.tsx`:

```tsx
import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import { api } from '@/lib/api'

interface ProgressCtx {
  xp: number
  totalStars: number
  rank: { name: string; icon: string }
  starsOf: (levelId: string) => number
  refresh: () => Promise<void>
  // 兼容 shim:旧 Lesson.tsx 仍调用 completeLevel,Task 13 重写后于 Task 14 删除
  completeLevel: (levelId: string, stars: number) => void
}

const Ctx = createContext<ProgressCtx | null>(null)

export function ProgressProvider({ children }: { children: ReactNode }) {
  const [levels, setLevels] = useState<Record<string, number>>({})
  const [xp, setXp] = useState(0)
  const [totalStars, setTotalStars] = useState(0)
  const [rank, setRank] = useState({ name: '小士兵', icon: '♟' })

  const refresh = useCallback(async () => {
    const p = await api.getProgress()
    setLevels(p.levels)
    setXp(p.xp)
    setTotalStars(p.total_stars)
    setRank({ name: p.rank_name, icon: p.rank_icon })
  }, [])

  useEffect(() => {
    refresh().catch(() => undefined)
  }, [refresh])

  const value = useMemo<ProgressCtx>(
    () => ({
      xp,
      totalStars,
      rank,
      refresh,
      starsOf: (id) => levels[id] ?? 0,
      // 兼容 shim:进度由后端在通关时自动记录,这里只需刷新;Task 14 删除
      completeLevel: () => void refresh().catch(() => undefined),
    }),
    [xp, totalStars, rank, levels, refresh],
  )

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>
}

export function useProgress(): ProgressCtx {
  const ctx = useContext(Ctx)
  if (!ctx) throw new Error('useProgress must be used within ProgressProvider')
  return ctx
}
```

- [ ] **Step 5: vite dev proxy**

修改 `vite.config.ts` 的 `server` 段:

```ts
  server: {
    port: 3000,
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
```

- [ ] **Step 6: 验证构建**

Run: `npm run build`
Expected: 构建成功。本任务的文件均为纯增量/平行替换(`progress.tsx` 对外接口不变),旧页面组件尚未改造、chess.js 仍在,构建不受影响。

- [ ] **Step 7: Commit**

```bash
git add src/lib/api.ts src/lib/fen.ts src/state/curriculum.tsx src/state/progress.tsx vite.config.ts
git commit -m "feat: frontend API client, FEN parser, and data contexts"
```

### Task 12: ChessBoard 去 chess.js

**Files:**
- Modify: `src/components/ChessBoard.tsx`(全量替换)

说明:棋盘改为纯渲染组件——`fen` 用 `parseFen` 本地解析;合法走法提示点(`targets`)与被将军格不再本地计算,改由父组件通过 `legalMoves`、`checkSquare` props 传入(数据来自 SessionState)。本任务与 Task 13 是原子变更,合并提交。

- [ ] **Step 1: 全量替换 ChessBoard.tsx**

```tsx
import { useEffect, useMemo, useState } from 'react'
import { parseFen } from '@/lib/fen'

const GLYPH: Record<string, string> = {
  wk: '♔', wq: '♕', wr: '♖', wb: '♗', wn: '♘', wp: '♙',
  bk: '♚', bq: '♛', br: '♜', bb: '♝', bn: '♞', bp: '♟',
}

const FILES = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']

interface Props {
  fen: string
  interactive?: boolean
  onMove?: (uci: string) => void
  orientation?: 'white' | 'black'
  highlight?: string[]
  arrows?: [string, string][]
  lastMove?: [string, string] | null
  shake?: boolean
  legalMoves?: string[]        // 当前行棋方的合法走法(UCI),来自后端
  checkSquare?: string | null  // 被将军一方的王所在格,来自后端
}

function sqToXY(sq: string): { x: number; y: number } {
  const f = FILES.indexOf(sq[0])
  const r = 8 - parseInt(sq[1])
  return { x: f * 12.5 + 6.25, y: r * 12.5 + 6.25 }
}

export default function ChessBoard({
  fen,
  interactive = false,
  onMove,
  orientation = 'white',
  highlight = [],
  arrows = [],
  lastMove = null,
  shake = false,
  legalMoves = [],
  checkSquare = null,
}: Props) {
  const { board, turn } = useMemo(() => parseFen(fen), [fen])
  const [selected, setSelected] = useState<string | null>(null)

  useEffect(() => {
    setSelected(null)
  }, [fen])

  const targets = useMemo(() => {
    if (!selected) return new Set<string>()
    return new Set(
      legalMoves.filter((m) => m.startsWith(selected)).map((m) => m.slice(2, 4)),
    )
  }, [legalMoves, selected])

  const ranks = orientation === 'white' ? [0, 1, 2, 3, 4, 5, 6, 7] : [7, 6, 5, 4, 3, 2, 1, 0]
  const files = orientation === 'white' ? [0, 1, 2, 3, 4, 5, 6, 7] : [7, 6, 5, 4, 3, 2, 1, 0]

  const handleTap = (sq: string) => {
    if (!interactive) return
    const piece = board[8 - parseInt(sq[1])][FILES.indexOf(sq[0])]
    if (selected && targets.has(sq)) {
      onMove?.(selected + sq + 'q') // 升变默认皇后;后端会忽略多余的 promotion
      setSelected(null)
      return
    }
    if (piece && piece.color === turn) {
      setSelected(selected === sq ? null : sq)
    } else {
      setSelected(null)
    }
  }

  return (
    <div
      className={`relative select-none ${shake ? 'animate-[boardshake_0.4s_ease-in-out]' : ''}`}
      style={{ containerType: 'inline-size' }}
    >
      <div className="grid w-full aspect-square rounded-2xl overflow-hidden shadow-[0_18px_40px_-18px_rgba(80,50,10,0.45)] ring-4 ring-[#7a5a33]"
        style={{ gridTemplateColumns: 'repeat(8, 1fr)', gridTemplateRows: 'repeat(8, 1fr)' }}>
        {ranks.map((r) =>
          files.map((f) => {
            const sq = `${FILES[f]}${8 - r}`
            const piece = board[r][f]
            const dark = (r + f) % 2 === 1
            const isSel = selected === sq
            const isTarget = targets.has(sq)
            const isLast = lastMove && (lastMove[0] === sq || lastMove[1] === sq)
            const isHi = highlight.includes(sq)
            const isCheck = checkSquare === sq
            return (
              <button
                key={sq}
                onClick={() => handleTap(sq)}
                className="relative flex items-center justify-center p-0 border-0 min-w-0 min-h-0 overflow-hidden"
                style={{
                  backgroundColor: isCheck
                    ? '#e05252'
                    : isSel
                      ? '#f7d354'
                      : isHi
                        ? '#b9d97a'
                        : isLast
                          ? dark
                            ? '#d4b26a'
                            : '#f0dcaa'
                          : dark
                            ? '#b07848'
                            : '#f3e3c3',
                }}
              >
                {isTarget && !piece && (
                  <span className="absolute w-[26%] h-[26%] rounded-full bg-[#2e7d52]/60" />
                )}
                {isTarget && piece && (
                  <span className="absolute inset-[6%] rounded-full ring-4 ring-[#e05252]/80" />
                )}
                {piece && (
                  <span
                    className="relative leading-none"
                    style={{
                      fontSize: 'clamp(20px, 6.4cqw, 52px)',
                      containerType: 'normal',
                      color: piece.color === 'w' ? '#ffffff' : '#2b2118',
                      textShadow:
                        piece.color === 'w'
                          ? '0 0 2px #2b2118, 0 2px 3px rgba(43,33,24,0.55)'
                          : '0 1px 2px rgba(255,255,255,0.25)',
                      fontFamily: '"Segoe UI Symbol","Noto Sans Symbols 2","DejaVu Sans",sans-serif',
                    }}
                  >
                    {GLYPH[piece.color + piece.type]}
                  </span>
                )}
                {f === (orientation === 'white' ? 0 : 7) && (
                  <span className={`absolute left-[4%] top-[2%] text-[10px] font-bold ${dark ? 'text-[#f3e3c3]' : 'text-[#b07848]'}`}>
                    {8 - r}
                  </span>
                )}
                {r === (orientation === 'white' ? 7 : 0) && (
                  <span className={`absolute right-[5%] bottom-[2%] text-[10px] font-bold ${dark ? 'text-[#f3e3c3]' : 'text-[#b07848]'}`}>
                    {FILES[f]}
                  </span>
                )}
              </button>
            )
          }),
        )}
      </div>

      {arrows.length > 0 && (
        <svg viewBox="0 0 100 100" className="absolute inset-0 w-full h-full pointer-events-none">
          <defs>
            <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
              <path d="M0,0 L10,5 L0,10 z" fill="#2e7d52" />
            </marker>
          </defs>
          {arrows.map(([from, to], i) => {
            const a = sqToXY(from)
            const b = sqToXY(to)
            const dx = b.x - a.x
            const dy = b.y - a.y
            const len = Math.hypot(dx, dy) || 1
            const sx = a.x + (dx / len) * 4
            const sy = a.y + (dy / len) * 4
            const ex = b.x - (dx / len) * 5
            const ey = b.y - (dy / len) * 5
            return (
              <line key={i} x1={sx} y1={sy} x2={ex} y2={ey} stroke="#2e7d52" strokeWidth="2.6"
                strokeLinecap="round" markerEnd="url(#arr)" opacity="0.9" />
            )
          })}
        </svg>
      )}
    </div>
  )
}
```

- [ ] **Step 2: 不单独验证,直接进入 Task 13**(此时 Lesson.tsx 仍是旧版,构建会失败,属预期)

### Task 13: Lesson.tsx 重写(session 驱动)+ App/Home/Map 适配

**Files:**
- Modify: `src/pages/Lesson.tsx`(全量替换)
- Modify: `src/App.tsx`(全量替换)
- Modify: `src/pages/Home.tsx`(改三处)
- Modify: `src/pages/Map.tsx`(改两处)

- [ ] **Step 1: 全量替换 Lesson.tsx**

```tsx
import { useCallback, useEffect, useRef, useState } from 'react'
import ChessBoard from '@/components/ChessBoard'
import Confetti from '@/components/Confetti'
import { sounds } from '@/lib/sound'
import { api, ApiError, type SessionState } from '@/lib/api'
import { useProgress } from '@/state/progress'
import { useCurriculum } from '@/state/curriculum'
import { ArrowLeft, ArrowRight, Lightbulb, RotateCcw, Star, Map as MapIcon, Swords } from 'lucide-react'

interface Props {
  levelId: string
  onExit: () => void
  onNext: (() => void) | null
}

const BOT_LABELS: Record<string, string> = {
  random: '随便走',
  greedy: '贪吃鬼',
  smart: '小聪明',
  master: '大师 Stockfish',
}

export default function Lesson({ levelId, onExit, onNext }: Props) {
  const { refresh } = useProgress()
  const { stockfishAvailable } = useCurriculum()

  const [st, setSt] = useState<SessionState | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [wrongFlash, setWrongFlash] = useState(0)
  const [showHint, setShowHint] = useState(false)
  const [wrongChoices, setWrongChoices] = useState<number[]>([])
  const [pickedChoice, setPickedChoice] = useState<number | null>(null)
  // 对手回应延迟动画:后端已推进局面,前端先展示自己走完的局面,700ms 后再展示回应
  const [replyShown, setReplyShown] = useState(false)
  const replyTimer = useRef<ReturnType<typeof setTimeout> | null>(null)

  const start = useCallback(async () => {
    try {
      const s = await api.createSession(levelId)
      setSt(s)
      setError(null)
      setReplyShown(false)
      setPickedChoice(null)
      setWrongChoices([])
      setShowHint(false)
    } catch (e) {
      setError(e instanceof Error ? e.message : '加载失败,请检查后端是否启动')
    }
  }, [levelId])

  useEffect(() => {
    void start()
    return () => {
      if (replyTimer.current) clearTimeout(replyTimer.current)
    }
  }, [start])

  const apply = (s: SessionState) => {
    if (s.step_index !== st?.step_index) {
      setShowHint(false)
      setWrongChoices([])
      setPickedChoice(null)
    }
    setSt(s)
    setReplyShown(false)
    if (replyTimer.current) clearTimeout(replyTimer.current)
    if (s.reply) {
      replyTimer.current = setTimeout(() => {
        setReplyShown(true)
        sounds.move()
      }, 700)
    }
    if (s.finished) void refresh().catch(() => undefined)
  }

  /** 会话过期(404)时重建会话从头开始本关,返回 true 表示已处理 */
  const recover404 = async (e: unknown): Promise<boolean> => {
    if (e instanceof ApiError && e.status === 404) {
      await start()
      return true
    }
    return false
  }

  const handleMove = async (uci: string) => {
    if (!st || busy) return
    setBusy(true)
    try {
      const s = await api.sessionMove(st.session_id, uci)
      if (s.last_result === 'wrong') {
        setWrongFlash((n) => n + 1)
        sounds.error()
      } else if (st.step.type === 'play') {
        sounds.move()
        if (s.play_status === 'won') sounds.checkmate()
        else if (s.play_status === 'lost' || s.play_status === 'draw') sounds.error()
      } else if (s.solved) {
        if (st.step.type === 'move') sounds.success()
        else sounds.checkmate() // mate / line 完成
      } else {
        sounds.move() // line 剧本中段
      }
      apply(s)
    } catch (e) {
      if (!(await recover404(e))) setError(e instanceof Error ? e.message : '出错了')
    } finally {
      setBusy(false)
    }
  }

  const handleChoice = async (i: number) => {
    if (!st || busy || st.solved) return
    setBusy(true)
    try {
      const s = await api.sessionChoice(st.session_id, i)
      if (s.last_result === 'wrong') {
        setWrongChoices((w) => [...w, i])
        setWrongFlash((n) => n + 1)
        sounds.error()
      } else {
        setPickedChoice(i)
        sounds.success()
      }
      apply(s)
    } catch (e) {
      if (!(await recover404(e))) setError(e instanceof Error ? e.message : '出错了')
    } finally {
      setBusy(false)
    }
  }

  const goNext = async () => {
    if (!st || busy) return
    setBusy(true)
    try {
      const s = await api.sessionNext(st.session_id)
      if (s.finished) sounds.fanfare()
      apply(s)
    } catch (e) {
      if (!(await recover404(e))) setError(e instanceof Error ? e.message : '出错了')
    } finally {
      setBusy(false)
    }
  }

  const restart = async (bot?: string) => {
    if (!st || busy) return
    setBusy(true)
    try {
      apply(await api.restartPlay(st.session_id, bot))
    } catch (e) {
      if (!(await recover404(e))) setError(e instanceof Error ? e.message : '出错了')
    } finally {
      setBusy(false)
    }
  }

  // ---------------- 加载/错误 ----------------
  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#fff8ea] px-4">
        <div className="bg-[#fffdf6] rounded-3xl border-2 border-[#1f1a17]/10 p-8 text-center max-w-sm">
          <p className="font-bold text-[#c0392b] mb-4">{error}</p>
          <button onClick={() => void start()}
            className="px-6 py-3 rounded-full bg-[#1f1a17] text-white font-bold hover:bg-[#3a322c] transition">
            重试
          </button>
        </div>
      </div>
    )
  }
  if (!st) {
    return <div className="min-h-screen bg-[#fff8ea] flex items-center justify-center font-display text-2xl">加载中……</div>
  }

  const step = st.step
  const accent = st.chapter_color
  const isPuzzle = step.type === 'mate' || step.type === 'move' || step.type === 'line'
  // 有对手回应且动画未播时,棋盘锁定并展示中间局面
  const awaitingReply = st.reply !== null && !replyShown
  const boardFen = awaitingReply ? st.fen : (st.reply?.fen ?? st.fen)
  const boardLastMove: [string, string] | null = awaitingReply ? st.last_move : (st.reply?.move ?? st.last_move)

  // ---------------- 通关结算 ----------------
  if (st.finished) {
    return (
      <div className="min-h-screen flex items-center justify-center px-4 py-10" style={{ backgroundColor: st.chapter_soft }}>
        <Confetti />
        <div className="w-full max-w-md bg-[#fffdf6] rounded-3xl shadow-xl p-8 text-center border-4 border-[#1f1a17]">
          <div className="text-6xl mb-2">🏆</div>
          <h2 className="font-display text-3xl mb-1">闯关成功!</h2>
          <p className="text-[#6b5d4f] mb-3">{st.chapter_title} · {st.level_title}</p>
          <div className="inline-block px-4 py-1.5 rounded-full text-sm font-bold text-white mb-4" style={{ backgroundColor: accent }}>
            获得技能:{st.level_skill}
          </div>
          <div className="flex justify-center gap-2 mb-5">
            {[1, 2, 3].map((n) => (
              <Star key={n} size={44} strokeWidth={1.5}
                className={n <= st.stars ? 'fill-[#f7c948] text-[#b8860b]' : 'fill-[#ece5d8] text-[#cfc4b0]'} />
            ))}
          </div>
          <p className="text-sm text-[#6b5d4f] mb-6">
            {st.mistakes === 0 ? '完美通关,一次都没错!菲舍尔也会为你鼓掌。' : `错了 ${st.mistakes} 次,复习一下还能拿更多星星哦!`}
          </p>
          <div className="flex flex-col gap-3">
            {onNext && (
              <button onClick={onNext} className="w-full py-3.5 rounded-full bg-[#1f1a17] text-white font-bold text-lg flex items-center justify-center gap-2 hover:bg-[#3a322c] transition">
                下一关 <ArrowRight size={20} />
              </button>
            )}
            <div className="flex gap-3">
              <button onClick={() => void start()}
                className="flex-1 py-3 rounded-full border-2 border-[#1f1a17] font-bold flex items-center justify-center gap-2 hover:bg-[#f3ead9] transition">
                <RotateCcw size={18} /> 再玩一次
              </button>
              <button onClick={onExit}
                className="flex-1 py-3 rounded-full border-2 border-[#1f1a17] font-bold flex items-center justify-center gap-2 hover:bg-[#f3ead9] transition">
                <MapIcon size={18} /> 回地图
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen" style={{ backgroundColor: st.chapter_soft }}>
      {/* 顶栏 */}
      <div className="sticky top-0 z-20 bg-[#fffdf6]/95 backdrop-blur border-b-2 border-[#1f1a17]/10">
        <div className="max-w-3xl mx-auto px-4 py-3 flex items-center gap-3">
          <button onClick={onExit} className="p-2 rounded-full hover:bg-[#f3ead9] transition" aria-label="返回">
            <ArrowLeft size={22} />
          </button>
          <div className="flex-1 min-w-0">
            <div className="text-xs font-bold" style={{ color: accent }}>{st.chapter_badge} · {st.chapter_title}</div>
            <div className="font-display text-lg leading-tight truncate">{st.level_title}</div>
          </div>
          <div className="flex items-center gap-1.5">
            {Array.from({ length: st.step_count }).map((_, i) => (
              <span key={i} className="w-2.5 h-2.5 rounded-full transition"
                style={{ backgroundColor: i < st.step_index ? accent : i === st.step_index ? '#f7c948' : '#ddd2bd' }} />
            ))}
          </div>
        </div>
      </div>

      <div className="max-w-3xl mx-auto px-4 py-6 pb-24">
        <div className={`grid gap-6 ${step.type === 'choice' || step.type === 'teach' ? 'md:grid-cols-[1fr_1fr] md:items-center' : ''}`}>
          {/* 棋盘 */}
          {boardFen && (
            <div key={`${st.step_index}-${wrongFlash}`} className="w-full max-w-[520px] mx-auto">
              <ChessBoard
                fen={boardFen}
                interactive={((isPuzzle && !st.solved) || (step.type === 'play' && st.play_status === 'playing')) && !awaitingReply && !busy}
                onMove={(uci) => void handleMove(uci)}
                orientation={step.orientation || 'white'}
                highlight={step.type === 'teach' ? step.highlight : undefined}
                arrows={step.type === 'teach' ? step.arrows : undefined}
                lastMove={boardLastMove}
                shake={wrongFlash > 0}
                legalMoves={awaitingReply ? [] : st.legal_moves}
                checkSquare={awaitingReply ? null : st.check_square}
              />
              {step.sideLabel && (
                <div className="mt-3 text-center text-sm font-bold text-[#6b5d4f]">{step.sideLabel}</div>
              )}
              {step.type === 'play' && (
                <div className="mt-3 text-center text-sm font-bold text-[#6b5d4f]">
                  {awaitingReply ? '🤖 对方思考中……' : `你已走 ${st.my_moves} 步`}
                </div>
              )}
            </div>
          )}

          {/* 文字区 */}
          <div>
            {step.type === 'teach' && (
              <div className="bg-[#fffdf6] rounded-3xl border-2 border-[#1f1a17]/10 p-6 shadow-sm">
                <h3 className="font-display text-2xl mb-3" style={{ color: accent }}>{step.title}</h3>
                {(step.text ?? []).map((t, i) => (
                  <p key={i} className="text-[17px] leading-relaxed text-[#3a322c] mb-2">{t}</p>
                ))}
                <button onClick={() => void goNext()} disabled={busy}
                  className="mt-4 px-6 py-3 rounded-full text-white font-bold flex items-center gap-2 hover:opacity-90 transition disabled:opacity-50"
                  style={{ backgroundColor: accent }}>
                  我明白了 <ArrowRight size={18} />
                </button>
              </div>
            )}

            {isPuzzle && (
              <div className="bg-[#fffdf6] rounded-3xl border-2 border-[#1f1a17]/10 p-6 shadow-sm">
                <div className="inline-block px-3 py-1 rounded-full text-xs font-bold text-white mb-3" style={{ backgroundColor: accent }}>
                  {step.type === 'mate' ? '⚡ 一步杀' : step.type === 'line' ? '🔥 连续杀' : '🎯 找到这步棋'}
                </div>
                <p className="text-lg font-bold leading-relaxed text-[#3a322c]">
                  {step.type === 'line' ? st.line_prompt : step.prompt}
                </p>

                {!st.solved && (
                  <div className="mt-4 flex items-center gap-3">
                    {step.hint && (
                      <button onClick={() => setShowHint(!showHint)}
                        className="flex items-center gap-1.5 px-4 py-2 rounded-full border-2 border-[#b8860b] text-[#b8860b] font-bold text-sm hover:bg-[#fdf3d7] transition">
                        <Lightbulb size={16} /> 提示
                      </button>
                    )}
                    <span className="text-sm text-[#a3927c]">点棋子 → 点目标格</span>
                  </div>
                )}
                {showHint && !st.solved && step.hint && (
                  <div className="mt-3 p-3 rounded-2xl bg-[#fdf3d7] text-[#7a5c10] text-[15px] leading-relaxed">
                    💡 {step.hint}
                  </div>
                )}

                {st.solved && (
                  <div className="mt-4">
                    <div className="p-4 rounded-2xl bg-[#e7f5ec] border-2 border-[#2E7D52]/30 text-[#20573b] font-bold leading-relaxed">
                      🎉 {st.success_text}
                    </div>
                    <button onClick={() => void goNext()} disabled={busy}
                      className="mt-4 px-6 py-3 rounded-full text-white font-bold flex items-center gap-2 hover:opacity-90 transition disabled:opacity-50"
                      style={{ backgroundColor: accent }}>
                      继续 <ArrowRight size={18} />
                    </button>
                  </div>
                )}
                {wrongFlash > 0 && !st.solved && (
                  <p className="mt-3 text-[#c0392b] font-bold text-sm">这一步不对,再想想,你可以的!</p>
                )}
              </div>
            )}

            {step.type === 'choice' && (
              <div className="bg-[#fffdf6] rounded-3xl border-2 border-[#1f1a17]/10 p-6 shadow-sm">
                <div className="inline-block px-3 py-1 rounded-full text-xs font-bold text-white mb-3" style={{ backgroundColor: accent }}>
                  🤔 想一想
                </div>
                <p className="text-lg font-bold leading-relaxed text-[#3a322c] mb-4">{step.question}</p>
                <div className="flex flex-col gap-2.5">
                  {(step.options ?? []).map((opt, i) => {
                    const isRight = pickedChoice === i
                    const isWrong = wrongChoices.includes(i)
                    return (
                      <button key={i} onClick={() => void handleChoice(i)}
                        disabled={st.solved || busy}
                        className={`text-left px-5 py-3.5 rounded-2xl border-2 font-bold text-[16px] transition ${
                          isRight
                            ? 'bg-[#e7f5ec] border-[#2E7D52] text-[#20573b]'
                            : isWrong
                              ? 'bg-[#fdecea] border-[#e05252]/40 text-[#c0392b] line-through opacity-70'
                              : 'bg-white border-[#1f1a17]/15 hover:border-[#1f1a17]/50 text-[#3a322c]'
                        }`}>
                        {opt}
                      </button>
                    )
                  })}
                </div>
                {st.solved && (
                  <div className="mt-4">
                    <div className="p-4 rounded-2xl bg-[#e7f5ec] border-2 border-[#2E7D52]/30 text-[#20573b] font-bold leading-relaxed">
                      ✅ {st.success_text}
                    </div>
                    <button onClick={() => void goNext()} disabled={busy}
                      className="mt-4 px-6 py-3 rounded-full text-white font-bold flex items-center gap-2 hover:opacity-90 transition disabled:opacity-50"
                      style={{ backgroundColor: accent }}>
                      继续 <ArrowRight size={18} />
                    </button>
                  </div>
                )}
              </div>
            )}

            {step.type === 'play' && (
              <div className="bg-[#fffdf6] rounded-3xl border-2 border-[#1f1a17]/10 p-6 shadow-sm">
                <div className="inline-block px-3 py-1 rounded-full text-xs font-bold text-white mb-3" style={{ backgroundColor: accent }}>
                  <Swords size={12} className="inline -mt-0.5 mr-1" /> 实战对弈
                </div>
                <p className="text-lg font-bold leading-relaxed text-[#3a322c]">{step.prompt}</p>

                {/* 开局前可选对手档位 */}
                {st.play_status === 'playing' && st.my_moves === 0 && (
                  <div className="mt-3 flex flex-wrap gap-2">
                    {(['random', 'greedy', 'smart'] as const).map((b) => (
                      <button key={b} onClick={() => void restart(b)} disabled={busy}
                        className={`px-3 py-1.5 rounded-full text-sm font-bold border-2 transition ${
                          st.bot_style === b
                            ? 'bg-[#1f1a17] text-white border-[#1f1a17]'
                            : 'border-[#1f1a17]/20 text-[#6b5d4f] hover:border-[#1f1a17]/60'
                        }`}>
                        {BOT_LABELS[b]}
                      </button>
                    ))}
                    {stockfishAvailable && (
                      <button onClick={() => void restart('master')} disabled={busy}
                        className={`px-3 py-1.5 rounded-full text-sm font-bold border-2 transition ${
                          st.bot_style === 'master'
                            ? 'bg-[#7C4DA0] text-white border-[#7C4DA0]'
                            : 'border-[#7C4DA0]/40 text-[#7C4DA0] hover:border-[#7C4DA0]'
                        }`}>
                        {BOT_LABELS.master}
                      </button>
                    )}
                  </div>
                )}

                {st.play_status === 'playing' && (
                  <div className="mt-4">
                    {step.hint && (
                      <button onClick={() => setShowHint(!showHint)}
                        className="flex items-center gap-1.5 px-4 py-2 rounded-full border-2 border-[#b8860b] text-[#b8860b] font-bold text-sm hover:bg-[#fdf3d7] transition">
                        <Lightbulb size={16} /> 提示
                      </button>
                    )}
                    {showHint && (
                      <div className="mt-3 p-3 rounded-2xl bg-[#fdf3d7] text-[#7a5c10] text-[15px] leading-relaxed">
                        💡 {step.hint}
                      </div>
                    )}
                  </div>
                )}

                {st.play_status === 'won' && (
                  <div className="mt-4">
                    <div className="p-4 rounded-2xl bg-[#e7f5ec] border-2 border-[#2E7D52]/30 text-[#20573b] font-bold leading-relaxed">
                      🏆 {st.success_text}
                    </div>
                    <button onClick={() => void goNext()} disabled={busy}
                      className="mt-4 px-6 py-3 rounded-full text-white font-bold flex items-center gap-2 hover:opacity-90 transition disabled:opacity-50"
                      style={{ backgroundColor: accent }}>
                      继续 <ArrowRight size={18} />
                    </button>
                  </div>
                )}
                {(st.play_status === 'lost' || st.play_status === 'draw') && (
                  <div className="mt-4">
                    <div className="p-4 rounded-2xl bg-[#fdecea] border-2 border-[#e05252]/30 text-[#8c2f23] font-bold leading-relaxed">
                      {st.end_text}
                    </div>
                    <button onClick={() => void restart()} disabled={busy}
                      className="mt-4 px-6 py-3 rounded-full text-white font-bold flex items-center gap-2 hover:opacity-90 transition disabled:opacity-50"
                      style={{ backgroundColor: accent }}>
                      <RotateCcw size={18} /> 再来一盘
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: 全量替换 App.tsx**

```tsx
import { useState } from 'react'
import { Routes, Route } from 'react-router'
import Home from './pages/Home'
import MapPage from './pages/Map'
import Lesson from './pages/Lesson'
import { ProgressProvider } from './state/progress'
import { CurriculumProvider, useCurriculum } from './state/curriculum'

type Page = { name: 'home' } | { name: 'map' } | { name: 'lesson'; levelId: string }

function Shell() {
  const [page, setPage] = useState<Page>({ name: 'home' })
  const { flatLevels, loading } = useCurriculum()

  if (loading) {
    return <div className="min-h-screen bg-[#fff8ea] flex items-center justify-center font-display text-2xl">加载中……</div>
  }

  // 所有页面都在 / 下渲染,站内用状态切换,保证静态预览可用
  if (page.name === 'lesson') {
    const idx = flatLevels.findIndex((f) => f.level.id === page.levelId)
    const next = idx >= 0 ? flatLevels[idx + 1] : undefined
    return (
      <Lesson
        key={page.levelId}
        levelId={page.levelId}
        onExit={() => setPage({ name: 'map' })}
        onNext={next ? () => setPage({ name: 'lesson', levelId: next.level.id }) : null}
      />
    )
  }
  if (page.name === 'map') {
    return <MapPage onOpen={(levelId) => setPage({ name: 'lesson', levelId })} onHome={() => setPage({ name: 'home' })} />
  }
  return <Home onStart={() => setPage({ name: 'map' })} />
}

export default function App() {
  return (
    <CurriculumProvider>
      <ProgressProvider>
        <Routes>
          <Route path="/" element={<Shell />} />
          <Route path="*" element={<Shell />} />
        </Routes>
      </ProgressProvider>
    </CurriculumProvider>
  )
}
```

- [ ] **Step 3: 改 Home.tsx(三处,其余 markup 不变)**

头部 imports 替换为:

```tsx
import ChessBoard from '@/components/ChessBoard'
import { useProgress } from '@/state/progress'
import { useCurriculum } from '@/state/curriculum'
import { Star, Play, BookOpen, Crown, Swords, Flag, Gamepad2 } from 'lucide-react'
```

组件开头替换为:

```tsx
export default function Home({ onStart }: Props) {
  const { xp, totalStars, rank, starsOf } = useProgress()
  const { flatLevels, totalPuzzles } = useCurriculum()
  const nextLevel = flatLevels.find((f) => starsOf(f.level.id) === 0)
```

footer 文案替换为(进度改存服务端):

```tsx
        <p>学习进度保存在本机服务器的数据库里,换浏览器也不丢哦。</p>
```

- [ ] **Step 4: 改 Map.tsx(两处,其余 markup 不变)**

头部 imports 替换为:

```tsx
import { useProgress } from '@/state/progress'
import { useCurriculum } from '@/state/curriculum'
import { Star, Play, ChevronLeft } from 'lucide-react'
```

组件开头替换为:

```tsx
export default function MapPage({ onOpen, onHome }: Props) {
  const { starsOf, totalStars, xp, rank } = useProgress()
  const { chapters, flatLevels } = useCurriculum()
```

- [ ] **Step 5: 验证构建**

Run: `npm run build`
Expected: 构建成功,无 TS 错误。此时 chess.js 依赖仍在但已无业务引用(`src/lib/bot.ts`、`src/data/curriculum.ts` 成为死代码,下个任务删除)。

- [ ] **Step 6: 手动冒烟(dev 模式)**

```bash
cd backend && ../.venv/bin/uvicorn app.main:app --port 8000 &
npm run dev
```

浏览器打开 `http://localhost:3000`,人工核对:
- 首页正常显示,进入地图能看到章节与关卡;
- 进入第 1 关:teach 步点「我明白了」→ move 步走 a1→a5 正确通过;走错会晃动 + 报错音;
- 实战篇 play 关出现档位选择按钮;
- 通关后回地图,星星与 XP 显示更新。

- [ ] **Step 7: Commit(与 Task 12 合并)**

```bash
git add src/components/ChessBoard.tsx src/pages/Lesson.tsx src/App.tsx src/pages/Home.tsx src/pages/Map.tsx
git commit -m "feat: rewrite frontend as API-driven thin client"
```

### Task 14: 清理 JS 遗留

**Files:**
- Delete: `src/lib/bot.ts`
- Delete: `src/data/curriculum.ts`
- Modify: `package.json`(移除 chess.js)
- Modify: `src/state/progress.tsx`(删除 completeLevel 兼容 shim)

- [ ] **Step 1: 确认无引用后删除死代码**

```bash
grep -rn "chess.js" src/ || echo "no chess.js imports"
grep -rn "lib/bot\|data/curriculum" src/ || echo "no dead imports"
```
Expected: 两组都无输出(仅 echo 的确认文字)。**若有残留引用,先回到 Task 13 修正,不要继续。**

```bash
rm src/lib/bot.ts src/data/curriculum.ts
npm uninstall chess.js
rmdir src/data 2>/dev/null || true
```

- [ ] **Step 2: 删除 progress.tsx 的 completeLevel shim**

`src/state/progress.tsx` 中:
1. `ProgressCtx` 接口删除这两行:

```tsx
  // 兼容 shim:旧 Lesson.tsx 仍调用 completeLevel,Task 13 重写后于 Task 14 删除
  completeLevel: (levelId: string, stars: number) => void
```

2. `value` 的 useMemo 中删除这两行:

```tsx
      // 兼容 shim:进度由后端在通关时自动记录,这里只需刷新;Task 14 删除
      completeLevel: () => void refresh().catch(() => undefined),
```

- [ ] **Step 3: 验证构建**

Run: `npm run build`
Expected: 构建成功。若报 `completeLevel` 相关错误,说明 Lesson.tsx 未按 Task 13 重写干净,回去修。

- [ ] **Step 4: 全量后端测试回归**

Run: `cd backend && ../.venv/bin/pytest tests/ -v`
Expected: 全部通过

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "chore: remove chess.js and dead frontend logic"
```

### Task 15: 启动脚本 + Docker + 文档

**Files:**
- Create: `start.sh`
- Create: `Dockerfile`
- Create: `docker-compose.yml`
- Create: `.dockerignore`
- Modify: `.gitignore`(追加 Python 条目)
- Modify: `README.md`(全量替换)

- [ ] **Step 1: start.sh**

`start.sh`:

```bash
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
```

`chmod +x start.sh`

- [ ] **Step 2: Dockerfile / compose / .dockerignore**

`Dockerfile`:

```dockerfile
# 阶段一:构建前端
FROM node:20-slim AS frontend
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY index.html vite.config.ts tsconfig.json tsconfig.app.json tsconfig.node.json \
     tailwind.config.js postcss.config.js components.json ./
COPY src ./src
RUN npm run build

# 阶段二:Python 运行时(含 stockfish)
FROM python:3.12-slim
RUN apt-get update \
 && apt-get install -y --no-install-recommends stockfish \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY backend/pyproject.toml ./
COPY backend/app ./app
RUN pip install --no-cache-dir .
COPY backend/data/curriculum.json ./data/curriculum.json
COPY --from=frontend /app/dist ./dist
ENV DIST_DIR=/app/dist DB_PATH=/app/db/progress.db
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

`docker-compose.yml`:

```yaml
services:
  deb-chess:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - progress-data:/app/db   # 进度数据库持久化

volumes:
  progress-data:
```

`.dockerignore`:

```
node_modules
dist
.venv
.git
docs
data
**/__pycache__
**/*.pyc
backend/data/progress.db
```

- [ ] **Step 3: .gitignore 确认**

Python 条目已在 Task 1 Step 7 添加。`cat .gitignore` 确认 `.venv/`、`backend/data/progress.db` 均在列;缺失则补上。

- [ ] **Step 4: README 全量替换**

`README.md`:

```markdown
# 菲舍尔国际象棋练级营 (deb-chess)

面向儿童的国际象棋教学应用,课程方法源自《鲍比·菲舍尔教你下国际象棋》:
看局面、自己想、对答案,反复识别杀王模式形成直觉。

## 架构

- **后端(Python)**:FastAPI + python-chess。负责课程数据、走法校验、将杀判定、
  bot(random/greedy/smart 手写三档 + Stockfish 大师档)、进度存储(SQLite)。
- **前端(React/Vite)**:纯展示层,所有棋局逻辑通过 `/api` 调用后端。

## 本地运行

```bash
./start.sh        # 一键:构建前端 + 起后端,打开 http://localhost:8000
```

开发模式(前后端分离热更新):

```bash
# 终端 1:后端
python3 -m venv .venv && .venv/bin/pip install -e 'backend[dev]'
cd backend && ../.venv/bin/uvicorn app.main:app --reload --port 8000

# 终端 2:前端(/api 已代理到 :8000)
npm install && npm run dev   # http://localhost:3000
```

## Docker

```bash
docker compose up --build    # http://localhost:8000(镜像内含 stockfish)
```

## 测试

```bash
cd backend && ../.venv/bin/pytest tests/ -v
```

## 课程数据

- 数据源:`backend/data/curriculum.json`(由 `backend/scripts/convert_curriculum.sh`
  从旧版 `src/data/curriculum.ts` 一次性转换生成,原文件已删除)。
- 修改课程后直接编辑 JSON,然后跑校验:
  `python3 backend/scripts/validate_curriculum.py`(校验所有 FEN 与答案走法)。
```

- [ ] **Step 5: 验证 start.sh**

Run: `./start.sh`(后台)然后 `curl -s localhost:8000/api/health`
Expected: `{"ok":true}`;浏览器打开 `http://localhost:8000` 能看到首页。Ctrl-C 停掉。

- [ ] **Step 6: 验证 Docker(可选,Docker 未运行则跳过并注明)**

```bash
docker build -t deb-chess .
docker run --rm -p 8000:8000 deb-chess &
curl -s localhost:8000/api/health
```
Expected: `{"ok":true}` 且 `curl -s localhost:8000/ | head -5` 返回 index.html。

- [ ] **Step 7: Commit**

```bash
git add start.sh Dockerfile docker-compose.yml .dockerignore .gitignore README.md
git commit -m "feat: one-command startup, Docker packaging, and docs"
```

### Task 16: 端到端验收

- [ ] **Step 1: 全量自动测试**

```bash
cd backend && ../.venv/bin/pytest tests/ -v
npm run build
```
Expected: pytest 全绿;前端构建成功。

- [ ] **Step 2: 生产模式 smoke(curl 走通完整流程)**

```bash
./start.sh &
sleep 3
curl -s localhost:8000/api/health
# → {"ok":true}

curl -s localhost:8000/api/curriculum | python3 -c "
import sys, json
raw = sys.stdin.read()
d = json.loads(raw)
assert 'accepted' not in raw and 'script' not in raw, '答案字段泄露!'
print('chapters:', len(d['chapters']), 'levels:', d['total_levels'], 'stockfish:', d['stockfish_available'])"
# → chapters: 5 levels: 20 stockfish: true/false

SID=$(curl -s -X POST localhost:8000/api/sessions -H 'Content-Type: application/json' \
  -d '{"level_id":"w1"}' | python3 -c 'import sys,json;print(json.load(sys.stdin)["session_id"])')

curl -s -X POST localhost:8000/api/sessions/$SID/next | python3 -c 'import sys,json;d=json.load(sys.stdin);print("step:",d["step_index"],d["step"]["type"])'
# → step: 1 move

curl -s -X POST localhost:8000/api/sessions/$SID/move -H 'Content-Type: application/json' -d '{"move":"a1a4"}' \
  | python3 -c 'import sys,json;print("wrong move →",json.load(sys.stdin)["last_result"])'
# → wrong move → wrong

curl -s -X POST localhost:8000/api/sessions/$SID/move -H 'Content-Type: application/json' -d '{"move":"a1a5"}' \
  | python3 -c 'import sys,json;d=json.load(sys.stdin);print("right move → solved:",d["solved"])'
# → right move → solved: True

curl -s localhost:8000/api/progress | python3 -m json.tool
# → levels/xp 字段齐全
```

- [ ] **Step 3: 浏览器人工验收清单**(`http://localhost:8000`)

- 首页/地图/关卡页渲染正常,无 console 报错;
- 完成一整关后星星、XP、段位在地图上即时更新;
- 刷新页面进度仍在(存在 SQLite);
- play 关走错被将死 → 「再来一盘」恢复正常;
- 答案无法从 Network 面板泄露(检查 `/api/curriculum` 响应无 `accepted`/`script`/`answer` 字段)。

- [ ] **Step 4: 最终 commit(如有改动)并收尾**

```bash
git status   # 应干净或仅有验收修正
git log --oneline | head -20
```
