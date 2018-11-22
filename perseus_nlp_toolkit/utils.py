from collections import namedtuple
from requests import get
import re
import functools

def reverse_dict(dic):
    return {v: k for k, v in dic.items()}


pos = {'-': '-', "d": 'adverb', 'n': 'noun', 'm': 'numeral', 'p': 'pron', 'v': 'verb', 't': 'verb', 'x': 'irregular',
       'l': 'article', 'e': 'exclamation', 'a': 'adjective', 'r': 'preposition', 'c': 'conjunction', 'g': 'adverb',
       'u': 'punctuation', 'i': 'irregular', }

person = {'1': "1st", '-': '-', '3': '3rd', '2': '2nd'}
number = {'s': 'singular', '-': '-', 'p': 'plural', 'd': 'dual'}
tense = reverse_dict(
    {'imperfect': 'i', 'future': 'f', 'perfect': 'r', '-': '-', 'future_perfect': 't', 'aorist': 'a', 'pluperfect': 'l',
     'present': 'p'})
mood = reverse_dict(
    {'optative': 'o', '-': '-', 'imperative': 'm', 'indicative': 'i', 'infinitive': 'n', 'subjunctive': 's',
     'participle': 'p'})
voice = reverse_dict({'middle': 'm', 'passive': 'p', '-': '-', 'mediopassive': 'e', 'active': 'a'})
gender = reverse_dict({'neuter': 'n', 'masculine': 'm', 'feminine': 'f', '-': '-'})
case = reverse_dict({'accusative': 'a', 'nominative': 'n', 'vocative': 'v', '-': '-', 'dative': 'd', 'genitive': 'g'})
degree = reverse_dict({'superl': 's', '-': '-', 'comp': 'c'})


Sentence = namedtuple("Sentence", ["id", "document_id", "subdoc"])
Word = namedtuple("Word", ['id', 'form', 'lemma', 'postag', 'head', 'relation', 'cite'])
Artificial = namedtuple("Artificial", ['id', 'form', 'lemma', 'postag', 'head', 'relation', 'cite', 'type'])

class Morph():
    def __init__(self, tag):
        assert len(tag) == 9, "Tag: {} is invalid".format(tag)
        self.pos = pos[tag[0]]
        self.person = person[tag[1]]
        self.number = number[tag[2]]
        self.tense = tense[tag[3]]
        self.mood = mood[tag[4]]
        self.voice = voice[tag[5]]
        self.gender = gender[tag[6]]
        self.case = case[tag[7]]
        self.degree = degree[tag[8]]

    @property
    def full(self):
        return {'pos': self.pos, 'person': self.person, 'number': self.number, 'tense': self.tense, 'mood': self.mood,
                'voice': self.voice, 'gender': self.gender, 'case': self.case, 'degree': self.degree, }

@functools.lru_cache(maxsize=512)
def _is_morph_word(word):
    u = 'http://morph.perseids.org/analysis/word?lang=grc&engine=morpheusgrc&word={}'.format(word)
    j = get(u).json()
    try:
        hasBody = j["RDF"]["Annotation"]["hasBody"]
        isw = True
    except KeyError:
        isw = False
    return isw



def fix_bad_apostrophe_words(words):
    reg = re.compile("\u0313$")

    for i, w in enumerate(words):
        w = w.replace("\u02bc", "'")
        if w[-1] == "\u0313":
            if _is_morph_word(w) == False:
                words[i] = reg.sub("'", w)
    return words

def fix_bad_apostrophe_sents(sents):
    for s in sents:
        s = fix_bad_apostrophe_words(s)

    return sents