# 全站双语化实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** deb-chess 全站双语化:默认英文,顶栏「EN | 中」切换,UI 框架与全部课程正文双语。

**Architecture:** 后端 `curriculum.py` 所有用户文本改为 `{'zh','en'}` 结构(Bilingual 模型),API 按 lang 扁平化;前端自研轻量 i18n context + en/zh 词典,LangToggle 切换时重建课程数据与会话。

**Tech Stack:** pydantic v2, FastAPI, React context(无第三方 i18n 库)。

**Spec:** `docs/superpowers/specs/2026-10-09-bilingual-i18n-design.md`

## 关键接口契约(跨任务一致性)

- `Loc`:`{'zh': str, 'en': str}`(pydantic 模型 `Bilingual`,两键均必填)。
- `loc_text(field: Bilingual, lang: str) -> str`:取 field[lang],缺则 en,再缺 zh。
- 后端 API:所有用户文本按 lang 扁平化输出(响应里**不出现** Bilingual 结构)。
- 会话:`LessonSession(curriculum, level_id, lang='en', ...)`;`POST /api/sessions` body `{level_id, lang}`。
- 错误:`IllegalMove(code)`;`ERRORS = {code: {'zh': ..., 'en': ...}}`;422 响应 `{"detail": {"code": ..., "zh": ..., "en": ...}}`。
- 前端:`useLang() -> {lang, setLang, t}`;localStorage key `deb-chess-lang`(值 `'en'|'zh'`,默认 `'en'`)。

---

### Task 1: 后端 Bilingual 模型与扁平化

**Files:**
- Modify: `backend/app/models.py`
- Modify: `backend/tests/conftest.py`(自动包装文本字段)
- Modify: `backend/tests/test_models.py`

- [ ] **Step 1: 修改 models.py(失败的测试先行)**

`backend/tests/test_models.py` 全量替换:

```python
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
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd backend && ../.venv/bin/pytest tests/test_models.py -v`
Expected: FAIL(curriculum.py 还是纯中文,`Bilingual` 不存在或校验失败)。

- [ ] **Step 3: 修改 models.py**

在 `backend/app/models.py` 中(以下为完整替换内容):

```python
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
```

- [ ] **Step 4: 修改 conftest.py(纯字符串自动包装为双语,既有测试零改动)**

`backend/tests/conftest.py` 全量替换:

```python
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
        'id': 'c1', 'badge': '测试', 'title': '测试章', 'intro': '', 'color': '#000000',
        'soft': '#ffffff',
        'levels': [{'id': 't1', 'title': '测试关', 'goal': 'g', 'skill': 's',
                    'steps': [_wrap(s) for s in steps]}],
    }]})


@pytest.fixture
def curriculum_factory():
    return make_curriculum
```

- [ ] **Step 5: 跑测试确认通过(conftest 相关)**

Run: `cd backend && ../.venv/bin/pytest tests/test_session.py tests/test_play.py tests/test_bot.py tests/test_db.py -q`
Expected: 全部通过(test_models 中加载真实课程的两个用例仍失败——curriculum.py 尚未双语化,属预期,Task 2 修复)。

- [ ] **Step 6: Commit**

```bash
git add backend/app/models.py backend/tests/conftest.py backend/tests/test_models.py
git commit -m "feat: bilingual pydantic models with lang flattening"
```

### Task 2: curriculum.py 双语化(翻译课程正文)

**Files:**
- Modify: `backend/data/curriculum.py`(82 个步骤全部双语)

本任务是把 `curriculum.py` 中所有用户文本改为 `{'zh': 原文, 'en': 译文}`。**以下给出 warmup 章(3 关 15 步)的完整成品作为范例与验收基准**,其余 4 章(endgame/middlegame/opening/battle)由执行者按相同规范逐章翻译,每章完成后立即跑验收门禁。

**翻译规范:**
1. 只翻译用户文本字段(`title/text/prompt/prompts/hint/successText/failText/drawText/sideLabel/question/options/explain`,章节 `badge/title/intro`,关卡 `title/goal/skill`);`id/fen/accepted/script/bot/win/answer/orientation/endsWithMate/arrows/highlight/color/soft` 原样保留。
2. 英文风格:给英语儿童看的简短口语句,感叹号风格与中文一致;棋步用 SAN/坐标原样(如 `a1→a5`、`Ra8`、`Nc7+`)不翻译。
3. 中文标点(,:!"")不要出现在英文里;英文用标准半角标点。
4. **不得改动任何 FEN/答案/剧本**,每章翻完必须过校验器。

- [ ] **Step 1: 用脚本把 warmup 章替换为以下成品**

用 python 脚本读取 `backend/data/curriculum.py`,将 `CHAPTERS[0]`(id=warmup)整体替换为下面的内容,再用 `pprint.pformat(chapters, width=100, sort_dicts=False)` 写回(文件头注释保持不变):

