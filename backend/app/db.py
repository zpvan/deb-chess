"""进度存储:SQLite。规则平移自原前端 src/state/progress.tsx:
- 首通:xp += 60 + stars*20;刷新纪录:xp += (新 best - 旧 best)*20;持平或更差:不加。
- 星级只升不降。"""
import sqlite3
from pathlib import Path
from typing import Union

from app.progress_rules import rank_for, xp_gain  # noqa: F401(供 static_facade 等复用)


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

    def get(self, lang: str = 'en') -> dict:
        levels = {r[0]: r[1] for r in self._conn.execute('SELECT level_id, stars FROM levels')}
        row = self._conn.execute("SELECT value FROM meta WHERE key='xp'").fetchone()
        xp = row[0] if row else 0
        return {
            'levels': levels,
            'xp': xp,
            'total_stars': sum(levels.values()),
            **rank_for(xp, lang),
        }

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

    def close(self) -> None:
        self._conn.close()
