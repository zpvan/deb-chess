import random

import pytest

from app.core.session import IllegalMove, LessonSession

MATE_FEN = '6k1/5ppp/8/8/8/8/8/R5K1 w - - 0 1'       # a1a8 一步杀
QUEEN_FEN = '4k3/8/8/8/8/8/q7/R3K3 w - - 0 1'       # a1a2 吃掉黑后
ROOK_ENDGAME = '6k1/8/8/8/8/8/8/R5K1 w - - 0 1'     # 车王对单王

PLAY = {'type': 'play', 'fen': MATE_FEN, 'bot': 'random', 'win': 'mate',
        'prompt': 'p', 'successText': '赢了', 'failText': '输了', 'drawText': '和了'}


def mk(factory, step):
    return LessonSession(factory([step]), 't1', rng=random.Random(42))


def test_play_win_by_mate(curriculum_factory):
    s = mk(curriculum_factory, PLAY)
    st = s.submit_move('a1a8')
    assert st['play_status'] == 'won'
    assert st['solved'] is True
    assert '赢了' in st['success_text']
    assert st['my_moves'] == 1


def test_play_win_by_queen_capture(curriculum_factory):
    s = mk(curriculum_factory, {**PLAY, 'fen': QUEEN_FEN, 'win': 'mateOrQueen'})
    st = s.submit_move('a1a2')
    assert st['play_status'] == 'won'


def test_play_bot_replies(curriculum_factory):
    s = mk(curriculum_factory, {**PLAY, 'fen': ROOK_ENDGAME, 'bot': 'smart'})
    st = s.submit_move('a1a2')  # 未分胜负 → bot 回应
    assert st['play_status'] == 'playing'
    assert st['my_moves'] == 1
    assert st['reply'] is not None
    assert st['reply']['fen'] != st['fen']  # reply.fen 是 bot 走完之后
    assert len(st['legal_moves']) > 0


def test_play_move_after_game_over_raises(curriculum_factory):
    s = mk(curriculum_factory, PLAY)
    s.submit_move('a1a8')
    with pytest.raises(IllegalMove):
        s.submit_move('a8a1')


def test_restart_play(curriculum_factory):
    s = mk(curriculum_factory, {**PLAY, 'fen': ROOK_ENDGAME, 'bot': 'smart'})
    s.submit_move('a1a2')
    st = s.restart_play()
    assert st['fen'] == ROOK_ENDGAME
    assert st['my_moves'] == 0
    assert st['play_status'] == 'playing'
    assert st['mistakes'] == 1  # 对局中途重开算一次小失误
    assert st['reply'] is None


def test_restart_play_switch_bot(curriculum_factory):
    s = mk(curriculum_factory, {**PLAY, 'fen': ROOK_ENDGAME})
    st = s.restart_play(bot_style='greedy')
    assert st['bot_style'] == 'greedy'
    assert st['mistakes'] == 0  # 尚未走子,换档不算失误
    with pytest.raises(IllegalMove):
        s.restart_play(bot_style='terminator')