```python
{
 'id': 'warmup',
 'badge': {'zh': '热身站', 'en': 'Warm-up'},
 'title': {'zh': '认识棋子朋友', 'en': 'Meet the Pieces'},
 'intro': {'zh': '先和六个棋子朋友打个招呼,学会它们怎么走。',
           'en': 'Say hi to the six piece friends and learn how they move.'},
 'color': '#8C6D3F',
 'soft': '#F3E7CE',
 'levels': [
  {'id': 'w1',
   'title': {'zh': '棋子走法小课堂', 'en': 'How the Pieces Move'},
   'goal': {'zh': '学会六种棋子的走法', 'en': 'Learn how all six pieces move'},
   'skill': {'zh': '六种棋子走法', 'en': 'Moves of all six pieces'},
   'steps': [
    {'type': 'teach',
     'title': {'zh': '直走与斜走:车、象、后', 'en': 'Straight and Diagonal: Rook, Bishop, Queen'},
     'text': [{'zh': '车走直线,横竖都行;象走斜线,像滑滑梯;后最厉害,直线斜线都会。',
               'en': 'The rook moves in straight lines; the bishop slides diagonally; the queen does both — she is the strongest!'},
              {'zh': '注意:它们都不能跳过别的棋子。下面挨个试一试!',
               'en': "Careful: they can't jump over other pieces. Now try each one below!"}],
     'fen': '4k3/8/8/8/8/8/8/R2QK2B w - - 0 1',
     'arrows': [['a1', 'a5'], ['d1', 'h5'], ['h1', 'c6']]},
    {'type': 'move',
     'fen': '4k3/8/8/8/8/8/8/R3K3 w - - 0 1',
     'prompt': {'zh': '车走直线:把车从 a1 走到 a5!',
                'en': 'The rook moves straight: move it from a1 to a5!'},
     'accepted': ['a1a5'],
     'hint': {'zh': '先点车,再点同一条竖线上的 a5。',
              'en': 'Tap the rook, then tap a5 on the same file.'},
     'successText': {'zh': '车直直地走上了 a5。', 'en': 'The rook zoomed straight to a5.'}},
    {'type': 'move',
     'fen': '4k3/8/8/8/8/8/8/2B1K3 w - - 0 1',
     'prompt': {'zh': '象走斜线:把象从 c1 滑到 g5!',
                'en': 'The bishop moves diagonally: slide it from c1 to g5!'},
     'accepted': ['c1g5'],
     'hint': {'zh': '找斜线:c1-d2-e3-f4-g5。',
              'en': 'Follow the diagonal: c1-d2-e3-f4-g5.'},
     'successText': {'zh': '象沿着斜线滑到了 g5。', 'en': 'The bishop slid to g5.'}},
    {'type': 'move',
     'fen': '4k3/8/8/8/8/8/8/3QK3 w - - 0 1',
     'prompt': {'zh': '后两样都会:让皇后从 d1 斜走到 h5!',
                'en': 'The queen does both: move her from d1 to h5!'},
     'accepted': ['d1h5'],
     'hint': {'zh': '斜线:d1-e2-f3-g4-h5。', 'en': 'Diagonal: d1-e2-f3-g4-h5.'},
     'successText': {'zh': '皇后驾到 h5!', 'en': 'The queen arrives on h5!'}},
    {'type': 'teach',
     'title': {'zh': '特殊走法:马、兵、王', 'en': 'Special Moves: Knight, Pawn, King'},
     'text': [{'zh': '马跳“日”字,还能跳过别的棋子;兵只许向前,第一步可冲两格,吃子要斜着吃;王每次只走一格,但八个方向都行。',
               'en': 'The knight jumps in an L-shape and can hop over pieces; pawns only go forward — two squares on their first move — but capture diagonally; the king moves one square in any direction.'},
              {'zh': '王是最宝贵的:王被吃掉(将死)就输啦!',
               'en': 'The king is the most precious: if he is checkmated, you lose!'}],
     'fen': '4k3/8/8/8/8/8/4P3/1N2K3 w - - 0 1',
     'arrows': [['b1', 'c3'], ['e2', 'e4'], ['e1', 'e2']]},
    {'type': 'move',
     'fen': '4k3/8/8/8/8/8/8/1N2K3 w - - 0 1',
     'prompt': {'zh': '马跳“日”字:从 b1 跳到 c3!',
                'en': 'The knight jumps in an L: hop from b1 to c3!'},
     'accepted': ['b1c3'],
     'hint': {'zh': '先直走两格,再拐一格。', 'en': 'Two squares straight, then one to the side.'},
     'successText': {'zh': '马蹄哒哒,跳到 c3。', 'en': 'Clip-clop! The knight lands on c3.'}},
    {'type': 'move',
     'fen': '4k3/8/8/8/8/8/4P3/4K3 w - - 0 1',
     'prompt': {'zh': '小兵冲锋:从 e2 冲到 e4!',
                'en': 'Pawn charge: rush from e2 to e4!'},
     'accepted': ['e2e4'],
     'hint': {'zh': '小兵第一步可以冲两格。', 'en': 'A pawn may dash two squares on its first move.'},
     'successText': {'zh': '小兵冲到 e4。', 'en': 'The pawn charges to e4.'}},
    {'type': 'move',
     'fen': '4k3/8/8/8/8/8/8/4K3 w - - 0 1',
     'prompt': {'zh': '王慢慢走:从 e1 走到 e2!',
                'en': 'The king strolls: step from e1 to e2!'},
     'accepted': ['e1e2'],
     'hint': {'zh': '王一次只走一格。', 'en': 'The king moves just one square at a time.'},
     'successText': {'zh': '六个棋子朋友都学会啦!', 'en': 'You know all six piece friends now!'}}]},
  {'id': 'w-special',
   'title': {'zh': '三种特殊走法', 'en': 'Three Special Moves'},
   'goal': {'zh': '学会王车易位、兵的升变、吃过路兵', 'en': 'Learn castling, promotion, and en passant'},
   'skill': {'zh': '特殊走法', 'en': 'Special moves'},
   'steps': [
    {'type': 'teach',
     'title': {'zh': '书上的三个“例外规则”', 'en': 'Three Exception Rules'},
     'text': [{'zh': '国际象棋有三种不走寻常路的特殊走法,一个一个来看:',
               'en': 'Chess has three special moves that break the usual rules. Let us see them one by one:'},
              {'zh': '① 王车易位:王和车一起跳,让王躲到安全角落;',
               'en': '1. Castling: the king and rook jump together to tuck the king into a safe corner.'},
              {'zh': '② 兵的升变:小兵冲到底线,变身成皇后;',
               'en': '2. Promotion: a pawn that reaches the last rank turns into a queen!'},
              {'zh': '③ 吃过路兵:对方小兵冲两格路过你旁边,你可以斜着吃掉它。',
               'en': '3. En passant: if an enemy pawn dashes two squares past yours, you may capture it diagonally.'},
              {'zh': '下面一个一个来试!', 'en': 'Now try each one!'}]},
    {'type': 'move',
     'fen': 'r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1',
     'prompt': {'zh': '① 王车易位:把白王从 e1 走到 g1,看看会发生什么神奇的事!',
                'en': '1. Castling: move the white king from e1 to g1 and watch the magic!'},
     'accepted': ['e1g1'],
     'hint': {'zh': '点王,再点 g1(跳过 f1)——车会自动跳到王旁边!',
              'en': 'Tap the king, then g1 (skipping f1) — the rook hops over by itself!'},
     'successText': {'zh': '王车易位完成!记住三个条件:王和车都没动过、中间没有棋子、王没被将军也不经过受攻击的格子。',
                     'en': 'Castled! Remember the three rules: king and rook never moved, nothing between them, and the king is not in check nor passes through an attacked square.'}},
    {'type': 'move',
     'fen': '7k/P7/8/8/8/8/8/K7 w - - 0 1',
     'prompt': {'zh': '② 兵的升变:小兵冲到对面底线就能变身!让 a7 的小兵冲到底线!',
                'en': '2. Promotion: a pawn reaching the far rank transforms! Push the a7 pawn to the last rank!'},
     'accepted': ['a7a8', 'a7a8q'],
     'hint': {'zh': '点小兵,再点 a8——它会变成皇后!',
              'en': 'Tap the pawn, then a8 — it becomes a queen!'},
     'successText': {'zh': '升变成功!a8 皇后诞生,还顺便将军!(残局篇还会专门练这个)',
                     'en': 'Promoted! A queen is born on a8 — with check! (The endgame chapter practices this more.)'}},
    {'type': 'move',
     'fen': '4k3/8/8/3pP3/8/8/8/4K3 w - d6 0 2',
     'prompt': {'zh': '③ 吃过路兵:黑兵刚从 d7 冲两格到 d5,想从白兵身边溜过去!白兵可以斜走一格到 d6,把它吃掉。试试!',
                'en': '3. En passant: the black pawn just dashed from d7 to d5, sneaking past your pawn! Capture it by moving your pawn diagonally to d6. Try it!'},
     'accepted': ['e5d6'],
     'hint': {'zh': '点 e5 的白兵,再点 d6(黑兵右前方的空格)。',
              'en': 'Tap your e5 pawn, then d6 (the empty square beside the black pawn).'},
     'successText': {'zh': '吃过路兵!白兵斜到 d6,d5 的黑兵被吃掉了。记住:只能趁它刚冲两格的下一回合吃!',
                     'en': 'En passant! Your pawn lands on d6 and the d5 pawn is gone. Remember: you can only do this right after the enemy pawn dashes two squares!'}}]},
  {'id': 'w2',
   'title': {'zh': '第一次“将死”', 'en': 'Your First Checkmate'},
   'goal': {'zh': '体验把对方王“将死”', 'en': 'Feel what it is like to checkmate the enemy king'},
   'skill': {'zh': '将军与将死的直觉', 'en': 'Instinct for check and mate'},
   'steps': [
    {'type': 'teach',
     'title': {'zh': '将军与将死', 'en': 'Check and Checkmate'},
     'text': [{'zh': '你的棋子攻击对方的王,叫“将军”——拉响警报!',
               'en': 'When your piece attacks the enemy king, that is "check" — the alarm rings!'},
              {'zh': '如果王怎么都逃不掉,就叫“将死”,你就赢了。',
               'en': 'If the king cannot escape at all, that is "checkmate" — you win!'},
              {'zh': '记住:学棋先学将死,赢棋的感觉最棒!',
               'en': 'Remember: learn checkmate first — winning feels the best!'}],
     'fen': '6k1/5ppp/8/8/8/8/8/4R1K1 w - - 0 1'},
    {'type': 'mate',
     'fen': '6k1/5ppp/8/8/8/8/8/4R1K1 w - - 0 1',
     'prompt': {'zh': '白棋先走,一步把黑王将死!',
                'en': 'White to move — checkmate in one!'},
     'hint': {'zh': '黑王身后被自己的小兵堵死了。把车开到底线去!',
              'en': 'The black king is boxed in by its own pawns. Drive the rook to the back rank!'},
     'successText': {'zh': '将死!这就是著名的“底线杀”。',
                     'en': 'Checkmate! This is the famous "back-rank mate".'}},
    {'type': 'mate',
     'fen': '7k/6pp/8/8/8/8/8/R5K1 w - - 0 1',
     'prompt': {'zh': '黑王躲进了角落 h8,还能一步将死吗?',
                'en': 'The black king hides in the corner on h8. Can you still mate in one?'},
     'hint': {'zh': '角落里更没有退路。车冲到底线!',
              'en': 'The corner has even fewer escapes. Rook to the back rank!'},
     'successText': {'zh': 'Ra8 将死!角落也不是避风港。',
                     'en': 'Ra8 mate! The corner is no safe harbor either.'}}]}],
}
```

