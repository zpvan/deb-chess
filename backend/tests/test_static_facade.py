import json

import pytest

from app import static_facade as sf


@pytest.fixture(autouse=True)
def fresh_facade():
    """每个用例重置门面状态。"""
    sf.reset()
    yield


def unwrap(raw: str):
    return json.loads(raw)


def test_curriculum_en_zh():
    en = unwrap(sf.get_curriculum('en'))
    zh = unwrap(sf.get_curriculum('zh'))
    assert en['ok'] and zh['ok']
    assert en['data']['chapters'][0]['title'] == 'Meet the Pieces'
    assert zh['data']['chapters'][0]['title'] == '认识棋子朋友'


def test_meta_no_stockfish():
    m = unwrap(sf.meta())
    assert m['ok'] is True
    assert m['data']['stockfish_available'] is False
    assert 'master' in m['data']['bot_styles']  # 列表不变,前端自行隐藏


def test_full_lesson_flow_and_progress():
    sid = unwrap(sf.create_session('w1', 'en'))['data']['session_id']
    # teach → next
    st = unwrap(sf.session_next(sid))['data']
    assert st['step_index'] == 1
    # 非法走法 → 422 双语错误
    bad = unwrap(sf.session_move(sid, 'a1b2'))
    assert bad['ok'] is False and bad['status'] == 422
    assert bad['detail']['code'] == 'illegal'
    # 错误走法
    st = unwrap(sf.session_move(sid, 'a1a4'))['data']
    assert st['last_result'] == 'wrong'
    # 正确走法 → 英文成功文案
    st = unwrap(sf.session_move(sid, 'a1a5'))['data']
    assert st['solved'] is True
    assert isinstance(st['success_text'], str) and 'a5' in st['success_text']
    # 会话语言保持:zh 会话返回中文标题
    sid_zh = unwrap(sf.create_session('w1', 'zh'))['data']['session_id']
    assert unwrap(sf.get_session(sid_zh))['data']['level_title'] == '棋子走法小课堂'


def test_progress_persist_hook():
    sf.set_progress_json('{"levels": {"w1": 2}, "xp": 100}')
    assert unwrap(sf.get_progress('en'))['data']['xp'] == 100
    assert unwrap(sf.get_progress('zh'))['data']['rank_name'] == '小骑士'
    sid = unwrap(sf.create_session('w2', 'en'))['data']['session_id']
    # w2:teach → next,两步一步杀
    unwrap(sf.session_next(sid))
    st = unwrap(sf.session_move(sid, 'e1e8'))['data']
    assert st['solved'] is True
    unwrap(sf.session_next(sid))
    st2 = unwrap(sf.session_move(sid, 'a1a8'))['data']
    assert st2['solved'] is True
    fin = unwrap(sf.session_next(sid))['data']
    assert fin['finished'] is True
    # 通关后进度已更新(可回写持久化)
    saved = sf.get_progress_json()
    p = json.loads(saved)
    assert p['levels']['w2'] >= 1
    assert p['xp'] > 100


def test_unknown_session_404():
    r = unwrap(sf.session_move('deadbeef', 'a1a5'))
    assert r['ok'] is False and r['status'] == 404


def test_unknown_level_404():
    r = unwrap(sf.create_session('nope', 'en'))
    assert r['ok'] is False and r['status'] == 404
