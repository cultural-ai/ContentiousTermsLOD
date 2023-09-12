# How Culturally Sensitive Terms are Used in Linked Open Data
## The repository of the research paper

The online Appendix is available at [cultural-ai.github.io/LODlit](https://cultural-ai.github.io/LODlit/)

### Data

* We reuse the previously developed [knowledge graph of contentious terminology](https://github.com/cultural-ai/wordsmatter), [paper](https://doi.org/10.1007/978-3-031-33455-9_30);
* From the knowledge graph, we extract culturally sensitive terms to inspect them in LOD-datasets; the process is in the notebook [getting_query_terms.ipynb](getting_query_terms.ipynb), the resulting file is [query_terms.json](query_terms.json); there are 75 EN and 82 NL canonical forms of terms, which are lniked to their inflected forms (for example, "aboriginal" and "aboriginals"); with both canonical and inflected forms, there are 154 EN and 242 NL terms;
* We query terms in four LOD datasets:
  * Wikidata (EN and NL);
  * The Getty Art & Architechture Thesaurus (AAT) (EN and NL);
  * Princeton WordNet (version 3.1) (only EN);
  * Open Dutch WordNet (version 1.3) (only NL);
  
* For details on querying each dataset, see README in the corresponding directories:
  * [Wikidata](Wikidata)
  * [AAT](AAT)
  * [PWN](PWN)
  * [ODWN](ODWN)

### Sets constructed for analysis

  #### Set 1: all retrieved literals
  #### Set 2: disambiguated literals
  #### Set 3: literlas of resources from the knowledge graph

### Sensitivity markers

  #### Explicit markers
  #### Implicit markers

### LODlit package

[LODlit_package](https://github.com/cultural-ai/LODlit/tree/main/LODlit_package) allows to query terms in Wikidata, AAT, PWN, and ODWN.
The package can be used to both reproduce our research results and retrieve literals from the LOD datasets for other purposes.
Read more in the package documentation.
  
### Paper footnotes

* \[13]: The list of exluded categories in Wikidata at the filtering step is in the file [statements_filter.json](Wikidata/statements_filter.json);
* \[13]: The number of search results from Wikidata before and after filtering is in the file [n_entities_by_term.csv](Wikidata/n_entities_by_term.csv), the number of retrieved entities (<= 10K) is in [n_entities_retrieved_by_term.csv](Wikidata/n_entities_retrieved_by_term.csv); the number of **entities** after filtering proper names out (Set 1) is in [n_entities_clean_by_term.csv](Wikidata/n_entities_clean_by_term.csv) and the number of **hits** by canonical forms is in [n_hits_by_lemma.csv](Wikidata/n_hits_by_lemma.csv);