- [ ] **Step 2: warmup 章验收门禁**

```bash
.venv/bin/python backend/scripts/validate_curriculum.py   # Expected: 全部棋题校验通过 ✓
cd backend && ../.venv/bin/pytest tests/test_models.py::test_load_real_curriculum tests/test_models.py::test_public_step_flattens_and_strips -q
```
Expected: 2 passed(w1 已双语)。`test_all_text_fields_are_bilingual` 仍失败(其余章未翻,属预期)。

- [ ] **Step 3: Commit warmup**

```bash
git add backend/data/curriculum.py
git commit -m "content: bilingual warmup chapter"
```

- [ ] **Step 4: 翻译 endgame 章(执行者完成)**

打开 `backend/data/curriculum.py` 中 `id: 'endgame'` 的章节,按 Step 1 成品的相同方式,将每个用户文本字段改写为 `{'zh': 原文, 'en': 译文}`(用 python 脚本或逐段编辑;pprint 写回)。翻译规范见任务开头四点。**翻完必须过门禁**:

```bash
.venv/bin/python backend/scripts/validate_curriculum.py
cd backend && ../.venv/bin/pytest tests/test_models.py::test_load_real_curriculum -q
```
Expected: 全部通过。

```bash
git add backend/data/curriculum.py
git commit -m "content: bilingual endgame chapter"
```

- [ ] **Step 5: 翻译 middlegame 章**

同 Step 4 流程与门禁,commit message: `content: bilingual middlegame chapter`。

- [ ] **Step 6: 翻译 opening 章**

同 Step 4 流程与门禁,commit message: `content: bilingual opening chapter`。

- [ ] **Step 7: 翻译 battle 章**

同 Step 4 流程与门禁,commit message: `content: bilingual battle chapter`。

- [ ] **Step 8: 全部完成后总验收**

```bash
cd backend && ../.venv/bin/pytest tests/test_models.py -v
```
Expected: 4 passed(含 `test_all_text_fields_are_bilingual`——**全部 82 步双语**)。

### Task 3: API 语言管道(sessions/progress/errors)

**Files:**
- Modify: `backend/app/core/session.py`
- Modify: `backend/app/db.py`
- Modify: `backend/app/main.py`
- Modify: `backend/tests/test_api.py`
- Modify: `backend/tests/test_db.py`

- [ ] **Step 1: 更新 test_db.py(双语段位)**

`backend/tests/test_db.py` 中 `test_empty_progress` 与 `test_complete_level_first_time` 的断言更新(get 增加 lang 参数,`rank_name` 按语言):

```python
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
    assert p['xp'] == 60 + 2 * 20
    assert p['rank_name'] == 'Knight Rookie'
    assert db.get(lang='zh')['rank_name'] == '小骑士'
    db.close()
```

- [ ] **Step 2: 修改 db.py(RANKS 双语 + get(lang))**

`backend/app/db.py` 中 RANKS 与 get 替换为:

```python
RANKS = [
    (0, '小士兵', 'Pawn Rookie', '♟'),
    (100, '小骑士', 'Knight Rookie', '♞'),
    (250, '小主教', 'Bishop Rookie', '♝'),
    (450, '小城堡', 'Rook Rookie', '♜'),
    (700, '小皇后', 'Queen Rookie', '♛'),
    (1000, '小棋王', 'King Rookie', '♚'),
]
```

