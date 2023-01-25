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
    #change path
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

def odwn(le_ids:list, path_odwn:str) -> dict:
    '''
    Getting Lemma, sense definitions, examples, synset ID, synset definitions of ODWN Lexical Entries
    le_ids: list of Lexical Entries IDs (str)
    path_odwn: str path to the directory with OpenDutchWordnet (not including the module itself, for example 'user/Downloads')
    Returns a dict: {'le_id': {'lemma': '',
                                'sense_def': '',
                                'examples': [],
                                'synset_ID': '',
                                'synset_def': []}
    '''
    # importing ODWN
    sys.path.insert(0,path_odwn)
    from OpenDutchWordnet import Wn_grid_parser
    # creating an instance
    instance = Wn_grid_parser(Wn_grid_parser.odwn)
    
    # importing all synset definitions
    path_to_glosses = "https://raw.githubusercontent.com/cultural-ai/wordsmatter/main/ODWN/odwn_synset_glosses.json"
    synset_glosses = requests.get(path_to_glosses).json()
    
    results_odwn = {}

    for le_id in le_ids:
        le = instance.les_find_le(le_id)
        synset_id = le.get_synset_id()

        sense_def = le.get_definition()
        if sense_def == '':
            sense_def = None

        results_odwn[le_id] = {'lemma': le.get_lemma(),
                                'sense_def': sense_def,
                                'examples': le.get_sense_example(),
                                'synset_ID': synset_id,
                                'synset_def': synset_glosses.get(synset_id)}
    return results_odwn

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
            if 'scopeNote' in result:
                scopeNote = result['scopeNote']['value']
            if 'prefLabel_comment' in result:
                prefLabel_comment = result['prefLabel_comment']['value']
            if 'altLabel_comment' in result:
                altLabel_comment = result['altLabel_comment']['value']

            result_dict[uri]['lang'] = lang
            result_dict[uri]['prefLabel'] = result['prefLabel']['value']
            result_dict[uri]['altLabels'] = altLabels
            result_dict[uri]['prefLabel_comment'] = prefLabel_comment
            result_dict[uri]['altLabel_comment'] = altLabel_comment
            result_dict[uri]['scopeNote'] = scopeNote
        
    return result_dict

# Wikidata

def wd(qids:list,lang:str,user_agent:str) -> list:
    
    """
    Requesting labels, aliases, descriptions of Wikidata entities
    qids: list of entity IDs (str) (requests 50 entities at a time slicing the list)
    lang: str with language code; for example, 'en' or 'nl';
    (see language codes in Wikidata: https://www.wikidata.org/w/api.php?action=help&modules=wbgetentities)
    user_agent: str with user-agent's info; required by Wikidata (see: https://meta.wikimedia.org/wiki/User-Agent_policy)
    Returns a list of dicts: [{'QID': {'type': '',
                     'id': 'QID',
                     'labels': {'lang': {'language': 'lang', 'value': ''}},
                     'descriptions': {'lang': {'language': 'lang','value': ''}},
                     'aliases': {'lang': [{'language': 'lang', 'value': ''}]
    """
    
    wd_results = []

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
        literals = d.json()

        for qid, value in literals['entities'].items():
            wd_results.append({qid:value})

    return wd_results

def get_literals(resource:str) -> str:
    '''
    Getting literal values of related matches
    resource: str name of the resource 'aat', 'wikidata', 'pwn', 'odwn', 'nmvw' 
    path_odwn: str path to the directory with OpenDutchWordnet (not including the module itself, for example 'user/Downloads')
    Saves json files with literal values:
    aat: 'aat_rm_en.json','aat_rm_nl.json'
    wikidata: 'wikidata_rm_en.json','wikidata_rm_nl.json'
    pwn: 'pwn_rm.json'
    odwn: 'odwn_rm.json'
    nmvw: 'nmvw_rm.json'
    
    '''
    
    # importing related matches
    path_to_rm = 'https://github.com/cultural-ai/wordsmatter/raw/main/rm.json'
    related_matches = requests.get(path_to_rm).json()

    if resource == 'aat':
        # AAT in EN
        aat_en = [v['related_matches']['aat'][0] for v in related_matches.values() if v['lang'] == 'en' \
                  and 'None' not in v['related_matches']['aat']]
        aat_en_results = aat(aat_en,'en')
        with open('aat_rm_en.json', 'w') as jf:
            json.dump(aat_en_results, jf)
        print("AAT EN is saved")

        # AAT in NL
        aat_nl = [v['related_matches']['aat'][0] for v in related_matches.values() if v['lang'] == 'nl' \
                  and 'None' not in v['related_matches']['aat']]
        aat_nl_results = aat(aat_nl,'nl')
        with open('aat_rm_nl.json', 'w') as jf:
            json.dump(aat_nl_results, jf)
        print("AAT NL is saved")
    
    if resource == 'wikidata':
        user_agent = input("Enter your user agent details for Wikidata:")
        
        # Wikidata in EN
        wikidata_en = [v['related_matches']['wikidata'][0] for v in related_matches.values() if v['lang'] == 'en' \
                  and 'None' not in v['related_matches']['wikidata']]
        wikidata_en_results = wd(wikidata_en,'en',user_agent)
        with open('wikidata_rm_en.json', 'w') as jf:
            json.dump(wikidata_en_results, jf)
        print("Wikidata EN is saved")

        # Wikidata in NL
        wikidata_nl = [v['related_matches']['wikidata'][0] for v in related_matches.values() if v['lang'] == 'nl' \
                  and 'None' not in v['related_matches']['wikidata']]
        wikidata_nl_results = wd(wikidata_nl,'nl',user_agent)
        with open('wikidata_rm_nl.json', 'w') as jf:
            json.dump(wikidata_nl_results, jf)
        print("Wikidata NL is saved")
        
    if resource == 'pwn':
        # PWN
        pwn_synsets = []

        for v in related_matches.values():
            if v['lang'] == 'en' and 'None' not in v['related_matches']['pwn']:
                pwn_synsets.extend(v['related_matches']['pwn'])

        pwn_results = pwn(pwn_synsets)
        with open('pwn_rm.json', 'w') as jf:
            json.dump(pwn_results, jf)
        print("PWN is saved")
        
    if resource == 'odwn':
        path_odwn = input("Path to your local OpenDutchWordNet directory:")
        #6 ODWN
        odwn_synsets = []

        for v in related_matches.values():
            if v['lang'] == 'nl' and 'None' not in v['related_matches']['odwn']:
                odwn_synsets.extend(v['related_matches']['odwn'])

        odwn_results = odwn(odwn_synsets,path_odwn)
        with open('odwn_rm.json', 'w') as jf:
            json.dump(odwn_results, jf)
        print("ODWN is saved")
        
    if resource == 'nmvw':
        #7 NMVW
        nmvw_handles = [v['related_matches']['nmvw'][0] for v in related_matches.values() if v['lang'] == 'nl' \
                  and 'None' not in v['related_matches']['nmvw']]
        nmvw_results = nmvw(nmvw_handles)
        with open('nmvw_rm.json', 'w') as jf:
            json.dump(nmvw_results, jf)
        print("NMVW is saved")
    
    return ("All files are saved")

if __name__ == "__main__":
    main()