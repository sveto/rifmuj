"""Makes the database from the plaintext dictionary."""

import more_itertools as mit
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from data.data_model import engine, Base, Word
from hagen import get_hagen_words

def generate_db() -> None:
    started = datetime.now()
    print(f'Started: {started}')
    
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    
    session = Session()
    try:
        print('Clearing the db table...')
        session.query(Word).delete()
        
        print('Populating the db table from the dictionary file:')
        words = get_hagen_words()
        
        chunks = mit.chunked(words, 100_000)
        for index, chunk in enumerate(chunks):
            print(f' chunk {index} ({chunk[0].spell} — {chunk[-1].spell})...')
            session.bulk_save_objects(chunk)
        
        print('Committing data into the db...')
        session.commit()
    finally:
        session.close()
    
    finished = datetime.now()
    print(f'Finished: {finished}')
    print(f'Elapsed: {finished - started}')

if __name__ == '__main__':
    generate_db()
