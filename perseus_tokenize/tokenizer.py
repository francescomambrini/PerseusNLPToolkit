"""
Series of word-tokenizers to use with the MyCapitain texts.
"""

pattern_sample = r'''([A-Z]\.)+        # abbreviations, e.g. U.S.A.
   | \w+(-\w+)*        # words with optional internal hyphens
   | \$?\d+(\.\d+)?%?  # currency and percentages, e.g. $12.40, 82%
   | \.\.\.            # ellipsis
   | [][.,;"'?():-_`]  # these are separate tokens; includes ], [
'''

tb_pattern = r'''[κχ](?=\w?[ὐὖὔἰἴἀἂἄἈὠᾀᾆἠὢὤὦᾦ])        # deal with the crasis of καί
            | εἴ|οὐ|μη|μή(?=τε\b|δ[έἐ]\b|[τδθ][᾽']\b)  # conjunctions: εἴτε, ουδέ, μηδέ etc.
            | \w+[᾽']?      # white-space separated words
            | \.\.\.        # ellipsis or lacuna
            |[^\w\s]+
'''

#remember to pass re.VERBOSE as flag

from nltk.tokenize import RegexpTokenizer
import re


class PerseusTreebankTokenizer(RegexpTokenizer):
    super.__init__()


class PerseusWordPunctTokenizer(RegexpTokenizer):
    pass