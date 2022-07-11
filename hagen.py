from typing import Iterable, List, Dict, Set, Type, TypeVar
from dataclasses import dataclass
import re
import more_itertools as mit
from data.data_model import Word
from phonetics.phonetizer import phonetize
from phonetics.rhyme import get_basic_rhyme
from phonetics.accent import normalize_accented_spell, normalize_spell
from morphology.features import morph_abbr

file_name = 'data/hagen-morph.txt'
file_encoding = 'windows-1251'

T = TypeVar('T', bound='Row')
@dataclass
class Row:
    id: int
    spell: str
    accented_spell: str
    gram: Set[str]
    
    @classmethod
    def from_line(cls: Type[T], line: str) -> T:
        parts = line.split('|')
        return cls(
            id=int(parts[-1].strip()),
            spell=normalize_spell(parts[0].strip()),
            accented_spell=normalize_accented_spell(parts[2].strip()),
            gram=set(morph_abbr[g] for g in parts[1].split() if g in morph_abbr)
        )

class Article:
    def __init__(self, lines: List[str]) -> None:
        # removing lines marked with *
        usable_lines = (l for l in lines if not l.startswith('*'))
        
        rows = (Row.from_line(l) for l in usable_lines)
        splitted_rows = (r for row in rows for r in self.split_double_accents(row))
        unique_rows = self.combine_identical_forms(splitted_rows)
        
        self.rows = unique_rows
        self.id = unique_rows[0].id if len(self.rows) > 0 else 0
    
    double_accent = re.compile(r"^(.*)'(.*)'(.*)$")
    
    @staticmethod
    def split_double_accents(r: Row) -> Iterable[Row]:
        match = Article.double_accent.match(r.accented_spell)
        if match:
            accented_1 = f"{match[1]}'{match[2]}{match[3]}"
            accented_2 = f"{match[1]}{match[2]}'{match[3]}"
            yield Row(r.id, r.spell, accented_1, r.gram)
            yield Row(-r.id, r.spell, accented_2, r.gram)  # HACK: negative id 
        else:
            yield r
    
    @staticmethod
    def combine_identical_forms(rows: Iterable[Row]) -> List[Row]:
        """Leaves only unique forms unioning grammatical features."""
        groups: Dict[str, Row] = {}
        for row in rows:
            k = row.accented_spell
            if k not in groups:
                groups[k] = row
            else:
                groups[k].gram |= row.gram
        return list(groups.values())


def get_words() -> Iterable[Word]:
    for article in get_articles():
        yield from get_article_words(article)

def get_articles() -> Iterable[Article]:
    with open(file_name, encoding=file_encoding) as file:
        lines = (line.strip() for line in file)
        line_groups = mit.split_at(lines, lambda line: line == '')
        articles = (Article(group) for group in line_groups)
        yield from articles

def get_article_words(article: Article) -> Iterable[Word]:
    for row in article.rows:
        trans = phonetize(row.accented_spell)
        basic_rhyme = get_basic_rhyme(trans)
        if basic_rhyme:
            gram = ''.join(row.gram)
            yield Word(row.id, article.id, row.spell, trans, basic_rhyme, gram)
