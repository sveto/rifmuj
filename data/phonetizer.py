"""Makes the database from the plaintext dictionary."""

from typing import List, Tuple, Iterable, Dict, Set, Optional, Callable
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
cons = sonorant_cons + paired_voiced_cons + unpaired_unvoiced_cons + paired_unvoiced_cons
softable_cons = [c for c in cons if c not in hard_only_cons]
voiceable_cons = paired_unvoiced_cons + paired_unvoiced_cons.upper()
unvoiceable_cons = paired_voiced_cons + paired_voiced_cons.upper()
voicing_cons = paired_voiced_cons[1:] + paired_voiced_cons[1:].upper()  # without ‘в’
unvoicing_cons = unpaired_unvoiced_cons + unpaired_unvoiced_cons.upper() + voiceable_cons

def change(from_: str, to: str) -> Callable[[str], str]:
    changing_dict = {key: value for key, value in zip(from_, to)}
    return lambda s: changing_dict[s]

phonemize = change(vows, vow_phonemes + vow_phonemes)
reductLess = change(vow_phonemes, 'ииаау')
reductMore = change(vow_phonemes, 'ииииу')
voice = change(voiceable_cons, unvoiceable_cons)
unvoice = change(unvoiceable_cons, voiceable_cons)


class PhonTransform:
    def __init__(self, search_pattern: str, *rules: Dict[str, str]) -> None:
        self.searchPattern = re.compile(search_pattern, re.VERBOSE)
        rule_dict = {k: v for rule in rules for k, v in rule.items()}
        self.ruleFunc = lambda match: rule_dict[match.group()]
    
    def apply_to(self, word: str) -> str:
        return self.searchPattern.sub(self.ruleFunc, word)

phon_transforms = [
    # softness and stress
    PhonTransform(
        rf"""[{cons}]?[{vows}{signs}][{accents}]?  # optional consonant, then, vowel or sign, then, optional accent
           | [{soft_only_cons}]                    # soft-only consonant that should be uppercased """,
        # vowel:
        {f'{v}{a}': f'{phonemize(v).upper()}' for v in plain_vows for a in accents},
        {f'{jv}{a}': f'Й{phonemize(jv).upper()}' for jv in jot_vows for a in accents},
        {f'{v}': f'{reductLess(phonemize(v))}' for v in plain_vows},
        {f'{jv}': f'Й{reductMore(phonemize(jv))}' for jv in jot_vows},
        # vowel + consonant:
        {f'{c}{v}{a}': f'{c}{phonemize(v).upper()}' for c in cons for v in vows for a in accents},
        {f'{sc}{jv}{a}': f'{sc.upper()}{phonemize(jv).upper()}' for sc in softable_cons for jv in jot_vows for a in accents},
        {f'{soc}{v}{a}': f'{soc.upper()}{phonemize(v).upper()}' for soc in soft_only_cons for v in vows for a in accents},
        {f'{c}{v}': f'{c}{reductLess(phonemize(v))}' for c in cons for v in vows},
        {f'{sc}{jv}': f'{sc.upper()}{reductMore(phonemize(jv))}' for sc in softable_cons for jv in jot_vows},
        {f'{soc}{v}': f'{soc.upper()}{reductMore(phonemize(v))}' for soc in soft_only_cons for v in vows},
        # consonant:
        {f'{c}{s}': f'{c}' for c in cons for s in signs},
        {f'{sc}ь': f'{sc.upper()}' for sc in softable_cons},
        {f'{soc}{s}': f'{soc.upper()}' for soc in soft_only_cons for s in signs},
        {f'{soc}': f'{soc.upper()}' for soc in soft_only_cons},
        # incorrect formating in the file:
        {f'{s}': f'' for s in signs},
        {f'{s}{a}': f'' for s in signs for a in accents},
        {f'{c}{s}{a}': f'{c}' for c in cons for s in signs for a in accents}
    ),
    # voicing and cluster simplification
    PhonTransform(
        rf"""[{voiceable_cons}]{{1,2}}(?=[{voicing_cons}])         # unvoiced cluster before a voicing consonant
           | [{unvoiceable_cons}]{{1,2}}(?=[{unvoicing_cons}]|\b)  # voiced cluster before an unvoicing consonant or word-finally
           # TODO: cluster simplification """,
        # voicing:
        {f'{c}': f'{voice(c)}' for c in voiceable_cons},
        {f'{c1}{c2}': f'{voice(c1)}{voice(c2)}' for c1 in voiceable_cons for c2 in voiceable_cons},
        # unvoicing:
        {f'{c}': f'{unvoice(c)}' for c in unvoiceable_cons},
        {f'{c1}{c2}': f'{unvoice(c1)}{unvoice(c2)}' for c1 in unvoiceable_cons for c2 in unvoiceable_cons},
        # cluster simplification:
        # TODO
    )
]

# TODO: allow exceptions from this rule!
ogo_pattern = re.compile(r"((?:о|е)'?)г(о'?(?:ся)?)$")

def phonetize(raw_trans: str) -> str:
    trans = ogo_pattern.sub(r"\1в\2", raw_trans)
    return ft.reduce(lambda w, t: t.apply_to(w), phon_transforms, trans)


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
