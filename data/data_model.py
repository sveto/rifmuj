from sqlalchemy import create_engine, Table, Column, String, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
engine = create_engine('sqlite:///data/database.sqlite', echo=False)


class Word(Base): # type: ignore
    __tablename__ = 'words'
    word_id = Column(Integer, primary_key=True)
    lemma_id = Column(Integer, ForeignKey('words.word_id'))
    spell = Column(String)
    trans = Column(String)
    rhyme = Column(String, index=True)
    gram = Column(String)

    def __init__(self, word_id: int, lemma_id: int, spell: str, trans: str, rhyme: str, gram: str) -> None:
        self.word_id = word_id
        self.lemma_id = lemma_id
        self.spell = spell
        self.trans = trans
        self.rhyme = rhyme
        self.gram = gram

    def __repr__(self) -> str:
        return f'#{self.word_id} ({self.lemma_id}) {self.spell} [{self.trans}] -{self.rhyme} ({self.gram.strip()})'
