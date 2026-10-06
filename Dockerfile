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
COPY backend/data/curriculum.py ./data/curriculum.py
COPY --from=frontend /app/dist ./dist
ENV DIST_DIR=/app/dist DB_PATH=/app/db/progress.db
EXPOSE 8642
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8642"]
