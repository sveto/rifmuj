from typing import Iterable, List, Tuple
import re
from .repertoire import vowel_ltrs, sign_ltrs, vowels, stressed_vowels, consonants

def normalize_accent_marks(word: str) -> str:
    return accent_replacements.sub("'", word)

def prettify_accent_marks(word: str) -> str:
    return accent_replacements.sub('\N{COMBINING ACUTE ACCENT}', word)

def remove_accent_marks(word: str) -> str:
    # accent marks in `word` should already be normalized
    return word.replace("'", '')

def is_correctly_accented(word: str) -> bool:
    # accent marks in `word` should already be normalized
    return bool(correctly_accented.match(word))

def get_accent_by_transcription(spell: str, trans: str) -> str:
    syllables = zip(spell_syllable.finditer(spell), trans_syllable.finditer(trans))
    return ''.join(s[0] + "'" if t['stressed'] else s[0] for s, t in syllables)

def get_accent_variants(spell: str) -> Iterable[str]:
    syllables = list(spell_syllable.finditer(spell))
    if syllables[0]['vowel']:
        for i, _ in enumerate(s for s in syllables if s['vowel']):
            yield ''.join(s[0] + "'" if i == j else s[0] for j, s in enumerate(syllables))
    else:
        yield spell

accent_replacements = re.compile(r"['_\N{COMBINING ACUTE ACCENT}]")
correctly_accented = re.compile(rf"^[^']*[{vowel_ltrs}]'[^']*$")

# These regexes find C*V syllables and a C+ cluster at the end if present
spell_syllable = re.compile(rf'[^{vowel_ltrs}]*(?P<vowel>[{vowel_ltrs}])|[^{vowel_ltrs}]+')
trans_syllable = re.compile(rf'[{consonants}]*(?:(?P<stressed>[{stressed_vowels}])|[{vowels}])|[{consonants}]+')
