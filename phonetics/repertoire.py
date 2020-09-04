from typing import Callable

separators = ' ,-'
accents = "'`"

# Letters
signs = 'ъь'
plain_vowels = 'ыэаоу'
jot_vowels   = 'иеяёю'
vowels = plain_vowels + jot_vowels
unpaired_unvoiced_cons = 'цчщ'
soft_only_cons = 'йчщ'
hard_only_cons = 'жшц'

# Letters and phonemes
# (uppercase vowel phonemes are stressed, uppercase consonant phonemes are palatalized)
vowel_phonemes = 'иэаоу'
sonorant_cons = 'ймнлр'
paired_voiced_cons   = 'бвдзжгh'
paired_unvoiced_cons = 'пфтсшкх'
consonants = sonorant_cons + paired_voiced_cons + paired_unvoiced_cons + unpaired_unvoiced_cons
softable_cons = [c for c in consonants if c not in hard_only_cons]
voiceable_cons = paired_unvoiced_cons + paired_unvoiced_cons.upper()
unvoiceable_cons = paired_voiced_cons + paired_voiced_cons.upper()
voicing_cons = paired_voiced_cons[1:] + paired_voiced_cons[1:].upper()  # without ‘в’
unvoicing_cons = unpaired_unvoiced_cons + unpaired_unvoiced_cons.upper() + voiceable_cons
stressed_vowel_phonemes = vowel_phonemes.upper()
consonant_phonemes = (sonorant_cons + paired_voiced_cons + paired_unvoiced_cons +
    sonorant_cons.upper() + paired_voiced_cons.upper() + paired_unvoiced_cons.upper())

def change(from_: str, to: str) -> Callable[[str], str]:
    """Returns a string-transforming function which maps every character
    from `from_` in the input to the corresponding character in `to`.
    """
    changing_dict = {key: value for key, value in zip(from_, to)}
    return lambda s: ''.join(changing_dict.get(c, c) for c in s)

# Transformations
phonemize = change(  plain_vowels + jot_vowels    ,
                to=vowel_phonemes + vowel_phonemes)
reduct_less = change(vowel_phonemes, to='ииаау')
reduct_more = change(vowel_phonemes, to='ииииу')
voice = change(voiceable_cons, to=unvoiceable_cons)
unvoice = change(unvoiceable_cons, to=voiceable_cons)
