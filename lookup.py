from typing import Iterable, List, Dict, Tuple, Callable, TypeVar
import more_itertools as mit
from sqlalchemy.orm import Session, sessionmaker
from .phonetics.phonetizer import phonetize
from .phonetics.rhymer import Rhyme
from .phonetics.accent import *
from .data.data_model import engine, Word

Session = sessionmaker(bind=engine)

def lookup_word(
    query: str,
    xj: bool = False,
    zv: bool = False,
    uu: bool = False,
    yy: bool = False,
    nu: int = 0
) -> Tuple[List[str], List[str]]:
    """Returns a list of possible accented forms and a list of rhymes.
    At least one of those is always empty.
    """
    # TODO: consider a more sane return type
    
    normalized = normalize_accent_marks(query)
    is_accented = is_correctly_accented(normalized)
    spell = remove_accent_marks(normalized)
    
    words = get_words_by_spell(spell)
    
    # TODO: do something with the mess below
    
    accented_words = sorted(group_by(words, get_accent).items(), key=lambda aw: aw[0])
    if is_accented:
        accented_words = [(a, w) for a, w in accented_words if a == normalized]
    
    # the word is absent in the database
    if len(accented_words) == 0:
        variants = [normalized] if is_accented else get_accent_variants(spell)
        accented_words = [(accented, [create_word(spell, accented)]) for accented in variants]
    
    # more than one variant of accenting exist
    if len(accented_words) > 1:
        return ([prettify_accent_marks(accented) for accented, _ in accented_words], [])
    # only one variant of accenting exists
    else:
        _, word_list = accented_words[0]
        print(f'len(word_list) = {len(word_list)}')
        # for now, just using the first word. TODO: use all words
        word = word_list[0]
        rhyming_words = get_rhyming_words(word, xj, zv, uu, yy, nu)
        return ([], group_by_lemma(rhyming_words))

def create_word(spell: str, accented: str) -> Word:
    trans = phonetize(accented)
    rhyme = Rhyme(trans).get_basic_rhyme()
    return Word(0, 0, spell, trans, rhyme, '')

def get_words_by_spell(spell: str) -> Iterable[Word]:
    session = Session()
    try:
        yield from session.query(Word).filter_by(spell=spell)
    finally:
        session.close()

def get_rhyming_words(
    word: Word,
    xj: bool = False,
    zv: bool = False,
    uu: bool = False,
    yy: bool = False,
    nu: int = 0
) -> Iterable[Word]:
    session = Session()
    try:
        words = (session.query(Word)
            .filter(Word.rhyme == word.rhyme)
            .filter(Word.lemma_id != word.lemma_id)
            .order_by(Word.lemma_id)
        )
        # TODO: filter using xj, zv, uu, yy, and nu
        return words
    finally:
        session.close()

def group_by_lemma(words: Iterable[Word]) -> List[str]:
    lemmas = mit.groupby_transform(words, lambda w: w.lemma_id, lambda w: w.spell)
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

def get_accent(word: Word) -> str:
    return get_accent_by_transcription(word.spell, word.trans)

# TODO: move
T = TypeVar('T')
K = TypeVar('K')
def group_by(iterable: Iterable[T], key: Callable[[T], K]) -> Dict[K, List[T]]:
    groups: Dict[K, List[T]] = {}
    for item in iterable:
        k = key(item)
        if k in groups: groups[k].append(item)
        else: groups[k] = [item]
    return groups