from typing import Iterable, List, Dict
import more_itertools as mit
from data.data_model import Word
from phonetics.phonetizer import phonetize
from phonetics.rhymer import Rhyme

file_name = 'data/hagen-morph.txt'
file_encoding = 'windows-1251'

class Row:
    def __init__(self, line: str) -> None:
        parts = line.split('|')
        self.spell = parts[0].strip().lower()
        self.gram  = set(gram_abbr[g] for g in parts[1].split())
        self.accented_spell = parts[2].strip().lower()
        self.id = int(parts[-1].strip())

class Article:
    def __init__(self, lines: List[str]) -> None:
        # removing lines marked with *
        usable_lines = (l for l in lines if not l.startswith('*'))
        
        rows = (Row(l) for l in usable_lines)
        unique_rows = self.combine_identical_forms(rows)
        
        self.rows = unique_rows
        self.id = unique_rows[0].id if len(self.rows) > 0 else 0
    
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


def get_hagen_words() -> Iterable[Word]:
    for article in get_hagen_articles():
        yield from get_article_words(article)

def get_hagen_articles() -> Iterable[Article]:
    with open(file_name, encoding=file_encoding) as file:
        lines = (line.strip() for line in file)
        line_groups = mit.split_at(lines, lambda line: line == '')
        articles = (Article(group) for group in line_groups)
        yield from articles

def get_article_words(article: Article) -> Iterable[Word]:
    for row in article.rows:
        trans = phonetize(row.accented_spell)
        rhyme = Rhyme(trans).get_basic_rhyme()
        gram = ''.join(row.gram)
        yield Word(row.id, article.id, row.spell, trans, rhyme, gram)

gram_abbr = {
    'сущ'   : 'Nn',
    'прл'   : 'Ad',
    'гл'    : 'Vb',
    'нар'   : 'Av',
    'мест'  : 'Pn',
    'числ'  : 'Nu',
    'прч'   : 'Pc',
    'дееп'  : 'Tg',
    'межд'  : 'Ij',
    'предл' : 'Pp',
    'союз'  : 'Cj',
    'част'  : 'Pi',
    'предик': 'Pd',
    'ввод'  : 'Ph',
    'нескл' : 'Id',
    'им'    : 'No',
    'род'   : 'Ge',
    'дат'   : 'Da',
    'вин'   : 'Ac',
    'тв'    : 'In',
    'пр'    : 'Lo',
    'парт'  : 'Pa',
    'счет'  : 'Cn',
    'зват'  : 'Vo',
    'ед'    : 'Sg',
    'мн'    : 'Pl',
    'муж'   : 'Ma',
    'жен'   : 'Fe',
    'ср'    : 'Ne',
    'общ'   : 'Co',
    'неод'  : 'Ia',
    'одуш'  : 'An',
    'крат'  : 'Br',
    'сравн' : 'Cm',
    'прев'  : 'Sl',
    'неизм' : 'Al',
    'инф'   : 'If',
    'пов'   : 'Ip',
    '2вид'  : 'Ba',
    'прош'  : 'Pt',
    'наст'  : 'Pr',
    'буд'   : 'Fu',
    'несов' : 'Im',
    'сов'   : 'Pf',
    'безл'  : 'Il',
    'непер' : 'It',
    'воз'   : 'Rf',
    'перех' : 'Tr',
    'пер/не': 'Ti',
    'страд' : 'Pv',
    '1-е'   : '1p',
    '2-е'   : '2p',
    '3-е'   : '3p',
    'неопр' : 'Ie',
    'кол'   : 'Cr',
    'поряд' : 'Or',
    'собир' : 'Cl',
    'вопр'  : 'Qs',
    'опред' : 'Df',
    'обст'  : 'Aj',
    'кач'   : 'Qu',
    'спос'  : 'Md',
    'степ'  : 'Dg',
    'врем'  : 'Tm',
    'места' : 'Lc',
    'напр'  : 'Dr',
    'причин': 'Cs',
    'цель'  : 'Oj',
}
