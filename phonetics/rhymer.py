from __future__ import annotations
from typing import List, Dict, Callable, Type, TypeVar, Match
from enum import Enum, auto
import re
import functools as ft
from .repertoire import *

class Rhyme:
    def __init__(self, transcription: str) -> None:
        parts = split_into_parts.match(transcription)
        if parts is not None:
            self.pretonic_part = parts.group('pre')
            self.stressed_vowel = parts.group('stress')
            self.posttonic_syllables = split_into_syllables.findall(parts.group('post'))
            self.final_consonant = parts.group('final')
        else:
            self.pretonic_part = transcription
            self.stressed_vowel = ''
            self.posttonic_syllables = []
            self.final_consonant = ''
    
    def __repr__(self) -> str:
        post = '.'.join(c + v for c, v in self.posttonic_syllables)
        return f'{self.pretonic_part}[{self.stressed_vowel}]{post}|{self.final_consonant}'
    
    def get_basic_rhyme(self) -> str:
        posttonic = ''.join(unvoice(c) + 'i' for c, v in self.posttonic_syllables)
        if posttonic:
            return self.stressed_vowel + posttonic
        elif self.final_consonant:
            return self.stressed_vowel + self.final_consonant
        else:
            return self.pretonic_part[-1:] + self.stressed_vowel


split_into_parts = re.compile(rf'''^
    (?P<pre>.*)
    (?P<stress>[{stressed_vowels}])
    (?P<post>.*?)
    (?P<final>[{consonants}]*)
    $''', re.VERBOSE)

split_into_syllables = re.compile(rf'([{consonants}]*)([{vowels}])')
