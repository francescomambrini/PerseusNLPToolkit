from collections import namedtuple
from requests import get
import re
import functools
from nltk.internals import java, config_java
import os
import tempfile
from subprocess import PIPE

class MateCaller:
    def __init__(self, mate_folder, path_to_model, java_options="-Xmx3G"):
        self._java_options = java_options
        self._mate_root = mate_folder
        self._model = path_to_model
        self._classpath = "anna-3.61.jar"

        # Configure java.
        config_java(options=self._java_options)

    def _execute(self, java_class, infile, outfile):
        cwd = os.getcwd()
        os.chdir(self._mate_root)
        os.chdir(self._mate_root)
        cmd = [java_class, "-model", self._model, "-test", infile, "-out", outfile]
        stdout, stderr = java(cmd, classpath=self._classpath, stdout=PIPE, stderr=PIPE)
        os.chdir(cwd)

        return stdout, stderr

    def _to_conll09(self, sentences, lemma_col=None, tag_col=None):
        """Transforms sentence list (each sentence a list of tokens) into a conll09-like tabular file.

        Parameters
        ----------
        sentences : iter
            a list/iterable of sentences. Each sentence is a list of tokens; each token might be a string or a tuple
            (tok,anno1,anno2,anno_n...)

        Returns
        -------
        str : a conll09-like tabular representation of the sentences
        """
        Token = namedtuple('Token', ['form', 'lemma', 'pos'])
        lemma = '_'
        postag = '_'
        txt = ''
        for s in sentences:
            for idx,w in enumerate(s, start=1):
                if isinstance(w, str):
                    w = (w,)
                if lemma_col:
                    lemma = w[int(lemma_col)]
                if tag_col:
                    _t = w[int(lemma_col)]
                    postag = "".join([l+'|' for l in _t]).rstrip("|")
                t = Token(w[0], lemma, postag)
                # ID FORM LEMMA PLEMMA POS PPOS FEAT PFEAT HEAD PHEAD DEPREL PDEPREL FILLPRED PRED APREDs
                txt += f"{idx}\t{t.form}\t{t.lemma}\t_\t{t.pos[0]}\t_\t{t.pos}\t_\t_\t_\t_\t_\t_\t_\t_\n"
            txt += "\n"
        return txt

    def _conll2tagged(self, conll_sents):

        tagged_sents = []
        for s in conll_sents:
            sent = [(l.split("\t")[1], l.split("\t")[5]) for l in s.rstrip().split("\n")]
            tagged_sents.append(sent)
        return tagged_sents

    def _annotate_sents(self, sents, j_class, lemma_col, tag_col, outfile=None):
        from nltk.corpus.reader.util import read_blankline_block

        input_txt = self._to_conll09(sents, lemma_col, tag_col)

        with tempfile.NamedTemporaryFile(mode='w+', delete=True) as input_file, \
                tempfile.NamedTemporaryFile(mode='w+', delete=True) as output_file:

            # prepare the input file
            input_file.writelines(input_txt)
            input_file.flush()
            stdout, stderr = self._execute(j_class, input_file.name, output_file.name)

            output_file.seek(0)

            conll = []
            while True:
                block = read_blankline_block(output_file)
                if block:
                    conll.extend(block)
                else:
                    break
        if outfile:
            with open(outfile, 'w') as out:
                "\n".join(conll)
        return conll

    def lemmatize(self, infile, outfile):
        return self._execute("is2.lemmatizer.Lemmatizer", infile, outfile)

    def parse(self, infile, outfile):
        return self._execute("is2.parser.Parser", infile, outfile)

def reverse_dict(dic):
    return {v: k for k, v in dic.items()}


pos = {'-': '-', "d": 'adverb', 'n': 'noun', 'm': 'numeral', 'p': 'pron', 'v': 'verb', 't': 'verb', 'x': 'irregular',
       'l': 'article', 'e': 'exclamation', 'a': 'adjective', 'r': 'preposition', 'c': 'conjunction', 'g': 'adverb',
       'u': 'punctuation', 'i': 'exclamation', }

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
