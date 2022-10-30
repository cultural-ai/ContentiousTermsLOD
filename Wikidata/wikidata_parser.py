import requests
import json
import re
import time

def parse_values_of_properies(query_results:dict, QID:str, propepties:list) -> dict:

    """
    Parses the values (id) of the properties of entities from Wikidata response,
    for example: get the values of the properrty P31 for the entity Q104534511;
    Takes Wikidata response in json format, QID (str) (only 1 QID),
    and properties (list of str; for example ['P31','P279']);
    Return a dict {'QID': {'property':{'property_ID': ''}}};
    The empty value of the property id is intended for its label
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


def request_claims(qids:list, propepties:list, headers:dict, path='', index=1) -> list:

    """
    Sends request to Wikidata: getting claims of entities
    qids: list of entities (str) to work on;
    properties: list of str; for example ['P31','P279'];
    headers: for Wikidata to define "user-agent";
    path: optional; str path where to save json files (including '/');
    index: optional, to indicate the output file index;
    Saves results in json
    Returns a list of entities claims of which were not requested due to request errors
    (empty if everything was successfully requested)
    """

    # 'wbgetentities' constant params
    url = "https://www.wikidata.org/w/api.php"
    params = {"action":"wbgetentities",
              "ids":"", # string of entities (max=50)
              "props":"claims",
              "format":"json"}

    results = []
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
                results.append(parse_values_of_properies(claims,entity,propepties))

            # - SAVING RESULTS - #
    
            with open(f'{path}claims_{index}.json', 'w') as json_file:
                json.dump(results, json_file)
            # to prevent server errors
            time.sleep(3)

        else:
            failed_entities.extend(qids[start_quid_str:end_quid_str])

    return failed_entities


def request_labels_of_property_values(qids:list, headers:dict, path='', index=1) -> list:
    """
    Getting en labels of the property values
    qids: list of entities (str) to work on;
    headers: for Wikidata to define "user-agent";
    path: optional; str path where to save json files (including '/');
    index: optional, to indicate the output file index;
    Saves results in json
    Returns a list of entities claims of which were not requested due to request errors
    (empty if everything was successfully requested)
    """
    
    # 'wbgetentities' constant params
    url = "https://www.wikidata.org/w/api.php"
    params = {"action":"wbgetentities",
              "ids":"", # string of entities (max=50)
              "props":"labels",
              "languages":"en|nl", # requesting 2 languages at the same time
              "format":"json"}
    
    results = {}
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
        ids_string = "" # putting Qs in one string
        end_quid_str = end_quid_str + 50 # max 50 entities per request

        for q in qids[start_quid_str:end_quid_str]:
            ids_string = ids_string + f"{q}|"

        start_quid_str = start_quid_str + 50

        # updating params
        params["ids"] = ids_string.rstrip("|")

        # sending a request
        d = requests.get(url,params=params,headers=headers)
        labels = d.json() # claims per request
        
        if 'entities' in labels:
            for entity,l in labels['entities'].items():
                two_langs = {"en":"","nl":""}
                if 'labels' in l:
                    if "en" in l['labels']:
                        two_langs["en"] = l['labels']["en"]['value']
                    if "nl" in l['labels']:
                        two_langs["nl"] = l['labels']["nl"]['value']
                results[entity] = two_langs

            # - SAVING RESULTS - #
    
            with open(f'{path}labels_property_values_{index}.json', 'w') as json_file:
                json.dump(results, json_file)
                
            # to prevent server errors    
            time.sleep(3)

        else:
            failed_entities.extend(qids[start_quid_str:end_quid_str])

    return failed_entities

def find_where_query_term_appears(query_results:dict, lang:str) -> dict:
    """
    Finding where a target term appears in the search results: label, description, aliases
    Takes Wikidata search results in json (query API request with search generator) and
    lang – tha language string ("en" or "nl")
    Returns dict with info about every hit and where a term was found
    """
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