```python
    def get(self, lang: str = 'en') -> dict:
        levels = {r[0]: r[1] for r in self._conn.execute('SELECT level_id, stars FROM levels')}
        row = self._conn.execute("SELECT value FROM meta WHERE key='xp'").fetchone()
        xp = row[0] if row else 0
        rank = next((r for r in reversed(RANKS) if xp >= r[0]), RANKS[0])
        return {
            'levels': levels,
            'xp': xp,
            'total_stars': sum(levels.values()),
            'rank_name': rank[2] if lang == 'en' else rank[1],
            'rank_icon': rank[3],
        }
```

`complete_level` 内部 `return self.get()` 改为 `return self.get(lang)`,签名改为 `def complete_level(self, level_id: str, stars: int, lang: str = 'en') -> dict:`。

- [ ] **Step 3: 修改 session.py(lang + 双语错误 + 双语模板)**

在 `backend/app/core/session.py` 中做以下修改:

3a. 顶部 imports 更新,`BOT_STYLES` 后追加错误表与模板:

```python
from app.models import Curriculum, loc_text, public_step

BOT_STYLES = ('random', 'greedy', 'smart', 'master')
PUZZLE_TYPES = ('mate', 'move', 'line')

ERRORS = {
    'move_format': {'zh': '走法格式不对(应为如 e2e4 的格式)', 'en': 'Invalid move format (use e.g. e2e4)'},
    'illegal': {'zh': '这步棋不符合规则哦!', 'en': 'That move is not legal!'},
    'cannot_move': {'zh': '当前步骤不能走子', 'en': 'You cannot make a move right now'},
    'game_over': {'zh': '本局已结束,请点击"再来一盘"', 'en': 'This game is over — tap "Play again"'},
    'cannot_answer': {'zh': '当前步骤不能作答', 'en': 'Nothing to answer right now'},
    'unknown_bot': {'zh': '未知对手档位', 'en': 'Unknown bot level'},
    'finish_step': {'zh': '先完成这一步再走哦!', 'en': 'Finish this step first!'},
    'not_play': {'zh': '当前不是对弈步骤', 'en': 'This is not a play step'},
}

FAST_MATE_TEXT = {
    'zh': '更快将死!比参考答案还少用了步数,太厉害了!',
    'en': 'Even faster mate! Fewer moves than the reference — amazing!',
}

PLAY_WIN_TEMPLATE = {
    'zh': '{text}(用了 {n} 步)',
    'en': '{text} (in {n} moves)',
}
```

3b. `IllegalMove` 改为携带 code:

```python
class IllegalMove(ValueError):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code
```

3c. `parse_move` 中的 raise 改为 `raise IllegalMove('move_format')` / `raise IllegalMove('illegal')`。

3d. `LessonSession.__init__` 签名加 `lang: str = 'en'`,存 `self.lang = lang`。

3e. `state()` 中标题类字段扁平化:

```python
            'level_title': loc_text(self.level.title, self.lang),
            'level_skill': loc_text(self.level.skill, self.lang),
            'chapter_title': loc_text(self.chapter.title, self.lang),
            'chapter_badge': loc_text(self.chapter.badge, self.lang),
```

`'step': public_step(step)` 改为 `'step': public_step(step, self.lang)`;
line_prompt 赋值改为 `line_prompt = loc_text(step.prompts[i], self.lang)`。

3f. 文案生成处:
- `_handle_mate`:`self.success_text = loc_text(self.step.successText, self.lang)`
- `_handle_move`: 同上
- `_handle_line`:`self.success_text = (FAST_MATE_TEXT[self.lang] if self.fast_mate else loc_text(step.successText, self.lang))`
- `submit_choice`:`self.success_text = loc_text(self.step.explain, self.lang)`
- `_play_move` 三处 `self.success_text = f'{step.successText}(用了 {self.my_moves} 步)'` 改为:

```python
            self.success_text = PLAY_WIN_TEMPLATE[self.lang].format(
                text=loc_text(step.successText, self.lang), n=self.my_moves)
```

- `_play_move` drawText/failText 改 `loc_text(..., self.lang)`
- 所有 `raise IllegalMove('...')` 换成对应 code:`'cannot_move'`(submit_move 的两处)、`'game_over'`(_play_move)、`'cannot_answer'`(submit_choice)、`'finish_step'`(advance)、`'unknown_bot'`(restart_play)、`'not_play'`(restart_play 非 play 步骤)。

- [ ] **Step 4: 修改 main.py(lang 参数 + 双语错误响应)**

`backend/app/main.py` 修改:

4a. imports 增加:

```python
from fastapi import Query
from typing import Literal
from app.core.session import BOT_STYLES, ERRORS, IllegalMove, LessonSession
from app.models import load_curriculum, loc_text, public_step, _flatten
```

(原 `from app.core.session import ... IllegalMove ...` 行合并更新;`_flatten` 用于 curriculum 扁平化。)

4b. `NewSession` 加字段:`lang: Literal['en', 'zh'] = 'en'`。

4c. 错误处理:所有 `raise HTTPException(422, str(e))` 改为:

```python
        except IllegalMove as e:
            msg = ERRORS[e.code]
            raise HTTPException(422, {'code': e.code, 'zh': msg['zh'], 'en': msg['en']})
```

4d. curriculum 端点:

```python
    @app.get('/api/curriculum')
    def get_curriculum(lang: Literal['en', 'zh'] = Query('en')):
        chapters = []
        for ch in curriculum.chapters:
            levels = []
            for lv in ch.levels:
                levels.append({
                    'id': lv.id,
                    'title': loc_text(lv.title, lang),
                    'goal': loc_text(lv.goal, lang),
                    'skill': loc_text(lv.skill, lang),
                    'steps': [public_step(st, lang) for st in lv.steps],
                })
            chapters.append({
                'id': ch.id,
                'badge': loc_text(ch.badge, lang),
                'title': loc_text(ch.title, lang),
                'intro': loc_text(ch.intro, lang),
                'color': ch.color,
                'soft': ch.soft,
                'levels': levels,
            })
        return {
            'chapters': chapters,
            'total_levels': len(curriculum.flat_levels()),
            'total_puzzles': curriculum.total_puzzles,
            'stockfish_available': stockfish.available(),
            'bot_styles': list(BOT_STYLES),
        }
```

4e. progress 端点:`def get_progress(lang: Literal['en', 'zh'] = Query('en')): return db.get(lang)`。

4f. `new_session` 创建:`s = LessonSession(curriculum, body.level_id, lang=body.lang, stockfish=stockfish)`;`maybe_record` 中 `db.complete_level(s.level.id, s.stars)` 不动(返回不带语言,无妨)。

