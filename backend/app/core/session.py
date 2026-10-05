"""课程会话状态机。每个关卡一个 LessonSession,持有 python-chess Board,
覆盖 6 种步骤类型。逻辑平移自原前端 src/pages/Lesson.tsx。"""
import random
import uuid
from typing import Optional

import chess

from app.engine.bot import black_queen_gone, pick_bot_move
from app.engine.stockfish_bot import StockfishBot
from app.models import Curriculum, public_step

BOT_STYLES = ('random', 'greedy', 'smart', 'master')
PUZZLE_TYPES = ('mate', 'move', 'line')


class IllegalMove(ValueError):
    pass


def is_draw(board: chess.Board) -> bool:
    """对齐 chess.js 的 isDraw():逼和/子力不足/三次重复/五十回合。"""
    return (board.is_stalemate() or board.is_insufficient_material()
            or board.can_claim_threefold_repetition() or board.can_claim_fifty_moves())


def parse_move(board: chess.Board, uci: str) -> chess.Move:
    uci = uci.strip().lower()
    try:
        move = chess.Move.from_uci(uci)
    except ValueError:
        raise IllegalMove(f'走法格式不对:{uci}(应为如 e2e4 的格式)')
    if move in board.legal_moves:
        return move
    # 前端对非升变走法也可能附带 'q'(旧版 chess.js 行为),容忍之
    if len(uci) == 5:
        alt = chess.Move.from_uci(uci[:4])
        if alt in board.legal_moves:
            return alt
    raise IllegalMove('这步棋不符合规则哦!')


