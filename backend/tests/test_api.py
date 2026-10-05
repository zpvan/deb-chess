import json

import pytest
from fastapi.testclient import TestClient

from app.main import create_app

TINY_CURRICULUM = [{
    'id': 'c1', 'badge': '测试', 'title': '测试章', 'intro': '', 'color': '#000', 'soft': '#fff',
    'levels': [{
        'id': 't1', 'title': '测试关', 'goal': 'g', 'skill': 's',
        'steps': [
            {'type': 'teach', 'title': 't', 'text': ['x']},
            {'type': 'move', 'fen': '4k3/8/8/8/8/8/8/R3K3 w - - 0 1',
             'prompt': 'p', 'accepted': ['a1a5'], 'successText': 'ok'},
        ],
    }],
}]


@pytest.fixture
def client(tmp_path):
    cur = tmp_path / 'cur.json'
    cur.write_text(json.dumps(TINY_CURRICULUM), encoding='utf-8')
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


def test_full_lesson_flow(client):
    # 创建会话
    r = client.post('/api/sessions', json={'level_id': 't1'})
    assert r.status_code == 201
    sid = r.json()['session_id']
    # 未知关卡 404
    assert client.post('/api/sessions', json={'level_id': 'nope'}).status_code == 404
    # GET 恢复状态
    assert client.get(f'/api/sessions/{sid}').json()['step_index'] == 0
    # teach → next
    st = client.post(f'/api/sessions/{sid}/next').json()
    assert st['step_index'] == 1
    # 非法走法 422
    r = client.post(f'/api/sessions/{sid}/move', json={'move': 'a1b2'})
    assert r.status_code == 422
    # 合法但错误
    st = client.post(f'/api/sessions/{sid}/move', json={'move': 'a1a4'}).json()
    assert st['last_result'] == 'wrong'
    # 正确
    st = client.post(f'/api/sessions/{sid}/move', json={'move': 'a1a5'}).json()
    assert st['solved'] is True
    # 通关 → 自动写进度(1 次失误 → 2 星 → xp = 60 + 2*20)
    st = client.post(f'/api/sessions/{sid}/next').json()
    assert st['finished'] is True and st['stars'] == 2
    p = client.get('/api/progress').json()
    assert p['levels'] == {'t1': 2}
    assert p['xp'] == 100
    # 未知会话 404
    assert client.post('/api/sessions/deadbeef/move', json={'move': 'a1a5'}).status_code == 404


def test_progress_initially_empty(client):
    p = client.get('/api/progress').json()
    assert p['xp'] == 0 and p['levels'] == {}
