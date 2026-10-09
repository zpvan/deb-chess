import random

import pytest

from app.core.session import IllegalMove, LessonSession

ROOK_FEN = '4k3/8/8/8/8/8/8/R3K3 w - - 0 1'      # 白车 a1,可 a1a5
MATE_FEN = '6k1/5ppp/8/8/8/8/8/R5K1 w - - 0 1'  # a1a8 一步杀
PAWN_FEN = '4k3/8/8/8/8/8/4P3/4K3 w - - 0 1'   # 白兵 e2


def mk(factory, steps):
    return LessonSession(factory(steps), 't1', rng=random.Random(42))


def test_teach_then_advance(curriculum_factory):
    s = mk(curriculum_factory, [
        {'type': 'teach', 'title': 't', 'text': ['x']},
        {'type': 'teach', 'title': 't2', 'text': ['y']},
    ])
    assert s.state()['step_index'] == 0
    st = s.advance()
    assert st['step_index'] == 1
    st = s.advance()  # 最后一步再推进 → 通关
    assert st['finished'] is True
    assert st['stars'] == 3  # 零失误


def test_advance_blocked_on_unsolved_puzzle(curriculum_factory):
    s = mk(curriculum_factory, [
        {'type': 'move', 'fen': ROOK_FEN, 'prompt': 'p', 'accepted': ['a1a5'], 'successText': 'ok'},
    ])
    with pytest.raises(IllegalMove):
        s.advance()


def test_mate_step_right_and_wrong(curriculum_factory):
    s = mk(curriculum_factory, [
        {'type': 'mate', 'fen': MATE_FEN, 'prompt': 'p', 'successText': '将杀!'},
    ])
    st = s.submit_move('a1a2')  # 合法但不是将杀
    assert st['last_result'] == 'wrong'
    assert st['mistakes'] == 1
    assert st['fen'] == MATE_FEN  # 局面回滚
    st = s.submit_move('a1a8')
    assert st['last_result'] == 'correct'
    assert st['solved'] is True
    assert st['success_text'] == '将杀!'
    assert st['last_move'] == ['a1', 'a8']


def test_move_step_accepted(curriculum_factory):
    s = mk(curriculum_factory, [
        {'type': 'move', 'fen': ROOK_FEN, 'prompt': 'p', 'accepted': ['a1a5'], 'successText': 'ok'},
    ])
    st = s.submit_move('a1a4')  # 合法但非答案
    assert st['last_result'] == 'wrong'
    st = s.submit_move('a1a5')
    assert st['solved'] is True


def test_illegal_move_raises(curriculum_factory):
    s = mk(curriculum_factory, [
        {'type': 'move', 'fen': ROOK_FEN, 'prompt': 'p', 'accepted': ['a1a5'], 'successText': 'ok'},
    ])
    with pytest.raises(IllegalMove):
        s.submit_move('a1b2')  # 车不能斜走
    with pytest.raises(IllegalMove):
        s.submit_move('xxxx')  # 格式错误


def test_extra_promotion_char_tolerated(curriculum_factory):
    # 旧版前端对非升变走法也附带 'q'(chess.js 会忽略),后端须容忍
    s = mk(curriculum_factory, [
        {'type': 'move', 'fen': ROOK_FEN, 'prompt': 'p', 'accepted': ['a1a5'], 'successText': 'ok'},
    ])
    st = s.submit_move('a1a5q')
    assert st['solved'] is True


def test_line_step_script_with_reply(curriculum_factory):
    s = mk(curriculum_factory, [
        {'type': 'line', 'fen': PAWN_FEN, 'script': ['e2e4', 'e8e7', 'e4e5'],
         'endsWithMate': False, 'prompts': ['冲兵!', '再冲!'], 'successText': 'ok'},
    ])
    st = s.submit_move('e2e3')  # 不按剧本
    assert st['last_result'] == 'wrong'
    assert st['line_prompt'] == '冲兵!'
    st = s.submit_move('e2e4')
    assert st['last_result'] == 'correct'
    assert st['solved'] is False
    assert st['reply'] is not None and st['reply']['move'] == ['e8', 'e7']  # 对手自动应对
    assert st['line_prompt'] == '再冲!'
    st = s.submit_move('e4e5')  # 最后一步
    assert st['solved'] is True


def test_line_step_fast_mate(curriculum_factory):
    # 剧本更长,但直接一步将死 → 算成功且 fast_mate
    s = mk(curriculum_factory, [
        {'type': 'line', 'fen': MATE_FEN, 'script': ['a1a7', 'g7g6', 'a7a8'],
         'prompts': ['p1', 'p2'], 'successText': 'ok'},
    ])
    st = s.submit_move('a1a8')
    assert st['solved'] is True
    assert st['fast_mate'] is True
    assert 'faster mate' in st['success_text'].lower()


def test_choice_step(curriculum_factory):
    s = mk(curriculum_factory, [
        {'type': 'choice', 'fen': ROOK_FEN, 'sideLabel': '白方', 'question': 'q?',
         'options': ['甲', '乙'], 'answer': 1, 'explain': '因为乙对'},
    ])
    st = s.submit_choice(0)
    assert st['last_result'] == 'wrong'
    assert st['mistakes'] == 1
    st = s.submit_choice(1)
    assert st['solved'] is True
    assert st['success_text'] == '因为乙对'


def test_stars_by_mistakes(curriculum_factory):
    steps = [
        {'type': 'move', 'fen': ROOK_FEN, 'prompt': 'p', 'accepted': ['a1a5'], 'successText': 'ok'},
        {'type': 'teach', 'title': 't', 'text': ['x']},
    ]
    s = mk(curriculum_factory, steps)
    s.submit_move('a1a4')  # 错 1 次
    s.submit_move('a1a5')
    s.advance()
    st = s.advance()
    assert st['finished'] is True
    assert st['stars'] == 2  # 1-2 次失误 → 2 星


def test_state_has_no_answers(curriculum_factory):
    s = mk(curriculum_factory, [
        {'type': 'move', 'fen': ROOK_FEN, 'prompt': 'p', 'accepted': ['a1a5'], 'successText': 'ok'},
    ])
    assert 'accepted' not in s.state()['step']
