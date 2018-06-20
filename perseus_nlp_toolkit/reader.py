from nltk.corpus.reader.util import *
from nltk.corpus.reader.api import *
from nltk.tokenize import *
from nltk.tokenize.punkt import PunktLanguageVars

from MyCapytain.resources.texts.local.capitains.cts import CapitainsCtsText
from MyCapytain.common.constants import Mimetypes, XPATH_NAMESPACES


class AncientGreekPunktVar(PunktLanguageVars):
    # note that there are two middle dots:
    # \u00b7 and \u0387!

    sent_end_chars = ("\u0387","·",'.', ';', ":")
    _re_non_word_chars = r"(?:[\";\*:@\'··])"

class CapitainCorpusReader(CorpusReader):
    """
    Reader for corpora that consist of MyCapitain-compliant documents.
    Sentences and words can be tokenized using the default tokenizers,
    or by custom tokenizers specified as parameters to the constructor.
    """

    # CorpusView = StreamBackedCorpusView
    """Here we should create a corpus viewer, but it was too hard..."""

    def __init__(self, root, fileids,
                 word_tokenizer=WordPunctTokenizer(),
                 sent_tokenizer=PunktSentenceTokenizer(lang_vars=AncientGreekPunktVar()),
                 exclude_tags=['tei:note'],
                 # para_block_reader=read_blankline_block,
                 encoding='utf8'):
        """
        Construct a new citable corpus reader for a set of documents
        located at the given root directory.

        Parameters
        ----------
        root : str
            The root directory for this corpus.
        fileids : str or list
            A list or regexp specifying the fileids in this corpus.
        word_tokenizer : nltk Tokenizer
            Tokenizer for breaking sentences or paragraphs into words
        sent_tokenizer : nltk Tokenizer
            Tokenizer for breaking paragraphs into sentences
        exclude_tags : list
            TEI tags whose text should not be extracted.
        """

        CorpusReader.__init__(self, root, fileids, encoding)
        self._word_tokenizer = word_tokenizer
        self._sent_tokenizer = sent_tokenizer
        self._tags_to_exclude = exclude_tags

    def _get_citable_text(self, fileid):
        """
        Parameters
        ----------
        fileid: str
            The file identifier of the file to read

        Returns
        -------
        CapitainsCtsText object

        """

        with open(self._root.join(fileid)) as f:
            text = CapitainsCtsText(resource=f)
        return text

    def _set_fileids(self, fileids):
        """If fileids is None, then return the whole corpus;
        if it is a single file then return a 1-element list

        Returns
        -------
        list
            of file pointer(s)

        """
        if fileids is None:
            fileids = self._fileids
        elif isinstance(fileids, string_types):
            fileids = [fileids]
        return fileids

    def raw(self, fileids=None):
        """Returns the given file(s) as a single string.

        Parameters
        ----------
        fileids : None, list, str, path
            file identifier or pointer. If None, then the whole corpus is returned

        Returns
        -------
        str

        """
        fileids = self._set_fileids(fileids)

        raw_texts = []
        for f in fileids:
            text = self._get_citable_text(f)
            raw_texts.extend(self._read_paras(text))

        return concat(raw_texts)

    def words(self, fileids=None):
        """
        :return: the given file(s) as a list of words
            and punctuation symbols.
        :rtype: list(str)
        """
        fileids = self._set_fileids(fileids)
        words = []
        for f in fileids:
            text = self._get_citable_text(f)
            words.extend(self._read_words(text))
        return words

    def sents(self, fileids=None):
        """
        :return: the given file(s) as a list of
            sentences or utterances, each encoded as a list of word
            strings.
        :rtype: list(list(str))
        """
        if self._sent_tokenizer is None:
            raise ValueError('No sentence tokenizer for this corpus')

        fileids = self._set_fileids(fileids)
        sents = []
        for f in fileids:
            text = self._get_citable_text(f)
            sents.extend(self._read_sents(text))

        return sents

    def cite_words(self, fileid):
        """
        Parameters
        ----------
        fileid : str
            the file name of the text you want to get citable words from

        Returns
        -------
        list(tuple(str,str))
            the text as list of tuple (cite, token)

        """
        if not isinstance(fileid, string_types):
            raise TypeError('Expected a single file identifier string')
        text = self._get_citable_text(fileid)
        return self._read_words(text, include_cites=True)

    def cite_sents(self, fileid):
        """
        Parameters
        ----------
        fileid : str
            the file name of the text you want to get citable words from

        Returns
        -------
        list(list(tuple(str,str)))
            the text as list of lists (sentences); each sentence is a list of tuples (cite, token)

        """
        if not isinstance(fileid, string_types):
            raise TypeError('Expected a single file identifier string')
        text = self._get_citable_text(fileid)
        return self._read_sents(text, include_cites=True)

    def corpus_cite_words(self):
        """
        Get text identifier, tokens and citations for all the tokens in all the files of the corpus.

        WARNING:
        the file id's must be formatted using a cts compatible format: auth_id.work_id

        Returns
        -------
        list (tuple)
            list of (text_id, cite, token)

        """
        import os
        cite_words = []
        for f in self.fileids():
            txt_ids = os.path.basename(f).split(".")[:2]
            _words = [(".".join(txt_ids), w[0], w[1]) for w in self.cite_words(f)]
            cite_words.extend(_words)
        return cite_words


    def paras(self, fileids=None):
        """
        Returns a series of sections, corresponding to the last citeable level identified
        by Capitain. It does not do much more than what the Capitain API does, but it may
        be helpful for some use cases.

        :return: the given file(s) as a list of
            sections.
        :rtype: list (str)
        """
        fileids = self._set_fileids(fileids)
        paras = []
        for f in fileids:
            text = self._get_citable_text(f)
            paras.extend(self._read_paras(text))
        return paras


    def _read_words(self, capitain_file, include_cites=False):
        secs = self._read_paras(capitain_file, include_cites)
        text = " ".join(secs) if not include_cites else "".join(secs[1])
        if include_cites:
            spans = self._word_tokenizer.span_tokenize(text)
            words = self._word_tokenizer.tokenize(text)
            cite_words = []
            for span,word in zip(spans, words):
                c = self._return_cite(span, secs[0])
                cite_words.append((c, word))
            return cite_words
        else:
            text = "".join(concat(secs))
            return self._word_tokenizer.tokenize(text)

    def _read_sents(self, capitain_file, include_cites=False):
        secs = self._read_paras(capitain_file, include_cites)

        text = "".join(secs) if not include_cites else "".join(secs[1])
        rawsents = self._sent_tokenizer.tokenize(text)
        sents = [self._word_tokenizer.tokenize(s) for s in rawsents]

        if not include_cites:
            return sents
        else:
            # get the cite_words and regroup them with sents
            sizes = [len(s) for s in sents]
            _cite_words = self._read_words(capitain_file, include_cites=True)
            it = iter(_cite_words)
            cite_sents = [[next(it) for _ in range(size)] for size in sizes]
            return cite_sents



    def _return_cite(self, span, cites):
        for c in cites:
            if span[-1] <= c[-1]:
                return c[0]

    def _read_paras(self, capitain_file, include_cites=False):
        """

        Parameters
        ----------
        capitain_file : CapitainsCtsText
            the cts object to read text and cites from
        include_cites : bool
            whether to return text only or refs + text

        Returns : list
        -------
            list of textual sections, or list of references and texts

        """
        paras = []
        refs = []
        b, e = 0, 0
        for ref in capitain_file.getReffs(level=len(capitain_file.citation)):
            psg = capitain_file.getTextualNode(subreference=ref, simple=True)
            t = psg.export(Mimetypes.PLAINTEXT, exclude=self._tags_to_exclude) + " "
            paras.append(t)
            e += len(t)
            refs.append((ref, b, e))
            b = e
        if include_cites:
            return refs, paras
        else:
            return paras


class CiteCorpusView(StreamBackedCorpusView):
    """
    A specialized corpus view for cts-compliant documents.
    Not implemented yet.

    It may help in case of very large corpora, because MyCapitain can be slow when the cite scheme
    is very fine-grained (e.g. with poetry, where you have a cite element per line).
    """

    def __init__(self, fileid):
        raise NotImplementedError
