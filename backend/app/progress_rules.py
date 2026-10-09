"""进度规则(纯 Python,无依赖):
- XP:首通 60 + stars*20;刷新纪录补差 (新 best - 旧 best)*20;持平或更差不加。
- 星级只升不降。
- 段位双语。

被 db.py(SQLite 持久化,服务器版)与 static_facade.py(Pyodide 静态版)共用。"""

RANKS = [
    (0, '小士兵', 'Pawn Rookie', '♟'),
    (100, '小骑士', 'Knight Rookie', '♞'),
    (250, '小主教', 'Bishop Rookie', '♝'),
    (450, '小城堡', 'Rook Rookie', '♜'),
    (700, '小皇后', 'Queen Rookie', '♛'),
    (1000, '小棋王', 'King Rookie', '♚'),
]


def rank_for(xp: int, lang: str = 'en') -> dict:
    """按 XP 计算段位。rank_name 按 lang 返回中/英文。"""
    rank = next((r for r in reversed(RANKS) if xp >= r[0]), RANKS[0])
    return {'rank_name': rank[2] if lang == 'en' else rank[1], 'rank_icon': rank[3]}


def xp_gain(prev_stars: int, stars: int) -> tuple[int, int]:
    """返回 (新的最佳星级, 本次获得的 XP)。"""
    best = max(prev_stars, stars)
    gained = 60 + stars * 20 if prev_stars == 0 else max(0, (best - prev_stars) * 20)
    return best, gained
