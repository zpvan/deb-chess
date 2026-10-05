# deb-chess 开源准备实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 完成 deb-chess 开源所需的全部工作:清除 git 历史中的版权书页、GPL-3.0 许可、双语文档套件、CI、仓库元数据与 v1.0.0 发布。

**Architecture:** 无代码变更——纯仓库治理任务。核心风险操作是 git filter-repo 历史重写(第一个任务,一次做对),其余为文件新增与 GitHub 配置。

**Tech Stack:** git filter-repo, GitHub CLI (gh), GitHub Actions, Playwright(截图)。

**Spec:** `docs/superpowers/specs/2026-10-06-open-source-preparation-design.md`

**背景知识(执行者需知):**
- 仓库:`git@github.com:zpvan/deb-chess.git`,分支 `main`,本地工作区 `/Users/knox/Documents/GitWorkSpace/deb-chess`。
- `data/`(约 29MB)是《Bobby Fischer Teaches Chess》书页扫描件,已在历史与远端,必须全历史清除。**应用代码不引用 data/ 中的任何文件**,删除不影响运行。
- 后端测试命令:`cd backend && ../.venv/bin/pytest tests/ -v`(37 passed, 2 skipped 为正常,stockfish 未装时跳过)。
- 前端构建命令:`npm run build`。

---

### Task 1: data/ 历史清除(高风险,一次做对)

**Files:**
- Delete(全历史): `data/Bobby-Fischer-Teaches-Chess/`(约 489 个文件)
- Create: `data/README.md`

- [ ] **Step 1: 备份 data/ 到仓库外**

```bash
mv /Users/knox/Documents/GitWorkSpace/deb-chess/data ~/deb-chess-book-data-backup
ls ~/deb-chess-book-data-backup/Bobby-Fischer-Teaches-Chess | head -3
```
Expected: 显示 `assets`、`index.html` 等;仓库内 `data/` 已不存在。

- [ ] **Step 2: 确认工作区干净并安装 git-filter-repo**

```bash
cd /Users/knox/Documents/GitWorkSpace/deb-chess
git status --porcelain   # 必须无输出;有输出则先提交或 stash
.venv/bin/pip install git-filter-repo
```

- [ ] **Step 3: 重写历史(从所有 commit 删除 data 路径)**

```bash
.venv/bin/git-filter-repo --path data --invert-paths --force
```
Expected: 输出 `Parsed N commits`、`Rewriting history... finished`。注意:filter-repo 会**自动删除 origin remote**(安全机制),Step 5 重新添加。

- [ ] **Step 4: 本地验证清除效果**

```bash
git log --all --oneline -- data        # Expected: 无输出
ls data 2>&1                           # Expected: No such file or directory
git count-objects -vH | grep size-pack # Expected: 约 <2MB(原 ~30MB)
git log --oneline | wc -l              # Expected: 与重写前 commit 数相同(hash 全部变了是正常的)
```

- [ ] **Step 5: 恢复 remote 并 force push**

```bash
git remote add origin git@github.com:zpvan/deb-chess.git
git push origin main --force
```
Expected: 推送成功。远端历史已被干净版本覆盖。

- [ ] **Step 6: 创建 data/README.md 占位说明**

`data/README.md`:

```markdown
# Book Data (not included)

The page scans of *Bobby Fischer Teaches Chess* are **not** part of this
repository — they are copyrighted material and were removed from the git
history.

The application does **not** reference these files; it runs fully without
them. If you own the book and want the reference material locally, place it
here as `Bobby-Fischer-Teaches-Chess/` (this directory is git-ignored
content-wise except for this README).

书页扫描件版权归原作者所有,本仓库不包含、不分发。应用运行不依赖这些文件。
```

- [ ] **Step 7: 提交并推送**

```bash
git add data/README.md
git commit -m "Add data directory README explaining book data exclusion"
git push origin main
```

- [ ] **Step 8: 远端验证(全新 clone)**

```bash
git clone git@github.com:zpvan/deb-chess.git /tmp/deb-chess-verify
du -sh /tmp/deb-chess-verify/.git        # Expected: <2MB
ls /tmp/deb-chess-verify/data            # Expected: 只有 README.md
rm -rf /tmp/deb-chess-verify
```

### Task 2: LICENSE 与包元数据

**Files:**
- Create: `LICENSE`
- Modify: `package.json`(name、license)
- Modify: `backend/pyproject.toml`(license)

