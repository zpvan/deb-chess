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
