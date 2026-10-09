import importlib.util
import json
from pathlib import Path
from typing import Annotated, Literal, Optional, Union

from pydantic import BaseModel, Field

# 课程数据为 Python 模块(backend/data/curriculum.py,暴露 CHAPTERS: list[dict])
DEFAULT_DATA = Path(__file__).resolve().parents[1] / 'data' / 'curriculum.py'

Lang = Literal['en', 'zh']


class Bilingual(BaseModel):
    """用户可见文本:中英双语。"""
    zh: str
    en: str


def loc_text(field: Bilingual, lang: str) -> str:
    if lang == 'zh':
        return field.zh
    return field.en


def _flatten(value, lang: str):
    """递归扁平化:模型/字典/列表中的 Bilingual 全部解析为 lang 字符串。"""
    if isinstance(value, Bilingual):
        return loc_text(value, lang)
    if isinstance(value, BaseModel):
        return _flatten(value.model_dump(), lang)
    if isinstance(value, dict):
        if set(value.keys()) == {'zh', 'en'}:
            return value.get(lang, value.get('en', value.get('zh', '')))
        return {k: _flatten(v, lang) for k, v in value.items()}
    if isinstance(value, list):
        return [_flatten(v, lang) for v in value]
    return value


class TeachStep(BaseModel):
    type: Literal['teach']
    title: Bilingual
    text: list[Bilingual]
    fen: Optional[str] = None
    highlight: Optional[list[str]] = None
    arrows: Optional[list[tuple[str, str]]] = None


class MateStep(BaseModel):
    type: Literal['mate']
    fen: str
    prompt: Bilingual
    hint: Optional[Bilingual] = None
    successText: Bilingual
    orientation: Optional[Literal['white', 'black']] = None


class MoveStep(BaseModel):
    type: Literal['move']
    fen: str
    prompt: Bilingual
    accepted: list[str]
    hint: Optional[Bilingual] = None
    successText: Bilingual
    orientation: Optional[Literal['white', 'black']] = None


class LineStep(BaseModel):
    type: Literal['line']
    fen: str
    script: list[str]
    endsWithMate: bool = True
    prompts: list[Bilingual]
    hint: Optional[Bilingual] = None
    successText: Bilingual


class ChoiceStep(BaseModel):
    type: Literal['choice']
    fen: str
    sideLabel: Bilingual
    question: Bilingual
    options: list[Bilingual]
    answer: int
    explain: Bilingual
    orientation: Optional[Literal['white', 'black']] = None


class PlayStep(BaseModel):
    type: Literal['play']
    fen: str
    bot: Literal['random', 'greedy', 'smart']
    win: Literal['mate', 'mateOrQueen']
    prompt: Bilingual
    hint: Optional[Bilingual] = None
    successText: Bilingual
    failText: Bilingual
    drawText: Bilingual


Step = Annotated[
    Union[TeachStep, MateStep, MoveStep, LineStep, ChoiceStep, PlayStep],
    Field(discriminator='type'),
]


class Level(BaseModel):
    id: str
    title: Bilingual
    goal: Bilingual
    skill: Bilingual
    steps: list[Step]


class Chapter(BaseModel):
    id: str
    badge: Bilingual
    title: Bilingual
    intro: Bilingual
    color: str
    soft: str
    levels: list[Level]


class Curriculum(BaseModel):
    chapters: list[Chapter]

    def flat_levels(self) -> list[tuple[Chapter, Level, int]]:
        out: list[tuple[Chapter, Level, int]] = []
        for ch in self.chapters:
            for lv in ch.levels:
                out.append((ch, lv, len(out)))
        return out

    def find_level(self, level_id: str) -> Optional[tuple[Chapter, Level, int]]:
        for ch, lv, idx in self.flat_levels():
            if lv.id == level_id:
                return ch, lv, idx
        return None

    @property
    def total_puzzles(self) -> int:
        return sum(1 for _, lv, _ in self.flat_levels() for s in lv.steps if s.type != 'teach')


# 答案字段:绝不下发给前端
ANSWER_FIELDS = {'accepted', 'script', 'answer', 'explain', 'successText', 'failText', 'drawText'}


def public_step(step: Step, lang: str = 'en') -> dict:
    raw = {
        k: v
        for k, v in step.model_dump(mode='python').items()
        if k not in ANSWER_FIELDS and v is not None
    }
    return _flatten(raw, lang)


def load_chapters(path: Union[str, Path, None] = None) -> list[dict]:
    """加载课程数据。默认读 Python 模块;测试可传 JSON 文件路径。"""
    path = Path(path) if path else DEFAULT_DATA
    if path.suffix == '.py':
        spec = importlib.util.spec_from_file_location('curriculum_data', path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.CHAPTERS
    return json.loads(path.read_text(encoding='utf-8'))


def load_curriculum(path: Union[str, Path, None] = None) -> Curriculum:
    return Curriculum.model_validate({'chapters': load_chapters(path)})