- [ ] **Step 5: 更新 test_api.py(TINY_CURRICULUM 双语 + lang 断言)**

`backend/tests/test_api.py` 全量替换:

```python
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
]


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
```

- [ ] **Step 6: 全量后端测试**

Run: `cd backend && ../.venv/bin/pytest tests/ -q`
Expected: 全部通过(37+ 项;session/play 测试因 conftest 自动包装无需改动)。

- [ ] **Step 7: Commit**

```bash
git add backend/app/core/session.py backend/app/db.py backend/app/main.py backend/tests/test_api.py backend/tests/test_db.py
git commit -m "feat: lang-aware sessions, bilingual ranks and errors"
```

### Task 4: 前端 i18n 基础设施

**Files:**
- Create: `src/i18n/index.tsx`
- Create: `src/i18n/en.ts`
- Create: `src/i18n/zh.ts`
- Modify: `src/App.tsx`(挂 LanguageProvider + document.title)

- [ ] **Step 1: 词典 en.ts**

`src/i18n/en.ts`:

```ts
const en = {
  'app.title': 'deb-chess Training Camp',
  'app.loading': 'Loading…',
  'common.retry': 'Retry',
  'common.error': 'Something went wrong',
  'common.continue': 'Continue',
  'common.next': 'Next level',
  'common.playAgain': 'Play again',
  'common.backToMap': 'Back to map',
  'common.iUnderstand': 'Got it',
  'common.xpSuffix': '{xp} XP',

  'home.badge': "A world champion's way to learn chess",
  'home.hero.pre': 'Start from the ',
  'home.hero.accent': 'endgame',
  'home.hero.post': ',',
  'home.hero.line2': 'and become a little chess king!',
  'home.intro': 'Made for first-grade chess kids: look at the board, think for yourself, and earn stars for right answers. From the simplest back-rank mate to full opening repertoires!',
  'home.start': 'Start playing',
  'home.continue': 'Keep playing',
  'home.stats.levels': '♟ {n} levels',
  'home.stats.puzzles': '⭐ {n} interactive puzzles',
  'home.stats.play': '⚔️ Play vs bot',
  'home.stats.stars': '🏆 Star rewards',
  'home.boardCaption': 'The classic back-rank mate: rook to a8, and the black king is trapped by its own pawns!',
  'home.pathTitle': 'Why learn backwards?',
  'home.pathDesc': 'Learn checkmates first and every game has a goal. This site follows that idea with three journeys.',
  'home.path1.title': 'Chapter 1 · Endgames',
  'home.path1.desc': 'Rook, queen, knight, bishop, pawn — which ones can mate a bare king, and how?',
  'home.path2.title': 'Chapter 2 · Middlegames',
  'home.path2.desc': 'Forks, pins, discovered checks, and winning material — plus mating streaks.',
  'home.path3.title': 'Chapter 3 · Openings',
  'home.path3.desc': 'Italian, Spanish, Queen’s Gambit, Sicilian, King’s Indian — the classics, all covered.',
  'home.path4.title': 'Battle · Real Games',
  'home.path4.desc': 'Play real games against the computer, then prove your skills with rook-and-king mate.',
  'home.methodTitle': 'Programmed practice',
  'home.methodQuote': '"This book will teach you to analyze chess problems faster and to memorize key patterns. Work through it from the beginning and soon you will spot mates in seconds."',
  'home.methodBy': '— The world champion’s training secret: drill mate patterns until they become instinct',
  'home.footer': 'Your progress is saved in the server database on this machine — it survives browser changes.',

  'map.title': 'Level Map',
  'map.levelPrefix': 'Level {n} · ',
  'map.footerTip': 'Master endgame mates first, then middlegame tactics, then openings. Every level earns stars!',

  'lesson.badge.mate': '⚡ Mate in 1',
  'lesson.badge.line': '🔥 Mating streak',
  'lesson.badge.move': '🎯 Find the move',
  'lesson.badge.choice': '🤔 Think',
  'lesson.badge.play': 'Play vs Bot',
  'lesson.hint': 'Hint',
  'lesson.tapGuide': 'Tap a piece → tap a target square',
  'lesson.wrong': 'Not that one — think again, you can do it!',
  'lesson.thinking': '🤖 Opponent is thinking…',
  'lesson.myMoves': 'You have played {n} moves',
  'lesson.finished.title': 'Level complete!',
  'lesson.finished.skill': 'Skill earned: ',
  'lesson.finished.perfect': 'Perfect clear — not a single mistake. Amazing!',
  'lesson.finished.mistakes': '{n} mistakes — replay to earn more stars!',
  'lesson.loadError': 'Failed to load. Is the backend running?',
  'lesson.bot.random': 'Casual',
  'lesson.bot.greedy': 'Greedy',
  'lesson.bot.smart': 'Clever',
  'lesson.bot.master': 'Master Stockfish',

  'theme.toLight': 'Switch to light mode',
  'theme.toDark': 'Switch to dark mode',
  'nav.back': 'Back',
  'nav.home': 'Home',
}

export default en
```

- [ ] **Step 2: 词典 zh.ts**

`src/i18n/zh.ts`:

