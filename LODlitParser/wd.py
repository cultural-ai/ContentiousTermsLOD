# Wikidata module

import json
import requests
import time
import re

def get_search_hits(search_term:str,lang:str,user_agent:str,filter_by_keywords='',filter_by_statements='',stemming=False) -> dict:
    """
    Getting search hits of a term in Wikidata
    search_term: str a term or a phrase to search in Wikidata
    lang: str with language code; for example, 'en' or 'nl';
    # (see language codes in Wikidata: https://www.wikidata.org/w/api.php?action=help&modules=wbgetentities)
    user_agent: str with user-agent's info; required by Wikidata (see: https://meta.wikimedia.org/wiki/User-Agent_policy)
    filter_by_keywords: str optional, set the keywords to exclude from the search results with dashes like "-scientific -article"; default is ''
    filter_by_statements: str optional; set the statements to exclude from the search results, specifying property and its value like "P31=Q5"
    # (meaning that entities with the property P31 ("instance of") with the value "Q5" ("human") will be excluded);
    # multiple statements are possible, separate them with a whitespace; default is ''
    stemming: bool is to perform stemming of the search term (works only for English); default is False
    """

    search_hits = {}

    # 'query' with 'search' generator: constant params
    url = "https://www.wikidata.org/w/api.php"
    params = {"action":"query",
              "prop":"entityterms",
              "wbetlanguage":lang,
              "generator":"search",
              "gsrsearch":f'"{search_term}"', # term goes here (quotes for stemming off)
              "gsrlimit":"1", # 1 result is enough to get the hits info
              "gsrinfo":"totalhits",
              "format":"json"}
    headers = {"user-agent":user_agent}

    # stemming
    if stemming == True:
        params["gsrsearch"] = search_term

    r = requests.get(url,params=params,headers=headers)
    hits = r.json()['query']['searchinfo']['totalhits']
    search_hits[search_term] = hits

    return search_hits


def get_lit(qids:list,lang:str,user_agent:str) -> list:
    
    """
    Getting labels, aliases, descriptions of Wikidata entities
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