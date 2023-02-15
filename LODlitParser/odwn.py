# Open Dutch WordNet parser
# Download OpenDutchWordnet from "https://github.com/cultural-ai/OpenDutchWordnet"

import sys
import json
import csv
import re

def _set_odwn(path_odwn:str):
    """
    path_odwn: str path to the directory with OpenDutchWordnet (not including the module itself, for example "user/Downloads")
    Inserts the path to the OpenDutchWordnet module
    Download OpenDutchWordnet from "https://github.com/cultural-ai/OpenDutchWordnet"
    Returns an instance using Wn_grid_parser
    """

    sys.path.insert(0,path_odwn)
    from OpenDutchWordnet import Wn_grid_parser
    # creating an instance
    odwn_instance = Wn_grid_parser(Wn_grid_parser.odwn)

    return odwn_instance

def get_le_info(le_ids:list, path_odwn:str) -> dict:
    """
    Getting Lemma, sense definitions, examples, synset ID, synset definitions of ODWN Lexical Entries
    le_ids: list of Lexical Entries IDs (str), for example "appel-n-1"
    path_odwn: str path to the directory with OpenDutchWordnet (not including the module itself, for example "user/Downloads")
    Returns a dict: {"le_id": {"lemma": "",
                                "sense_def": "",
                                "examples": [],
                                "synset_ID": "",
                                "synset_def": []}
    """
    # importing ODWN
    instance = _set_odwn(path_odwn)
    
    # change later
    # importing all synset definitions from GitHub
    # path_to_glosses = "https://raw.githubusercontent.com/cultural-ai/wordsmatter/main/ODWN/odwn_synset_glosses.json"
    # synset_glosses = requests.get(path_to_glosses).json()
    with open("/Users/anesterov/reps/LODlit/ODWN/odwn_synset_glosses.json","r") as jf:
        synset_glosses = json.load(jf)
    
    results_odwn = {}

    for le_id in le_ids:
        le = instance.les_find_le(le_id)
        synset_id = le.get_synset_id()

        sense_def = le.get_definition()
        if sense_def == "":
            sense_def = None

        results_odwn[le_id] = {"lemma": le.get_lemma(),
                                "sense_def": sense_def,
                                "examples": le.get_sense_example(),
                                "synset_ID": synset_id,
                                "synset_def": synset_glosses.get(synset_id)}
    return results_odwn

def _shape_search_results(instance:"wn_grid_parser.Wn_grid_parser",query_term:str,le:"le.Le",all_synset_definitions:dict,found_in:str,example="") -> dict:
    
    """
    Returns a dict of search results
    This function does not perform searching,
    But puts the search results of "find_terms" in a dict
    """
    
    result_dict = {}
    result_dict["query_term"] = query_term
    result_dict["le_id"] = le.get_id()
    result_dict["le_written_form"] = le.get_lemma()
    result_dict["sense_id"] = le.get_sense_id()
    result_dict["sense_definition"] = le.get_definition()
    result_dict["sense_examples"] = le.get_sense_example()

    if le.get_synset_id() != None:
        synset_id = le.get_synset_id()
        result_dict["synset_id"] = synset_id
        result_dict["synonyms"] = [les.get_lemma() for les in instance.les_all_les_of_one_synset(synset_id)]
        if synset_id in all_synset_definitions.keys():
            result_dict["synset_definitions"] = all_synset_definitions[synset_id]
        else:
            result_dict["synset_definitions"] = []
    else:
        result_dict["synset_id"] = ""
        result_dict["synonyms"] = []
        result_dict["synset_definitions"] = []
        
    result_dict["found_in"] = found_in
    
    if found_in == "sense_examples":
        # there can be multiple examples; writing the example the term was found in
        result_dict["found_in_example"] = example
    
    return result_dict

def find_terms(query_terms:list, path_odwn:str) -> dict:
    '''
    Searching for a query term in lemmas (written form of Lexical Entry (LE)), sense definitions, sense examples, and synset definitions (glosses) of ODWN
    query_term: list of terms to search in ODWN (str), phrases are also allowed
    path_odwn: str path to the directory with OpenDutchWordnet (not including the module itself, for example "user/Downloads")
    Returns a dict with the LE or synset info by query term if the query term was found
    if found in LE or its children tags:
        {query_term:[{"query_term": "",
                    "le_id": "",
                   "le_written_form": "",
                   "sense_id": "",
                   "sense_definition": "",
                   "sense_examples": [],
                   "synset_id": "",
                   "synonyms": [],
                   "synset_definitions": [],
                   "found_in": ""}]};
    if found in a synset definition, but that synset is not attached to any LEs:
        {query_term:[{"query_term": "",
                   "synset_id": "",
                   "synonyms": [],
                   "synset_definitions": [],
                   "found_in": "synset_definitions",
                   "found_in_synset_definition": ""}]}
    '''

    # importing ODWN
    instance = _set_odwn(path_odwn)
    
    # change later
    # importing all synset definitions from GitHub
    # path_to_glosses = "https://raw.githubusercontent.com/cultural-ai/wordsmatter/main/ODWN/odwn_synset_glosses.json"
    # synset_glosses = requests.get(path_to_glosses).json()
    with open("/Users/anesterov/reps/LODlit/ODWN/odwn_synset_glosses.json","r") as jf:
        synset_glosses = json.load(jf)

    results = {}

    for query_term in query_terms:

        results_per_term = []

        # searching in lemmas
        for le in instance.lemma_get_generator(query_term,ignore_case=True):
            results_per_term.append(_shape_search_results(instance,query_term,le,synset_glosses,"le"))

        # Iterating over all Lexical Entries
        
        # searching in sense definitions
        for le in instance.les_get_generator():
            if len(re.findall(f"\\b{query_term}\\b",le.get_definition(),re.IGNORECASE)) > 0:
                results_per_term.append(_shape_search_results(instance,query_term,le,synset_glosses,"sense_definition"))

            # searching in sense examples
            for example in le.get_sense_example():
                if len(re.findall(f"\\b{query_term}\\b",example,re.IGNORECASE)) > 0:
                    results_per_term.append(_shape_search_results(instance,query_term,le,synset_glosses,"sense_examples",example))

        # searching in synset definitions
        for synset_id, definitions in synset_glosses.items():
            for d in definitions:
                if len(re.findall(f"\\b{query_term}\\b",d,re.IGNORECASE)) > 0:
                        # results_per_term for synsets are different, so we don"t use "_shape_search_results()"
                        result_dict = {}
                        result_dict["query_term"] = query_term
                        result_dict["synset_id"] = synset_id
                        result_dict["synonyms"] = [les.get_lemma() for les in instance.les_all_les_of_one_synset(synset_id)]
                        result_dict["synset_definitions"] = synset_glosses[synset_id]
                        result_dict["found_in"] = "synset_definitions"
                        # there can be multiple definitions; writing the definition the term was found in
                        result_dict["found_in_synset_definition"] = d
                        results_per_term.append(result_dict)

        results[query_term] = results_per_term

    return results