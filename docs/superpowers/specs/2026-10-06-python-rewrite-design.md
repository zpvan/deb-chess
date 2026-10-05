# deb-chess Python 改写设计文档

日期:2026-10-06
状态:已批准

## 背景与目标

deb-chess 是一个面向儿童的国际象棋教学 Web 应用,课程内容源自《鲍比·菲舍尔教你下国际象棋》。当前实现为 React + TypeScript + Vite 纯前端 SPA,棋局规则用 chess.js,进度存 localStorage。

**目标:将项目改写为 Python 语言项目**,棋局逻辑、课程数据、进度存储全部迁移到 Python 后端,前端收缩为纯展示层。

## 关键决策(调研结论)

### 棋库选型

对比 JS / Python / Rust / C 四个生态后(详见会话调研记录):

- 引擎层面:Stockfish(C++ 编写)为世界最强,且通过 UCI 协议与语言无关,任何语言均可调用。
- 规则库层面:**python-chess** 功能最全(FEN/SAN/PGN/attackers 检测/UCI 引擎协议/开局库/残局库),是教学类项目事实标准。性能虽不及 Rust(shakmaty/cozy-chess),但对一次只处理一个局面的教学应用完全过剩。

**结论:python-chess 做规则库 + Stockfish(UCI)做大师档 bot。**

### 已确认的决策

| 决策点 | 结论 |
|---|---|
| 项目形态 | Python Web 应用(FastAPI 后端 + 保留 React 前端) |
| 棋局状态 | 后端权威:python-chess 维护局面、校验走法、判定将杀 |
| 后端框架 | FastAPI |
| 进度存储 | 后端 SQLite(单用户默认档案,无注册登录) |
| Bot | 手写三档(random/greedy/smart)平移 + 新增 Stockfish 大师档 |
| 课程数据 | JSON 数据文件,后端启动时加载 |
| 部署 | 本地单进程(uvicorn + 静态托管)与 Docker 两者都要 |

## 总体架构

```
浏览器 (React 前端,薄客户端)
   │  HTTP/JSON
   ▼
FastAPI 后端 ── python-chess (局面/规则权威)
   ├── 课程服务:加载 curriculum.json
   ├── 会话管理:每节课一个对局会话 (内存, session id)
   ├── Bot 引擎:手写三档 (random/greedy/smart) + Stockfish 大师档 (UCI)
   └── 进度服务:SQLite (星级、XP、段位)
```

**前端职责收缩为纯展示层**:渲染棋盘(现有 `ChessBoard.tsx` 绘制部分保留)、采集用户走法、播放音效/动画。`chess.js`、`src/lib/bot.ts`、`src/data/curriculum.ts`、`src/state/progress.tsx`(localStorage 版)全部删除,由后端 API 替代。

