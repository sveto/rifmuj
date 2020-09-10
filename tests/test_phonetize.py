import pytest
from phonetics.phonetizer import phonetize

@pytest.mark.parametrize('accented_spell, transcription', [
    # jot vowels and signs
    ("плю'нь",      'pLUN'),
    ("илья'",       'YiLYA'),
    ("съе'л",       'sYEl'),
    ("почтальо'н",  'paTCtaLYOn'),
    ("ло'жь",       'lOc'),
    
    # vowel reduction
    ("колесо'",     'kaLisO'),
    ("лягу'шка",    'LigUcka'),
    ("до'ля",       'dOLa'),
    ("янта'рная",   'YintArnaYa'),
    ("ра'дио",      'rADio'),
    ("бегемо`топодо'бный", 'BiGimotapadObniY'),
    
    # complex consonants
    ("ци'рк",       'tsIrk'),
    ("ме'ч",        'METC'),
    ("щи'т",        'CIt'),
    ("счё'т",       'COt'),
    ("вещдо'к",     'ViJdOk'),
    
    # consonant voicing
    ("сво'д",       'svOt'),
    ("пое'здка",    'paYEstka'),
    ("ро'стбиф",    'rOzdBif'),
    ("овца'",       'aftsA'),
    ("плацда'рм",   'pladzdArm'),
    ("ка'к бы",     'kAgbi'),
    
    # cluster simplification
    ("ле'стница",   'LEsNitsa'),
    ("по'здно",     'pOzna'),
    
    # repeating consonants
    ("рассо'л",     'rasOl'),
    ("мета'лл",     'MitAl'),
    ("металли'ст",  'MitaLIst'),
    ("отда'ть",     'adAT'),
    
    # gen sg adj endings
    ("его'",        'YivO'),
    ("зло'го",      'zlOva'),
    ("кра'сного",   'krAsnava'),
    ("си'него",     'SINiva'),
    ("боя'вшегося", 'baYAfcivaSa'),
    ("кого'-нибудь",'kavONibuT'),
    
    # reflexive verbs
    ("куса'лся",    'kusAlSa'),
    ("куса'ться",   'kusAtsa'),
    ("куса'ется",   'kusAYitsa'),
    
    # orthographic pangram
    ("э`кс-гра'ф, плю'ш изъя'т, бьё'м чу'ждый це'н хво'щ",
        'egzgrAfpLUcYizYAdBYOmTCUjdiYtsEnxvOC'),
])
def test_phonetize(accented_spell: str, transcription: str) -> None:
    assert phonetize(accented_spell) == transcription
