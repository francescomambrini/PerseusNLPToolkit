import pytest
import os
from cite_corpus_reader.reader import CapitainCorpusReader

root_1st = os.path.expanduser('~/cltk_data/greek/text/greek_text_first1kgreek/data')
root_perseus = os.path.expanduser('~/cltk_data/greek/text/cltk_data/greek/text/canonical-greekLit-master/data')


@pytest.fixture
def aesch():
    return CapitainCorpusReader(root_perseus, "tlg0085/tlg.*/tlg.*\.xml")


def test_print_concordances(aesch):

    pass

