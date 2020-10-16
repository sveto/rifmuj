import pytest
from phonetics.accent import normalize_accented_spell, is_correctly_accented
from phonetics.phonetizer import phonetize
from phonetics.rhyme import get_basic_rhyme, normalized_rhyme_distance

@pytest.mark.parametrize('word, basic_rhyme', [
    ('а́',       'A'),
    ('голова́',  'vA'),
    ('голо́в',   'Of'),
    ('голо́вка', 'Ofki'),
    ('го́лову',  'Olifi'),
])
def test_basic_rhyme(word: str, basic_rhyme: str) -> None:
    trans = get_transcription(word)
    assert get_basic_rhyme(trans) == basic_rhyme


@pytest.mark.parametrize('word, better_rhyme, worse_rhyme', [
    ('па́лка', 'га́лка', 'селёдка'),
    ('ко́т', 'террако́т', 'боло́т'),
    ('Во́лга', 'до́лго', 'во́лка'),
    ('гли́ст', 'ли́ст', 'бугри́ст'),
    # ('', '', ''),
])
def test_better_rhyme(word: str, better_rhyme: str, worse_rhyme: str) -> None:
    word_trans   = get_transcription(word)
    better_trans = get_transcription(better_rhyme)
    worse_trans  = get_transcription(worse_rhyme)
    
    word_basic_rhyme   = get_basic_rhyme(word_trans)
    better_basic_rhyme = get_basic_rhyme(better_trans)
    worse_basic_rhyme  = get_basic_rhyme(worse_trans)
    assert word_basic_rhyme == better_basic_rhyme
    
    if word_basic_rhyme == worse_basic_rhyme:
        better_distance = normalized_rhyme_distance(word_trans, better_trans)
        worse_distance  = normalized_rhyme_distance(word_trans, worse_trans)
        assert better_distance < worse_distance


def get_transcription(word: str) -> str:
    accented_spell = normalize_accented_spell(word)
    assert is_correctly_accented(accented_spell)
    return phonetize(accented_spell)
