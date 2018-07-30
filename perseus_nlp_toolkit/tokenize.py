"""
Series of word-tokenizers to use with the MyCapitain texts.
"""

from nltk.tokenize import RegexpTokenizer
from nltk.tokenize.punkt import PunktLanguageVars
import re

# pattern_sample = r'''([A-Z]\.)+        # abbreviations, e.g. U.S.A.
#   | \w+(-\w+)*        # words with optional internal hyphens
#   | \$?\d+(\.\d+)?%?  # currency and percentages, e.g. $12.40, 82%
#   | \.\.\.            # ellipsis
#   | [][.,;"'?():-_`]  # these are separate tokens; includes ], [
# '''

# remember to pass re.VERBOSE as flag!
tb_pattern = r'''[κχ](?=\w?[ὐὖὔἰἴἀἂἄἈὠᾀᾆἠὢὤὦᾦ])        # deal with the crasis of καί
            | (?:εἴ|οὐ|μη|μή)(?=τε\b|δ[έἐ]\b|[τδθ][᾽'])  # conjunctions: εἴτε, ουδέ, μηδέ etc.
            | \w+[᾽']?      # white-space separated words
            | \.\.\.        # ellipsis or lacuna
            |[^\w\s]+
'''


class AncientGreekPunktVar(PunktLanguageVars):
    # note that there are two middle dots:
    # \u00b7 and \u0387!

    sent_end_chars = ("\u0387","·",'.', ';', ":")
    _re_non_word_chars = r"(?:[\";\*:@\'··])"


class PerseusTreebankTokenizer(RegexpTokenizer):
    def __init__(self):
        RegexpTokenizer.__init__(self, tb_pattern,
                                 flags=re.UNICODE | re.MULTILINE | re.DOTALL | re.VERBOSE)


class PerseusWordPunctTokenizer(RegexpTokenizer):
    def tokenize(self, text):
        raise NotImplementedError
