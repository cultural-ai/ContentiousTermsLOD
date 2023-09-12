# LODlit
## Simplifying retrieval of literals from Linked Open Data

Different LOD-datasets are available online in different formats with diffferent user-friendliness levels.
LODlit allows you to search over different linked open datasets in one place using keywords and outputs the search results in the same json structure convinient for further processing.

For example, LODlit retrieves labels, aliases, and descriptions of Wikidata entities by search terms in a specific language with optional search filtering. It is also possible to get literals in different languages by entity identifiers.
Additionally, LODlit provides the functionality to make bag-of-words from literals for natural language processing, for example, to calculate cosine similarity between literals.

Currently, LODlit supports parsing from [Wikidata](https://www.wikidata.org/wiki/Wikidata:Main_Page), [Getty Art & Architecture Thesaurus (AAT)](https://www.getty.edu/research/tools/vocabularies/aat/), [Princeton WordNet (3.1)](https://wordnet.princeton.edu/), and [Open Dutch WordNet (1.3)](https://github.com/cultural-ai/OpenDutchWordnet).

### Installation

```pip install LODlit```

LODlit is available on [PyPI](https://pypi.org/project/LODlit/). The current version is 0.5.0.

* To parse Princeton WordNet 3.1: After NLTK is installed, download the [wordnet31](https://github.com/nltk/nltk_data/blob/gh-pages/packages/corpora/wordnet31.zip) corpus; Put the content of "wordnet31" to "wordnet" in "nltk_data/corpora" (it is not possible to import wordnet31 from nltk.corpus directly; see explanations on [the WordNet website](https://wordnet.princeton.edu/download/current-version) (retrieved on 10.02.2023): "WordNet 3.1 DATABASE FILES ONLY. You can download the WordNet 3.1 database files. Note that this is not a full package as those above, nor does it contain any code for running WordNet. However, you can replace the files in the database directory of your 3.0 local installation with these files and the WordNet interface will run, returning entries from the 3.1 database. This is simply a compressed tar file of the WordNet 3.1 database files"; Use `pwn31.check_version()` to ensure that WordNet 3.1 is imported;

* To parse Open Dutch WordNet: Download the ODWN from [https://github.com/cultural-ai/OpenDutchWordnet](https://github.com/cultural-ai/OpenDutchWordnet);

### License

[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
