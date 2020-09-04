from typing import Iterable, List, Tuple, Optional
import itertools as it
import more_itertools as mit
from sqlalchemy.orm import Session, sessionmaker
from .phonetics.phonetizer import phonetize
from .phonetics.rhymer import Rhyme
from .data.data_model import engine, Word

Session = sessionmaker(bind=engine)

def lookup_rhymes(
    query: str,
    xj: bool = False,
    zv: bool = False,
    uu: bool = False,
    yy: bool = False,
    nu: int = 0
) -> List[str]:
    session = Session()
    spell = normalize_accent_marks(query.strip().lower())
    
    word = lookup_word(session, spell)
    if word is None:
        trans = phonetize(spell)
        rhyme = Rhyme(trans).get_basic_rhyme()
        word = Word(0, 0, spell, trans, rhyme, '')
    
    
    return group_by_lemma(lookup_rhyming_words(session, word, xj, zv, uu, yy, nu))

def lookup_rhyming_words(
    session: Session, 
    word: Word,
    xj: bool = False,
    zv: bool = False,
    uu: bool = False,
    yy: bool = False,
    nu: int = 0
) -> Iterable[Tuple[int, str]]:
    words = (session.query(Word.lemma_id, Word.spell)
        .filter(Word.rhyme == word.rhyme)
        .filter(Word.lemma_id != word.lemma_id)
        .order_by(Word.lemma_id)
    )
    # TODO: filter using xj, zv, uu, yy, and nu
    return words

def group_by_lemma(words: Iterable[Tuple[int, str]]) -> List[str]:
    lemmas = mit.groupby_transform(words, lambda w: w[0], lambda w: w[1])
    result = (group_word_forms(list(forms)) for lemma, forms in lemmas)
    return list(sorted(result))

def group_word_forms(forms: List[str]) -> str:
    if len(forms) > 1:
        common_prefix_len = min(len(form) for form in forms)
        while not mit.all_equal(form[:common_prefix_len] for form in forms):
            common_prefix_len -=1
        return forms[0] + ', ' + ', '.join(f'-{form[common_prefix_len:]}' for form in forms[1:])
    else:
        return forms[0]
    

def lookup_word(session: Session, spell: str) -> Word:
    return session.query(Word).filter_by(spell=spell).first()

def normalize_accent_marks(word: str) -> str:
    return (word
        .replace("_", "'")
        .replace("\N{COMBINING ACUTE ACCENT}", "'"))
