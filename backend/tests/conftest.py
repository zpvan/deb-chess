import pytest

from app.models import Curriculum


def make_curriculum(steps: list[dict]) -> Curriculum:
    return Curriculum.model_validate({'chapters': [{
        'id': 'c1', 'badge': '测试', 'title': '测试章', 'intro': '', 'color': '#000000',
        'soft': '#ffffff',
        'levels': [{'id': 't1', 'title': '测试关', 'goal': 'g', 'skill': 's', 'steps': steps}],
    }]})


@pytest.fixture
def curriculum_factory():
    return make_curriculum
