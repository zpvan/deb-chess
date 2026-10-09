from app.db import ProgressDB


def test_empty_progress(tmp_path):
    db = ProgressDB(tmp_path / 'p.db')
    p = db.get()
    assert p == {'levels': {}, 'xp': 0, 'total_stars': 0, 'rank_name': 'Pawn Rookie', 'rank_icon': '♟'}
    assert db.get(lang='zh')['rank_name'] == '小士兵'
    db.close()


def test_complete_level_first_time(tmp_path):
    db = ProgressDB(tmp_path / 'p.db')
    p = db.complete_level('w1', 2)
    assert p['levels'] == {'w1': 2}
    assert p['xp'] == 60 + 2 * 20  # 首通 60 + stars*20
    assert p['rank_name'] == 'Knight Rookie'  # xp >= 100
    assert db.get(lang='zh')['rank_name'] == '小骑士'
    db.close()


def test_replay_keeps_best_and_grants_diff(tmp_path):
    db = ProgressDB(tmp_path / 'p.db')
    db.complete_level('w1', 3)   # xp: 60+60=120
    p = db.complete_level('w1', 1)  # 更差:不加分,星级不降
    assert p['levels']['w1'] == 3
    assert p['xp'] == 120
    p = db.complete_level('w1', 3)  # 持平:不加分
    assert p['xp'] == 120
    db.close()


def test_persistence_across_instances(tmp_path):
    path = tmp_path / 'p.db'
    ProgressDB(path).complete_level('w1', 1)
    db = ProgressDB(path)
    assert db.get()['levels'] == {'w1': 1}
    db.close()
