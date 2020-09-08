from phonetics.phonetizer import phonetize

def test_jot_vowels_and_signs() -> None:
    assert phonetize("плю'нь") == 'pLUN'
    assert phonetize("илья'") == 'YiLYA'
    assert phonetize("съе'л") == 'sYEl'
    assert phonetize("почтальо'н") == 'paTCtaLYOn'
    assert phonetize("ло'жь") == 'lOc'

def test_vowel_reduction() -> None:
    assert phonetize("колесо'") == 'kaLisO'
    assert phonetize("бегемо`топодо'бный") == 'BiGimotapadObniY'
    assert phonetize("лягу'шка") == 'LigUcka'
    assert phonetize("до'ля") == 'dOLa'
    assert phonetize("янта'рная") == 'YintArnaYa'
    assert phonetize("ра'дио") == 'rADio'

def test_complex_consonants() -> None:
    assert phonetize("ци'рк") == 'tsIrk'
    assert phonetize("ме'ч") == 'METC'
    assert phonetize("щи'т") == 'CIt'
    assert phonetize("счё'т") == 'COt'
    assert phonetize("вещдо'к") == 'ViJdOk'

def test_consonant_voicing() -> None:
    assert phonetize("сво'д") == 'svOt'
    assert phonetize("пое'здка") == 'paYEstka'
    assert phonetize("ро'стбиф") == 'rOzdBif'
    assert phonetize("овца'") == 'aftsA'
    assert phonetize("плацда'рм") == 'pladzdArm'
    assert phonetize("ка'к бы") == 'kAgbi'

def test_cluster_simplification() -> None:
    assert phonetize("ле'стница") == 'LEsNitsa'
    assert phonetize("по'здно") == 'pOzna'

def test_repeating_consonants() -> None:
    assert phonetize("рассо'л") == 'rasOl'
    assert phonetize("мета'лл") == 'MitAl'
    assert phonetize("металли'ст") == 'MitaLIst'
    assert phonetize("отда'ть") == 'adAT'

def test_gen_sg_adj_endings() -> None:
    assert phonetize("его'") == 'YivO'
    assert phonetize("зло'го") == 'zlOva'
    assert phonetize("кра'сного") == 'krAsnava'
    assert phonetize("си'него") == 'SINiva'
    assert phonetize("боя'вшегося") == 'baYAfcivaSa'
    assert phonetize("кого'-нибудь") == 'kavONibuT'

def test_reflexive_verbs() -> None:
    assert phonetize("куса'лся") == 'kusAlSa'
    assert phonetize("куса'ться") == 'kusAtsa'
    assert phonetize("куса'ется") == 'kusAYitsa'

def test_orthographic_pangram() -> None:
    assert (phonetize("э`кс-гра'ф, плю'ш изъя'т, бьё'м чу'ждый це'н хво'щ")
        == 'egzgrAfpLUcYizYAdBYOmTCUjdiYtsEnxvOC')
