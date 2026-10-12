import random

import pytest

from app.core.session import IllegalMove, LessonSession

ROOK_FEN = '4k3/8/8/8/8/8/8/R3K3 w - - 0 1'      # 白车 a1,可 a1a5
MATE_FEN = '6k1/5ppp/8/8/8/8/8/R5K1 w - - 0 1'  # a1a8 一步杀


def mk(factory, steps):
    return LessonSession(factory(steps), 't1', rng=random.Random(42))


def move_step(accepted='a1a5', fen=ROOK_FEN):
    return {'type': 'move', 'fen': fen, 'prompt': 'p', 'accepted': [accepted], 'successText': 'ok'}


def mate_step():
    return {'type': 'mate', 'fen': MATE_FEN, 'prompt': 'p', 'successText': 'ok'}


def test_jump_resets_target_step(curriculum_factory):
    s = mk(curriculum_factory, [move_step(), mate_step(), move_step()])
    s.submit_move('a1a4')  # 在第 0 步错一次
    st = s.jump_to(2)
    assert st['step_index'] == 2
    assert st['solved'] is False
    assert st['fen'] == ROOK_FEN  # 棋盘重置为目标步初始局面
    assert st['mistakes'] == 1    # 失误不清零
    assert st['last_result'] is None


def test_jump_out_of_range(curriculum_factory):
    s = mk(curriculum_factory, [move_step(), mate_step()])
    with pytest.raises(IllegalMove) as e:
        s.jump_to(-1)
    assert e.value.code == 'jump_range'
    with pytest.raises(IllegalMove) as e:
        s.jump_to(2)
    assert e.value.code == 'jump_range'


def test_solved_steps_kept_after_jump_back(curriculum_factory):
    s = mk(curriculum_factory, [move_step(), mate_step(), move_step()])
    s.submit_move('a1a5')          # 解出第 0 步
    assert s.state()['solved_steps'] == [0]
    s.jump_to(2)
    st = s.jump_to(0)              # 跳回已解出的第 0 步
    assert st['solved'] is False   # 显示为未解,可重做
    assert st['solved_steps'] == [0]  # 但"曾解出"记录保留


def test_jump_blocked_after_finished(curriculum_factory):
    s = mk(curriculum_factory, [mate_step()])
    s.submit_move('a1a8')
    st = s.advance()
    assert st['finished'] is True
    with pytest.raises(IllegalMove) as e:
        s.jump_to(0)
    assert e.value.code == 'already_finished'


def test_advance_skips_solved_and_stops_at_teach(curriculum_factory):
    steps = [move_step(),
             {'type': 'teach', 'title': 't', 'text': ['x']},
             mate_step()]
    s = mk(curriculum_factory, steps)
    s.submit_move('a1a5')   # 解出 0
    s.jump_to(2)
    s.submit_move('a1a8')   # 解出 2
    s.jump_to(0)
    s.submit_move('a1a5')   # 重做 0
    st = s.advance()
    assert st['step_index'] == 1  # teach 不被跳过
    st = s.advance()
    assert st['finished'] is True  # 已解出的 2 被跳过,直接通关
    assert st['stars'] == 3        # 全程零失误


def test_advance_at_end_jumps_to_first_unsolved(curriculum_factory):
    s = mk(curriculum_factory, [move_step(), mate_step()])
    s.jump_to(1)
    s.submit_move('a1a8')   # 只解出最后一步
    st = s.advance()
    assert st['finished'] is False
    assert st['step_index'] == 0   # 自动跳回第一道未解题
    assert st['solved'] is False
    s.submit_move('a1a5')
    st = s.advance()
    assert st['finished'] is True
    assert st['stars'] == 3