- [ ] **Step 1: 获取 GPL-3.0 全文**

```bash
gh api licenses/gpl-3.0 --jq .body > LICENSE || curl -sL https://www.gnu.org/licenses/gpl-3.0.txt > LICENSE
head -3 LICENSE   # Expected: "GNU GENERAL PUBLIC LICENSE" / "Version 3, 29 June 2007"
wc -l LICENSE     # Expected: 600+ 行
```

- [ ] **Step 2: 修改 package.json**

`package.json` 顶部两处修改(`"private": true` 保留):

```json
{
  "name": "deb-chess",
  "private": true,
  "version": "1.0.0",
  "license": "GPL-3.0",
  "type": "module",
```

- [ ] **Step 3: 修改 backend/pyproject.toml**

在 `[project]` 段的 `version = "0.1.0"` 后追加一行,并把 version 改为 1.0.0:

```toml
version = "1.0.0"
license = {text = "GPL-3.0"}
```

- [ ] **Step 4: 验证**

Run: `npm run build && cd backend && ../.venv/bin/pytest tests/ -q 2>&1 | tail -1`
Expected: 构建成功;`37 passed, 2 skipped`

- [ ] **Step 5: Commit 并推送**

```bash
git add LICENSE package.json backend/pyproject.toml
git commit -m "Add GPL-3.0 license and update package metadata"
git push origin main
```

### Task 3: README 截图

**Files:**
- Create: `docs/screenshots/home.png`、`map.png`、`lesson.png`

- [ ] **Step 1: 清理本地进度并启动应用(保证截图是全新用户视角)**

```bash
rm -f backend/data/progress.db
(./start.sh > /tmp/deb-chess-shots.log 2>&1 &)
sleep 3
curl -s localhost:8000/api/health   # Expected: {"ok":true}
```

- [ ] **Step 2: 在临时目录安装 Playwright(不污染项目依赖)**

```bash
mkdir -p /tmp/deb-shots && cd /tmp/deb-shots
npm init -y > /dev/null 2>&1
npm install playwright > /dev/null 2>&1
npx playwright install chromium
```
Expected: chromium 安装成功(下载约 120MB)。**若此步因网络失败:停止并询问用户**——改为用户手动截图后放入 `docs/screenshots/`,README 图片引用保持不变。

- [ ] **Step 3: 截图脚本**

`/tmp/deb-shots/shots.mjs`:

```js
import { chromium } from 'playwright'

const OUT = '/Users/knox/Documents/GitWorkSpace/deb-chess/docs/screenshots'
const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1280, height: 800 } })

await page.goto('http://localhost:8000')
await page.waitForTimeout(2000)
await page.screenshot({ path: `${OUT}/home.png` })

// 首页 → 地图
await page.getByRole('button', { name: /闯关/ }).first().click()
await page.waitForTimeout(1000)
await page.screenshot({ path: `${OUT}/map.png` })

// 地图 → 第 1 关
await page.getByRole('button', { name: /第 1 关/ }).click()
await page.waitForTimeout(1000)
await page.screenshot({ path: `${OUT}/lesson.png` })

await browser.close()
console.log('done')
```

```bash
cd /tmp/deb-shots && node shots.mjs
ls -la /Users/knox/Documents/GitWorkSpace/deb-chess/docs/screenshots/
```
Expected: 3 个 png 文件,每个 >50KB(空白页会很小,可作为 sanity check)。

- [ ] **Step 4: 人工检查截图内容**

Read 三张 png(用 Read 工具查看图片),确认:home.png 显示首页主视觉;map.png 显示章节列表;lesson.png 显示棋盘与教学卡片。若内容不对,调整 shots.mjs 的选择器/等待时间重跑。

- [ ] **Step 5: 停服务并提交**

```bash
pkill -f uvicorn
cd /Users/knox/Documents/GitWorkSpace/deb-chess
git add docs/screenshots/
git commit -m "Add README screenshots"
git push origin main
```

### Task 4: 双语文档套件

**Files:**
- Modify: `README.md`(全量替换为英文版)
- Create: `README_ZH.md`
- Create: `CONTRIBUTING.md`
- Create: `CODE_OF_CONDUCT.md`
- Create: `.github/ISSUE_TEMPLATE/bug_report.md`
- Create: `.github/ISSUE_TEMPLATE/feature_request.md`
- Create: `.github/PULL_REQUEST_TEMPLATE.md`

