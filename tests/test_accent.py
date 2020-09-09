import pytest
from phonetics.accent import *
from phonetics.phonetizer import phonetize

@pytest.mark.parametrize('input, output', [
    ("му'ка", "му'ка"),
    ("мука_", "мука'"),
    ("му́ка",  "му'ка"),
])
def test_normalize_accent_marks(input: str, output: str) -> None:
    assert normalize_accent_marks(input) == output

@pytest.mark.parametrize('input, output', [
    ("горы",  "горы"),
    ("го'ры", "го́ры"),
    ("горы'", "горы́"),
])
def test_prettify_accent_marks(input: str, output: str) -> None:
    assert prettify_accent_marks(input) == output

@pytest.mark.parametrize('input, output', [
    ("творог",   "творог"),
    ("творо'г",  "творог"),
    ("тво'ро'г", "творог"),
])
def test_remove_accent_marks(input: str, output: str) -> None:
    assert remove_accent_marks(input) == output

@pytest.mark.parametrize('input, result', [
    ("ло'жить",  True),
    ("ложи'ть",  True),
    ("ложить",   False),
    ("ло'жи'ть", False),
    ("лож'ить",  False),
    ("ложить'",  False),
    ("'ложить",  False),
])
def test_is_correctly_accented(input: str, result: bool) -> None:
    assert is_correctly_accented(input) == result

@pytest.mark.parametrize('accented',
    ["пе'рвый", "второ'й", "а'льфа", "ерунда'", "ао'рист", "рлье'х", "к"]
)
def test_get_accent_by_transcription(accented: str) -> None:
    spell = remove_accent_marks(accented)
    trans = phonetize(accented)
    assert get_accent_by_transcription(spell, trans) == accented

@pytest.mark.parametrize('spell, variants', [
    ('к', ["к"]),
    ('вспять', ["вспя'ть"]),
    ('отнял',  ["о'тнял", "отня'л"]),
    ('ханука', ["ха'нука", "хану'ка", "ханука'"]),
])
def test_get_accent_variants(spell: str, variants: List[str]) -> None:
    assert list(get_accent_variants(spell)) == variants
