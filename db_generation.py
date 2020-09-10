"""Makes the database from the plaintext dictionary."""

import more_itertools as mit
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from data.data_model import engine, Base, Word
import hagen

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
        words = hagen.get_words()
        
        chunks = mit.chunked(words, 100_000)
        for index, chunk in enumerate(chunks):
            print(f' chunk {index} ({chunk[0].spell} — {chunk[-1].spell})...')
            session.bulk_save_objects(chunk)
        
        print('Committing data into the db...')
        session.commit()
    finally:
        session.close()
    
    print('Vacuuming the db...')
    with engine.connect() as connection:
        connection.execute("VACUUM")
    
    finished = datetime.now()
    print(f'Finished: {finished}')
    print(f'Elapsed: {finished - started}')

if __name__ == '__main__':
    generate_db()
