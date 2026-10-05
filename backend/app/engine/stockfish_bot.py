"""Stockfish 大师档:UCI 协议调用本机 stockfish 二进制。
未安装时优雅降级:available() 返回 False,pick() 返回 None。"""
import os
import shutil
from typing import Optional

import chess
import chess.engine


class StockfishBot:
    def __init__(self, path: Optional[str] = None, skill: int = 10, time_limit: float = 0.2):
        self._path = path or os.environ.get('STOCKFISH_PATH', 'stockfish')
        self._skill = skill
        self._limit = chess.engine.Limit(time=time_limit)
        self._engine: Optional[chess.engine.SimpleEngine] = None

    def available(self) -> bool:
        if self._engine is not None:
            return True
        if shutil.which(self._path) is None and not os.path.exists(self._path):
            return False
        try:
            self._engine = chess.engine.SimpleEngine.popen_uci(self._path)
            self._engine.configure({'Skill Level': self._skill})
            return True
        except Exception:
            self._engine = None
            return False

    def pick(self, board: chess.Board) -> Optional[chess.Move]:
        if not self.available():
            return None
        try:
            return self._engine.play(board, self._limit).move
        except Exception:
            return None

    def close(self) -> None:
        if self._engine is not None:
            self._engine.quit()
            self._engine = None
