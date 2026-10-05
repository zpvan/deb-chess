"""内存会话存储,带 TTL(默认 2 小时)。本地单用户应用足够。"""
import time
from typing import Optional

from app.core.session import LessonSession


class SessionStore:
    def __init__(self, ttl_seconds: int = 7200):
        self._sessions: dict[str, tuple[float, LessonSession]] = {}
        self._ttl = ttl_seconds

    def put(self, session: LessonSession) -> None:
        self._purge()
        self._sessions[session.id] = (time.time(), session)

    def get(self, session_id: str) -> Optional[LessonSession]:
        self._purge()
        item = self._sessions.get(session_id)
        if item is None:
            return None
        self._sessions[session_id] = (time.time(), item[1])  # 续期
        return item[1]

    def _purge(self) -> None:
        now = time.time()
        for k in [k for k, (t, _) in self._sessions.items() if now - t > self._ttl]:
            del self._sessions[k]
