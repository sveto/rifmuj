"""Makes the database from the plaintext dictionary."""

from __future__ import annotations
from typing import List, Tuple, Iterable, Dict, Set, Optional, Callable, Type, TypeVar, Match
from enum import Enum, auto
import re
import functools as ft
import itertools as it
import more_itertools as mit
import multiprocessing as mp
from sqlalchemy import create_engine, Table, Column, String, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()
engine = create_engine('sqlite:///abcd.sqlite', echo=False)


bounds = ' ,-'
accents = "'`"
plain_vows   = 'ыэаоу'
jot_vows     = 'иеяёю'
vow_phonemes = 'иэаоу'
signs = 'ъь'
sonorant_cons = 'ймнлр'
unpaired_unvoiced_cons = 'хцчщ'
paired_voiced_cons   = 'вбзджг'
paired_unvoiced_cons = 'фпстшк'
soft_only_cons = 'йчщ'
hard_only_cons = 'жшц'

vows = plain_vows + jot_vows
cons = sonorant_cons + paired_voiced_cons + paired_unvoiced_cons + unpaired_unvoiced_cons
softable_cons = [c for c in cons if c not in hard_only_cons]
voiceable_cons = paired_unvoiced_cons + paired_unvoiced_cons.upper()
unvoiceable_cons = paired_voiced_cons + paired_voiced_cons.upper()
voicing_cons = paired_voiced_cons[1:] + paired_voiced_cons[1:].upper()  # without ‘в’
unvoicing_cons = unpaired_unvoiced_cons + unpaired_unvoiced_cons.upper() + voiceable_cons

def change(from_: str, to: str) -> Callable[[str], str]:
    changing_dict = {key: value for key, value in zip(from_, to)}
    return lambda s: changing_dict[s]

phonemize = change(vows, vow_phonemes + vow_phonemes)
reduct_less = change(vow_phonemes, 'ииаау')
reduct_more = change(vow_phonemes, 'ииииу')
voice = change(voiceable_cons, unvoiceable_cons)
unvoice = change(unvoiceable_cons, voiceable_cons)

class VowPosition(Enum):
    after_hard = auto()
    after_soft = auto()
    isolated   = auto()

class VowStress(Enum):
    stressed         = auto()
    semistressed     = auto()
    unstressed_final = auto()
    unstressed       = auto()

def detect_stress(match: Match) -> VowStress:
    accent = match.group('accent')
    if   accent == "'": return VowStress.stressed
    elif accent == "`": return VowStress.semistressed
    elif match.group('word_end') is not None: return VowStress.unstressed_final
    else: return VowStress.unstressed

def phonetize_vow(position: VowPosition, stress: VowStress, vow: str) -> str:
    ph = phonemize(vow)
    if   stress == VowStress.stressed: return ph.upper()
    elif stress == VowStress.semistressed: return ph
    elif stress == VowStress.unstressed_final:
        if position == VowPosition.isolated: return ph
        else: return reduct_less(ph)
    else:
        if position == VowPosition.after_soft: return reduct_more(ph)
        else: return reduct_less(ph)

TCaseEnum = TypeVar('TCaseEnum', bound=Enum)
class PhonTransform:
    def __init__(self, search_pattern: str, sub_func: Callable[[Match], str]) -> None:
        self.searchPattern = re.compile(search_pattern, re.VERBOSE)
        self.sub_func = sub_func
    
    def apply_to(self, word: str) -> str:
        return self.searchPattern.sub(self.sub_func, word)
    
    @classmethod
    def replacement(cls, search_pattern: str, replacement: str) -> PhonTransform:
        sub_func = lambda match: replacement
        return cls(search_pattern, sub_func)
    
    @classmethod
    def rules(cls, search_pattern: str, *rules: Dict[str, str]) -> PhonTransform:
        rule_dict = {k: v for rule in rules for k, v in rule.items()}
        sub_func = lambda match: rule_dict[match.group()]
        return cls(search_pattern, sub_func)
    
    @classmethod
    def rules_with_cases(cls, search_pattern: str, CaseEnum: Type[TCaseEnum], detect_case: Callable[[Match], TCaseEnum], rules: Callable[[TCaseEnum], List[Dict[str, str]]]) -> PhonTransform:
        cases: List[TCaseEnum] = list(CaseEnum)
        rule_dict = {case: {k: v for rule in rules(case) for k, v in rule.items()} for case in cases}
        sub_func = lambda match: rule_dict[detect_case(match)][match.group('base')]
        return cls(search_pattern, sub_func)

