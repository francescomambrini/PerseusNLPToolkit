# What is this?

It's a collections of small python modules made to enhance the interoperability ot the awesome 
[NLTK](http://nltk.org/) and [CLTK](http://cltk.org/) 
with CTS-compatible texts that follow the [guidelines](http://capitains.org/pages/guidelines) of Capitains, 
and especially those of the Perseus DL and [First 1K Years of Greek](https://github.com/OpenGreekAndLatin/First1KGreek).

At the moment, I have a put together:

* a [corpus reader](http://www.nltk.org/howto/corpus.html) for Capitains-compliant XML files. It works with all the 
First1K texts that you can download using [CLTK downloader](http://docs.cltk.org/en/latest/importing_corpora.html). 
It lets you load and tokenize your corpus and store citations for all your tokens.
* a Greek tokenizer (in progress) that *should* work well with [Perseus treebank](https://perseusdl.github.io/treebank_data/)
* a concordance indexer to create ([enhanced!]()) concordances from CTS-compatible texts