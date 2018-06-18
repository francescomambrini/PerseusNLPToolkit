from nltk.text import Text, ConcordanceIndex, BigramCollocationFinder
from collections import namedtuple


ConcordanceLine = namedtuple('ConcordanceLine',
                             ['left', 'query', 'right', 'offset', 'cite',
                              'left_print', 'right_print', 'line'])


class CitableConcordanceIndex(ConcordanceIndex):
    def __init__(self, tokens, cites, key= lambda x : x):
        ConcordanceIndex.__init__(self, tokens, key)
        if len(tokens) != len(cites):
            raise ValueError("Tokens and citations do not seem to match")
        self._cites = cites

    def _get_form_tokens(self):
        if all(isinstance(n, tuple) for n in self._tokens):
            forms = [t[0] for t in self._tokens]
        else:
            forms = self._tokens
        return forms

    def offsets(self, word):
        return self._offsets[word]

    def find_concordance(self, word, width=80):
        """
        Find the concordance lines given the query word.
        """
        half_width = (width - len(word) - 2) // 2
        context = width // 4  # approx number of words of context

        # Find the instances of the word to create the ConcordanceLine
        concordance_list = []
        offsets = self.offsets(word)
        forms = self._get_form_tokens()
        if offsets:
            for i in offsets:
                query_word = forms[i]
                # Find the context of query word.
                left_context = forms[i - context:i]
                right_context = forms[i + 1:i + context]
                # Create the pretty lines with the query_word in the middle.
                left_print = ' '.join(left_context)[-half_width:]
                right_print = ' '.join(right_context)[:half_width]
                # Find the cite
                cite = self._cites[i]
                # The WYSIWYG line of the concordance.
                line_print = ' '.join([left_print, query_word, right_print]) #"{} ({})".format(, cite)
                # Create the ConcordanceLine
                concordance_line = ConcordanceLine(left_context, query_word, right_context, i, cite,
                                                   left_print, right_print, line_print)
                concordance_list.append(concordance_line)
        return concordance_list

    def print_concordance(self, word, include_cite=True, width=80, lines=25):
        """
        Print concordance lines given the query word.

        Parameters
        ----------
        word : str
            The target word
        include_cite : bool
            Whether to append the citation at the end of the concordance line (default=True)
        width : int
            The width of each line, in characters (default=80)
        lines : int
            The number of lines to display (default=25)

        Returns
        -------
        None

        """
        concordance_list = self.find_concordance(word, width=80)

        if not concordance_list:
            print("no matches")
        else:
            lines = min(lines, len(concordance_list))
            print("Displaying {} of {} matches:".format(lines, len(concordance_list)))
            for i, concordance_line in enumerate(concordance_list[:lines]):
                if include_cite:
                    print("{} ({})".format(concordance_line.line, concordance_line.cite))
                else:
                    print(concordance_line.line)


class PerseusPlainText(Text):
    def __init__(self):
        pass


class PerseusAnnotateText(Text):
    pass