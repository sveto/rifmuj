from typing import Iterable, List, Dict, Tuple, Callable, TypeVar
from dataclasses import dataclass
from abc import ABC
import itertools as it
import more_itertools as mit
from random import randrange
from sqlalchemy.orm import Session, sessionmaker
from .phonetics.phonetizer import phonetize
from .phonetics.rhyme import Rhyme, normalized_rhyme_distance
from .phonetics.accent import *
from .data.data_model import engine, Word

@dataclass
class RhymeResult:
    rhyme: str
    distance: float

@dataclass
class LookupResult(ABC):
    prettified_input_word: str

@dataclass
class LookupResultVariants(LookupResult):
    variants: List[str]

@dataclass
class LookupResultRhymes(LookupResult):
    rhymes: List[List[RhymeResult]]

LookupResult.register(LookupResultVariants)
LookupResult.register(LookupResultRhymes)


Session = sessionmaker(bind=engine)

def lookup_word(query: str) -> LookupResult:
    """Returns an object containing
    the prettified version of the input word,
    and either a list of possible accented forms if there are more than one
    or a list of rhymes otherwise.
    """
    session = Session()
    try:
        normalized = normalize_accented_spell(query)
        is_accented = is_correctly_accented(normalized)
        spell = normalize_spell(normalized)
        
        words = get_words_by_spell(session, spell)
        
        # TODO: do something with the mess below
        
        words_by_accent = sorted(group_by(words, get_accent).items(), key=lambda aw: aw[0])
        if is_accented:
            words_by_accent = [(a, w) for a, w in words_by_accent if a == normalized]
        
        # the word is absent in the database
        if len(words_by_accent) == 0:
            variants = [normalized] if is_accented else get_accent_variants(spell)
            words_by_accent = [(accented, [create_word(spell, accented)]) for accented in variants]
        
        # more than one variant of accenting exist
        if len(words_by_accent) > 1:
            return LookupResultVariants(
                prettify_accent_marks(spell),
                [prettify_accent_marks(accented) for accented, _ in words_by_accent]
            )
        # only one variant of accenting exists
        else:
            accented, word_list = words_by_accent[0]
            # for now, just using the first word. TODO: use all words
            word = word_list[0]
            rhyming_words_with_dists = get_rhyming_words_with_dists(session, word)
            return LookupResultRhymes(
                prettify_accent_marks(accented),
                group_by_lemma(rhyming_words_with_dists)
            )
    finally:
        session.close()

def lookup_random_word() -> LookupResultRhymes:
    """Gets a random word from the db and returns an object containing
    the prettified version of the word and a list of its rhymes.
    """
    session = Session()
    try:
        count = session.query(Word.word_id).count()
        
        while True:
            random = randrange(count)
            word = session.query(Word).offset(random).limit(1).one()
            rhyming_words_with_dists = list(get_rhyming_words_with_dists(session, word))
            if len(rhyming_words_with_dists) > 0:
                break
            # try again if there are no rhymes
        
        accented = get_accent(word)
        return LookupResultRhymes(
            prettify_accent_marks(accented),
            group_by_lemma(rhyming_words_with_dists)
        )
    finally:
        session.close()


def create_word(spell: str, accented: str) -> Word:
    trans = phonetize(accented)
    rhyme = Rhyme.from_transcription(trans)
    basic_rhyme = rhyme.get_basic_rhyme() if rhyme is not None else ''
    return Word(0, 0, spell, trans, basic_rhyme, '')

def get_words_by_spell(session: Session, spell: str) -> Iterable[Word]:
    yield from session.query(Word).filter_by(spell=spell)

def get_rhyming_words_with_dists(session: Session, word: Word) -> Iterable[Tuple[Word, float]]:
    rhyming_words = (session.query(Word)
        .filter(Word.rhyme == word.rhyme)
        .filter(Word.lemma_id != word.lemma_id)
        .order_by(Word.lemma_id)
    )
    return ((rhyming_word, get_word_distance(word, rhyming_word)) for rhyming_word in rhyming_words)

def get_word_distance(w1: Word, w2: Word) -> float:
    return normalized_rhyme_distance(w1.trans, w2.trans)

def group_by_lemma(words_with_dists: Iterable[Tuple[Word, float]]) -> List[List[RhymeResult]]:
    lemmas = it.groupby(words_with_dists, lambda wd: wd[0].lemma_id)
    result = (group_word_forms([(yoficate_by_transcription(form.spell, form.trans), dist) for form, dist in forms_with_dists])
        for lemma, forms_with_dists in lemmas)
    return list(sorted(result, key=lambda lemma: lemma[0].distance))

def group_word_forms(forms_with_dists: List[Tuple[str, float]]) -> List[RhymeResult]:
    common_prefix_len = min(len(form) for form, _ in forms_with_dists)
    while not mit.all_equal(form[:common_prefix_len] for form, _ in forms_with_dists):
        common_prefix_len -=1
    
    forms_with_dists.sort(key=lambda fd: fd[1])
    base_form = forms_with_dists[0]
    flex_forms = ((f'-{form[common_prefix_len:]}', dist) for form, dist in forms_with_dists[1:])
    
    return [RhymeResult(form, dist) for form, dist in it.chain([base_form], flex_forms)]

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