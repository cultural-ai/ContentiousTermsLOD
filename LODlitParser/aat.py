# Getty AAT
# A module to parse query results (json) from Getty Art&Archiechture Thesaurus
# to use 'get_bows', download stopwords from nltk: nltk.download('stopwords')

import json
import gzip
import re
import csv
from SPARQLWrapper import SPARQLWrapper, JSON
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

def main():
	if __name__ == "__main__":
		main()

def sparql(aat_uri:list, lang:str) -> dict:
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


def _get_entity_info(entity_id:str, lang:str, aat_gzip:dict) -> dict:
    '''
    This function is used for 'find_term_in_literals'
    Getting the values of prefLabel (str), altLabel (list), prefLabel_comment (str), altLabel_comment(list), and scopeNote (str)
    by entity ID in AAT
    entity_id: str, entity ID in AAT (for example, '300189559')
    lang: str, 'en' or 'nl'; language of entities info
    aat_gzip: dict, ungzipped json file with search results (ungzips in the main function)
    Returns a dict {'entity': '',
					 'scopeNote': '',
					 'prefLabel_comment': '',
					 'prefLabel': '',
					 'altLabel': [],
					 'altLabel_comment': []}
    '''

    results = {}
    results['entity'] = entity_id
    altLabel_list = []
    altLabel_comment_list = []
    results['scopeNote'] = ''
    results['prefLabel_comment'] = ''
    
    for triple in aat_gzip["results"]["bindings"]:
        if entity_id in triple['Subject']['value']:
            
            # prefLabel
            if 'prefLabel' in triple['Predicate']['value']:
                for triple_t in aat_gzip["results"]["bindings"]:
                    if triple_t['Subject']['value'] == triple['Object']['value']:
                        if 'literalForm' in triple_t['Predicate']['value']:
                            results['prefLabel'] = triple_t['Object']['value']
                        # prefLabel comment
                        if 'comment' in triple_t['Predicate']['value']:
                            results['prefLabel_comment'] = triple_t['Object']['value']
                        
            # altLabel
            if 'altLabel' in triple['Predicate']['value']:
                for triple_t in aat_gzip["results"]["bindings"]:
                    if triple_t['Subject']['value'] == triple['Object']['value']:
                        if 'literalForm' in triple_t['Predicate']['value']:
                            altLabel_list.append(triple_t['Object']['value'])
                        # altLabel comment
                        if 'comment' in triple_t['Predicate']['value']:
                            altLabel_comment_list.append(triple_t['Object']['value'])
                            
            # scopeNote
            if 'scopeNote' in triple['Predicate']['value']:
                for triple_t in aat_gzip["results"]["bindings"]:
                    if triple_t['Subject']['value'] == triple['Object']['value']:
                        results['scopeNote'] = triple_t['Object']['value']
                            
            results['altLabel'] = altLabel_list
            results['altLabel_comment'] = altLabel_comment_list
                        
    return results

