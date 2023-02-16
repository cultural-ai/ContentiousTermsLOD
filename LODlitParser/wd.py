# Wikidata module
# to use 'get_bows', download stopwords from nltk: nltk.download('stopwords')

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import json
import requests
import time
import re

def main():
    if __name__ == "__main__":
        main()

def get_search_hits(search_term:str,lang:str,user_agent:str,filter_by_keywords=[],filter_by_statements=[],stemming=False) -> dict:
    """
    Getting search hits of a term in Wikidata
    search_term: str a term or a phrase to search in Wikidata
    lang: str with language code; for example, 'en' or 'nl';
    # (see language codes in Wikidata: https://www.wikidata.org/w/api.php?action=help&modules=wbgetentities)
    user_agent: str with user-agent's info; required by Wikidata (see: https://meta.wikimedia.org/wiki/User-Agent_policy)
    filter_by_keywords: list optional;  the keywords to exclude from the search results; default is []
    filter_by_statements: list optional; list of tuples with statements to exclude from the search results, specifying property and its value like [('P31','Q5'),('P31', 'Q16521')]
    # (meaning that entities with the property P31 ("instance of") with the values "Q5" ("human") and "Q16521" ("taxon") will be excluded);
    # multiple statements are possible, separate them with a whitespace; default is ''
    stemming: bool is to perform stemming of the search term (works only for English); default is False
    Returns a dict
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

    # filtering by keywords
    if filter_by_keywords != []:
        keyword_str = ''
        for kw in filter_by_keywords:
            keyword_str = keyword_str + f" -{kw}"
        params["gsrsearch"] = params["gsrsearch"] + keyword_str

    # filtering by statements    
    if filter_by_statements != []:
        statements_str = ''
        for t in filter_by_statements:
            statements_str = statements_str + f" -haswbstatement:{t[0]}={t[1]}"
        params["gsrsearch"] = params["gsrsearch"] + statements_str

    r = requests.get(url,params=params,headers=headers)
    hits = r.json()['query']['searchinfo']['totalhits']
    search_hits[search_term] = hits

    return search_hits


def get_lit_by_term(search_term:str,lang:str,user_agent:str,filter_by_keywords=[],filter_by_statements=[],stemming=False) -> dict:
    """
    Getting Qids, their labels, aliases, descriptions by a query term; to support stemming, set stemming=True
    search_term: str a term or a phrase to search in Wikidata
    lang: str with language code; for example, 'en' or 'nl';
    # (see language codes in Wikidata: https://www.wikidata.org/w/api.php?action=help&modules=wbgetentities)
    user_agent: str with user-agent's info; required by Wikidata (see: https://meta.wikimedia.org/wiki/User-Agent_policy)
    filter_by_keywords: list optional;  the keywords to exclude from the search results; default is []
    filter_by_statements: list optional; list of tuples with statements to exclude from the search results, specifying property and its value like [('P31','Q5'),('P31', 'Q16521')]
    # (meaning that entities with the property P31 ("instance of") with the values "Q5" ("human") and "Q16521" ("taxon") will be excluded);
    stemming: bool is to perform stemming of the search term (works only for English); default is False
    Returns a dict
    """

    # 'query' with 'search' generator: constant params
    url = "https://www.wikidata.org/w/api.php"
    params = {"action":"query",
              "prop":"entityterms",
              "wbetlanguage":lang,
              "generator":"search",
              "gsrsearch":f'"{search_term}"', # quotes for stemming off
              "gsrlimit":"max", # getting all results
              "gsroffset":"0", # offset
              "gsrinfo":"totalhits",
              "gsrsort":"incoming_links_desc", # sorting results by incoming links
              "format":"json",} 
    headers = {"user-agent":user_agent}

    results = {} # dict to store the results

    # stemming
    if stemming == True:
        params["gsrsearch"] = search_term # stemming on
    
    # filtering by keywords
    if filter_by_keywords != []:
        keyword_str = ''
        for kw in filter_by_keywords:
            keyword_str = keyword_str + f" -{kw}"
        params["gsrsearch"] = params["gsrsearch"] + keyword_str

    # filtering by statements    
    if filter_by_statements != []:
        statements_str = ''
        for t in filter_by_statements:
            statements_str = statements_str + f" -haswbstatement:{t[0]}={t[1]}"
        params["gsrsearch"] = params["gsrsearch"] + statements_str    
    
    # counter for offset
    gsroffset = 0

    # sending requests
    w = requests.get(url,params=params,headers=headers)
    wikidata_json = w.json()
    time.sleep(2) # to prevent 502
        
    # checking the number of hits
    hits = wikidata_json['query']['searchinfo']['totalhits']
        
    # if there are no results
    if hits == 0:
        results[search_term] = wikidata_json['query']
        loops = 0
            
    # saving results from the first loop
    else:
        results[search_term] = wikidata_json['query']['pages']

    # - CONDITIONS FOR LOOPS- #

    # if there are less than 500 hits for a term, no loops are needed
    if hits < 500:
        loops = 0

    # 10K is max; and if hits > 500, offset is needed
    if 10000 > hits > 500 and hits % 500 > 0:
        loops = hits // 500
        
    # minus one loop if there's no remainder
    if 10000 > hits > 500 and hits % 500 == 0:
        loops = hits // 500 - 1
        
    # as the first loop is already done, max = 19
    if hits > 10000:
        loops = 19

    # - REQUEST LOOPS - #   

    for i in range(0,loops):
        gsroffset = gsroffset + 500
        # setting the offset and sending a new request
        params["gsroffset"] = f"{gsroffset}"
        w_i = requests.get(url,params=params,headers=headers)
        wikidata_json_i = w_i.json()
        
        # saving the results
        results[search_term].update(wikidata_json_i['query']['pages'])
        time.sleep(2)

    return results


def get_lit_by_q(qids:list,lang:str,user_agent:str) -> list:
    
    """
    Getting labels, aliases, descriptions of Wikidata entities by their Qids
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


