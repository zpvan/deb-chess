"""静态版(Pyodide)门面:与 FastAPI 路由对应的纯函数,全部返回 JSON 字符串。

模块级状态:课程(惰性加载)、SessionStore、进度(内存 dict)。
JS 侧通过 set_progress_json/get_progress_json 对接 localStorage 持久化。
"""
import json

from app.core.session import ERRORS, IllegalMove, LessonSession
from app.core.store import SessionStore
from app.progress_rules import rank_for, xp_gain
from app.models import load_curriculum, loc_text, public_step

_curriculum = None
_store = None
_progress = {'levels': {}, 'xp': 0}


def init() -> None:
    """加载课程数据(幂等)。所有公开函数内部会自动调用。"""
    global _curriculum, _store
    if _curriculum is None:
        _curriculum = load_curriculum()
    if _store is None:
        _store = SessionStore()


def reset() -> None:
    """测试用:清空全部状态。"""
    global _curriculum, _store, _progress
    _curriculum = None
    _store = None
    _progress = {'levels': {}, 'xp': 0}


# ---------- 进度持久化(JS 对接 localStorage) ----------

def set_progress_json(raw: str) -> None:
    global _progress
    try:
        data = json.loads(raw)
        _progress = {'levels': dict(data.get('levels', {})), 'xp': int(data.get('xp', 0))}
    except (ValueError, TypeError):
        pass


def get_progress_json() -> str:
    return json.dumps(_progress, ensure_ascii=False)


def _ok(data) -> str:
    return json.dumps({'ok': True, 'data': data}, ensure_ascii=False)


def _err(status: int, detail) -> str:
    return json.dumps({'ok': False, 'status': status, 'detail': detail}, ensure_ascii=False)


def _get_session(sid: str):
    return _store.get(sid)


def _maybe_record(s: LessonSession) -> None:
    if s.finished and not s.progress_recorded:
        prev = _progress['levels'].get(s.level.id, 0)
        best, gained = xp_gain(prev, s.stars)
        _progress['levels'][s.level.id] = best
        _progress['xp'] += gained
        s.progress_recorded = True


# ---------- 公开 API ----------

def get_curriculum(lang: str = 'en') -> str:
    init()
    chapters = []
    for ch in _curriculum.chapters:
        levels = [{
            'id': lv.id,
            'title': loc_text(lv.title, lang),
            'goal': loc_text(lv.goal, lang),
            'skill': loc_text(lv.skill, lang),
            'steps': [public_step(st, lang) for st in lv.steps],
        } for lv in ch.levels]
        chapters.append({
            'id': ch.id,
            'badge': loc_text(ch.badge, lang),
            'title': loc_text(ch.title, lang),
            'intro': loc_text(ch.intro, lang),
            'color': ch.color,
            'soft': ch.soft,
            'levels': levels,
        })
    return _ok({
        'chapters': chapters,
        'total_levels': len(_curriculum.flat_levels()),
        'total_puzzles': _curriculum.total_puzzles,
        'stockfish_available': False,
        'bot_styles': ['random', 'greedy', 'smart', 'master'],
    })


def meta() -> str:
    init()
    return _ok({'stockfish_available': False,
                'bot_styles': ['random', 'greedy', 'smart', 'master']})


def get_progress(lang: str = 'en') -> str:
    init()
    levels = _progress['levels']
    return _ok({
        'levels': levels,
        'xp': _progress['xp'],
        'total_stars': sum(levels.values()),
        **rank_for(_progress['xp'], lang),
    })


def create_session(level_id: str, lang: str = 'en') -> str:
    init()
    try:
        s = LessonSession(_curriculum, level_id, lang=lang)
    except KeyError:
        return _err(404, f'level not found: {level_id}')
    _store.put(s)
    return _ok(s.state())


def get_session(sid: str) -> str:
    init()
    s = _get_session(sid)
    if s is None:
        return _err(404, 'session not found or expired')
    return _ok(s.state())


def _op(sid: str, fn) -> str:
    init()
    s = _get_session(sid)
    if s is None:
        return _err(404, 'session not found or expired')
    try:
        state = fn(s)
    except IllegalMove as e:
        msg = ERRORS[e.code]
        return _err(422, {'code': e.code, 'zh': msg['zh'], 'en': msg['en']})
    _maybe_record(s)
    return _ok(state)


def session_move(sid: str, uci: str) -> str:
    return _op(sid, lambda s: s.submit_move(uci))


def session_choice(sid: str, index: int) -> str:
    return _op(sid, lambda s: s.submit_choice(index))


def session_next(sid: str) -> str:
    return _op(sid, lambda s: s.advance())


def restart_play(sid: str, bot: str | None = None) -> str:
    return _op(sid, lambda s: s.restart_play(bot_style=bot))
