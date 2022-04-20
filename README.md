# LODlit

### How are the terms denoting historically marginalised people used in LOD?

* The initial lists of terms from WM [in Dutch](https://github.com/cultural-ai/LODlit/blob/main/query_terms_nl.txt) and [English](https://github.com/cultural-ai/LODlit/blob/main/query_terms_en.txt)
* [getting_word_forms](https://github.com/cultural-ai/LODlit/blob/main/getting_word_forms.ipynb) – script to get word forms in Dutch and English;

  ###### SPARQL-query to DBnary to get English word forms

  64 words from the English version of WM were queried. Plurals were changed to single form to math the canonical forms in DBnary.
  
  [DBnary](http://kaiko.getalp.org/about-dbnary/) served as a source for the English word forms.
  
  There might be different entries for the same lemma in DBnary. For example, "Kaffir" (noun) and "kaffir" (noun). And some of these entries might not have otherForms ("kaffir"(noun) (http://kaiko.getalp.org/dbnary/eng/kaffir__Noun__1) has only a canonical form). So, we queried only the entries that have 1 or more word forms:

  ("ontolex:otherForm / ontolex:writtenRep ?otherForm_lit ." – this is not optional!)

  The script takes 12 min, each term takes around 11 sec to query.

  ###### HTTP-requests to INT LexicalService to get Dutch word forms

  67 words from the Dutch version of WM were queried. Words were not modified.

  [INT LexiconService](http://sk.taalbanknederlands.inl.nl/LexiconService/) was used to obtain the word forms.

  2 HTTP-requests were run to (1) get lemmas of the terms (in case if they do not match the canonical form in the lexicon, for example 'gehandicapten') and (2) get word forms for every found lemma.
  
  See the LexiconService documentation in 2 files: [LexiconService_Manual_april2021](https://github.com/cultural-ai/LODlit/blob/main/LexiconService_Manual_april2021.pdf), [LexiconService_AvailableDatasets_april2021](https://github.com/cultural-ai/LODlit/blob/main/LexiconService_AvailableDatasets_april2021.pdf)
  
  The resulting datasets with Dutch [nl_wordforms.json](https://github.com/cultural-ai/LODlit/blob/main/nl_wordforms.json) and English [eng_wordforms.json](https://github.com/cultural-ai/LODlit/blob/main/en_wordforms.json) word forms in json have the same structure
  {"query_word": {"lemmata":\[{"lemma_URI":"\*","lemma":"\*","pos":"\*","wordforms":\["\*"]}]}}
  
The following repositories contain files related to querying the terms in corresponding LOD-resources:
* Getty AAT
* WordNet (including OpenDutchWordNet)
* Wikidata