def get_labels_by_q(qids:list,lang:list,user_agent:str) -> dict:

    """
    Getting labels of entities by QIDs
    qids: list of entities' QIDs (str) to work on;
    lang: list of str with language code; for example, ['en','nl'];
    (see language codes in Wikidata: https://www.wikidata.org/w/api.php?action=help&modules=wbgetentities)
    user_agent: str with user-agent's info; required by Wikidata (see: https://meta.wikimedia.org/wiki/User-Agent_policy)
    Returns a dict: {"labels":dict with labels by lang,"failed":list of QIDs that were failed}
    """

    # 'wbgetentities' constant params
    url = "https://www.wikidata.org/w/api.php"
    params = {"action":"wbgetentities",
              "ids":"", # string of entities (max=50)
              "props":"labels", # only labels
              "format":"json"}
    headers = {"user-agent":user_agent}

    request = {}
    failed_entities = []

    # languages
    if len(lang) > 1:
        languages = ''
        for l in lang:
            languages = languages + f"{l}|"
        # updating params
        params["languages"] = languages.rstrip("|")
    else:
        params["languages"] = lang[0]

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
        labels = d.json()

        if 'entities' in labels:
            for entity,lbl in labels['entities'].items():
                per_lang = {}
                for l in lang:
                    if 'labels' in lbl:
                        if l in lbl['labels']:
                            per_lang[l] = lbl['labels'][l]['value']

                request[entity] = per_lang

            # to prevent server errors    
            time.sleep(2)

        else:
            failed_entities.extend(qids[start_quid_str:end_quid_str])

    results = {"labels":request,"failed":failed_entities}

    return results

def _claims_parse_properties(query_results:dict, QID:str, propepties:list) -> dict:
    """
    Parses the values of the properties of entities from Wikidata response,
    for example: get the values of the properrty P31 for the entity Q104534511;
    Takes Wikidata response in json format, QID (str) (only 1 QID),
    and properties (list of str; for example ['P31','P279']);
    Return a dict {'QID': {'property_ID':{'property_value': ''}}};
    The empty value of the property_value is intended for its label, which is queried using another function
    """
    dict_per_qid = {}
    dict_per_qid[QID] = {}
    
    for p in propepties:

        dict_per_qid[QID][p] = {}
        if 'missing' not in query_results['entities'][QID].keys():
            claims_per_qid = query_results['entities'][QID]['claims']
            # getting property values
            if p in claims_per_qid:
                for i in claims_per_qid[p]:
                    if 'datavalue' in i['mainsnak']:
                        dict_per_qid[QID][p][i['mainsnak']['datavalue']['value'].get('id')] = ""
                    
    return dict_per_qid