```ts
import type en from './en'

const zh: typeof en = {
  'app.title': 'deb-chess 练级营',
  'app.loading': '加载中……',
  'common.retry': '重试',
  'common.error': '出错了',
  'common.continue': '继续',
  'common.next': '下一关',
  'common.playAgain': '再来一盘',
  'common.backToMap': '回地图',
  'common.iUnderstand': '我明白了',
  'common.xpSuffix': '{xp}分',

  'home.badge': '世界冠军的学棋方法',
  'home.hero.pre': '从',
  'home.hero.accent': '终局',
  'home.hero.post': '开始,',
  'home.hero.line2': '一步步成为小棋王!',
  'home.intro': '专为一年级小棋士设计:先看图想一想,再动手走棋,答对就能赢星星。从最简单的“底线杀”练起,直到学会完整的开局!',
  'home.start': '开始闯关',
  'home.continue': '继续闯关',
  'home.stats.levels': '♟ 共 {n} 关',
  'home.stats.puzzles': '⭐ {n} 道互动棋题',
  'home.stats.play': '⚔️ 实战对弈',
  'home.stats.stars': '🏆 星星奖励',
  'home.boardCaption': '经典的“底线杀”:车冲 a8,黑王被自己的小兵困住!',
  'home.pathTitle': '为什么是“倒着学”?',
  'home.pathDesc': '先学杀王,棋越下越有目标。本站按这个思路设计了三段旅程。',
  'home.path1.title': '第一章 · 终局',
  'home.path1.desc': '单车、单后、单马、单象、单兵——谁能杀光杆王?怎么杀?',
  'home.path2.title': '第二章 · 中局',
  'home.path2.desc': '击双、牵制、闪将、得子四大武器,挑战“连续杀”。',
  'home.path3.title': '第三章 · 开局',
  'home.path3.desc': '意大利、西班牙、后翼弃兵、西西里、古印度——经典开局套路一网打尽。',
  'home.path4.title': '实战篇 · 对弈',
  'home.path4.desc': '和电脑真刀真枪下棋,再用“车王杀王”实操检验真本事。',
  'home.methodTitle': '程序化练习法',
  'home.methodQuote': '“这本书会教你更快地分析棋题,找到要记住的关键模式。只要从头开始一题一题做下去,几秒钟之内你就能认出杀棋。”',
  'home.methodBy': '—— 世界冠军的练棋秘诀:反复识别杀王模式,直到形成直觉',
  'home.footer': '学习进度保存在本机服务器的数据库里,换浏览器也不丢哦。',

  'map.title': '闯关地图',
  'map.levelPrefix': '第 {n} 关 · ',
  'map.footerTip': '先把终局的“杀王”练熟,再学中局战术,最后学开局。循序渐进,每关都能拿星星!',

  'lesson.badge.mate': '⚡ 一步杀',
  'lesson.badge.line': '🔥 连续杀',
  'lesson.badge.move': '🎯 找到这步棋',
  'lesson.badge.choice': '🤔 想一想',
  'lesson.badge.play': '实战对弈',
  'lesson.hint': '提示',
  'lesson.tapGuide': '点棋子 → 点目标格',
  'lesson.wrong': '这一步不对,再想想,你可以的!',
  'lesson.thinking': '🤖 对方思考中……',
  'lesson.myMoves': '你已走 {n} 步',
  'lesson.finished.title': '闯关成功!',
  'lesson.finished.skill': '获得技能:',
  'lesson.finished.perfect': '完美通关,一次都没错!太厉害了!',
  'lesson.finished.mistakes': '错了 {n} 次,复习一下还能拿更多星星哦!',
  'lesson.loadError': '加载失败,请检查后端是否启动',
  'lesson.bot.random': '随便走',
  'lesson.bot.greedy': '贪吃鬼',
  'lesson.bot.smart': '小聪明',
  'lesson.bot.master': '大师 Stockfish',

  'theme.toLight': '切换到浅色模式',
  'theme.toDark': '切换到深色模式',
  'nav.back': '返回',
  'nav.home': '首页',
}

export default zh
```

- [ ] **Step 3: i18n context**

`src/i18n/index.tsx`:

```tsx
import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import en from './en'
import zh from './zh'

export type Lang = 'en' | 'zh'

const DICTS: Record<Lang, Record<string, string>> = { en, zh }
const KEY = 'deb-chess-lang'

interface LangCtx {
  lang: Lang
  setLang: (l: Lang) => void
  t: (key: string, vars?: Record<string, string | number>) => string
}

const Ctx = createContext<LangCtx | null>(null)

function initial(): Lang {
  try {
    const saved = localStorage.getItem(KEY)
    if (saved === 'en' || saved === 'zh') return saved
  } catch { /* ignore */ }
  return 'en'
}

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>(initial)

  const setLang = useCallback((l: Lang) => {
    setLangState(l)
    try {
      localStorage.setItem(KEY, l)
    } catch { /* ignore */ }
  }, [])

  useEffect(() => {
    document.title = DICTS[lang]['app.title']
  }, [lang])

  const t = useCallback(
    (key: string, vars?: Record<string, string | number>) => {
      let s = DICTS[lang][key] ?? DICTS.en[key] ?? key
      if (vars) {
        for (const [k, v] of Object.entries(vars)) s = s.replace(`{${k}}`, String(v))
      }
      return s
    },
    [lang],
  )

  const value = useMemo(() => ({ lang, setLang, t }), [lang, setLang, t])
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>
}

export function useLang(): LangCtx {
  const ctx = useContext(Ctx)
  if (!ctx) throw new Error('useLang must be used within LanguageProvider')
  return ctx
}
```

- [ ] **Step 4: App.tsx 挂 Provider**

`src/App.tsx` 中 `export default function App()` 的返回替换为(其余不动):

```tsx
export default function App() {
  return (
    <LanguageProvider>
      <CurriculumProvider>
        <ProgressProvider>
          <Routes>
            <Route path="/" element={<Shell />} />
            <Route path="*" element={<Shell />} />
          </Routes>
        </ProgressProvider>
      </CurriculumProvider>
    </LanguageProvider>
  )
}
```

imports 增加:`import { LanguageProvider } from './i18n'`;Shell 中 `'加载中……'` 改为 `{t('app.loading')}`(Shell 内 `const { t } = useLang()`,import `useLang` from './i18n')。

- [ ] **Step 5: 验证构建**

Run: `npm run build`
Expected: 构建成功(页面文案尚未接入词典,后续任务接入)。

- [ ] **Step 6: Commit**

```bash
git add src/i18n/ src/App.tsx
git commit -m "feat: frontend i18n infrastructure with en/zh dictionaries"
```

### Task 5: 前端接入(api.ts lang 参数、Providers、LangToggle、三页文案)

**Files:**
- Modify: `src/lib/api.ts`
- Modify: `src/state/curriculum.tsx`
- Modify: `src/state/progress.tsx`
- Create: `src/components/LangToggle.tsx`
- Modify: `src/components/ThemeToggle.tsx`(aria-label 双语)
- Modify: `src/pages/Home.tsx`、`src/pages/Map.tsx`、`src/pages/Lesson.tsx`

- [ ] **Step 1: api.ts 支持 lang 与双语错误**

`src/lib/api.ts` 修改:

1a. `req` 函数错误处理段替换为:

```ts
async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(BASE + path, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
  if (!res.ok) {
    let msg = `Request failed (${res.status})`
    try {
      const d = await res.json()
      const lang = currentLang()
      if (typeof d.detail === 'string') msg = d.detail
      else if (d.detail && typeof d.detail === 'object') {
        msg = d.detail[lang] ?? d.detail.en ?? msg
      }
    } catch { /* ignore */ }
    throw new ApiError(msg, res.status)
  }
  return res.json()
}

function currentLang(): 'en' | 'zh' {
  try {
    const l = localStorage.getItem('deb-chess-lang')
    if (l === 'zh') return 'zh'
  } catch { /* ignore */ }
  return 'en'
}
```

1b. api 方法签名更新:

