import pandas as pd
import re
from functools import lru_cache


class MorpheusLookupLemmatizer():
    """
    A lemmatizer that performs a simple lookup in a table with forms, tags and lemmata
    generated from the Morpheus. Morpheus is the parser of Greek and Latin used by the Perseus DL.
    The class assumes that the tokens are already tagged with morphology (use the classes in tagger).

    Morpheus generates almost 1M forms+tags (which are by no means all that you can find, by the way).
    Generally, morph-tag + word is more than enough to disambiguate between ambiguous forms.
    A lookup in a db would perhaps be more efficient, but the users would need to setup and
    configure a database on their machine in order for them to use it. Instead, we rely on `pandas` and on a
    CSV export of the Morpheus greek parses for fast lookups.

    The CSV file is stored in a bz2 archive in the folder `lib`. It is relatively light (3.3 MB) and
    was generated using G. Celano's [utf-8 conversions](https://github.com/gcelano/MorpheusGreekUnicode)
    of Morpheus' betacode tables.
    """

    def __init__(self, path_to_data="lib/morpheus/morpheus_dataframe.csv.bz2"):
        self._path = path_to_data
        self._df = pd.read_csv(self._path, compression="bz2")

    #def lemmatize_cited_word(self, cite, form, postag):
    #    t = self.lemmatize_word(form, postag)
    #    return (cite,) + t

    @lru_cache(maxsize=512)
    def lemmatize_word(self, form, postag):
        """
        Generate a tuple with form, lemma, tag.

        Parameters
        ----------
        form : str
            the word to be lemmatized
        postag : str
            a 9-char string with full moprhological analysis. This tag is the same
            as those used in the AGLDT treebank. They can be generated using the taggers in `tagger.py`

        Returns
        -------
        tuple : (form, lemma, tag)
            if lemma is not found for the form+tag couple, the second element in the tuple is an empty string

        """
        # normalize the postag returned by the taggers
        postag = postag.replace("|", "")
        if re.search(r'^[a-z]_$', postag):
            postag = postag.replace("_", "--------")
        try:
            l = self._df[(self._df.Form == form) & (self._df.Tag == postag)].Lemma.values[0]
        except IndexError:
            l = ""
        if postag == "u--------":
            l = "punct"
        return (form, l, postag)

    def lemmatize_sentence(self, sent, include_cite=False):
        lemmsent = []
        for token in sent:
            if include_cite:
                t = self.lemmatize_word(token[1], token[2])
                t = (token[0],) + t

            else:
                t = self.lemmatize_word(token[0], token[1])
            lemmsent.append(t)
        return lemmsent

    def lemmatize_sentences(self, sents, include_cite=False):
        return [self.lemmatize_sentence(s, include_cite=include_cite)
                for s in sents]
