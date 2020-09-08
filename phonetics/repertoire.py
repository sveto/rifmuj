from typing import Dict, Callable

separators = ' ,-'
accents = "'`"

# Letters
sign_ltrs = 'ъь'
plain_vowel_ltrs = 'ыэаоу'
jot_vowel_ltrs   = 'иеяёю'
vowel_ltrs = plain_vowel_ltrs + jot_vowel_ltrs
consonant_ltrs = 'ймнлрфптсшкхвбдзжгhцчщ'
soft_only_cons_ltrs = 'йчщ'
hard_only_cons_ltrs = 'жшц'
softable_cons_ltrs = [c for c in consonant_ltrs if c not in hard_only_cons_ltrs]

# Phonemes
# (uppercase vowel phonemes are stressed, uppercase consonant phonemes are palatalized)
vowels = 'ieaou'
stressed_vowels = vowels.upper()
sonorant_cons = 'ymnlr'
paired_voiced_cons   = 'vbdzjgh'
paired_unvoiced_cons = 'fptsckx'
voiceable_cons = paired_unvoiced_cons + paired_unvoiced_cons.upper()
unvoiceable_cons = paired_voiced_cons + paired_voiced_cons.upper()
voicing_cons = paired_voiced_cons[1:] + paired_voiced_cons[1:].upper()  # without [v]
consonants = sonorant_cons + sonorant_cons.upper() + unvoiceable_cons + voiceable_cons

def change(from_: str, to: str, also: Dict[str, str]={}) -> Callable[[str], str]:
    """Returns a string-transforming function which maps every character
    from `from_` in the input to the corresponding character in `to`.
    """
    changing_dict = {key: value for key, value in zip(from_, to)}
    changing_dict.update(also)
    return lambda s: ''.join(changing_dict.get(c, c) for c in s)

# Transformations
phonemize = change(
    plain_vowel_ltrs + jot_vowel_ltrs + consonant_ltrs,
    to=   vowels     +     vowels     + sonorant_cons + paired_unvoiced_cons + paired_voiced_cons,
    also={'ц': 'ts', 'ч': 'TC', 'щ': 'C'}
)
reduct_less = change(vowels, to='iiaau')
reduct_more = change(vowels, to='iiiiu')
voice = change(voiceable_cons, to=unvoiceable_cons)
unvoice = change(unvoiceable_cons, to=voiceable_cons)
