import pytest
import os
from  perseus_nlp_toolkit import CapitainCorpusReader

root_1st = os.path.expanduser('~/cltk_data/greek/text/greek_text_first1kgreek/data')
root_perseus = os.path.expanduser('~/cltk_data/greek/text/canonical-greekLit-master/data')


@pytest.fixture
def aesch():
    return CapitainCorpusReader(root_perseus, "tlg0085/tlg.*/tlg.*grc[0-9]\.xml")


@pytest.fixture
def aristot_dha():
    f = "tlg0086/tlg014/tlg0086.tlg014.1st1K-grc1.xml"
    return CapitainCorpusReader(root_1st, f)


def test_init():
    assert os.path.isdir(root_1st)


def test_para_fileid(aristot_dha):
    assert len(aristot_dha.fileids()) == 1


def test_corpus(aesch):
    assert len(aesch.fileids()) == 7