from nltk.internals import java, config_java
import os
import tempfile
from subprocess import PIPE


class MateMorphTagger():
    def __init__(self, mate_folder, path_to_model, java_options="-Xmx3G"):
        self._java_options = java_options
        self._mate_root = mate_folder
        self._model = path_to_model
        self._classpath = "anna-3.61.jar"

        # Configure java.
        config_java(options=self._java_options)

    def _prepare_input(self, sentences):
        txt = ''
        for s in sentences:
            for idx,w in enumerate(s):
                txt += "{}\t{}\n".format(idx+1, w)
            txt += "\n"
        return txt

    def tag(self, infile, outfile):
        cwd = os.getcwd()
        os.chdir(self._mate_root)
        os.chdir(self._mate_root)
        cmd = ["is2.tag.Tagger", "-model", self._model, "-test", infile, "-out", outfile]
        stdout, stderr = java(cmd, classpath=self._classpath, stdout=PIPE, stderr=PIPE)
        os.chdir(cwd)

        return stdout, stderr

    def tag_sents(self, sents):
        from nltk.corpus.reader.util import read_blankline_block

        input_txt = self._prepare_input(sents)

        with tempfile.NamedTemporaryFile(mode='w+', delete=True) as input_file, \
                tempfile.NamedTemporaryFile(mode='w+', delete=True) as output_file:

            # prepare the input file
            input_file.writelines(input_txt)
            input_file.flush()
            stdout, stderr = self.tag(input_file.name, output_file.name)

            output_file.seek(0)

            conll = []
            while True:
                block = read_blankline_block(output_file)
                if block:
                    conll.extend(block)
                else:
                    break
        tagged_sents = []
        for s in conll:
            sent = [(l.split("\t")[1], l.split("\t")[5]) for l in s.rstrip().split("\n")]
            tagged_sents.append(sent)
        return tagged_sents
        #return conll

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