def get_claims(qids:list, propepties:list, user_agent:str, path='') -> str:

    """
    Getting claims by QIDs and properties
    qids: list of entities (str) to work on, if len > 50, results will be saved in batches (separate files)
    properties: list of str; for example ['P31','P279']; getting claims only with the properties specified in this list
    user_agent: str with user-agent's info; required by Wikidata (see: https://meta.wikimedia.org/wiki/User-Agent_policy)
    path: optional; str path where to save json files (including '/');
    Saves the request results in json files due to large size;
    Returns str when files are saved and whether there are failed entities;
    Saves failed entities (due to request errors) in a separate txt file;
    Uses another function (_claims_parse_properties) to parse the indicated properties from the request results
    """

    # 'wbgetentities' constant params
    url = "https://www.wikidata.org/w/api.php"
    params = {"action":"wbgetentities",
              "ids":"", # string of entities (max=50)
              "props":"claims",
              "format":"json"}
    headers = {"user-agent":user_agent}

    failed_entities = []

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
        
        results = {}

        ids_string = "" # putting Qs in one string
        end_quid_str = end_quid_str + 50 # max 50 entities per request

        for q in qids[start_quid_str:end_quid_str]:
            ids_string = ids_string + f"{q}|"

        start_quid_str = start_quid_str + 50

        # updating params
        params["ids"] = ids_string.rstrip("|")

        # sending a request
        d = requests.get(url,params=params,headers=headers)
        claims = d.json() # claims per request

        if 'entities' in claims:
            for entity in claims['entities']:
                results.update(_claims_parse_properties(claims,entity,propepties))

            # - SAVING RESULTS IN BATCHES - #
    
            with open(f'{path}claims_{start_quid_str}.json', 'w') as json_file:
                json.dump(results, json_file)
            # to prevent server errors
            time.sleep(2)

        else:
            failed_entities.extend(qids[start_quid_str:end_quid_str])

    if len(failed_entities) > 0:
        with open(f'{path}failed_entities.txt','w') as txt_file:
            for q in failed_entities:
                txt_file.writelines(f"{q}\n")
        output_str = f"Requests are saved in {path}. There are {len(failed_entities)} failed entities, see the .txt file"
    else:
        output_str = f"Requests are saved in {path}"

    return output_str

def find_where_query_term_appears(query_results_path:str, lang:str) -> dict:
    """
    Finding where a target term appears in the search results: label, description, or aliases
    query_results_path: str, the path to the search results  (the output of 'get_lit_by_term'), including '/'
    lang – str language string ("en" or "nl") corresponding to the results language of 'get_lit_by_term'
    Returns dict with info about every hit and where a term was found
    """
    
    # importing query results
    with open(query_results_path,'r') as jf:
        query_results = json.load(jf)

    target_terms_dict_wikidata = {}

    for query_term, hits in query_results.items():
        
        results_per_query_term = []

        for page_id, values in hits.items():
            if 'entityterms' in values:
                
                # checking labels
                if 'label' in values['entityterms']:
                    if len(re.findall(f'\\b{query_term}\\b',values['entityterms']['label'][0],re.IGNORECASE)) > 0:
                        dict_per_hit = {}
                        dict_per_hit['query_term'] = query_term
                        dict_per_hit['lang'] = lang
                        dict_per_hit['QID'] = values['title']
                        dict_per_hit['prefLabel'] = values['entityterms']['label'][0]
                        dict_per_hit['aliases'] = values['entityterms'].get('alias')
                        dict_per_hit['description'] = values['entityterms'].get('description')
                        dict_per_hit['index'] = values['index']
                        dict_per_hit['found_in'] = 'prefLabel'
                        results_per_query_term.append(dict_per_hit)
                        
                # checking aliases        
                if 'alias' in values['entityterms']:
                    for a in values['entityterms']['alias']:
                        if len(re.findall(f'\\b{query_term}\\b',a,re.IGNORECASE)) > 0:
                            dict_per_hit = {}
                            dict_per_hit['query_term'] = query_term
                            dict_per_hit['lang'] = lang
                            dict_per_hit['QID'] = values['title']
                            if values['entityterms'].get('label') != None:
                                dict_per_hit['prefLabel'] = values['entityterms']['label'][0]
                            else:
                                dict_per_hit['prefLabel'] = None
                            dict_per_hit['aliases'] = values['entityterms']['alias']
                            dict_per_hit['description'] = values['entityterms'].get('description')
                            dict_per_hit['index'] = values['index']
                            dict_per_hit['found_in'] = 'aliases'
                            results_per_query_term.append(dict_per_hit)
                            
                # checking descriptions            
                if 'description' in values['entityterms']:
                    if len(re.findall(f'\\b{query_term}\\b',values['entityterms']['description'][0],re.IGNORECASE)) > 0:
                        dict_per_hit = {}
                        dict_per_hit['query_term'] = query_term
                        dict_per_hit['lang'] = lang
                        dict_per_hit['QID'] = values['title']
                        if values['entityterms'].get('label') != None:
                            dict_per_hit['prefLabel'] = values['entityterms']['label'][0]
                        else:
                            dict_per_hit['prefLabel'] = None
                        dict_per_hit['aliases'] = values['entityterms'].get('alias')
                        dict_per_hit['description'] = values['entityterms']['description'][0]
                        dict_per_hit['index'] = values['index']
                        dict_per_hit['found_in'] = 'description'
                        results_per_query_term.append(dict_per_hit)
                        
        target_terms_dict_wikidata[query_term] = results_per_query_term

    return target_terms_dict_wikidata


