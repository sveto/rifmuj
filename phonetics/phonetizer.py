from __future__ import annotations
from typing import List, Dict, Callable, Type, TypeVar, Match
from enum import Enum, auto
import re
import functools as ft
from .repertoire import *

class VowelPosition(Enum):
    after_hard = auto()
    after_soft = auto()
    isolated   = auto()
VP = VowelPosition  # a short alias

class VowelStress(Enum):
    stressed         = auto()
    semistressed     = auto()
    unstressed_final = auto()
    unstressed       = auto()
VS = VowelStress  # a short alias

def detect_stress(match: Match) -> VowelStress:
    accent = match.group('accent')
    if   accent == "'": return VS.stressed
    elif accent == "`": return VS.semistressed
    elif match.group('word_end') is not None: return VS.unstressed_final
    else: return VS.unstressed

def phonetize_vowel(position: VowelPosition, stress: VowelStress, vowel: str) -> str:
    ph = phonemize(vowel)
    if   stress == VS.stressed: return ph.upper()
    elif stress == VS.semistressed: return ph
    elif stress == VS.unstressed_final:
        if position == VP.isolated: return ph
        else: return reduct_less(ph)
    else:
        if position == VP.after_soft: return reduct_more(ph)
        else: return reduct_less(ph)


TCaseEnum = TypeVar('TCaseEnum', bound=Enum)
class PhonTransform:
    """Represents a string transformation.
    Replaces every match of the search pattern in the input string
    with the result of the substitution function.
    
    Use classmethods to create transformations of different types.
    """
    def __init__(self, search_pattern: str, sub_func: Callable[[Match], str]) -> None:
        self.searchPattern = re.compile(search_pattern, re.VERBOSE)
        self.sub_func = sub_func
    
    def apply_to(self, string: str) -> str:
        """Returns the result of the transformation application to the argument string."""
        return self.searchPattern.sub(self.sub_func, string)
    
    @classmethod
    def replacement(cls, search_pattern: str, replacement: str) -> PhonTransform:
        """The most simple transformation type.
        Replaces all matches of the `search_pattern` with the `replacement` string.
        """
        sub_func = lambda match: replacement
        return cls(search_pattern, sub_func)
    
    @classmethod
    def rules(cls, search_pattern: str, *rules: Dict[str, str]) -> PhonTransform:
        """Dictionary-based transformation type.
        Replaces each key matching the `search_pattern`
        with the corresponding value from the dictionary.
        
        For convenience, the dictionary is split into `rules`. Each rule
        is a small sub-dictionary defining a part of possible situations.
        
        When combining rules into a single dictionary, the latest
        rules in the list have priority over the preceding ones.
        """
        rule_dict = {k: v for rule in rules for k, v in rule.items()}
        sub_func = lambda match: rule_dict[match.group()]
        return cls(search_pattern, sub_func)
    
    @classmethod
    def rules_with_cases(cls, search_pattern: str, CaseEnum: Type[TCaseEnum], detect_case: Callable[[Match], TCaseEnum], rules: Callable[[TCaseEnum], List[Dict[str, str]]]) -> PhonTransform:
        """This type of transformation is similar to the previous one,
        but more flexible.
        
        The `rules` are defined using a lambda whitch can return different 
        lists of rules in different cases from the `CaseEnum` enumeration.
        
        When a match of the `search_pattern` occurs, the `detect_case` function
        determines whitch case corresponds to the current match, and the replacement
        string is taken from the corresponding list of rules.
        
        The group of the `search_pattern` named `key` is used as the dictionary key,
        not the whole match. The pattern can also define other groups that can be
        analyzed in the `detect_case` function.
        """
        cases: List[TCaseEnum] = list(CaseEnum)
        rule_dict = {case: {k: v for rule in rules(case) for k, v in rule.items()} for case in cases}
        sub_func = lambda match: rule_dict[detect_case(match)][match.group('key')]
        return cls(search_pattern, sub_func)