class LessonSession:
    def __init__(self, curriculum: Curriculum, level_id: str,
                 stockfish: Optional[StockfishBot] = None, rng: Optional[random.Random] = None):
        found = curriculum.find_level(level_id)
        if found is None:
            raise KeyError(f'未知关卡:{level_id}')
        self.chapter, self.level, self.level_index = found
        self.id = uuid.uuid4().hex
        self.rng = rng or random.Random()
        self.stockfish = stockfish
        self.idx = 0
        self.mistakes = 0
        self.finished = False
        self.stars = 0
        self.progress_recorded = False
        self._reset_step_state()

    @property
    def step(self):
        return self.level.steps[self.idx]

    def _reset_step_state(self) -> None:
        self.solved = False
        self.fast_mate = False
        self.line_pos = 0
        self.last_move: Optional[list[str]] = None
        self.play_status: Optional[str] = None
        self.my_moves = 0
        self.bot_style: Optional[str] = self.step.bot if self.step.type == 'play' else None
        self.success_text: Optional[str] = None
        self.end_text: Optional[str] = None
        self.last_result: Optional[str] = None
        self.reply: Optional[dict] = None
        self._display_fen: Optional[str] = None
        self.board: Optional[chess.Board] = (
            chess.Board(self.step.fen) if getattr(self.step, 'fen', None) else None)
        if self.step.type == 'play':
            self.play_status = 'playing'

    # ---------- 公开状态 ----------
    def state(self) -> dict:
        step = self.step
        interactive = ((step.type in PUZZLE_TYPES and not self.solved)
                       or (step.type == 'play' and self.play_status == 'playing'))
        check_square = None
        if self.board is not None and self.board.is_check():
            check_square = chess.square_name(self.board.king(self.board.turn))
        line_prompt = None
        if step.type == 'line':
            i = min(self.line_pos // 2, len(step.prompts) - 1)
            line_prompt = step.prompts[i]
        return {
            'session_id': self.id,
            'level_id': self.level.id,
            'level_title': self.level.title,
            'level_skill': self.level.skill,
            'chapter_title': self.chapter.title,
            'chapter_badge': self.chapter.badge,
            'chapter_color': self.chapter.color,
            'chapter_soft': self.chapter.soft,
            'step_index': self.idx,
            'step_count': len(self.level.steps),
            'step': public_step(step),
            # 有 reply 时展示用户走完的中间局面,前端延迟后再展示 reply.fen
            'fen': self._display_fen or (self.board.fen() if self.board else None),
            'legal_moves': [m.uci() for m in self.board.legal_moves]
                           if (interactive and self.board) else [],
            'check_square': check_square,
            'last_move': self.last_move,
            'solved': self.solved,
            'fast_mate': self.fast_mate,
            'line_prompt': line_prompt,
            'play_status': self.play_status,
            'my_moves': self.my_moves,
            'bot_style': self.bot_style,
            'mistakes': self.mistakes,
            'finished': self.finished,
            'stars': self.stars,
            'success_text': self.success_text,
            'end_text': self.end_text,
            'last_result': self.last_result,
            'reply': self.reply,
        }

    # ---------- 推进 ----------
    def advance(self) -> dict:
        if self.finished:
            return self.state()
        step = self.step
        if step.type in PUZZLE_TYPES + ('choice', 'play') and not self.solved:
            raise IllegalMove('先完成这一步再走哦!')
        if self.idx + 1 >= len(self.level.steps):
            self.stars = 3 if self.mistakes == 0 else 2 if self.mistakes <= 2 else 1
            self.finished = True
        else:
            self.idx += 1
            self._reset_step_state()
        return self.state()

    # ---------- 走子 ----------
    def submit_move(self, uci: str) -> dict:
        if self.finished or self.board is None:
            raise IllegalMove('当前步骤不能走子')
        if self.step.type == 'play':
            return self._play_move(uci)
        if self.step.type not in PUZZLE_TYPES or self.solved:
            raise IllegalMove('当前步骤不能走子')
        self.reply = None
        self._display_fen = None
        move = parse_move(self.board, uci)
        handler = {'mate': self._handle_mate, 'move': self._handle_move,
                   'line': self._handle_line}[self.step.type]
        handler(move)
        return self.state()

    def _wrong(self) -> None:
        self.mistakes += 1
        self.last_result = 'wrong'

    def _handle_mate(self, move: chess.Move) -> None:
        self.board.push(move)
        if self.board.is_checkmate():
            self.solved = True
            self.last_move = [move.uci()[:2], move.uci()[2:4]]
            self.last_result = 'correct'
            self.success_text = self.step.successText
        else:
            self.board.pop()
            self._wrong()

    def _handle_move(self, move: chess.Move) -> None:
        bare = move.uci()[:4]
        if bare in self.step.accepted or move.uci() in self.step.accepted:
            self.board.push(move)
            self.solved = True
            self.last_move = [bare[:2], bare[2:]]
            self.last_result = 'correct'
            self.success_text = self.step.successText
        else:
            self._wrong()

    def _handle_line(self, move: chess.Move) -> None:
        step = self.step
        script = step.script
        bare = move.uci()[:4]
        self.board.push(move)
        mated = self.board.is_checkmate()
        hit = script[self.line_pos] in (bare, move.uci())
        if not (mated or hit):
            self.board.pop()
            self._wrong()
            return
        self.last_move = [bare[:2], bare[2:]]
        is_last = self.line_pos == len(script) - 1
        # 任何时候直接将死都算成功(更快杀法同样算挑战成功)
        if mated or is_last or self.line_pos + 1 >= len(script):
            self.fast_mate = mated and not is_last
            self.solved = True
            self.last_result = 'correct'
            self.success_text = ('更快将死!比参考答案还少用了步数,太厉害了!'
                                 if self.fast_mate else step.successText)
            return
        # 自动走出对手的应对
        user_fen = self.board.fen()
        self.line_pos += 1
        reply_uci = script[self.line_pos]
        reply_move = parse_move(self.board, reply_uci)
        self.board.push(reply_move)
        self.line_pos += 1
        self.last_result = 'correct'
        self._display_fen = user_fen
        self.reply = {'move': [reply_move.uci()[:2], reply_move.uci()[2:4]],
                      'fen': self.board.fen()}

    # ---------- 选择题 ----------
    def submit_choice(self, index: int) -> dict:
        if self.step.type != 'choice' or self.solved:
            raise IllegalMove('当前步骤不能作答')
        if index == self.step.answer:
            self.solved = True
            self.last_result = 'correct'
            self.success_text = self.step.explain
        else:
            self._wrong()
        return self.state()

    # ---------- 实战对弈 ----------
    def _pick_bot(self) -> Optional[chess.Move]:
        if self.bot_style == 'master':
            if self.stockfish is not None:
                m = self.stockfish.pick(self.board)
                if m is not None:
                    return m
            return pick_bot_move(self.board, 'smart', self.rng)  # 无 stockfish 时兜底
        return pick_bot_move(self.board, self.bot_style or 'random', self.rng)

    def _play_move(self, uci: str) -> dict:
        step = self.step
        if self.play_status != 'playing':
            raise IllegalMove('本局已结束,请点击"再来一盘"')
        self.reply = None
        self._display_fen = None
        move = parse_move(self.board, uci)
        self.board.push(move)
        self.my_moves += 1
        self.last_move = [move.uci()[:2], move.uci()[2:4]]

        if self.board.is_checkmate():
            self.play_status = 'won'
            self.solved = True
            self.success_text = f'{step.successText}(用了 {self.my_moves} 步)'
            self.last_result = 'correct'
            return self.state()
        if step.win == 'mateOrQueen' and black_queen_gone(self.board):
            self.play_status = 'won'
            self.solved = True
            self.success_text = f'{step.successText}(用了 {self.my_moves} 步)'
            self.last_result = 'correct'
            return self.state()
        if is_draw(self.board):
            self.play_status = 'draw'
            self.end_text = step.drawText
            return self.state()

        # 电脑应对(同步返回,前端延迟动画展示)
        user_fen = self.board.fen()
        bm = self._pick_bot()
        if bm is not None:
            self.board.push(bm)
            self._display_fen = user_fen
            self.reply = {'move': [bm.uci()[:2], bm.uci()[2:4]], 'fen': self.board.fen()}
            if self.board.is_checkmate():
                self.play_status = 'lost'
                self.end_text = step.failText
            elif is_draw(self.board):
                self.play_status = 'draw'
                self.end_text = step.drawText
        return self.state()

    def restart_play(self, bot_style: Optional[str] = None) -> dict:
        step = self.step
        if step.type != 'play':
            raise IllegalMove('当前不是对弈步骤')
        if bot_style is not None:
            if bot_style not in BOT_STYLES:
                raise IllegalMove(f'未知对手档位:{bot_style}')
            self.bot_style = bot_style
        # 尚未走子的换档/重开不算失误;对局中途重开算一次小失误(影响星级)
        fresh = self.play_status == 'playing' and self.my_moves == 0
        if not fresh:
            self.mistakes += 1
        self.board = chess.Board(step.fen)
        self.last_move = None
        self.reply = None
        self._display_fen = None
        self.play_status = 'playing'
        self.my_moves = 0
        self.solved = False
        self.success_text = None
        self.end_text = None
        self.last_result = None
        return self.state()
