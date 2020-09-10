import pytest
from phonetics.accent import *
from phonetics.phonetizer import phonetize

@pytest.mark.parametrize('input, output', [
    ("му'ка",       "му'ка"),
    ("мука_",       "мука'"),
    ("му́ка",        "му'ка"),
    ("свёкла",      "свё'кла"),
    ("свё'кла",     "свё'кла"),
    ("свёкла'",     "свё'кла'"),
    (" с!вё`к,ла.", "свё'кла"),
])
def test_normalize_accented_spell(input: str, output: str) -> None:
    assert normalize_accented_spell(input) == output

@pytest.mark.parametrize('input, output', [
    ("творог",   "творог"),
    ("творо'г",  "творог"),
    ("тво'ро'г", "творог"),
    ("мёд",      "мед"),
    ("мё'д",     "мед"),
    ("м2ё,д ",   "мед"),
])
def test_normalize_spell(input: str, output: str) -> None:
    assert normalize_spell(input) == output

@pytest.mark.parametrize('input, output', [
    ("взгля'д", "взгляд"),
    ("горы",    "горы"),
    ("го'ры",   "го́ры"),
    ("горы'",   "горы́"),
    ("тё'ща",   "тёща"),
])
def test_prettify_accent_marks(input: str, output: str) -> None:
    assert prettify_accent_marks(input) == output

@pytest.mark.parametrize('input, result', [
    ("ло'жить",  True),
    ("ложи'ть",  True),
    ("ложить",   False),
    ("ло'жи'ть", False),
    ("лож'ить",  False),
    ("ложить'",  False),
    ("'ложить",  False),
    ("ко'вё'р",  False),
    ("ковё'р",   True),
])
def test_is_correctly_accented(input: str, result: bool) -> None:
    assert is_correctly_accented(input) == result

@pytest.mark.parametrize('spell, trans, yoficated', [
    ('все', 'fSE', 'все'),
    ('все', 'fSO', 'всё'),
    ('пошел', 'pacOl', 'пошёл'),
])
def test_yoficate_by_transcription(spell: str, trans: str, yoficated: str) -> None:
    assert yoficate_by_transcription(spell, trans) == yoficated

@pytest.mark.parametrize('accented',
    ["пе'рвый", "второ'й", "а'льфа", "ерунда'", "ао'рист", "рлье'х", "к", "селё'дка"]
)
def test_get_accent_by_transcription(accented: str) -> None:
    spell = normalize_spell(accented)
    trans = phonetize(accented)
    assert get_accent_by_transcription(spell, trans) == accented

@pytest.mark.parametrize('spell, variants', [
    ('к',      ["к"]),
    ('вспять', ["вспя'ть"]),
    ('отнял',  ["о'тнял", "отня'л"]),
    ('ханука', ["ха'нука", "хану'ка", "ханука'"]),
    ('берег',  ["бе'рег", "бё'рег", "бере'г", "берё'г"]),
])
def test_get_accent_variants(spell: str, variants: List[str]) -> None:
    assert list(get_accent_variants(spell)) == variants
