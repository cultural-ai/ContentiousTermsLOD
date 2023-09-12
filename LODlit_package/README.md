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

### License

[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