# List of transformations used in the `phonetize` function.
# The order is significant: the transformations are applied in that order.
phon_transforms = [
    
    # genitive singular adjective endings
    PhonTransform.rules(
        rf"[ое]'?го'?(?:ся)?(?=$|[{separators}])",
        # different stress positions:
        {f"{v}го{r}":  f"{v}во{r}"  for v in 'ое' for r in ['', 'ся']},
        {f"{v}'го{r}": f"{v}'во{r}" for v in 'ое' for r in ['', 'ся']},
        {f"{v}го'{r}": f"{v}во'{r}" for v in 'ое' for r in ['', 'ся']}
    ),
    
    # softness and stress
    PhonTransform.rules_with_cases(
        rf'''(?P<key>[{consonants}]ьо                    # special case: consonant + ьо
                    |[{consonants}]?[{vowels}{signs}]    # optional consonant, then, vowel or sign
                    |[{soft_only_cons}]                  # soft-only consonant that should be uppercased
             )(?P<accent>[{accents}]?)(?P<word_end>\b)?  # groups for stress type detection
          ''',
        VowelStress,
        detect_stress,
        lambda stress: [
            # -ьо:
            {f'{c}ьо': f'{c.upper()}Й{phonetize_vowel(VP.after_soft, stress, "о")}' for c in consonants},
            {f'{hc}ьо': f'{hc}Й{phonetize_vowel(VP.after_soft, stress, "о")}' for hc in hard_only_cons},
            # vowel:
            {f'{v}': f'{phonetize_vowel(VP.isolated, stress, v)}' for v in plain_vowels},
            {f'{jv}': f'Й{phonetize_vowel(VP.after_soft, stress, jv)}' for jv in jot_vowels},
            # vowel + consonant:
            {f'{c}{v}': f'{c}{phonetize_vowel(VP.after_hard, stress, v)}' for c in consonants for v in vowels},
            {f'{sc}{jv}': f'{sc.upper()}{phonetize_vowel(VP.after_soft, stress, jv)}' for sc in softable_cons for jv in jot_vowels},
            {f'{soc}{v}': f'{soc.upper()}{phonetize_vowel(VP.after_soft, stress, v)}' for soc in soft_only_cons for v in vowels},
            # consonant:
            {f'{c}{s}': f'{c}' for c in consonants for s in signs},
            {f'{sc}ь': f'{sc.upper()}' for sc in softable_cons},
            {f'{soc}{s}': f'{soc.upper()}' for soc in soft_only_cons for s in signs},
            {f'{soc}': f'{soc.upper()}' for soc in soft_only_cons},
            # incorrect formating in the file:
            {f'{s}': '' for s in signs}
        ]
    ),
    
    # consonant clusters
    PhonTransform.rules(
        r'''[тТ]Са\b          # reflexive verb endings
           |[цЩ]|[сСшзЗж]Ч    # complex consonants
           |[сСзЗ][тТдД][нН]  # cluster simplification
         ''',
        # reflexive verb endings
        {f'{t}Са': 'тса' for t in 'тТ'},
        # complex consonants
        {'ц': 'тс'},
        {'Ч': 'ТШ'},
        {cc: 'Ш' for cc in ['Щ', 'сЧ', 'СЧ', 'шЧ', 'зЧ', 'ЗЧ', 'жЧ']},
        # cluster simplification:
        {f'{s}{t}{n}': f'{s}{n}' for s in 'сСзЗ' for t in 'тТдД' for n in 'нН'}
    ),
    
    # removing word separators
    PhonTransform.replacement(rf'[{separators}]+', ''),
    
    # assimilation by voiceness
    PhonTransform.rules(
        rf'''[{voiceable_cons}]{{1,2}}(?=[{voicing_cons}])         # unvoiced cluster before a voicing consonant
            |[{unvoiceable_cons}]{{1,2}}(?=[{unvoicing_cons}]|\b)  # voiced cluster before an unvoicing consonant or word-finally
          ''',
        # voicing:
        {f'{c}': f'{voice(c)}' for c in voiceable_cons},
        {f'{c1}{c2}': f'{voice(c1)}{voice(c2)}' for c1 in voiceable_cons for c2 in voiceable_cons},
        # unvoicing:
        {f'{c}': f'{unvoice(c)}' for c in unvoiceable_cons},
        {f'{c1}{c2}': f'{unvoice(c1)}{unvoice(c2)}' for c1 in unvoiceable_cons for c2 in unvoiceable_cons},
    ),
    
    # removing repeating consonants
    PhonTransform.rules(
        rf'(?i)([{consonants}])\1', # the same consonant twice, case insensitive
        {f'{c}{c}': c for c in consonants + consonants.upper()},
        {f'{c.upper()}{c}': c for c in consonants},
        {f'{c}{c.upper()}': c.upper() for c in consonants}
    ),
]


def phonetize(accented_spell: str) -> str:
    """Returns the phonetic transcription of a word by its accented spelling.
    Examples can be found in `test_phonetize.py`.
    """
    result = accented_spell
    for t in phon_transforms:
        result = t.apply_to(result)
    return result
