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
plainVows   = 'ыэаоу'
jotVows     = 'иеяёю'
vowPhonemes = 'иэаоу'
signs = 'ъь'
sonorantCons = 'ймнлр'
unpairedUnvoicedCons = 'хцчщ'
pairedVoicedCons   = 'вбзджг'
pairedUnvoicedCons = 'фпстшк'
softOnlyCons = 'йчщ'
hardOnlyCons = 'жшц'

vows = plainVows + jotVows
cons = sonorantCons + pairedVoicedCons + unpairedUnvoicedCons + pairedUnvoicedCons
softableCons = [c for c in cons if c not in hardOnlyCons]
voiceableCons = pairedUnvoicedCons + pairedUnvoicedCons.upper()
unvoiceableCons = pairedVoicedCons + pairedVoicedCons.upper()
voicingCons = pairedVoicedCons[1:] + pairedVoicedCons[1:].upper()  # without ‘в’
unvoicingCons = unpairedUnvoicedCons + unpairedUnvoicedCons.upper() + voiceableCons

def change(from_: str, to: str) -> Callable[[str], str]:
    changingDict = {key: value for key, value in zip(from_, to)}
    return lambda s: changingDict[s]

phonemize = change(vows, vowPhonemes + vowPhonemes)
reductLess = change(vowPhonemes, 'ииаау')
reductMore = change(vowPhonemes, 'ииииу')
voice = change(voiceableCons, unvoiceableCons)
unvoice = change(unvoiceableCons, voiceableCons)


class PhonTransform:
    def __init__(self, searchPattern: str, *rules: Dict[str, str]) -> None:
        self.searchPattern = re.compile(searchPattern, re.VERBOSE)
        ruleDict = {k: v for rule in rules for k, v in rule.items()}
        self.ruleFunc = lambda match: ruleDict[match.group()]
    
    def applyTo(self, word: str) -> str:
        return self.searchPattern.sub(self.ruleFunc, word)

phonTransforms = [
    # softness and stress
    PhonTransform(
        rf"""[{cons}]?[{vows}{signs}][{accents}]?  # optional consonant, then, vowel or sign, then, optional accent
           | [{softOnlyCons}]                      # soft-only consonant that should be uppercased """,
        # vowel:
        {f'{v}{a}': f'{phonemize(v).upper()}' for v in plainVows for a in accents},
        {f'{jv}{a}': f'Й{phonemize(jv).upper()}' for jv in jotVows for a in accents},
        {f'{v}': f'{reductLess(phonemize(v))}' for v in plainVows},
        {f'{jv}': f'Й{reductMore(phonemize(jv))}' for jv in jotVows},
        # vowel + consonant:
        {f'{c}{v}{a}': f'{c}{phonemize(v).upper()}' for c in cons for v in vows for a in accents},
        {f'{sc}{jv}{a}': f'{sc.upper()}{phonemize(jv).upper()}' for sc in softableCons for jv in jotVows for a in accents},
        {f'{soc}{v}{a}': f'{soc.upper()}{phonemize(v).upper()}' for soc in softOnlyCons for v in vows for a in accents},
        {f'{c}{v}': f'{c}{reductLess(phonemize(v))}' for c in cons for v in vows},
        {f'{sc}{jv}': f'{sc.upper()}{reductMore(phonemize(jv))}' for sc in softableCons for jv in jotVows},
        {f'{soc}{v}': f'{soc.upper()}{reductMore(phonemize(v))}' for soc in softOnlyCons for v in vows},
        # consonant:
        {f'{c}{s}': f'{c}' for c in cons for s in signs},
        {f'{sc}ь': f'{sc.upper()}' for sc in softableCons},
        {f'{soc}{s}': f'{soc.upper()}' for soc in softOnlyCons for s in signs},
        {f'{soc}': f'{soc.upper()}' for soc in softOnlyCons},
        # incorrect formating in the file:
        {f'{s}': f'' for s in signs},
        {f'{s}{a}': f'' for s in signs for a in accents},
        {f'{c}{s}{a}': f'{c}' for c in cons for s in signs for a in accents}
    ),
    # voicing and cluster simplification
    PhonTransform(
        rf"""[{voiceableCons}]{{1,2}}(?=[{voicingCons}])         # unvoiced cluster before a voicing consonant
           | [{unvoiceableCons}]{{1,2}}(?=[{unvoicingCons}]|\b)  # voiced cluster before an unvoicing consonant or word-finally
           # TODO: cluster simplification """,
        # voicing:
        {f'{c}': f'{voice(c)}' for c in voiceableCons},
        {f'{c1}{c2}': f'{voice(c1)}{voice(c2)}' for c1 in voiceableCons for c2 in voiceableCons},
        # unvoicing:
        {f'{c}': f'{unvoice(c)}' for c in unvoiceableCons},
        {f'{c1}{c2}': f'{unvoice(c1)}{unvoice(c2)}' for c1 in unvoiceableCons for c2 in unvoiceableCons},
        # cluster simplification:
        # TODO
    )
]

# TODO: allow exceptions from this rule!
ogoPattern = re.compile(r"((?:о|е)'?)г(о'?(?:ся)?)$")

def phonetize(raw_trans: str) -> str:
    raw_trans = ogoPattern.sub(r"\1в\2", raw_trans)
    return ft.reduce(lambda w, t: t.applyTo(w), phonTransforms, raw_trans)


class TransWord(Base): # type: ignore
    __tablename__ = 'main'
    word = Column(String)
    gram = Column(String)
    trans = Column(String)
    word_id = Column(Integer, primary_key=True)
    starred = Column(Boolean)

    def __init__(self, word: str, gram: str, trans: str, word_id: int, starred: bool) -> None:
        self.word = word
        self.gram = gram
        self.trans = trans
        self.word_id = word_id
        self.starred = starred

    def __repr__(self) -> str:
        star = '*' if self.starred else ''
        return f"#{self.word_id} {star}{self.word}: {self.trans} [{self.gram.strip()}]"


def lineToWord(line: str) -> Optional[TransWord]:
    parts = line.split('|')
    if len(parts) >= 4:
        raw_word = parts[0].strip().lower()
        starred = raw_word.startswith('*')
        word = raw_word[1:] if starred else raw_word
        gram = parts[1]
        raw_trans = parts[2].strip().lower()
        trans = phonetize(raw_trans)
        word_id = int(parts[-1].strip())
        return TransWord(word, gram, trans, word_id, starred)
    else:
        return None


if __name__ == "__main__":
    started = datetime.now()
    print(f"Started: {started}")

    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    print('Clearing the db table...')
    session.query(TransWord).delete()

    print('Populating the db table from the dictionary file:')
    with open('hagen-morph.txt', encoding='windows-1251') as file:
        # with mp.Pool() as pool:
        #     optWords = pool.imap_unordered(lineToWord, file, chunksize=1_000)
            optWords = map(lineToWord, file)
            words = (word for word in optWords if word is not None)
            chunks = mit.chunked(words, 100_000)
            for index, chunk in enumerate(chunks):
                print(f' chunk {index} ({chunk[0].word} — {chunk[-1].word})...')
                session.bulk_save_objects(chunk)
    
    print('Committing data into the db...')
    session.commit()
    
    finished = datetime.now()
    print(f"Finished: {finished}")
    print(f"Elapsed: {finished - started}")
