from nltk.internals import java, config_java
import os
import tempfile
from subprocess import PIPE
from .utils import MateCaller


class MateMorphTagger(MateCaller):
    def __init__(self, mate_folder, path_to_model, java_options="-Xmx3G"):
        MateCaller.__init__(mate_folder, path_to_model, java_options)
        self._java_class = 'is2.tag.Tagger'

    def tag_sents(self, sents, lemma_col=None, outfile=None):
        c = self._annotate_sents(sents, self._java_class, lemma_col, outfile)

    def tag_cite_sents(self, cite_sents):
        _sents = [[w[1] for w in s] for s in cite_sents]
        _cites = [[w[0] for w in s] for s in cite_sents]
        tagged = self.tag_sents(_sents)
        tagged_cited = []
        assert len(tagged) == len(_cites), "Tagged sentences and citations not in sync"
        for ts, cs in zip(tagged, _cites):
            assert len(ts) == len(cs), "Tagged words and citations not in sync"
            sent = []
            for tw,cw in zip(ts,cs):
                sent.append((cw, tw[0], tw[1]))
            tagged_cited.append(sent)
        return tagged_cited



