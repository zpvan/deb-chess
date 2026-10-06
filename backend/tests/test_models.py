from app.models import load_curriculum, public_step


def test_load_real_curriculum():
    cur = load_curriculum()  # 默认加载 backend/data/curriculum.py
    flats = cur.flat_levels()
    assert len(flats) > 0
    ids = [lv.id for _, lv, _ in flats]
    assert len(ids) == len(set(ids)), '关卡 id 必须唯一'
    assert cur.find_level('w1') is not None
    assert cur.find_level('no-such') is None
    assert cur.total_puzzles > 0


def test_public_step_strips_answers():
    cur = load_curriculum()
    _, level, _ = cur.find_level('w1')
    move_step = next(s for s in level.steps if s.type == 'move')
    pub = public_step(move_step)
    assert 'accepted' not in pub
    assert 'successText' not in pub
    assert pub['type'] == 'move'
    assert pub['fen'] == move_step.fen
