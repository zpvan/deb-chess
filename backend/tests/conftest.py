import pytest

from app.models import Curriculum

# 测试中直接用纯字符串写文案,这里自动包装成 Bilingual 结构
TEXT_FIELDS = {'title', 'text', 'prompt', 'prompts', 'hint', 'successText', 'failText',
               'drawText', 'sideLabel', 'question', 'options', 'explain', 'goal', 'skill',
               'intro', 'badge'}


def _wrap(value):
    if isinstance(value, str):
        return {'zh': value, 'en': value}
    if isinstance(value, list):
        return [_wrap(v) for v in value]
    if isinstance(value, dict):
        return {k: (_wrap(v) if k in TEXT_FIELDS else v) for k, v in value.items()}
    return value


def make_curriculum(steps: list[dict]) -> Curriculum:
    return Curriculum.model_validate({'chapters': [{
        'id': 'c1', 'badge': _wrap('测试'), 'title': _wrap('测试章'), 'intro': _wrap(''),
        'color': '#000000', 'soft': '#ffffff',
        'levels': [{'id': 't1', 'title': _wrap('测试关'), 'goal': _wrap('g'), 'skill': _wrap('s'),
                    'steps': [_wrap(s) for s in steps]}],
    }]})


@pytest.fixture
def curriculum_factory():
    return make_curriculum