def find_term_in_literals(query_term:str, lang:str) -> list:
    '''
    Finding query terms in the literal values of properties:
    prefLabel, altLabel, rdfs comment (for prefLabel and altLabel), and scopeNote
    query_term: str, for example 'term'
    ang: str, 'en' or 'nl'; language of the literals in which the query term is searched
    Returns a list of dicts with an AAT entity URI and the property name in the literal value of which the term was found
    '''

    # reading the gzip json file with aat search results
    # change the path to GitHub
    with gzip.open(f"/Users/anesterov/reps/LODlit/AAT/gzip_aat_subgraph_{lang}.json", 'r') as gzip_json:
    	aat_gzip = json.loads(gzip_json.read().decode('utf-8'))
    
    list_of_results = []
    
    for triple in aat_gzip["results"]["bindings"]:
        
        if triple['Object']['type'] == 'literal' \
        and len(re.findall(f'\\b{query_term}\\b',triple['Object']['value'],re.IGNORECASE)) > 0:
            
            results_per_hit = {}
            results_per_hit['query_term'] = query_term
            results_per_hit['aat_uri'] = ''
            
            # if a term found in scopeNote
                    
            if 'rdf-syntax' in triple['Predicate']['value']:
                results_per_hit['found_in'] = 'scopeNote'
                for triple_t in aat_gzip["results"]["bindings"]:
                    if triple_t['Object']['value'] == triple['Subject']['value']:
                        # getting entity URI
                        entity = triple_t['Subject']['value'].split('/')[-1]
                        
            # if a term found in pref or alt labels
            
            if 'literalForm' in triple['Predicate']['value']:
                for triple_t in aat_gzip["results"]["bindings"]:
                    if triple_t['Object']['value'] == triple['Subject']['value']:
                        # getting entity URI
                        entity = triple_t['Subject']['value'].split('/')[-1]
                        # altLabel or prefLabel 
                        if 'altLabel' in triple_t['Predicate']['value']:
                            results_per_hit['found_in'] = 'altLabel'
                        if 'prefLabel' in triple_t['Predicate']['value']:
                            results_per_hit['found_in'] = 'prefLabel'
                        
            # if a term found in rdfs comment
            
            if 'comment' in triple['Predicate']['value']:
                for triple_t in aat_gzip["results"]["bindings"]:
                    if triple_t['Object']['value'] == triple['Subject']['value']:
                        # getting entity URI
                        entity = triple_t['Subject']['value'].split('/')[-1]
                        # comment to altLabel or prefLabel
                        if 'altLabel' in triple_t['Predicate']['value']:
                            results_per_hit['found_in'] = 'altLabel_comment'
                        if 'prefLabel' in triple_t['Predicate']['value']:
                            results_per_hit['found_in'] = 'prefLabel_comment'
            
            results_per_hit['aat_uri'] = entity
            
            entity_info = _get_entity_info(entity, lang, aat_gzip)
            
            results_per_hit['prefLabel'] = entity_info['prefLabel']
            results_per_hit['prefLabel_comment'] = entity_info['prefLabel_comment']
            results_per_hit['altLabel'] = entity_info['altLabel']
            results_per_hit['altLabel_comment'] = entity_info['altLabel_comment']
            results_per_hit['scopeNote'] = entity_info['scopeNote']
            
            list_of_results.append(results_per_hit)
            
    return list_of_results

def get_bows(path_to_results:str, lang:str) -> dict:
    '''
    Getting bag of words (BoW) from the AAT search results for every search term
    path_to_results: str, a path to the search results (in json format)
    lang: str, 'en' or 'nl'
    Returns a dict with BoWs per hit per term: {term:[{aat_URI:['token1','token2','token3']}]}
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
            
            if hit["prefLabel"] != "":
                literals.append(hit["prefLabel"]) 
            if hit["prefLabel_comment"] != "":
                literals.append(hit["prefLabel_comment"])
            if hit["scopeNote"] != "":
                literals.append(hit["scopeNote"])
            # altLabel and altLabel comments are lists
            if hit["altLabel"] != []:
                literals.extend(hit["altLabel"])
            if hit["altLabel_comment"] != "":
                literals.extend(hit["altLabel_comment"])

            bow = []
            for lit in literals:
                bow.extend(lit.replace('(','').replace(')','').replace('-',' ').replace('/',' ')\
                           .replace(',','').lower().split(' '))

            # checking lang for stopwords
            if lang == 'en':
                bag_unique = [wnl.lemmatize(w) for w in set(bow) if w not in stopwords.words('english') \
                                    and re.search('(\W|\d)',w) == None and w != hit["query_term"] and w != '']
            if lang == 'nl':
                bag_unique = [wnl.lemmatize(w) for w in set(bow) if w not in stopwords.words('dutch') \
                                    and re.search('(\W|\d)',w) == None and w != hit["query_term"] and w != '']

            q_bag[hit["aat_uri"]] = bag_unique

            list_by_term.append(q_bag)

        all_bows[query_term] = list_by_term

    return all_bows