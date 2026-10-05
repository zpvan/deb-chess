import json
from pathlib import Path
from typing import Annotated, Literal, Optional, Union

from pydantic import BaseModel, Field


class TeachStep(BaseModel):
    type: Literal['teach']
    title: str
    text: list[str]
    fen: Optional[str] = None
    highlight: Optional[list[str]] = None
    arrows: Optional[list[tuple[str, str]]] = None


class MateStep(BaseModel):
    type: Literal['mate']
    fen: str
    prompt: str
    hint: Optional[str] = None
    successText: str
    orientation: Optional[Literal['white', 'black']] = None


class MoveStep(BaseModel):
    type: Literal['move']
    fen: str
    prompt: str
    accepted: list[str]
    hint: Optional[str] = None
    successText: str
    orientation: Optional[Literal['white', 'black']] = None


class LineStep(BaseModel):
    type: Literal['line']
    fen: str
    script: list[str]
    endsWithMate: bool = True
    prompts: list[str]
    hint: Optional[str] = None
    successText: str


class ChoiceStep(BaseModel):
    type: Literal['choice']
    fen: str
    sideLabel: str
    question: str
    options: list[str]
    answer: int
    explain: str
    orientation: Optional[Literal['white', 'black']] = None


class PlayStep(BaseModel):
    type: Literal['play']
    fen: str
    bot: Literal['random', 'greedy', 'smart']
    win: Literal['mate', 'mateOrQueen']
    prompt: str
    hint: Optional[str] = None
    successText: str
    failText: str
    drawText: str


Step = Annotated[
    Union[TeachStep, MateStep, MoveStep, LineStep, ChoiceStep, PlayStep],
    Field(discriminator='type'),
]


class Level(BaseModel):
    id: str
    title: str
    goal: str
    skill: str
    steps: list[Step]


class Chapter(BaseModel):
    id: str
    badge: str
    title: str
    intro: str
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


def public_step(step: Step) -> dict:
    return {
        k: v
        for k, v in step.model_dump(mode='json').items()
        if k not in ANSWER_FIELDS and v is not None
    }


def load_curriculum(path: Union[str, Path]) -> Curriculum:
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    return Curriculum.model_validate({'chapters': data})
