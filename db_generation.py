"""Makes the database from the plaintext dictionary."""

from typing import List, Iterable
import re
import itertools as it
import more_itertools as mit
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from functools import reduce

from phonetics.phonetizer import phonetize
from phonetics.rhymer import Rhyme
from data.data_model import engine, Base, Word

usable_form_pattern = re.compile(r'^\s*[^\s*]')  # form does not start with *

def strip_article(article: Iterable[List[str]]) -> List[List[str]]:
    """Removes unused (marked with *) and identical forms from an article."""
    usable_forms = [row for row in article if usable_form_pattern.match(row[0])]
    unique_forms = list(mit.unique_everseen(usable_forms, lambda row: row[2]))
    if len(unique_forms) < len(usable_forms):
        for un in unique_forms:
            grams = [r[1].strip().split(" ") for r in usable_forms if r[2] == un[2]]
            newgrams = set()
            for g in grams:
                newgrams.update(set(g))
            un[1] = " " + " ".join(list(newgrams)) + " "
    return unique_forms

def row_to_word(row: List[str], lemma: List[str]) -> Word:
    word_id = int(row[-1].strip())
    lemma_id = int(lemma[-1].strip())
    spell = row[0].strip().lower()
    trans = phonetize(row[2].strip().lower())
    rhyme = Rhyme(trans).get_basic_rhyme()
    gram = row[1]
    return Word(word_id, lemma_id, spell, trans, rhyme, gram)

def get_words_from_hagen_dictionary() -> Iterable[Word]:
    with open('data/hagen-morph.txt', encoding='windows-1251') as file:
        rows = (line.split('|') for line in file)
        articles = mit.split_at(rows, lambda row: len(row) < 4)
        stripped_articles = map(strip_article, articles)
        # TODO: make more readable:
        words = (row_to_word(row, article[0]) for article in stripped_articles for row in article)
        yield  from words

def generate_db() -> None:
    started = datetime.now()
    print(f'Started: {started}')
    
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print('Clearing the db table...')
    session.query(Word).delete()
    
    print('Populating the db table from the dictionary file:')
    words = get_words_from_hagen_dictionary()
    
    chunks = mit.chunked(words, 100_000)
    for index, chunk in enumerate(chunks):
        print(f' chunk {index} ({chunk[0].spell} — {chunk[-1].spell})...')
        session.bulk_save_objects(chunk)
    
    print('Committing data into the db...')
    session.commit()
    
    finished = datetime.now()
    print(f'Finished: {finished}')
    print(f'Elapsed: {finished - started}')


if __name__ == '__main__':
    generate_db()
