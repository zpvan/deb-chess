"""电脑对手:random 随便走 / greedy 贪吃+爱将军 / smart 还会避免送子。
逻辑平移自原前端 src/lib/bot.ts,行为保持一致。"""
import random

import chess

VAL = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0}


def score_moves(board: chess.Board, style: str, rng: random.Random) -> list[tuple[float, chess.Move]]:
    """给所有合法走法打分,按分数降序返回 (score, move) 列表。"""
    scored: list[tuple[float, chess.Move]] = []
    for m in board.legal_moves:
        s = rng.random() * 2
        captured = board.piece_type_at(m.to_square) if board.is_capture(m) else None
        board.push(m)
        if board.is_checkmate():
            s += 10000
        if captured is not None:
            s += VAL[captured] * 20
        if board.is_check():
            s += 8
        if style == 'smart':
            # 走完若会被对方白白吃掉,扣分(对方攻击者多于我方保护者且棋子比兵贵)
            enemy = board.turn
            piece = board.piece_type_at(m.to_square)  # push 之后,棋子在落点格
            attackers = len(board.attackers(enemy, m.to_square))
            defenders = len(board.attackers(not enemy, m.to_square))
            if attackers > defenders and VAL[piece] > 1:
                s -= VAL[piece] * 15
        board.pop()
        scored.append((s, m))
    scored.sort(key=lambda t: t[0], reverse=True)
    return scored


def pick_bot_move(board: chess.Board, style: str, rng: random.Random) -> chess.Move | None:
    moves = list(board.legal_moves)
    if not moves:
        return None
    if style == 'random':
        return rng.choice(moves)
    scored = score_moves(board, style, rng)
    # 在前 30% 里随机,保留一点变化
    top_n = max(1, int(len(scored) * 0.3))
    return rng.choice(scored[:top_n])[1]


def black_queen_gone(board: chess.Board) -> bool:
    """判断黑方是否还有皇后(用于"吃掉皇后也算赢")。"""
    return not any(
        p.piece_type == chess.QUEEN and p.color == chess.BLACK
        for p in board.piece_map().values()
    )