```ts
export const api = {
  getCurriculum: (lang: string) => req<CurriculumResponse>(`/curriculum?lang=${lang}`),
  getProgress: (lang: string) => req<ProgressResponse>(`/progress?lang=${lang}`),
  createSession: (levelId: string, lang: string) =>
    req<SessionState>('/sessions', { method: 'POST', body: JSON.stringify({ level_id: levelId, lang }) }),
  getSession: (id: string) => req<SessionState>(`/sessions/${id}`),
  sessionMove: (id: string, move: string) =>
    req<SessionState>(`/sessions/${id}/move`, { method: 'POST', body: JSON.stringify({ move }) }),
  sessionChoice: (id: string, index: number) =>
    req<SessionState>(`/sessions/${id}/choice`, { method: 'POST', body: JSON.stringify({ index }) }),
  sessionNext: (id: string) =>
    req<SessionState>(`/sessions/${id}/next`, { method: 'POST', body: '{}' }),
  restartPlay: (id: string, bot?: string) =>
    req<SessionState>(`/sessions/${id}/restart-play`, {
      method: 'POST',
      body: JSON.stringify({ bot: bot ?? null }),
    }),
}
```

- [ ] **Step 2: CurriculumProvider 依赖 lang**

`src/state/curriculum.tsx` 修改:顶部 import 增加 `import { useLang } from '@/i18n'`;`CurriculumProvider` 内:

```tsx
export function CurriculumProvider({ children }: { children: ReactNode }) {
  const { lang } = useLang()
  const [data, setData] = useState<CurriculumCtx>(EMPTY)

  useEffect(() => {
    setData((d) => ({ ...d, loading: true }))
    api
      .getCurriculum(lang)
      .then((res) => {
        const flatLevels: FlatLevel[] = res.chapters.flatMap((chapter) =>
          chapter.levels.map((level) => ({ chapter, level, index: -1 })),
        )
        flatLevels.forEach((f, i) => (f.index = i))
        setData({
          chapters: res.chapters,
          flatLevels,
          totalLevels: res.total_levels,
          totalPuzzles: res.total_puzzles,
          stockfishAvailable: res.stockfish_available,
          loading: false,
        })
      })
      .catch(() => setData({ ...EMPTY, loading: false }))
  }, [lang])

  return <Ctx.Provider value={data}>{children}</Ctx.Provider>
}
```

- [ ] **Step 3: ProgressProvider 依赖 lang**

`src/state/progress.tsx` 修改:import 增加 `import { useLang } from '@/i18n'`;Provider 内 `const { lang } = useLang()`;`refresh` 中 `api.getProgress()` 改 `api.getProgress(lang)`;refresh 的 useCallback 依赖数组加 `lang`。

- [ ] **Step 4: LangToggle 组件**

`src/components/LangToggle.tsx`:

```tsx
import { useLang, type Lang } from '@/i18n'

const OPTIONS: { value: Lang; label: string }[] = [
  { value: 'en', label: 'EN' },
  { value: 'zh', label: '中' },
]

export default function LangToggle() {
  const { lang, setLang } = useLang()
  return (
    <div className="flex items-center rounded-full border border-outline-variant p-0.5" role="group" aria-label="Language">
      {OPTIONS.map((o) => (
        <button
          key={o.value}
          onClick={() => setLang(o.value)}
          className={`px-2.5 py-1 rounded-full text-xs font-bold transition ${
            lang === o.value
              ? 'bg-primary-container text-on-primary-container'
              : 'text-on-surface-variant hover:bg-on-surface/10'
          }`}
        >
          {o.label}
        </button>
      ))}
    </div>
  )
}
```

- [ ] **Step 5: ThemeToggle aria-label 双语**

`src/components/ThemeToggle.tsx` 修改:import 增加 `import { useLang } from '@/i18n'`;组件内 `const { t } = useLang()`;`aria-label={dark ? t('theme.toLight') : t('theme.toDark')}`。

- [ ] **Step 6: Home.tsx 接入 t() 与 LangToggle**

对 `src/pages/Home.tsx` 做以下替换(import 增加 `LangToggle`、`useLang`):

6a. imports:

```tsx
import ChessBoard from '@/components/ChessBoard'
import ThemeToggle from '@/components/ThemeToggle'
import LangToggle from '@/components/LangToggle'
import { useLang } from '@/i18n'
import { useProgress } from '@/state/progress'
import { useCurriculum } from '@/state/curriculum'
import { Star, Play, BookOpen, Crown, Swords, Flag, Gamepad2 } from 'lucide-react'
```

6b. 组件开头:`const { t } = useLang()`。

6c. 顶栏标题 `{t('app.title')}`;星标与段位徽章文案不变(段位名来自 API 已双语);`<ThemeToggle />` 前插入 `<LangToggle />`。

6d. 主视觉区:

```tsx
          <div className="inline-block px-4 py-1.5 rounded-full bg-primary-container text-on-primary-container text-sm font-bold mb-5">
            {t('home.badge')}
          </div>
          <h1 className="font-display text-4xl sm:text-5xl leading-tight mb-5">
            {t('home.hero.pre')}<span className="text-primary">{t('home.hero.accent')}</span>{t('home.hero.post')}
            <br />
            {t('home.hero.line2')}
          </h1>
          <p className="text-lg text-on-surface-variant leading-relaxed mb-8">
            {t('home.intro')}
          </p>
```

按钮:`{nextLevel && nextLevel.index > 0 ? t('home.continue') : t('home.start')}`。

6e. 统计行:

```tsx
            <span>{t('home.stats.levels', { n: flatLevels.length })}</span>
            <span>{t('home.stats.puzzles', { n: totalPuzzles })}</span>
            <span>{t('home.stats.play')}</span>
            <span>{t('home.stats.stars')}</span>
```

6f. 棋盘说明:`{t('home.boardCaption')}`。

6g. 学习路径:标题 `{t('home.pathTitle')}`、描述 `{t('home.pathDesc')}`;4 张卡片数组改为(颜色/图标不变):

```tsx
          {[
            { icon: <Crown size={26} />, color: '#2E7D52', title: t('home.path1.title'), desc: t('home.path1.desc') },
            { icon: <Swords size={26} />, color: '#E07B2A', title: t('home.path2.title'), desc: t('home.path2.desc') },
            { icon: <Flag size={26} />, color: '#2F6FBA', title: t('home.path3.title'), desc: t('home.path3.desc') },
            { icon: <Gamepad2 size={26} />, color: '#7C4DA0', title: t('home.path4.title'), desc: t('home.path4.desc') },
          ].map((c) => (
```

6h. 方法区:`{t('home.methodTitle')}`、引言 `{t('home.methodQuote')}`、署名 `{t('home.methodBy')}`。

6i. footer:`{t('home.footer')}`。

- [ ] **Step 7: Map.tsx 接入**

