from __future__ import annotations
from typing import Optional
import itertools as it
import re
from .repertoire import vowels, stressed_vowels, consonants, unvoice
from .distance import Distance

class Syllable:
    def __init__(self, parts: re.Match) -> None:
        self.consonants = parts['cons']
        self.vowel = parts['vowel']

class Rhyme:
    def __init__(self, parts: re.Match) -> None:
        pretonic = split_syllable.finditer(parts['pre'])
        self.pretonic_syllables = [Syllable(match) for match in pretonic]
        
        stressed = split_syllable.match(parts['stress'])
        assert(stressed is not None)
        self.stressed_syllable = Syllable(stressed)
        
        posttonic = split_syllable.finditer(parts['post'])
        self.posttonic_syllables = [Syllable(match) for match in posttonic]
        
        self.final_consonants = parts['final']
    
    @classmethod
    def from_transcription(cls, transcription: str) -> Optional[Rhyme]:
        parts = split_by_stress.match(transcription)
        return cls(parts) if parts is not None else None


def get_basic_rhyme(transcription: str) -> str:
    rhyme = Rhyme.from_transcription(transcription)
    if rhyme is None:
        return ''
    
    stressed_vowel = rhyme.stressed_syllable.vowel
    posttonic_syl_count = len(rhyme.posttonic_syllables)
    
    if posttonic_syl_count > 0:
        posttonic_cluster = rhyme.posttonic_syllables[0].consonants
        cluster_last_cons = unvoice(posttonic_cluster[-1:])
        cluster_other_cons = '_' if len(posttonic_cluster) > 1 else ''
        return stressed_vowel + cluster_other_cons + cluster_last_cons + str(posttonic_syl_count)
    elif rhyme.final_consonants:
        return stressed_vowel + rhyme.final_consonants
    else:
        pretonic_cons = rhyme.stressed_syllable.consonants[-1:]
        return pretonic_cons + stressed_vowel

def normalized_rhyme_distance(trans1: str, trans2: str) -> float:
    """Returns the rhyme distance between two transcriptions
    normalized so that the value is in [0; 1].
    Only arguments with the same basic rhyme are valid!
    Distance is not commutative!
    """
    r1 = Rhyme.from_transcription(trans1)
    r2 = Rhyme.from_transcription(trans2)
    if r1 is None or r2 is None:
        return 1.0
    
    pretonic_syllables = ((s1, s2)
        for s1, s2 in it.zip_longest(r1.pretonic_syllables[::-1], r2.pretonic_syllables[::-1])
        if s1 is not None)
    pretonic_syl_dists = (
        syllable_distance(s1, s2, allow_wrong_voiceness=True) if s2 is not None else Distance(1.0)
        for s1, s2 in pretonic_syllables)
    pretonic_syl_weighted_dists = (
        dist * (pretonic_exp_base ** i)
        for i, dist in enumerate(pretonic_syl_dists))
    pretonic_dist = sum(pretonic_syl_weighted_dists, Distance.empty())
    
    stressed_syl_cons_dist = cluster_distance(
        r1.stressed_syllable.consonants,
        r2.stressed_syllable.consonants,
        allow_wrong_voiceness=True)
    
    posttonic_syllables = zip(r1.posttonic_syllables, r2.posttonic_syllables)
    posttonic_syl_dists = (syllable_distance(s1, s2) for s1, s2 in posttonic_syllables)
    posttonic_dist = sum(posttonic_syl_dists, Distance.empty())
    
    final_cons_dist = cluster_distance(r1.final_consonants, r2.final_consonants)
    
    distance = (
        pretonic_weight * pretonic_dist +
        stressed_syl_cons_weight * stressed_syl_cons_dist +
        posttonic_weight * posttonic_dist +
        final_cons_weight * final_cons_dist
    )
    return distance.normalized()


def phon_distance(ph1: str, ph2: str, allow_wrong_voiceness: bool=False) -> Distance:
    if ph1 == ph2:
        return Distance(0.0)
    elif allow_wrong_voiceness and unvoice(ph1) == unvoice(ph2):
        return Distance(wrong_voiceness_distance)
    else:
        return Distance(1.0)

def cluster_distance(cl1: str, cl2: str, allow_wrong_voiceness: bool=False) -> Distance:
    if len(cl1) != len(cl2):
        return Distance(1.0)
    elif len(cl1) == 0:
        return Distance(0.0)
    else:
        distances = (phon_distance(c1, c2, allow_wrong_voiceness) for c1, c2 in zip(cl1, cl2))
        return sum(distances, Distance.empty()) / len(cl1)

def syllable_distance(s1: Syllable, s2: Syllable, allow_wrong_voiceness: bool=False) -> Distance:
    return (cluster_distance(s1.consonants, s2.consonants, allow_wrong_voiceness) +
        vowel_to_cons_weight * phon_distance(s1.vowel, s2.vowel))

# constants:

wrong_voiceness_distance = 0.5  # in [0; 1]
vowel_to_cons_weight     = 1.5
pretonic_exp_base        = 0.7  # <= 1
pretonic_weight          = 0.2
stressed_syl_cons_weight = 0.8
posttonic_weight         = 1.2
final_cons_weight        = 1.0


# regexps:

split_by_stress = re.compile(rf'''^
    (?P<pre>.*?)
    (?P<stress>[{consonants}]*[{stressed_vowels}])
    (?P<post>.*?)
    (?P<final>[{consonants}]*)
    $''', re.VERBOSE)

split_syllable = re.compile(rf'(?P<cons>[{consonants}]*)(?P<vowel>[{vowels}])')
