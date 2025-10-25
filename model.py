
import pandas as pd
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import string

# Download required NLTK data (only first run)
nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)
nltk.download('punkt_tab', quiet=True)

lemmer = WordNetLemmatizer()

def LemTokens(tokens):
    return [lemmer.lemmatize(token) for token in tokens]

# Build punctuation removal map once
remove_punct_dict = {ord(punct): None for punct in string.punctuation}

def LemNormalize(text):
    """Lowercase, remove punctuation, tokenize, and lemmatize."""
    return LemTokens(nltk.word_tokenize(text.lower().translate(remove_punct_dict)))


def get_similarty(df, search_field, query, accuracy):
    """
    Compute cosine similarity between a query string and text column.
    Returns a DataFrame of similar rows above the given accuracy threshold (0–9).
    """
    if search_field not in df.columns:
        raise ValueError(f"Column '{search_field}' not found in DataFrame.")

    df_comp = df[[search_field]].dropna()
    names = df_comp[search_field].astype(str).tolist()

    # Add user input as the last item to compare against all others
    sent_tokens = names + [str(query)]

    # Vectorize using TF-IDF
    tfidf_vec = TfidfVectorizer(tokenizer=LemNormalize, stop_words='english')
    tfidf = tfidf_vec.fit_transform(sent_tokens)

    # Compute cosine similarity between query (last row) and all others
    vals = cosine_similarity(tfidf[-1], tfidf[:-1]).flatten()

    # Filter results above threshold
    threshold = float(accuracy) / 10.0
    idx_new = np.where(vals >= threshold)[0]
    flat_new = vals[idx_new]

    # Sort by descending accuracy
    sorted_indices = np.argsort(-flat_new)
    idx_new = idx_new[sorted_indices]
    flat_new = flat_new[sorted_indices]

    df_result = df.iloc[idx_new].copy()
    df_result.insert(0, "accuracy", flat_new.round(3))
    return df_result
