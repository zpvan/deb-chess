import os
from pathlib import Path
from typing import Optional, Union

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.core.session import BOT_STYLES, IllegalMove, LessonSession
from app.core.store import SessionStore
from app.db import ProgressDB
from app.engine.stockfish_bot import StockfishBot
from app.models import load_curriculum, public_step

BACKEND_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_DIR.parent
DEFAULT_CURRICULUM = BACKEND_DIR / 'data' / 'curriculum.json'
DEFAULT_DB = BACKEND_DIR / 'data' / 'progress.db'


class NewSession(BaseModel):
    level_id: str


class MoveIn(BaseModel):
    move: str


class ChoiceIn(BaseModel):
    index: int


class RestartIn(BaseModel):
    bot: Optional[str] = None


def create_app(curriculum_path: Union[str, Path] = DEFAULT_CURRICULUM,
               db_path: Optional[Union[str, Path]] = None,
               dist_dir: Optional[Union[str, Path]] = None) -> FastAPI:
    curriculum = load_curriculum(curriculum_path)
    db = ProgressDB(db_path or os.environ.get('DB_PATH', str(DEFAULT_DB)))
    stockfish = StockfishBot()
    store = SessionStore()
    app = FastAPI(title='deb-chess')

    def get_session(session_id: str) -> LessonSession:
        s = store.get(session_id)
        if s is None:
            raise HTTPException(404, '课程会话不存在或已过期,请重新开始本关')
        return s

    def maybe_record(s: LessonSession) -> None:
        if s.finished and not s.progress_recorded:
            db.complete_level(s.level.id, s.stars)
            s.progress_recorded = True

    @app.get('/api/health')
    def health():
        return {'ok': True}

    @app.get('/api/curriculum')
    def get_curriculum():
        return {
            'chapters': [
                {**ch.model_dump(mode='json', exclude={'levels'}),
                 'levels': [
                     {**lv.model_dump(mode='json', exclude={'steps'}),
                      'steps': [public_step(st) for st in lv.steps]}
                     for lv in ch.levels
                 ]}
                for ch in curriculum.chapters
            ],
            'total_levels': len(curriculum.flat_levels()),
            'total_puzzles': curriculum.total_puzzles,
            'stockfish_available': stockfish.available(),
            'bot_styles': list(BOT_STYLES),
        }

    @app.get('/api/progress')
    def get_progress():
        return db.get()

    @app.post('/api/sessions', status_code=201)
    def new_session(body: NewSession):
        try:
            s = LessonSession(curriculum, body.level_id, stockfish=stockfish)
        except KeyError:
            raise HTTPException(404, f'关卡不存在:{body.level_id}')
        store.put(s)
        return s.state()

    @app.get('/api/sessions/{sid}')
    def session_state(sid: str):
        return get_session(sid).state()

    @app.post('/api/sessions/{sid}/move')
    def move(sid: str, body: MoveIn):
        s = get_session(sid)
        try:
            state = s.submit_move(body.move)
        except IllegalMove as e:
            raise HTTPException(422, str(e))
        maybe_record(s)
        return state

    @app.post('/api/sessions/{sid}/choice')
    def choice(sid: str, body: ChoiceIn):
        s = get_session(sid)
        try:
            state = s.submit_choice(body.index)
        except IllegalMove as e:
            raise HTTPException(422, str(e))
        maybe_record(s)
        return state

    @app.post('/api/sessions/{sid}/next')
    def nxt(sid: str):
        s = get_session(sid)
        try:
            state = s.advance()
        except IllegalMove as e:
            raise HTTPException(422, str(e))
        maybe_record(s)
        return state

    @app.post('/api/sessions/{sid}/restart-play')
    def restart(sid: str, body: RestartIn):
        s = get_session(sid)
        try:
            return s.restart_play(bot_style=body.bot)
        except IllegalMove as e:
            raise HTTPException(422, str(e))

    dist = Path(dist_dir or os.environ.get('DIST_DIR', str(REPO_ROOT / 'dist')))
    if dist.is_dir():
        app.mount('/', StaticFiles(directory=dist, html=True), name='static')

    return app


app = create_app()
