from __future__ import annotations
from typing import Optional
import re
from .repertoire import vowels, stressed_vowels, consonants, unvoice
from .distance import Distance

class Syllable:
    def __init__(self, parts: re.Match) -> None:
        self.consonants = parts['cons']
        self.vowel = parts['vowel']

class Rhyme:
    def __init__(self, parts: re.Match) -> None:
        self.pretonic_part = parts['pre']
        self.stressed_vowel = parts['stress']
        posttonic = split_into_syllables.finditer(parts['post'])
        self.posttonic_syllables = [Syllable(match) for match in posttonic]
        self.final_consonant = parts['final']
    
    @classmethod
    def from_transcription(cls, transcription: str) -> Optional[Rhyme]:
        parts = split_into_parts.match(transcription)
        return cls(parts) if parts is not None else None
    
    def __repr__(self) -> str:
        post = '.'.join(s.consonants + s.vowel for s in self.posttonic_syllables)
        return f'{self.pretonic_part}[{self.stressed_vowel}]{post}|{self.final_consonant}'
    
    def get_basic_rhyme(self) -> str:
        posttonic = ''.join(unvoice(s.consonants) + 'i' for s in self.posttonic_syllables)
        if posttonic:
            return self.stressed_vowel + posttonic
        elif self.final_consonant:
            return self.stressed_vowel + self.final_consonant
        else:
            return self.pretonic_part[-1:] + self.stressed_vowel


def normalized_rhyme_distance(trans1: str, trans2: str) -> float:
    """Returns the rhyme distance between two transcriptions
    normalized so that the value is in [0; 1].
    """
    # TODO: add actual distance calculation! 
    return min(1.0, len(trans2) / 20.0)  # makes no sense, just to return something


# regexps:

split_into_parts = re.compile(rf'''^
    (?P<pre>.*)
    (?P<stress>[{stressed_vowels}])
    (?P<post>.*?)
    (?P<final>[{consonants}]*)
    $''', re.VERBOSE)

split_into_syllables = re.compile(rf'(?P<cons>[{consonants}]*)(?P<vowel>[{vowels}])')