## API 设计

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/curriculum` | 章节/关卡树(含 teach 内容、prompt,**不含 accepted 答案**) |
| POST | `/api/sessions` | `{level_id}` → 创建会话,返回首步状态 + FEN |
| POST | `/api/sessions/{id}/move` | `{move: "e2e4"}` → 后端校验,返回:是否正确、新 FEN、对手(bot/剧本)回应、是否进下一步、星级 |
| POST | `/api/sessions/{id}/hint` | 返回当前步骤提示 |
| GET | `/api/progress` | 总 XP、各关星级、当前段位 |
| POST | `/api/progress/complete` | `{level_id, stars}` 通关上报(沿用现有 XP 规则:首通 60 + stars×20,刷新纪录补差) |

- 走法统一用 UCI 格式(`e2e4`)传输,前端从棋盘坐标直接拼出,天然无歧义。
- API 下发课程时剥离 `accepted`/`script` 等答案字段,答案只留在后端内存。

## 会话模型

每个关卡步骤类型(teach/mate/move/line/choice/play)在后端对应一个状态机:`LessonSession` 持有 `python-chess.Board`、当前步骤索引、line 步骤的剧本进度。

- **手写 bot**:平移 `src/lib/bot.ts` 的 random/greedy/smart 三档。smart 档的 attackers 攻防检测用 `board.attackers()` 实现,行为与原版一致(吃子加分、将军加分、送子扣分、前 30% 随机)。
- **master 档**:Stockfish UCI,限制 depth/elo。启动时探测 Stockfish 是否可用,不可用时 `/api/curriculum` 中该档位标记为不可用,前端隐藏。

## 项目结构

```
deb-chess/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI 入口、静态文件托管
│   │   ├── api/                 # 路由: curriculum / sessions / progress
│   │   ├── core/
│   │   │   ├── session.py       # LessonSession 状态机(6 种步骤类型)
│   │   │   └── store.py         # 会话存储(内存 dict + TTL)
│   │   ├── engine/
│   │   │   ├── bot.py           # random/greedy/smart 三档(平移自 bot.ts)
│   │   │   └── stockfish_bot.py # master 档, UCI 协议
│   │   ├── models/              # Pydantic 模型(请求/响应/课程结构)
│   │   └── db.py                # SQLite: progress 表(level_id, stars, xp)
│   ├── data/
│   │   └── curriculum.json      # 课程数据(从 curriculum.ts 转换生成)
│   ├── scripts/
│   │   ├── convert_curriculum.mjs    # 一次性转换脚本 (Node)
│   │   └── validate_curriculum.py    # python-chess 逐题校验所有 FEN/accepted 走法
│   ├── tests/                   # pytest
│   └── pyproject.toml
├── src/                         # 前端: 删除 chess.js/bot/curriculum 逻辑, 改为 API client
├── data/Bobby-Fischer-Teaches-Chess/   # 图书图片资源(不动)
├── Dockerfile
└── docker-compose.yml
```

## 课程数据迁移

- `curriculum.ts`(约 1100 行,纯结构化字面量)用一次性 Node 脚本 `convert_curriculum.mjs` 导出为 `curriculum.json`。
- `validate_curriculum.py`:用 python-chess 校验每个 FEN 合法、每个 accepted 走法合法、line 剧本可完整走通——延续原项目"所有棋题经引擎校验"的质量保证,并纳入测试。

## 错误处理

| 场景 | 处理 |
|---|---|
| 非法走法(格式错/不合规则) | 422,返回友好提示文案,前端晃动棋子动画 |
| session 不存在/过期 | 404,前端自动重建会话并重放到当前步骤 |
| Stockfish 未安装 | 启动时探测,master 档标记不可用,前端隐藏该选项 |
| 前端网络错误 | toast 提示 + 重试按钮 |

## 测试方案(pytest)

- **单元**:bot 三档逻辑(贪心会吃子、smart 会避免送子)、XP 计算规则、会话状态机各步骤推进。
- **数据**:`validate_curriculum.py` 作为测试用例跑全量课程校验。
- **集成**:FastAPI TestClient 走通「创建会话 → 走对 → 走错 → 提示 → 通关 → 进度写入 SQLite」全流程。
- 前端不新增测试框架(与现状一致),手动验收。

## 部署

- **本地**:`npm run build` → FastAPI 挂载 `dist/` 静态目录,`uvicorn` 单进程,一个端口访问整个应用;提供 `./start.sh` 一键脚本。
- **Docker**:多阶段构建(node 构建前端 → python slim 镜像 + `apt install stockfish` → 拷入后端与静态产物),`docker-compose.yml` 单服务,可选使用。

## 仓库处置

改写完成后:删除 `package.json` 中的 `chess.js` 依赖,删除 `src/lib/bot.ts`、`src/data/curriculum.ts`、`src/state/progress.tsx`。Node 只承担前端构建,前端其余代码(页面、棋盘渲染、音效、动画)保留并改造为调 API。

## 非目标(YAGNI)

- 不做用户注册/登录(单用户默认档案)。
- 不做多人对弈/联网对战。
- 不引入前端测试框架。
- 不变更图书图片资源与课程教学内容本身。
