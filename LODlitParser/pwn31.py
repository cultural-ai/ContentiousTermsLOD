# Module for Princeton WordNet 3.1

# install NLTK
# Important! download wordnet31 ('https://github.com/nltk/nltk_data/blob/gh-pages/packages/corpora/wordnet31.zip');
# put the content of 'wordnet31' to 'wordnet' in 'nltk_data/corpora' (it is not possible to import wordnet31 from nltk.corpus; See explanations on the WordNet website (retrieved on 10.02.2023): https://wordnet.princeton.edu/download/current-version; "WordNet 3.1 DATABASE FILES ONLY. You can download the WordNet 3.1 database files. Note that this is not a full package as those above, nor does it contain any code for running WordNet. However, you can replace the files in the database directory of your 3.0 local installation with these files and the WordNet interface will run, returning entries from the 3.1 database. This is simply a compressed tar file of the WordNet 3.1 database files."
# to use 'get_bows', download stopwords from nltk: nltk.download('stopwords')

import json
import re
import nltk
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import warnings

def main():

    print("Install NLTK and download wordnet. Download wordnet31 from 'https://github.com/nltk/nltk_data/blob/gh-pages/packages/corpora/wordnet31.zip' and put the content of 'wordnet31' to 'wordnet' in 'nltk_data/corpora'")

    if __name__ == "__main__":
        main()

def check_version() -> str:
    return f"You have WordNet version {wn.get_version()}"

def find_term(query_term:str) -> list:
    '''
    Searching for a query term in synset lemmas, synset difinitions, and synset examples
    query_term: str, a term to search in synsets, phrases are also allowed
    Returns a list of dicts with the synset info if the query term was found:
    [{'query_term':query_term,
        'synset_id':'',
        'lemmata':[],
        'definition':'',
        'examples':[],
        'found_in':''}]
    '''

    if wn.get_version() != '3.1':
        warnings.warn("This module is created to parse WordNet 3.1. Your version is different. Download version 3.1 from 'https://github.com/nltk/nltk_data/blob/gh-pages/packages/corpora/wordnet31.zip' and put the content of 'wordnet31' to 'wordnet' in 'nltk_data/corpora'. Import wordnet again and check your version with .get_version()")

    search_results = []

    # searching in lemmata
    # getting synset_id, lemmata (synonyms), definition, examples
    for synset in wn.synsets(query_term):
        for le in synset.lemmas():
            # exact match between query term and lemma name
            if query_term == le.name().lower(): # lemmas can be capitalized
                result_dict = {}
                result_dict['query_term'] = query_term
                result_dict['synset_id'] = synset.name()
                result_dict['lemmata'] = [l.name() for l in synset.lemmas()]
                result_dict['definition'] = synset.definition()
                result_dict['examples'] = synset.examples()
                result_dict['found_in'] = 'lemmata'
                search_results.append(result_dict)

    # searching in all definitions
    for synset in list(wn.all_synsets()):
        if len(re.findall(f'\\b{query_term}\\b',synset.definition(),re.IGNORECASE)) > 0:
            result_dict = {}
            result_dict['query_term'] = query_term
            result_dict['synset_id'] = synset.name()
            result_dict['lemmata'] = [l.name() for l in synset.lemmas()]
            result_dict['definition'] = synset.definition()
            result_dict['examples'] = synset.examples()
            result_dict['found_in'] = 'definition'
            search_results.append(result_dict)

    # searching in all examples
    for example in synset.examples():
        if len(re.findall(f'\\b{query_term}\\b',example,re.IGNORECASE)) > 0:
            result_dict = {}
            result_dict['query_term'] = query_term
            result_dict['synset_id'] = synset.name()
            result_dict['lemmata'] = [l.name() for l in synset.lemmas()]
            result_dict['definition'] = synset.definition()
            result_dict['examples'] = synset.examples()
            result_dict['found_in'] = 'examples'
            search_results.append(result_dict)

    return search_results

def get_synsets_info(synsets:list) -> dict:
    '''
    Getting lemmata, definition, and examples of synsets
    synsets: a list of synsets IDs (str), for example ['cookie.n.01','cookie.n.02','cookie.n.03']
    Return a dict: {'synset_id': {'lemmata': [],
                                   'definition': '',
                                   'examples': []}
    '''
    
    synsets_info = {}
    
    for s in synsets:
        synset = wn.synset(s)
        lemmata = [l.name() for l in synset.lemmas()]
        definition = synset.definition()
        examples = synset.examples()
        
        # writing results 
        synsets_info[s] = {'lemmata': lemmata,
                         'definition': definition,
                         'examples': examples}
        
    return synsets_info

def get_bows(path_to_results:str) -> dict:
    '''
    Getting bag of words (BoW) from the Princeton WordNet 3.1 search results for every search term
    path_to_results: str, a path to the search results (in json format)
    Returns a dict with BoWs per hit per term: {term:[{synset_id:['token1','token2','token3']}]}
    '''
    wnl = WordNetLemmatizer()

    all_bows = {}
   
    with open(path_to_results,'r') as jf:
        search_results = json.load(jf)

    for query_term, results in search_results.items():

        list_by_term = []

        for hit in results:

            q_bag = {}
            literals = []

            literals.extend(hit["lemmata"])
    
            if hit["definition"] != "":
                literals.append(hit["definition"])
            if hit["examples"] != []:
                literals.extend(hit["examples"])

            bow = []
            for lit in literals:
                bow.extend(lit.replace('(','').replace(')','').replace('-',' ').replace('/',' ')\
                           .replace(',','').lower().split(' '))

            bag_unique = [wnl.lemmatize(w) for w in set(bow) if w not in stopwords.words('english') \
                                    and re.search('(\W|\d)',w) == None and w != hit["query_term"] and w != '']

            q_bag[hit["synset_id"]] = bag_unique

            list_by_term.append(q_bag)

        all_bows[query_term] = list_by_term

    return all_bows