phon_transforms = [
    # genitive singular adjective endings
    PhonTransform.rules(
        fr"[ое]'?го'?(?:ся)?(?=$|[{bounds}])",
        {f"{v}го{r}":  f"{v}во{r}"  for v in 'ое' for r in ['', 'ся']},
        {f"{v}'го{r}": f"{v}'во{r}" for v in 'ое' for r in ['', 'ся']},
        {f"{v}го'{r}": f"{v}во'{r}" for v in 'ое' for r in ['', 'ся']}
    ),
    
    # softness and stress
    PhonTransform.rules_with_cases(
        rf"""(?P<base>[{cons}]ьо                         # special case: consonant + ьо
                     |[{cons}]?[{vows}{signs}]           # optional consonant, then, vowel or sign
                     |[{soft_only_cons}]                 # soft-only consonant that should be uppercased
             )(?P<accent>[{accents}]?)(?P<word_end>\b)?  # groups for stress type detection """,
        VowStress,
        detect_stress,
        lambda stress: [
            # -ьо:
            {f"{c}ьо": f"{c.upper()}Й{phonetize_vow(VowPosition.after_soft, stress, 'о')}" for c in cons},
            {f"{hc}ьо": f"{hc}Й{phonetize_vow(VowPosition.after_soft, stress, 'о')}" for hc in hard_only_cons},
            # vowel:
            {f"{v}": f"{phonetize_vow(VowPosition.isolated, stress, v)}" for v in plain_vows},
            {f"{jv}": f"Й{phonetize_vow(VowPosition.after_soft, stress, jv)}" for jv in jot_vows},
            # vowel + consonant:
            {f"{c}{v}": f"{c}{phonetize_vow(VowPosition.after_hard, stress, v)}" for c in cons for v in vows},
            {f"{sc}{jv}": f"{sc.upper()}{phonetize_vow(VowPosition.after_soft, stress, jv)}" for sc in softable_cons for jv in jot_vows},
            {f"{soc}{v}": f"{soc.upper()}{phonetize_vow(VowPosition.after_soft, stress, v)}" for soc in soft_only_cons for v in vows},
            # consonant:
            {f"{c}{s}": f"{c}" for c in cons for s in signs},
            {f"{sc}ь": f"{sc.upper()}" for sc in softable_cons},
            {f"{soc}{s}": f"{soc.upper()}" for soc in soft_only_cons for s in signs},
            {f"{soc}": f"{soc.upper()}" for soc in soft_only_cons},
            # incorrect formating in the file:
            {f"{s}": f'' for s in signs}
        ]
    ),
    
    # consonant clusters
    PhonTransform.rules(
        r"""[тТ]Са\b          # reflexive verb endings
           |[цЩ]|[сСшзЗж]Ч    # complex consonants
           |[сСзЗ][тТдД][нН]  # cluster simplification """,
        # reflexive verb endings
        {f"{t}Са": 'тса' for t in 'тТ'},
        # complex consonants
        {'ц': 'тс'},
        {cc: 'ШЧ' for cc in ['Щ', 'сЧ', 'СЧ', 'шЧ', 'зЧ', 'ЗЧ', 'жЧ']},
        # cluster simplification:
        {f"{s}{t}{n}": f"{s}{n}" for s in 'сСзЗ' for t in 'тТдД' for n in 'нН'}
    ),
    
    # removing word separators
    PhonTransform.replacement(rf"[{bounds}]+", ''),
    
    # assimilation by voiceness
    PhonTransform.rules(
        rf"""[{voiceable_cons}]{{1,2}}(?=[{voicing_cons}])         # unvoiced cluster before a voicing consonant
            |[{unvoiceable_cons}]{{1,2}}(?=[{unvoicing_cons}]|\b)  # voiced cluster before an unvoicing consonant or word-finally """,
        # voicing:
        {f"{c}": f"{voice(c)}" for c in voiceable_cons},
        {f"{c1}{c2}": f"{voice(c1)}{voice(c2)}" for c1 in voiceable_cons for c2 in voiceable_cons},
        # unvoicing:
        {f"{c}": f"{unvoice(c)}" for c in unvoiceable_cons},
        {f"{c1}{c2}": f"{unvoice(c1)}{unvoice(c2)}" for c1 in unvoiceable_cons for c2 in unvoiceable_cons},
    )
]

def phonetize(raw_trans: str) -> str:
    trans = ft.reduce(lambda w, t: t.apply_to(w), phon_transforms, raw_trans)
    return trans


class TransWord(Base): # type: ignore
    __tablename__ = 'main'
    word_id = Column(Integer, primary_key=True)
    word = Column(String)
    trans = Column(String)
    gram = Column(String)

    def __init__(self, word_id: int, word: str, trans: str, gram: str) -> None:
        self.word_id = word_id
        self.word = word
        self.trans = trans
        self.gram = gram

    def __repr__(self) -> str:
        return f'#{self.word_id} {self.word}: {self.trans} [{self.gram.strip()}]'


usable_form_pattern = re.compile(r"^\s*[^\s*]")  # form does not start with ‘*’

def strip_article(article: List[List[str]]) -> Iterable[List[str]]:
    """Removes unused (marked with *) and identical forms from an article."""
    usable_forms = (row for row in article if usable_form_pattern.match(row[0]))
    unique_forms = mit.unique_everseen(usable_forms, lambda row: row[2])
    return unique_forms

def row_to_word(row: List[str]) -> TransWord:
    return TransWord(
        word_id = int(row[-1].strip()),
        word = row[0].strip().lower(),
        trans = phonetize(row[2].strip().lower()),
        gram = row[1]
    )


if __name__ == '__main__':
    started = datetime.now()
    print(f'Started: {started}')
    
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print('Clearing the db table...')
    session.query(TransWord).delete()
    
    print('Populating the db table from the dictionary file:')
    with open('hagen-morph.txt', encoding='windows-1251') as file:
        rows = (line.split('|') for line in file)
        articles = mit.split_at(rows, lambda row: len(row) < 4)
        stripped_articles = map(strip_article, articles)
        stripped_article_rows = (row for article in stripped_articles for row in article)
        words = map(row_to_word, stripped_article_rows)
        
        chunks = mit.chunked(words, 100_000)
        for index, chunk in enumerate(chunks):
            print(f' chunk {index} ({chunk[0].word} — {chunk[-1].word})...')
            session.bulk_save_objects(chunk)
    
    print('Committing data into the db...')
    session.commit()
    
    finished = datetime.now()
    print(f'Finished: {finished}')
    print(f'Elapsed: {finished - started}')
