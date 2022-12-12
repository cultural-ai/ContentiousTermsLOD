# lodlitparser
# install NLTK, download wordnet31 ('https://github.com/nltk/nltk_data/blob/gh-pages/packages/corpora/wordnet31.zip');
# put the content of 'wordnet31' to 'wordnet' in 'nltk_data/corpora' (there are issues with importing wordnet31 from nltk.corpus)
# download OpenDutchWordnet from 'https://github.com/cultural-ai/OpenDutchWordnet'

import json
import requests
import time
import re
import sys
from io import BytesIO
from zipfile import ZipFile
from SPARQLWrapper import SPARQLWrapper, JSON
from nltk.corpus import wordnet as wn

def main():
    print("Download wordnet31 from 'https://github.com/nltk/nltk_data/blob/gh-pages/packages/corpora/wordnet31.zip' and put the content of 'wordnet31' to 'wordnet' in 'nltk_data/corpora' (there are issues with importing wordnet31 from nltk.corpus")
    print("Download OpenDutchWordnet from 'https://github.com/cultural-ai/OpenDutchWordnet', pass the path to odwn")

def pwn(synsets:list) -> dict:
    '''
    Getting lemmata, definition, examples of a synset
    synsets: a list of synsets IDs (str)
    Return a dict: {'synset_id': {'lemmata': '',
                                   'definition': '',
                                   'examples': []}
    Requires NLTK, wordnet corpus version 3.1
    '''
    
    results_pwn = {}
    
    for s in synsets:
        synset = wn.synset(s)
        lemmata = [l.name() for l in synset.lemmas()]
        definition = synset.definition()
        examples = synset.examples()
        
        # writing results 
        results_pwn[s] = {'lemmata': lemmata,
                         'definition': definition,
                         'examples': examples}
        
    return results_pwn

# OpenDutch Wordnet

def odwn(synsets:list, path_odwn:str) -> dict:
    '''
    Getting lemmata, sense definitions, synset definitions, examples of ODWN synsets
    synsets: list of synset IDs (str)
    path_odwn: str path to the directory with OpenDutchWordnet (not including the module itself)
    '''
    # importing ODWN
    sys.path.insert(0,path_odwn)
    from OpenDutchWordnet import Wn_grid_parser
    # creating an instance
    instance = Wn_grid_parser(Wn_grid_parser.odwn)

    # importing synset_glosses
    path_synset_glosses = "https://raw.githubusercontent.com/cultural-ai/wordsmatter/main/ODWN/odwn_synset_glosses.json"
    
    with open(path_synset_glosses,'r') as jf:
        synset_glosses = json.load(jf)

    return None

####################

# Wereldculturen Thesaurus NMVW

def nmvw(term_ids:list) -> dict:
    '''
    Getting info about terms by their handle IDs in NMVW-thesaurus
    term_ids: list of term IDs (str)
    Returns a dict with query results: {'ID': {'prefLabel': '',
                                               'altLabel': [],
                                               'notes': [],
                                               'exactMatch': '',
                                               'scheme': ''}}
    '''
    
    # nmvw: importing thesaurus
    path_to_nmvw = 'https://github.com/cultural-ai/wordsmatter/raw/main/NMVW/nmvw_thesaurus.json.zip'
    nmvw_raw = requests.get(path_to_nmvw).content
    nmvw_zip = ZipFile(BytesIO(nmvw_raw))
    nmvw_json = json.loads(nmvw_zip.read(nmvw_zip.infolist()[0]).decode())

    results_nmvw = {}
    
    for term_id in term_ids:
        handle = 'https://hdl.handle.net/20.500.11840/termmaster' + term_id
        results_nmvw[handle] = nmvw_json.get(handle)
        
    return results_nmvw

# Getty AAT

