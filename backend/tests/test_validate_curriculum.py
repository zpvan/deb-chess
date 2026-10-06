import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from validate_curriculum import load_chapters, validate_all


def test_real_curriculum_is_valid():
    errors = validate_all(load_chapters())
    assert errors == [], '\n'.join(errors)


def test_validator_catches_bad_fen():
    bad = [{'id': 'c', 'levels': [{'id': 'L', 'steps': [
        {'type': 'mate', 'fen': 'not-a-fen', 'prompt': 'x', 'successText': 'y'}]}]}]
    errors = validate_all(bad)
    assert any('FEN' in e for e in errors)


def test_validator_catches_illegal_accepted_move():
    bad = [{'id': 'c', 'levels': [{'id': 'L', 'steps': [
        {'type': 'move', 'fen': '4k3/8/8/8/8/8/8/R3K3 w - - 0 1',
         'prompt': 'x', 'accepted': ['a1a9'], 'successText': 'y'}]}]}]
    errors = validate_all(bad)
    assert any('a1a9' in e for e in errors)
