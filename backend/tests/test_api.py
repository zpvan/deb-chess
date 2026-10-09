import json

import pytest
from fastapi.testclient import TestClient

from app.main import create_app

L = lambda zh, en: {'zh': zh, 'en': en}  # noqa: E731

TINY_CURRICULUM = [{
    'id': 'c1', 'badge': L('测试', 'Test'), 'title': L('测试章', 'Test Chapter'),
    'intro': L('', ''), 'color': '#000', 'soft': '#fff',
    'levels': [{
        'id': 't1', 'title': L('测试关', 'Test Level'), 'goal': L('目标', 'Goal'),
        'skill': L('技能', 'Skill'),
        'steps': [
            {'type': 'teach', 'title': L('教', 'Teach'), 'text': [L('看', 'Look')]},
            {'type': 'move', 'fen': '4k3/8/8/8/8/8/8/R3K3 w - - 0 1',
             'prompt': L('走', 'Move it'), 'accepted': ['a1a5'],
             'successText': L('对', 'Correct')},
        ],
    }],
}]


@pytest.fixture
def client(tmp_path):
    cur = tmp_path / 'cur.json'
    cur.write_text(json.dumps(TINY_CURRICULUM, ensure_ascii=False), encoding='utf-8')
    app = create_app(curriculum_path=cur, db_path=tmp_path / 'p.db', dist_dir=tmp_path / 'no-dist')
    return TestClient(app)


def test_health():
    from app.main import create_app as ca
    r = TestClient(ca(dist_dir='/nonexistent')).get('/api/health')
    assert r.status_code == 200 and r.json() == {'ok': True}


def test_curriculum_has_no_answers(client):
    r = client.get('/api/curriculum')
    assert r.status_code == 200
    assert 'accepted' not in r.text and 'successText' not in r.text
    body = r.json()
    assert body['total_levels'] == 1
    assert 'stockfish_available' in body


def test_curriculum_default_en_and_zh_param(client):
    en = client.get('/api/curriculum').json()
    zh = client.get('/api/curriculum?lang=zh').json()
    assert en['chapters'][0]['levels'][0]['title'] == 'Test Level'
    assert zh['chapters'][0]['levels'][0]['title'] == '测试关'
    assert en['chapters'][0]['levels'][0]['steps'][0]['title'] == 'Teach'


def test_full_lesson_flow(client):
    r = client.post('/api/sessions', json={'level_id': 't1'})
    assert r.status_code == 201
    sid = r.json()['session_id']
    assert r.json()['level_title'] == 'Test Level'  # 默认英文
    assert client.post('/api/sessions', json={'level_id': 'nope'}).status_code == 404
    assert client.get(f'/api/sessions/{sid}').json()['step_index'] == 0
    st = client.post(f'/api/sessions/{sid}/next').json()
    assert st['step_index'] == 1
    # 非法走法 422,错误带双语文案
    r = client.post(f'/api/sessions/{sid}/move', json={'move': 'a1b2'})
    assert r.status_code == 422
    detail = r.json()['detail']
    assert detail['code'] == 'illegal' and 'en' in detail and 'zh' in detail
    st = client.post(f'/api/sessions/{sid}/move', json={'move': 'a1a4'}).json()
    assert st['last_result'] == 'wrong'
    st = client.post(f'/api/sessions/{sid}/move', json={'move': 'a1a5'}).json()
    assert st['solved'] is True
    assert st['success_text'] == 'Correct'  # 会话默认英文
    st = client.post(f'/api/sessions/{sid}/next').json()
    assert st['finished'] is True and st['stars'] == 2
    p = client.get('/api/progress').json()
    assert p['levels'] == {'t1': 2}
    assert p['xp'] == 100
    assert p['rank_name'] == 'Knight Rookie'
    assert client.get('/api/progress?lang=zh').json()['rank_name'] == '小骑士'
    assert client.post('/api/sessions/deadbeef/move', json={'move': 'a1a5'}).status_code == 404


def test_session_lang_zh(client):
    r = client.post('/api/sessions', json={'level_id': 't1', 'lang': 'zh'})
    assert r.json()['level_title'] == '测试关'


def test_progress_initially_empty(client):
    p = client.get('/api/progress').json()
    assert p['xp'] == 0 and p['levels'] == {}