def aat(aat_uri:list, lang:str) -> dict:
    '''
    Querying prefLabel, altLabel, scopeNote, rdfs comments of concepts in AAT;
    Sends SPARQL queries to the AAT endpoint via SPARQLwrapper 
    aat_uri: list of AAT concepts IDs (str) ['ID']
    lang: str 'en' or 'nl'
    Returns a dict with query results: {'ID':{'lang':'en',
                                              'prefLabel':'',
                                              'altLabels':[],
                                              'scopeNote':'',
                                              'prefLabel_comment':'',
                                              'altLabel_comment':''}
    '''
    
    sparql = SPARQLWrapper("http://vocab.getty.edu/sparql")
    
    if lang == 'en':
        lang_code = '300388277'
    if lang == 'nl':
        lang_code = '300388256'
        
    result_dict = {}
        
    for uri in aat_uri:
        
        result_dict[uri] = {}
        
        query_string = '''SELECT ?prefLabel (GROUP_CONCAT(?altLabel;SEPARATOR="#") AS ?altLabels)
        ?scopeNote ?prefLabel_comment ?altLabel_comment
        WHERE {aat:''' + uri + ''' xl:prefLabel ?pL .?pL dcterms:language aat:''' + lang_code + ''';
        xl:literalForm ?prefLabel .
        OPTIONAL {?pL rdfs:comment ?prefLabel_comment . }
        OPTIONAL {aat:''' + uri + ''' xl:altLabel ?aL .
        ?aL dcterms:language aat:''' + lang_code + ''';
        xl:literalForm ?altLabel . 
        OPTIONAL { ?aL rdfs:comment ?altLabel_comment . }}
        OPTIONAL {aat:''' + uri + ''' skos:scopeNote / dcterms:language aat:'''+ lang_code + ''';
        skos:scopeNote / rdf:value ?scopeNote . }}
        GROUP BY ?prefLabel ?scopeNote ?prefLabel_comment ?altLabel_comment'''
        
        sparql.setQuery(query_string)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        
        altLabels = []
        scopeNote = None
        prefLabel_comment = None
        altLabel_comment = None
        
        for result in results['results']['bindings']:
            
            if 'altLabels' in result:
                altLabels = result['altLabels']['value'].split('#')
            if 'scopeNote' in results:
                scopeNote = result['scopeNote']['value']
            if 'prefLabel_comment' in results:
                prefLabel_comment = result['prefLabel_comment']['value']
            if 'altLabel_comment' in results:
                altLabel_comment = result['altLabel_comment']['value']

            result_dict[uri]['lang'] = lang
            result_dict[uri]['prefLabel'] = result['prefLabel']['value']
            result_dict[uri]['altLabels'] = altLabels
            result_dict[uri]['prefLabel_comment'] = prefLabel_comment
            result_dict[uri]['altLabel_comment'] = altLabel_comment
            result_dict[uri]['scopeNote'] = scopeNote
        
    return result_dict

# Wikidata

def wd(qids:list,lang:str,user_agent:str) -> dict:
    
    """
    Requesting labels, aliases, descriptions of Wikidata entities
    qids: list of entity IDs (str) (requests 50 entities at a time slicing the list)
    lang: str with language code; for example, 'en' or 'nl';
    (see language codes in Wikidata: https://www.wikidata.org/w/api.php?action=help&modules=wbgetentities)
    user_agent: str with user-agent's info; required by Wikidata (see: https://meta.wikimedia.org/wiki/User-Agent_policy)
    Returns a dict: {'QID': {'type': '',
                     'id': 'QID',
                     'labels': {'lang': {'language': 'lang', 'value': ''}},
                     'descriptions': {'lang': {'language': 'lang','value': ''}},
                     'aliases': {'lang': [{'language': 'lang', 'value': ''}
    """
    
    # 'wbgetentities' constant params
    url = "https://www.wikidata.org/w/api.php"
    params = {"action":"wbgetentities",
              "ids":"", # string of entities (max=50)
              "props":"labels|aliases|descriptions",
              "languages":lang,
              "format":"json"}
    headers = {"user-agent":user_agent}

    # - N LOOPS - #

    # if there's a remainder
    if len(qids) % 50 > 0:
        loops = len(qids) // 50 + 1 # add another loop for requests
    else:
        loops = len(qids) // 50

    # - REQUEST LOOPS - #   

    # counters to slice qids

    start_quid_str = 0
    end_quid_str = 0

    for i in range(0,loops):
        ids_string = "" # putting Qs in one string
        end_quid_str = end_quid_str + 50 # max 50 entities per request

        for q in qids[start_quid_str:end_quid_str]:
            ids_string = ids_string + f"{q}|"

        start_quid_str = start_quid_str + 50

        # updating params

        params["ids"] = ids_string.rstrip("|")

        # sending a request
        d = requests.get(url,params=params,headers=headers)
        literals = d.json() # claims per request

    return literals['entities']

if __name__ == "__main__":
    main()