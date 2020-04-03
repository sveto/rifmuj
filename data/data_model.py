from sqlalchemy import create_engine, Table, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
engine = create_engine('sqlite:///database.sqlite', echo=False)


class Word(Base): # type: ignore
    __tablename__ = 'words'
    word_id = Column(Integer, primary_key=True)
    spell = Column(String)
    trans = Column(String)
    gram = Column(String)

    def __init__(self, word_id: int, spell: str, trans: str, gram: str) -> None:
        self.word_id = word_id
        self.spell = spell
        self.trans = trans
        self.gram = gram

    def __repr__(self) -> str:
        return f'#{self.word_id} {self.spell}: {self.trans} [{self.gram.strip()}]'
