import pytest # type: ignore
from data.phonetizer import phonetize

def test_jot_vowels_and_signs():
    assert phonetize("плю'нь") == 'пЛУН'
    assert phonetize("илья'") == 'ЙиЛЙА'
    assert phonetize("съе'л") == 'сЙЭл'
    assert phonetize("почтальо'н") == 'паЧтаЛЙОн'

def test_vowel_reduction():
    assert phonetize("колесо'") == 'каЛисО'
    assert phonetize("бегемо`топодо'бный") == 'БиГимотападОбниЙ'
    assert phonetize("лягу'шка") == 'ЛигУшка'
    assert phonetize("до'ля") == 'дОЛа'
    assert phonetize("янта'рная") == 'ЙинтАрнаЙа'
    assert phonetize("ра'дио") == 'рАДио'

def test_complex_consonants():
    assert phonetize("ци'рк") == 'тсИрк'
    assert phonetize("щи'т") == 'ШЧИт'
    assert phonetize("счё'т") == 'ШЧОт'

def test_consonant_voicing():
    assert phonetize("сво'д") == 'свОт'
    assert phonetize("пое'здка") == 'паЙЭстка'
    assert phonetize("ро'стбиф") == 'рОздБиф'
    assert phonetize("овца'") == 'афтсА'
    assert phonetize("плацда'рм") == 'пладздАрм'
    assert phonetize("ка'к бы") == 'кАгби'

def test_cluster_simplification():
    assert phonetize("ле'стница") == 'ЛЭсНитса'
    assert phonetize("по'здно") == 'пОзна'

def test_gen_sg_adj_endings():
    assert phonetize("его'") == 'ЙивО'
    assert phonetize("зло'го") == 'злОва'
    assert phonetize("кра'сного") == 'крАснава'
    assert phonetize("си'него") == 'СИНива'
    assert phonetize("боя'вшегося") == 'баЙАфшиваСа'
    assert phonetize("кого'-нибудь") == 'кавОНибуТ'

def test_reflexive_verbs():
    assert phonetize("куса'лся") == 'кусАлСа'
    assert phonetize("куса'ться") == 'кусАтса'
    assert phonetize("куса'ется") == 'кусАЙитса'

def test_orthographic_pangram():
    assert (phonetize("э`кс-гра'ф, плю'ш изъя'т, бьё'м чу'ждый це'н хво'щ")
        == 'эгзгрАфпЛУшЙизЙАдБЙОмЧУждиЙтсЭнхвОШЧ')
