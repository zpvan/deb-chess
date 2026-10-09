from app.models import Bilingual, load_curriculum, loc_text, public_step


def test_load_real_curriculum():
    cur = load_curriculum()  # 默认加载 backend/data/curriculum.py
    flats = cur.flat_levels()
    assert len(flats) > 0
    ids = [lv.id for _, lv, _ in flats]
    assert len(ids) == len(set(ids)), '关卡 id 必须唯一'
    assert cur.find_level('w1') is not None
    assert cur.find_level('no-such') is None
    assert cur.total_puzzles > 0


def test_all_text_fields_are_bilingual():
    cur = load_curriculum()
    for ch, lv, _ in cur.flat_levels():
        for field in (ch.title, ch.badge, ch.intro, lv.title, lv.goal, lv.skill):
            assert isinstance(field, Bilingual)
            assert field.zh and field.en, f'{lv.id} 缺翻译'
        for s in lv.steps:
            for name, value in s.model_dump().items():
                if name in ('type', 'fen', 'accepted', 'script', 'bot', 'win',
                            'answer', 'orientation', 'endsWithMate', 'arrows', 'highlight'):
                    continue
                if value is None:
                    continue
                items = value if isinstance(value, list) else [value]
                for it in items:
                    assert isinstance(it, dict) and it.get('zh') and it.get('en'), \
                        f'{lv.id} step {name} 缺翻译: {it!r:.60}'


def test_public_step_flattens_and_strips():
    cur = load_curriculum()
    _, level, _ = cur.find_level('w1')
    move_step = next(s for s in level.steps if s.type == 'move')
    en = public_step(move_step, 'en')
    zh = public_step(move_step, 'zh')
    assert 'accepted' not in en and 'successText' not in en
    assert isinstance(en['prompt'], str)
    assert isinstance(zh['prompt'], str)
    assert en['prompt'] != zh['prompt']  # 两种语言不同


def test_loc_text_fallback():
    b = Bilingual(zh='中', en='EN')
    assert loc_text(b, 'en') == 'EN'
    assert loc_text(b, 'zh') == '中'
    assert loc_text(b, 'fr') == 'EN'  # 未知语言回退英文
