# lodlitparser
# install NLTK
# Important! download wordnet31 ('https://github.com/nltk/nltk_data/blob/gh-pages/packages/corpora/wordnet31.zip');
# put the content of 'wordnet31' to 'wordnet' in 'nltk_data/corpora' (it is not possible to import wordnet31 from nltk.corpus; See explanations on the WordNet website (retrieved on 10.02.2023): https://wordnet.princeton.edu/download/current-version; "WordNet 3.1 DATABASE FILES ONLY. You can download the WordNet 3.1 database files. Note that this is not a full package as those above, nor does it contain any code for running WordNet. However, you can replace the files in the database directory of your 3.0 local installation with these files and the WordNet interface will run, returning entries from the 3.1 database. This is simply a compressed tar file of the WordNet 3.1 database files."
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
    print("Install NLTK and download wordnet. Download wordnet31 from 'https://github.com/nltk/nltk_data/blob/gh-pages/packages/corpora/wordnet31.zip' and put the content of 'wordnet31' to 'wordnet' in 'nltk_data/corpora'")
    print("Download OpenDutchWordnet from 'https://github.com/cultural-ai/OpenDutchWordnet', pass the path to odwn")

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

if __name__ == "__main__":
    main()