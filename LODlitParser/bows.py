import re
import math
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import simplemma

def make_bows(text:list, lang:str, merge_bows=False) -> list:
    '''
    Makes a BoW from a list of str:
    removes non-word charachters (incl. punctuation, numbers),
    removes stop-words (nltk),
    lowercases, tokenises (split by space), lemmatises (NLTK lemmatiser for EN; simplemma for NL),
    removes tokens with fewer than 3 characters;
    text: a list of str to make BoWs from
    lang: str, language of strings, 'en' or 'nl'
    merge_bows: bool, if there are multiple texts, merge them in one BoW (True) or not (False), default False 
    Returns a BoW (list of lists)
    '''
    
    wnl = WordNetLemmatizer()

    bows = []
    
    for t in text:
        no_w_text = re.sub('(\W|\d)',' ',t)
        text_bow = no_w_text.split(' ')
        
        # checking lang
        if lang == 'en':
            text_bow_clean = [wnl.lemmatize(token.lower()) for token in text_bow if token.lower() not in stopwords.words('english') and token != '' and len(token) > 2]
        if lang == 'nl':
            # Dutch lemmatizer can output uppercase lemmas
            text_bow_clean = [simplemma.lemmatize(token.lower(),lang='nl').lower() for token in text_bow if token.lower() not in stopwords.words('dutch') and token != '' and len(token) > 2]
            
        if merge_bows == True:
            bows.extend(text_bow_clean)
        else:
            bows.append(text_bow_clean)
            
    return bows


def tf(doc:list, token:str) -> float:
    '''
    Calculates term frequency (TF)
    doc: list, all documents
    token: str, a token to get the TF score of
    Returns float
    '''
    n_found = len([t for t in doc if t == token])
    tf_score = n_found / len(doc)
    
    return tf_score


def idf(token:str, doc_freq:dict, n_docs:int) -> float:
    '''
    Calculates inverse document frequency (IDF):
        adds 1 to DF to avoid zero division
    token: str, a token to get the IDF score of
    doc_freq: dict, document frequency, in how many documents tokens appear
    n_docs: int, a number of documents
    Returns float
    '''
    idf_score = math.log(n_docs / (doc_freq[token] + 1))
        
    return idf_score


def get_top_tokens_tfidf(bow:list,doc_freq:dict,n_docs:int) -> list:
    '''
    Getting top tokens based on their TF-IDF weighting in one BoW
    Depends on the tf and idf functions
    bow: list of str, tokens in one BoW
    doc_freq: dict, document frequency, in how many documents tokens appear ({'token':int})
    n_docs: int, a number of documents
    Returns list: top 10 tokens in a bow by their TF-IDF scores
    '''
    top_tokens = []
    tf_idf_scores = {}
    
    for token in bow:
        tf_idf = tf(bow,token) * idf(token,doc_freq,n_docs)
        tf_idf_scores[token] = tf_idf
        
    tokens_scores = sorted(tf_idf_scores.items(), key=lambda x:x[1], reverse=True)
    
    if len(tokens_scores) < 10:
        top_tokens = [t[0] for t in tokens_scores]
    else:
        #cut_off_score = tokens_scores[9][1] # taking top 10 scores
        #top_tokens = [t[0] for t in tokens_scores if t[1] >= cut_off_score]
        #if len(top_tokens) > 10:
        top_tokens = [t[0] for t in tokens_scores[0:10]]
    
    return top_tokens