- [ ] **Step 1: README.md(英文主版,全量替换)**

```markdown
# deb-chess — Fischer Chess Training Camp

[中文版](README_ZH.md)

[![CI](https://github.com/zpvan/deb-chess/actions/workflows/ci.yml/badge.svg)](https://github.com/zpvan/deb-chess/actions/workflows/ci.yml)

A chess-learning web app for kids, inspired by the teaching method of
*Bobby Fischer Teaches Chess*: look at the position, think for yourself,
check the answer — drill mate patterns until they become intuition.
(UI text is in Chinese.)

![Home](docs/screenshots/home.png)

## Features

- **20 levels in 5 chapters** — endgames first, then middlegame tactics,
  openings, and real games against the computer
- **6 interactive step types**: teach, mate-in-1, find-the-move, mating
  lines, quizzes, play-vs-bot
- **4 bot difficulties**: 3 handcrafted styles (random / greedy / smart)
  plus a Stockfish "Master" tier (UCI, optional)
- **Stars / XP / ranks** progress system persisted in SQLite
- **Backend-authoritative**: every move is validated server-side with
  python-chess; puzzle answers never reach the browser

| Map | Lesson |
| --- | --- |
| ![Map](docs/screenshots/map.png) | ![Lesson](docs/screenshots/lesson.png) |

## Architecture

- **Backend (Python)** — FastAPI + python-chess: curriculum data, move
  validation, checkmate detection, bots, progress storage (SQLite)
- **Frontend (React 19 + Vite)** — thin presentation layer; all game
  logic goes through the `/api` REST endpoints

## Quick Start

```bash
./start.sh        # builds the frontend and starts the server
                  # → http://localhost:8000
```

With Docker (image includes Stockfish):

```bash
docker compose up --build   # → http://localhost:8000
```

Development mode (hot reload):

```bash
# terminal 1: backend
python3 -m venv .venv && .venv/bin/pip install -e 'backend[dev]'
cd backend && ../.venv/bin/uvicorn app.main:app --reload --port 8000

# terminal 2: frontend (/api is proxied to :8000)
npm install && npm run dev   # → http://localhost:3000
```

## Testing

```bash
cd backend && ../.venv/bin/pytest tests/ -v
```

The suite covers the bot logic, the lesson session state machine, the
progress rules, the REST API, and a full validation of every FEN and
answer move in the curriculum data.

## Curriculum Data

- Source of truth: `backend/data/curriculum.json`
  (5 chapters, 20 levels, 82 steps; lesson text in Chinese).
- After editing, run the validator — every FEN must be legal and every
  answer move must be playable:

  ```bash
  python3 backend/scripts/validate_curriculum.py
  ```

- Book page scans are **not** included (see `data/README.md`); the app
  does not need them.

## License & Copyright

- Code: **GPL-3.0** (see [LICENSE](LICENSE)), consistent with the GPL-3.0
  dependencies python-chess and Stockfish.
- *Bobby Fischer Teaches Chess* (book content and page images) is
  copyrighted by its publisher. This repository contains and distributes
  no book pages. Lesson text is original Chinese writing; the puzzles are
  classic checkmate patterns.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).
```

- [ ] **Step 2: README_ZH.md(中文副版)**

```markdown
# deb-chess — 菲舍尔国际象棋练级营

[English README](README.md)

[![CI](https://github.com/zpvan/deb-chess/actions/workflows/ci.yml/badge.svg)](https://github.com/zpvan/deb-chess/actions/workflows/ci.yml)

面向儿童的国际象棋教学应用,课程方法源自《鲍比·菲舍尔教你下国际象棋》:
看局面、自己想、对答案,反复识别杀王模式形成直觉。

![首页](docs/screenshots/home.png)

## 特性

- **5 章 20 关**——先终局,再中局战术,然后开局,最后实战对弈
- **6 种互动步骤**:教学、一步杀、找着法、连续杀、选择题、实战对弈
- **4 档电脑对手**:手写三档(随便走/贪吃鬼/小聪明)+ Stockfish 大师档(UCI,可选)
- **星星 / XP / 段位**进度系统,存储于 SQLite
- **后端权威**:所有走法由 python-chess 在服务端校验,答案永不下发浏览器

| 地图 | 关卡 |
| --- | --- |
| ![地图](docs/screenshots/map.png) | ![关卡](docs/screenshots/lesson.png) |

## 架构

- **后端(Python)**:FastAPI + python-chess。课程数据、走法校验、将杀判定、
  bot、进度存储(SQLite)。
- **前端(React 19 + Vite)**:纯展示层,所有棋局逻辑通过 `/api` 调用后端。

## 快速开始

```bash
./start.sh        # 构建前端并启动服务 → http://localhost:8000
```

Docker(镜像内含 Stockfish):

```bash
docker compose up --build   # → http://localhost:8000
```

开发模式(前后端热更新):

```bash
# 终端 1:后端
python3 -m venv .venv && .venv/bin/pip install -e 'backend[dev]'
cd backend && ../.venv/bin/uvicorn app.main:app --reload --port 8000

