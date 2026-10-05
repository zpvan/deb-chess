"""用 python-chess 校验 curriculum.json 中的所有棋题。

用法:
  python scripts/validate_curriculum.py   # 校验 backend/data/curriculum.json
也被 tests/test_validate_curriculum.py 作为用例调用。
"""
import json
import sys
from pathlib import Path

import chess

DATA = Path(__file__).resolve().parents[1] / 'data' / 'curriculum.json'


def _legal(board: chess.Board) -> set[str]:
    s = {m.uci() for m in board.legal_moves}
    return s | {u[:4] for u in s}


def _push(board: chess.Board, uci: str) -> chess.Move:
    move = chess.Move.from_uci(uci)
    if move not in board.legal_moves and len(uci) == 5:
        move = chess.Move.from_uci(uci[:4])
    board.push(move)
    return move


def validate_all(chapters: list[dict]) -> list[str]:
    errors: list[str] = []
    for ch in chapters:
        for lv in ch['levels']:
            for i, st in enumerate(lv['steps']):
                where = f"{lv['id']}[{i}]({st['type']})"
                fen = st.get('fen')
                if fen is None:
                    continue
                try:
                    board = chess.Board(fen)
                except ValueError:
                    errors.append(f'{where}: FEN 无法解析')
                    continue
                if not board.is_valid():
                    errors.append(f'{where}: FEN 局面不合法')

                t = st['type']
                if t == 'move':
                    legal = _legal(board)
                    for a in st['accepted']:
                        if a not in legal:
                            errors.append(f'{where}: accepted 走法不合法: {a}')
                elif t == 'mate':
                    if not any(board.gives_check(m) and _mates(board, m) for m in board.legal_moves):
                        errors.append(f'{where}: 不存在一步杀')
                elif t == 'line':
                    ok = True
                    for j, u in enumerate(st['script']):
                        try:
                            if u not in _legal(board):
                                raise ValueError(u)
                            _push(board, u)
                        except ValueError:
                            errors.append(f'{where}: script[{j}] 走法不合法: {u}')
                            ok = False
                            break
                    if ok and st.get('endsWithMate', True) and not board.is_checkmate():
                        errors.append(f'{where}: script 走完未将杀(endsWithMate 默认为 true)')
                elif t == 'play':
                    if st['bot'] not in ('random', 'greedy', 'smart'):
                        errors.append(f'{where}: 未知 bot: {st["bot"]}')
                    if st['win'] not in ('mate', 'mateOrQueen'):
                        errors.append(f'{where}: 未知 win: {st["win"]}')
    return errors


def _mates(board: chess.Board, move: chess.Move) -> bool:
    board.push(move)
    mated = board.is_checkmate()
    board.pop()
    return mated


def main() -> int:
    chapters = json.loads(DATA.read_text(encoding='utf-8'))
    errors = validate_all(chapters)
    if errors:
        print(f'发现 {len(errors)} 个问题:')
        for e in errors:
            print(' -', e)
        return 1
    print('全部棋题校验通过 ✓')
    return 0


if __name__ == '__main__':
    sys.exit(main())
