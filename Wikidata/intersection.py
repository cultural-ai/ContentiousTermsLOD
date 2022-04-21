import re
import nltk
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer

def get_close_match_literals(data_entityterms: dict, data_claims:dict, entity_id:str) -> list:
    
    """
    Returns BoW of a close match entity from Wikidata (label, aliases, description, the values of P31 and P279)
    """
    
    entity_literals = []
    k = 0

    for term, value in data_entityterms.items():
        for entity_info in value.values():
            if entity_info['title'] == entity_id and k < 1:
                k += 1
                
                # getting all literals
                    
                if 'label' in entity_info['entityterms']:
                    entity_literals.extend(entity_info['entityterms']['label'])

                if 'alias' in entity_info['entityterms']:
                    entity_literals.extend(entity_info['entityterms']['alias'])

                if 'description' in entity_info['entityterms']:
                    entity_literals.extend(entity_info['entityterms']['description'])

                if 'P31' in data_claims[entity_id]:
                    entity_literals.extend(list(data_claims[entity_id]['P31'].values()))

                if 'P279' in data_claims[entity_id]:
                    entity_literals.extend(list(data_claims[entity_id]['P279'].values()))

    return entity_literals

def get_entity_literals_by_target(data_entityterms: dict, data_claims:dict, target_term: str, entity_id:str, target_term_filter: bool = False) -> list:
    
    """
    Returns a list of the following literal values of an entity:

    #1 if target_term_filter False (default):
    return all literals: prefLabel, altLabel, description, the values of the properties P31('instance of') and P279 ('subclass of');

    #2 if target_term_filter True:
    - if the target term is mentioned in prefLabel and/or altLabel:
        return all literals;
    - if the target term is mentioned in description only:
        return description;
    """

    entity_literals = []

    for value in data_entityterms[target_term].values():

        if value['title'] == entity_id:

            # getting all literals
            if target_term_filter == False:

                if 'label' in value['entityterms']:
                    entity_literals.extend(value['entityterms']['label'])

                if 'alias' in value['entityterms']:
                    entity_literals.extend(value['entityterms']['alias'])

                if 'description' in value['entityterms']:
                    entity_literals.extend(value['entityterms']['description'])

                if 'P31' in data_claims[entity_id]:
                    entity_literals.extend(list(data_claims[entity_id]['P31'].values()))

                if 'P279' in data_claims[entity_id]:
                    entity_literals.extend(list(data_claims[entity_id]['P279'].values()))

            else:
                where_target_found = []

                # handling compund terms with dashes
                if '-' in target_term:
                    regex_target_term = target_term.replace('-','(-| )?')
                else:
                    regex_target_term = target_term

                if 'label' in value['entityterms']:
                    l = re.search(regex_target_term, value['entityterms']['label'][0], re.IGNORECASE)
                    if l != None:
                        where_target_found.append('l')

                if 'alias' in value['entityterms']:
                    for alias in value['entityterms']['alias']:
                        a = re.search(regex_target_term, alias, re.IGNORECASE)
                        if a != None:
                            where_target_found.append('a')

                if 'l' in where_target_found or 'a' in where_target_found:
                    if 'label' in value['entityterms']:
                        entity_literals.extend(value['entityterms']['label'])
                    if 'alias' in value['entityterms']:   
                        entity_literals.extend(value['entityterms']['alias'])

                if entity_literals != []:
                    if 'description' in value['entityterms']:
                        entity_literals.extend(value['entityterms']['description'])
                        entity_literals.extend(list(data_claims[value['title']]['P31'].values()))
                        entity_literals.extend(list(data_claims[value['title']]['P279'].values()))

                if entity_literals == [] and 'description' in value['entityterms']:
                    l = re.search(regex_target_term, value['entityterms']['description'][0], re.IGNORECASE)
                    if l != None:
                        entity_literals.extend(value['entityterms']['description']) 

    return entity_literals

def lemmatize_and_clean_en(tokens: list, target_term: str) -> list:
    """
    Lowercasing and splitting by space;
    Lemmatization with WordNetLemmatizer();
    Stopwords in Enlish (from NLTK corpus) are removed;
    Target word is removed;
    Non-word symbols, digits, '_' (\W|\d|_) are replaced with a space;
    Empty values '' are removed;
    
    """
    wnl = WordNetLemmatizer()
    tokenized = []
    
    for token in tokens:
        tokenized.extend(re.sub('(\W|\d|_)', ' ', token).lower().split(' '))
    
    tokenized_clean_unique = list(set([wnl.lemmatize(t) for t in tokenized if t not in stopwords.words('english') \
                            and target_term not in t and t != '']))
    
    return tokenized_clean_unique

def wordnet_tokens_en(target_term: str) -> dict:
    """
    Return a dict with synsets as keys and BoW as values;
    BoW includes words from the synses definition and synonyms (lemma_names);
    Uses the 'lemmatize_and_clean_en' function;
    
    """
    wn_synsets_bows = {}

    for synset in wn.synsets(target_term):

        if synset.pos() != 'v':

            list_of_literals = []

            list_of_literals.extend([synset.definition()])
            list_of_literals.extend(synset.lemma_names())
                
            wn_bag = lemmatize_and_clean_en(list_of_literals,target_term)

            wn_synsets_bows[synset.name()] = wn_bag
            
    return wn_synsets_bows