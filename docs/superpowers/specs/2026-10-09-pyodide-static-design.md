# deb-chess Pyodide 静态版设计文档

日期:2026-10-09
状态:已批准

## 背景与目标

deb-credit(Rust+Leptos→WASM)托管在 GitHub Pages(zpvan.github.io/deb-credit)。
deb-chess 是后端权威架构,GitHub Pages 只能托管静态文件,不能直接照搬。
**目标:用 Pyodide 把 Python 后端核心跑在浏览器里,产出纯静态站点,托管到 GitHub Pages。**

## 已确认的决策

| 决策点 | 结论 |
|---|---|
| 托管路径 | Pyodide 静态版(Python→WASM 跑在浏览器) |
| 部署目标 | GitHub Pages(zpvan.github.io/deb-chess),GitHub Actions 自动部署 |

## 设计

### ① 核心思路

浏览器加载 Pyodide(CDN)→ 安装 python-chess + pydantic → 把现有后端核心代码
(`session.py`/`bot.py`/`models.py` + XP 逻辑)写入 Pyodide 文件系统并 import →
前端不再发 HTTP 请求,直接调 Python 函数。`main.py` 的 FastAPI 壳被替换,核心逻辑零改动。

### ② 新增组件

| 组件 | 职责 |
|---|---|
| `backend/app/static_facade.py`(新) | 纯 Python 门面:create_session/move/choice/next/restart/get_curriculum/get_progress 等,返回 JSON 字符串;模块级 SessionStore;进度存内存 dict。pytest 直接可测 |
| `src/lib/pyodide-api.ts`(新) | 加载 Pyodide → 安装依赖 → 写入 Python 源码 → 暴露与 api.ts 完全相同的函数签名 |
| `scripts/bundle_py.mjs`(新) | 构建时把 backend/app/**/*.py + data/curriculum.py 打包成 src/lib/pybundle.ts(生成物,gitignore) |
| `src/lib/backend.ts`(新) | 统一出口:VITE_STATIC=1 时用 pyodideApi,否则用 api;前端其余代码无感知 |

### ③ 差异与降级(静态版)

- **进度持久化**:localStorage(Python 算 XP,JS 存取;facade 的 get_progress_json/set_progress_json 钩子接线)
- **Stockfish 大师档**:静态版隐藏(stockfish_available=False);以后可加 stockfish.wasm
- **首次加载**:Pyodide ~13MB + 几秒启动,带进度的加载页(双语);之后全部离线可用
- **双语/主题/全部课程**:原样工作

### ④ 构建与部署

- `npm run build:static`:VITE_STATIC=1 vite build(本地可预览)
- `.github/workflows/pages.yml`(照 deb-credit 样式):push main → 构建静态版 → Pages 部署;仓库 Pages 源改为 GitHub Actions
- 本地/Docker/CI 现有流程不受影响;CI 增加 static 构建冒烟 job

### ⑤ 验证

- pytest:static_facade 走完整关卡流程
- 静态产物用 python3 -m http.server 起服务,Playwright 真实浏览器:加载 → 第 1 关走棋 → 通关 → 刷新进度仍在
- CI 绿

## 非目标(YAGNI)

- 静态版 v1 不含 Stockfish 大师档;
- 不做 Pyodide 自托管(先用 CDN);
- 不改服务器版任何行为。
