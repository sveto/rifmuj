from typing import Iterable, List, Tuple
import more_itertools as mit
import re
from .repertoire import *

def normalize_accented_spell(word: str) -> str:
    word = word.strip().lower()
    word = accent_replacements.sub("'", word)
    word = yo_with_optional_accent.sub("ё'", word)
    word = forbidden_char.sub('', word)
    return word

def normalize_spell(word: str) -> str:
    word = word.strip().lower()
    word = accent_replacements.sub('', word)
    word = yo_with_optional_accent.sub("е", word)
    word = forbidden_char.sub('', word)
    return word

def prettify_accent_marks(word: str) -> str:
    syllable_count = mit.ilen(s for s in spell_syllable.finditer(word) if s['vowel'])
    word = yo_with_optional_accent.sub('ё', word)
    return word.replace("'", '\N{COMBINING ACUTE ACCENT}' if syllable_count > 1 else '')

def is_correctly_accented(accented_spell: str) -> bool:
    return bool(correctly_accented.match(accented_spell))

def get_accent_variants(spell: str) -> Iterable[str]:
    syllables = list(spell_syllable.finditer(spell))
    if syllables[0]['vowel']:
        for i, syllable in enumerate(s for s in syllables if s['vowel']):
            if syllable['vowel'] == 'е':
                yield ''.join(s[0] + "'" if i == j else s[0] for j, s in enumerate(syllables))
                yield ''.join(s['cons'] + "ё'" if i == j else s[0] for j, s in enumerate(syllables))
            else:
                yield ''.join(s[0] + "'" if i == j else s[0] for j, s in enumerate(syllables))
    else:
        yield spell

def yoficate_by_transcription(spell: str, trans: str) -> str:
    syllables = zip(spell_syllable.finditer(spell), trans_syllable.finditer(trans))
    return ''.join(process_syllable(s, t, False) for s, t in syllables)

def get_accent_by_transcription(spell: str, trans: str) -> str:
    syllables = zip(spell_syllable.finditer(spell), trans_syllable.finditer(trans))
    return ''.join(process_syllable(s, t, True) for s, t in syllables)

def process_syllable(spell: re.Match, trans: re.Match, mark_stress: bool) -> str:
    if spell['vowel'] == 'е' and trans['stressed'] == 'O':
        return spell['cons'] + ("ё'" if mark_stress else 'ё')
    elif mark_stress and trans['stressed']:
        return spell[0] + "'"
    else:
        return spell[0]

forbidden_char = re.compile(rf'[^{re.escape(separators)}{accents}{sign_ltrs}{vowel_ltrs}{consonant_ltrs}]')
accent_replacements = re.compile(r"['_\N{COMBINING ACUTE ACCENT}]")
yo_with_optional_accent = re.compile(r"ё['`]?")
correctly_accented = re.compile(rf"^[^']*[{vowel_ltrs}]'[^']*$")

# These regexes find C*V syllables and a C+ cluster at the end if present
spell_syllable = re.compile(rf'(?P<cons>[^{vowel_ltrs}]*)(?P<vowel>[{vowel_ltrs}])|[^{vowel_ltrs}]+')
trans_syllable = re.compile(rf'[{consonants}]*(?:(?P<stressed>[{stressed_vowels}])|[{vowels}])|[{consonants}]+')