def filter_proper_names(dataset_path:str, lang:str, path:'') -> str:
    """
    Filtering out proper names in the search results
    dataset_path: str, the path to the search results with claims ('results_w_claims_[lang].json')
    lang: str, the lang of the search results ('en' or 'nl')
    path: optional; str path where to save json files (including '/');
    Saves a json file with search results without proper names (results_clean_[lang].json)
    Returns a status str with N of filtered out entities
    """

    # importing results w claims
    with open(dataset_path,'r') as jf:
        dataset = json.load(jf)

    results_clean = {}
    n_filtered = 0

    if lang == 'en':
        Q5_value = 'human'
    if lang == 'nl':
        Q5_value = 'mens'

    for query_term,results in dataset.items():
        results_clean[query_term] = []
        for hit in results:
            count_Q5 = 0
            for p in hit['instance_of']:
                    if p == Q5_value:
                        count_Q5 += 1

            if hit['prefLabel'] != None and len(re.findall(f"\\b{hit['query_term'].capitalize()}\\b",hit['prefLabel'])) > 0 and count_Q5 > 0:
                n_filtered += 1

            else:
                results_clean[query_term].append(hit)

    with open(f"{path}results_clean_{lang}.json","w") as jf:
        json.dump(results_clean, jf)
                
    return f"File is saved. {n_filtered} entities are filtered out."


def get_bows(path_to_results:str, lang:str) -> dict:
    '''
    Getting bag of words (BoW) from the Wikidata search results for every search term
    path_to_results: str, a path to the search results (in json format)
    lang: str, 'en' or 'nl'
    Returns a dict with BoWs per hit per term: {term:[{QID:['token1','token2','token3']}]}
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
            
            literals.append(hit["prefLabel"]) # adding prefLabel

            if hit["found_in"] == "prefLabel" or hit["found_in"] == "aliases":
                literals.extend(hit["instance_of"])
                literals.extend(hit["subclass_of"])

            if hit["aliases"] != None:
                literals.extend(hit["aliases"]) # adding aliases

            # adding descriptions
            # descriptions can be str or list
            # None doesn't add
            if type(hit["description"]) == str:
                literals.append(hit["description"])
                
            if type(hit["description"]) == list:
                literals.extend(hit["description"])

            bow = []
            for lit in literals:
                # prefLabel, instance_of, subclass_of can be None
                if lit != None:
                    bow.extend(lit.replace('(','').replace(')','').replace('-',' ').replace('/',' ')\
                           .replace(',','').lower().split(' '))
            
            # checking lang for stopwords
            if lang == 'en':
                bag_unique = [wnl.lemmatize(w) for w in set(bow) if w not in stopwords.words('english') \
                                    and re.search('(\W|\d)',w) == None and w != hit["query_term"] and w != '']
            if lang == 'nl':
                bag_unique = [wnl.lemmatize(w) for w in set(bow) if w not in stopwords.words('dutch') \
                                    and re.search('(\W|\d)',w) == None and w != hit["query_term"] and w != '']
                
            q_bag[hit["QID"]] = bag_unique

            list_by_term.append(q_bag)

        all_bows[query_term] = list_by_term
        
    return all_bows