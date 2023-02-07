import json
import gzip
import re
import csv
from SPARQLWrapper import SPARQLWrapper, JSON

# Getty AAT
# A module to parse query results (json) from Getty Art&Archiechture Thesaurus

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


def _get_entity_info(entity_id:str, lang:str) -> dict:
    '''
    Getting the values of prefLabel (str), altLabel (list), prefLabel_comment (str), altLabel_comment(list), and scopeNote (str)
    by entity ID in AAT
    entity_id: str, entity ID in AAT (for example, '300189559')
    lang: str, 'en' or 'nl'; language of entities info
    Returns a dict
    '''

    # importing the search results in gzip
    # change the path
    with gzip.open(f"/Users/anesterov/reps/LODlit/AAT/gzip_aat_subgraph_{lang}.json", 'r') as gzip_json:
    	aat_gzip = json.loads(gzip_json.read().decode('utf-8'))

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