# 终端 2:前端(/api 已代理到 :8000)
npm install && npm run dev   # → http://localhost:3000
```

## 测试

```bash
cd backend && ../.venv/bin/pytest tests/ -v
```

测试覆盖:bot 逻辑、课程会话状态机、进度规则、REST API,
以及课程数据中所有 FEN 与答案走法的全量校验。

## 课程数据

- 数据源:`backend/data/curriculum.json`(5 章 20 关 82 步)。
- 修改课程后必须运行校验器(每个 FEN 合法、每个答案走法可走):

  ```bash
  python3 backend/scripts/validate_curriculum.py
  ```

- 书页扫描件不包含在本仓库(见 `data/README.md`),应用运行不依赖它们。

## 许可证与版权

- 代码:**GPL-3.0**(见 [LICENSE](LICENSE)),与 GPL-3.0 依赖
  python-chess、Stockfish 保持一致。
- 《Bobby Fischer Teaches Chess》书籍内容与书页图像版权归原出版方所有。
  本仓库不包含、不分发书页;课程文字为原创中文编写,棋题为经典杀王模式。

## 参与贡献

见 [CONTRIBUTING.md](CONTRIBUTING.md)。
```

- [ ] **Step 3: CONTRIBUTING.md(英文)**

```markdown
# Contributing to deb-chess

Thanks for your interest! This document explains how to set up the project
and what we expect in a pull request.

## Setup

```bash
python3 -m venv .venv && .venv/bin/pip install -e 'backend[dev]'
npm install
```

Run everything before submitting:

```bash
cd backend && ../.venv/bin/pytest tests/ -v   # backend tests
cd .. && npm run build                        # frontend type-check + build
```

Both must pass. CI runs the same checks on every PR.

## Curriculum changes

- Edit `backend/data/curriculum.json` only (there is no other source).
- Every change must pass `python3 backend/scripts/validate_curriculum.py`
  — it checks every FEN and every answer move with python-chess.
- Never reintroduce book page scans or other copyrighted material
  (see `data/README.md`).

## Code style

- Backend: plain type-annotated Python, pydantic models for payloads,
  TDD with pytest (write the failing test first).
- Frontend: keep it a thin presentation layer — no chess rules in the
  browser, all game logic belongs in the backend.
- Commits: small, imperative subject lines
  (e.g. `feat: add mate-in-two step type`).

## Pull requests

1. Fork and create a branch from `main`.
2. Keep the PR focused on one change.
3. Fill in the PR template and make sure CI is green.
```

- [ ] **Step 4: CODE_OF_CONDUCT.md(标准文本)**

```bash
curl -sL https://www.contributor-covenant.org/version/2/1/code_of_conduct.md -o CODE_OF_CONDUCT.md
head -2 CODE_OF_CONDUCT.md   # Expected: "# Contributor Covenant Code of Conduct"
```
若 curl 失败(网络),停止并告知用户手动下载后放入。

- [ ] **Step 5: Issue 模板**

`.github/ISSUE_TEMPLATE/bug_report.md`:

```markdown
---
name: Bug report
about: Something is broken
title: ''
labels: bug
---

**What happened?**

**What did you expect?**

**Steps to reproduce**
1.
2.
3.

**Environment**
- OS / browser:
- How you run the app (start.sh / Docker / dev mode):
```

`.github/ISSUE_TEMPLATE/feature_request.md`:

```markdown
---
name: Feature request
about: Suggest an idea
title: ''
labels: enhancement
---

**What problem does this solve?**

**Describe the solution you'd like**

**Alternatives you've considered**
```

- [ ] **Step 6: PR 模板**

`.github/PULL_REQUEST_TEMPLATE.md`:

