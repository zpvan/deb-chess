import shutil

import chess
import pytest

from app.engine.stockfish_bot import StockfishBot

pytestmark = pytest.mark.skipif(shutil.which('stockfish') is None, reason='stockfish 未安装')


def test_available_and_pick():
    bot = StockfishBot()
    assert bot.available()
    board = chess.Board('6k1/5ppp/8/8/8/8/8/R5K1 w - - 0 1')
    move = bot.pick(board)
    assert move is not None and move in list(board.legal_moves)
    bot.close()


def test_bad_path_unavailable():
    bot = StockfishBot(path='/nonexistent/stockfish')
    assert not bot.available()
    assert bot.pick(chess.Board()) is None