`src/pages/Map.tsx` 替换点:imports 增加 LangToggle/useLang;`const { t } = useLang()`;标题 `{t('map.title')}`;段位徽章 `{rank.icon} {rank.name} · {t('common.xpSuffix', { xp })}`;`<ThemeToggle />` 前插入 `<LangToggle />`;关卡名行 `{t('map.levelPrefix', { n: idx + 1 })}{lv.title}`;底部提示 `{t('map.footerTip')}`;`aria-label="首页"` 改 `aria-label={t('nav.home')}`。

- [ ] **Step 8: Lesson.tsx 接入**

`src/pages/Lesson.tsx` 替换点:

8a. imports 增加:`import LangToggle from '@/components/LangToggle'`、`import { useLang } from '@/i18n'`;删除本地 `BOT_LABELS` 常量。

8b. 组件内:`const { t, lang } = useLang()`;`start` 的 `api.createSession(levelId)` 改 `api.createSession(levelId, lang)`,useCallback 依赖数组加 `lang`(**切语言自动重建会话**);错误 catch 文案 `t('lesson.loadError')` 与 `t('common.error')`。

8c. 错误/加载页:`重试` → `{t('common.retry')}`;`加载中……` → `{t('app.loading')}`。

8d. 结算页:`闯关成功!` → `{t('lesson.finished.title')}`;`获得技能:` → `{t('lesson.finished.skill')}`;完美/失误文案 → `t('lesson.finished.perfect')` / `t('lesson.finished.mistakes', { n: st.mistakes })`;`下一关` → `{t('common.next')}`;`再玩一次` → `{t('common.playAgain')}`;`回地图` → `{t('common.backToMap')}`。

8e. 顶栏:`aria-label="返回"` → `aria-label={t('nav.back')}`;`<ThemeToggle />` 前插入 `<LangToggle />`。

8f. 棋盘下方:`🤖 对方思考中……` → `{t('lesson.thinking')}`;`你已走 {st.my_moves} 步` → `{t('lesson.myMoves', { n: st.my_moves })}`。

8g. 徽章行:

```tsx
                  {step.type === 'mate' ? t('lesson.badge.mate') : step.type === 'line' ? t('lesson.badge.line') : t('lesson.badge.move')}
```

choice 徽章 `{t('lesson.badge.choice')}`;play 徽章 `{t('lesson.badge.play')}`。

8h. 提示按钮 `提示` → `{t('lesson.hint')}`;`点棋子 → 点目标格` → `{t('lesson.tapGuide')}`;`继续` → `{t('common.continue')}`(3 处);`我明白了` → `{t('common.iUnderstand')}`;`这一步不对,再想想,你可以的!` → `{t('lesson.wrong')}`。

8i. bot 档位按钮文案 `BOT_LABELS[b]` → `{t(`lesson.bot.${b}`)}`;master 按钮 `{t('lesson.bot.master')}`;`再来一盘` → `{t('common.playAgain')}`。

- [ ] **Step 9: 验证构建**

Run: `npm run build`
Expected: 构建成功,无 TS 错误。

- [ ] **Step 10: Commit**

```bash
git add src/lib/api.ts src/state/ src/components/LangToggle.tsx src/components/ThemeToggle.tsx src/pages/
git commit -m "feat: wire i18n into pages with language toggle"
```

### Task 6: 端到端验证(英/中 × 三页截图 + 全量测试)

**Files:**
- Create(临时,不进仓库): `/tmp/deb-shots/i18n-check.mjs`

- [ ] **Step 1: 起服务**

```bash
pkill -f "uvicorn app.main" 2>/dev/null; sleep 1
(./start.sh > /tmp/i18n-check.log 2>&1 &)
sleep 4
curl -s localhost:8642/api/health
curl -s "localhost:8642/api/curriculum?lang=en" | python3 -c "import sys,json;d=json.load(sys.stdin);print(d['chapters'][0]['title'])"
curl -s "localhost:8642/api/curriculum?lang=zh" | python3 -c "import sys,json;d=json.load(sys.stdin);print(d['chapters'][0]['title'])"
```
Expected: `{"ok":true}`;`Meet the Pieces`;`认识棋子朋友`。

- [ ] **Step 2: 截图脚本**

`/tmp/deb-shots/i18n-check.mjs`:

```js
import { chromium } from 'playwright'

const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1280, height: 800 } })
const shots = []
async function snap(name) {
  await page.screenshot({ path: `/tmp/i18n-${name}.png` })
  shots.push(name)
}

// ---- 英文(默认) ----
await page.goto('http://localhost:8642')
await page.waitForTimeout(1500)
await snap('en-home')
await page.getByRole('button', { name: /playing/i }).first().click()
await page.waitForTimeout(800)
await snap('en-map')
await page.getByRole('button', { name: /Level 1/ }).click()
await page.waitForTimeout(800)
await snap('en-lesson')
await page.getByRole('button', { name: /Got it/ }).click()
await page.waitForTimeout(800)
await snap('en-lesson-move')

// ---- 切到中文(点分段开关的“中”) ----
await page.getByRole('button', { name: '中', exact: true }).click()
await page.waitForTimeout(1200)
await snap('zh-lesson')

// ---- 中文首页 ----
await page.goto('http://localhost:8642')
await page.waitForTimeout(1200)
await snap('zh-home')
await page.getByRole('button', { name: /闯关/ }).first().click()
await page.waitForTimeout(800)
await snap('zh-map')

await browser.close()
console.log('shots:', shots.join(', '))
```

Run: `cd /tmp/deb-shots && node i18n-check.mjs`
Expected: 7 张截图,无报错。

- [ ] **Step 3: 人工检查截图**

用 Read 工具逐张查看:
- en-*:全英文(标题 "deb-chess Training Camp"、Start playing、Level 1 · How the Pieces Move、Got it、Hint);
- zh-*:全中文(与改版前一致);
- 语言开关出现在三页顶栏,当前语言高亮。

发现问题修对应文件,重跑脚本复查。

- [ ] **Step 4: 停服务、全量测试、Commit 推送**

```bash
pkill -f "uvicorn app.main"
cd backend && ../.venv/bin/pytest tests/ -q   # Expected: 全部通过
cd .. && npm run build                          # Expected: 成功
git add -A && git status --porcelain
git commit -m "feat: bilingual site verified end-to-end" || true
git push origin main
```

- [ ] **Step 5: index.html 默认文案英文化(收尾)**

`index.html` 中:`<title>deb-chess 练级营</title>` → `<title>deb-chess Training Camp</title>`;meta description 改英文:

```html
<meta name="description" content="Learn chess the world champion's way: start from endgames, step by step, made for first-grade chess kids." />
```

(JS 会在运行时按语言更新 document.title。)构建验证后:

```bash
git add index.html && git commit -m "chore: English default html title and description"
git push origin main
```