```markdown
## What changed

## Why

## Checklist
- [ ] `cd backend && ../.venv/bin/pytest tests/ -v` passes
- [ ] `npm run build` passes
- [ ] Curriculum edits (if any) pass `python3 backend/scripts/validate_curriculum.py`
- [ ] No copyrighted material added
```

- [ ] **Step 7: Commit 并推送**

```bash
git add README.md README_ZH.md CONTRIBUTING.md CODE_OF_CONDUCT.md .github/
git commit -m "Add bilingual docs, contributing guide, CoC, and GH templates"
git push origin main
```

### Task 5: CI(GitHub Actions)

**Files:**
- Create: `.github/workflows/ci.yml`

- [ ] **Step 1: 写 workflow**

`.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install Stockfish
        run: sudo apt-get update && sudo apt-get install -y stockfish
      - name: Install backend
        run: pip install -e 'backend[dev]'
      - name: Run tests
        run: cd backend && pytest tests/ -v

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci
      - run: npm run build
```

- [ ] **Step 2: Commit 并推送,观察首次运行**

```bash
git add .github/workflows/ci.yml
git commit -m "Add CI workflow for backend tests and frontend build"
git push origin main
sleep 20
gh run list --limit 1
```
Expected: 最新 run 显示 CI / push。等它结束:`gh run watch`——**两个 job 都必须绿**(backend job 里 stockfish 已安装,之前的 2 个 skip 在 CI 中会真正跑起来,应为 39 passed)。

- [ ] **Step 3: 若 CI 红,修复后重推**

常见原因:`apt install stockfish` 包名、npm ci 的 lockfile 不同步。修复后 commit + push,重复 Step 2 直到绿。

### Task 6: 仓库元数据、清理与 v1.0.0 发布

**Files:**
- Delete: `info.md`

- [ ] **Step 1: 删除脚手架遗留文件**

```bash
rm info.md
git add -A && git commit -m "Remove scaffolding leftover info.md"
git push origin main
```

- [ ] **Step 2: 设置 GitHub 仓库元数据**

```bash
gh repo edit zpvan/deb-chess \
  --description "A chess-learning web app for kids, inspired by Bobby Fischer Teaches Chess. FastAPI + python-chess backend, React frontend." \
  --add-topic chess --add-topic education --add-topic fastapi \
  --add-topic react --add-topic python --add-topic kids \
  --homepage ""
gh repo view zpvan/deb-chess --json description,repositoryTopics | head -5
```
Expected: description 与 topics 已设置。

- [ ] **Step 3: 打 tag 并发布 v1.0.0**

```bash
git tag -a v1.0.0 -m "First open-source release"
git push origin v1.0.0
gh release create v1.0.0 --title "v1.0.0 — First open-source release" --notes "$(cat <<'EOF'
deb-chess is now open source (GPL-3.0)!

## Highlights
- FastAPI + python-chess backend-authoritative architecture
- 5 chapters / 20 levels / 82 interactive steps
- 4 bot difficulties including a Stockfish master tier
- SQLite progress (stars / XP / ranks)

## Notes
- Book page scans are NOT included (copyright) — the app does not need them
- Run locally with `./start.sh` or `docker compose up --build`
EOF
)"
```

- [ ] **Step 4: 最终验收(fresh clone 全流程)**

```bash
rm -rf /tmp/deb-chess-final
git clone git@github.com:zpvan/deb-chess.git /tmp/deb-chess-final
cd /tmp/deb-chess-final
ls                      # Expected: 无 info.md;有 LICENSE README.md README_ZH.md CONTRIBUTING.md
git log --all --oneline -- data | head -3   # Expected: 只有 data/README.md 那一个 commit
python3 -m venv .venv && .venv/bin/pip install -q -e 'backend[dev]'
npm install && npm run build
cd backend && ../.venv/bin/pytest tests/ -q 2>&1 | tail -1   # Expected: 37 passed, 2 skipped
cd .. && (./start.sh > /tmp/final.log 2>&1 &) && sleep 4
curl -s localhost:8000/api/health    # Expected: {"ok":true}
curl -s localhost:8000/ | head -2    # Expected: index.html
pkill -f uvicorn
```

- [ ] **Step 5: 浏览器人工验收**

打开 `http://localhost:8000`(用上一步的 clone 或本仓库 `./start.sh`),核对:首页截图与 README 一致、进入地图、完成第 1 关、星星更新。确认无误后收尾。
