import pandas as pd
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import string # to process standard python strings
# Preprocessing

nltk.download('popular', quiet=True) # for downloading packages
nltk.download('punkt') # first-time use only
nltk.download('wordnet') # first-time use only

lemmer = WordNetLemmatizer()
def LemTokens(tokens):
    return [lemmer.lemmatize(token) for token in tokens]
remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)
def LemNormalize(text):
    return LemTokens(nltk.word_tokenize(text.lower().translate(remove_punct_dict)))


def get_similarty(df , serach_filed, input, accuracy) :

    df_comp = df[[serach_filed]]
    names = np.array(df_comp[serach_filed])
    # for initial string compare
    sent_tokens = []
    for i in names:
        sent_tokens.append(np.str_(i))

    sent_tokens.append(input)
    TfidfVec = TfidfVectorizer(tokenizer=LemNormalize)
    tfidf = TfidfVec.fit_transform(sent_tokens)

    vals = cosine_similarity(tfidf[-1], tfidf)
    idx=vals.argsort()[0][-11:-1]
    flat = vals.flatten()
    flat.sort()
    req_tfidf = flat[-2]

    #print(flat[-11:-1])

    #print(idx)

    idx_new = []
    flat_new = []
    for i, itr in enumerate(flat[-11:-1], start=0):
        if itr >= float(accuracy/10):
            idx_new.append(idx[i])
            flat_new.append(itr)

    df_result = df.iloc[idx_new]
    df_result.insert(0, "accuracy", flat_new, True)

    return df_result[::-1]
