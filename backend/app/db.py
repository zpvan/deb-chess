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
