import random

import chess

from app.engine.bot import black_queen_gone, pick_bot_move, score_moves

# 白车 a1、白王 e1;黑后 a8、黑王 e8。白方可 Rxa8+ 白吃皇后。
GREEDY_FEN = 'q3k3/8/8/8/8/8/8/R3K3 w - - 0 1'
# 底线杀:Ra1a8 一步将杀。
MATE_FEN = '6k1/5ppp/8/8/8/8/8/R5K1 w - - 0 1'
# 白后 d1 走到 d5 会被 e6 黑兵白吃(无保护);d2 是安全着法。
SMART_FEN = '4k3/8/4p3/8/8/8/8/3QK3 w - - 0 1'


def test_random_returns_legal_move():
    board = chess.Board()
    rng = random.Random(42)
    assert pick_bot_move(board, 'random', rng) in list(board.legal_moves)


def test_no_moves_returns_none():
    board = chess.Board('7k/5Q2/6K1/8/8/8/8/8 b - - 0 1')  # 黑方逼和
    assert pick_bot_move(board, 'greedy', random.Random(1)) is None


def test_greedy_scores_queen_capture_highest():
    board = chess.Board(GREEDY_FEN)
    scored = score_moves(board, 'greedy', random.Random(42))
    assert scored[0][1].uci() == 'a1a8'  # 吃后 180 分,远超噪声 ±2


def test_greedy_prefers_mate():
    board = chess.Board(MATE_FEN)
    scored = score_moves(board, 'greedy', random.Random(42))
    assert scored[0][1].uci() == 'a1a8'  # +10000 将杀分


def test_smart_avoids_hanging_queen():
    board = chess.Board(SMART_FEN)
    scored = dict((m.uci(), s) for s, m in score_moves(board, 'smart', random.Random(42)))
    assert scored['d1d5'] < scored['d1d2']  # 送后 -135,噪声 ±2 无法翻盘


def test_pick_is_deterministic_with_seed():
    board = chess.Board(GREEDY_FEN)
    a = pick_bot_move(board, 'greedy', random.Random(7))
    b = pick_bot_move(board, 'greedy', random.Random(7))
    assert a == b


def test_black_queen_gone():
    assert not black_queen_gone(chess.Board(GREEDY_FEN))
    assert black_queen_gone(chess.Board(MATE_FEN))
