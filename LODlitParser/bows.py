import json

def cosine_similarity(term:str,lang:str):
    '''
    Vectrorizes BoWs of search results and related matches
    Calculates cosine similarity between the two vectors
    term: str, query term
    lang: str, 'en' or 'nl'
    '''
    # output: term, entity_id, resource, sim_rm (round)
    # read related matches and search results bows
    related_matches = all_rm[lang][term]['wikidata'] + all_rm['en']['black']['aat'] + all_rm['en']['black']['pwn']
    wikidata = wd_en['black'][349]['Q53094']
    rm_set = {t for t in related_matches}
    wd_set = {t for t in wikidata}
    rvector = rm_set.union(wd_set)