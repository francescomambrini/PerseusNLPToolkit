import pytest
from perseus_nlp_toolkit import CapitainCorpusReader

root = '/Users/fmambrini/cltk_data/greek/text/greek_text_first1kgreek/data'
root_perseus = '/Users/fmambrini/cltk_data/greek/text/'

@pytest.fixture
def aristot_dha():
    f = "tlg0086/tlg014/tlg0086.tlg014.1st1K-grc1.xml"
    return CapitainCorpusReader(root, f)


@pytest.fixture
def aeschylus():
    f = "tlg0085/tlg.*/tlg.*\.xml"
    return CapitainCorpusReader(root, f)


def test_para_fileid(aristot_dha):
    assert len(aristot_dha.fileids()) == 1


def test_corpus(aeschylus):
    assert len(aeschylus.fileids()) == 7


def test_para_reader(aristot_dha):
    raw = aristot_dha.raw()
    assert raw[:21] == 'ΠΕΡΙ ΤΑ ΖΩΙΑ ΙΣΤΟΡΙΩΝ'


def test_refs(aristot_dha):
    f = aristot_dha._get_citable_text(aristot_dha.fileids()[0])
    ref = aristot_dha._read_paras(f, include_cites=True)[0]
    assert ref[1] == ('1.2', 10224, 11057)


def test_word_readers(aristot_dha):
    words = aristot_dha.words()
    assert words[0] == 'ΠΕΡΙ'


def test_word_cites(aristot_dha):
    f = aristot_dha._get_citable_text(aristot_dha.fileids()[0])
    word_cites = aristot_dha._read_words(f, include_cites=True)
    assert word_cites[2006] == ('1.2', "Πάντων")