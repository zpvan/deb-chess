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
