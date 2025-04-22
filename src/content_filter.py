#data cleaning / preparation
import os, re, math
import pandas as pd
from collections import Counter
from typing import List
from preprocess import merge_movie_tags


base_path = os.path.dirname(os.path.dirname(__file__))
data_path = os.path.join(base_path, "data")

movies_rawData = pd.read_csv(os.path.join(data_path, "movies.csv"))
tags_rawData = pd.read_csv(os.path.join(data_path, "tags.csv"), encoding="utf-8")

movies = merge_movie_tags(movies_rawData, tags_rawData)

#ideas for tfidf from https://www.geeksforgeeks.org/ml-content-based-recommender-system/
def _clean(text):
    text = re.sub("[^\\w\\s]", " ", text.lower())
    text = re.sub(" +", " ", text)
    return text.strip()

def _tokenise(t):
    return _clean(t).split()

movies["text"] = (movies["title"].fillna("") + " " +
    movies["genres"].fillna("").str.replace("|", " ", regex=False) + " " +
    movies["tag"]
)

docs = [_tokenise(t) for t in movies["text"]]

vocab, df = {}, Counter()

for x in docs:
    seen = set()
    for w in x:
        if w not in vocab:
            vocab[w] = len(vocab)
        if w not in seen:
            df[w] += 1
            seen.add(w)


N = len(docs)

idf = {vocab[w]: math.log(N / (1 + df[w])) for w in vocab}

vectors, norms = [], []

for x in docs:
    tf = Counter(x)
    vec = {vocab[w]: (c / len(x)) * idf[vocab[w]] for w, c in tf.items()}
    vectors.append(vec)
    norms.append(math.sqrt(sum(v * v for v in vec.values())))

def _cosine(i: int, j: int) -> float:
    vi, vj = vectors[i], vectors[j]
    dot = sum(vi[k] * vj[k] for k in (vi.keys() & vj.keys()))
    if dot == 0:
        return 0.0
    return dot / (norms[i] * norms[j])

def use_content_filter(title: str, movies_df: pd.DataFrame,  k: int = 10) -> pd.DataFrame:
    idxs = movies_df.index[movies_df["title"].str.lower() == title.lower()]
    if len(idxs) == 0:
        raise ValueError(f"Movie '{title}' not found.")
    idx = idxs[0]

    btitle = re.sub(r"\(\d{4}\)", "", title).strip().lower()
    sequence_movie = re.compile(rf"^{re.escape(btitle)}(\s|:|\d|part|episode)", re.IGNORECASE)

    sims = []
    for j in range(len(movies_df)):
        if j == idx:
            continue
        potientail_movie = movies_df.iloc[j]["title"].lower()
        if sequence_movie.match(potientail_movie):
            continue  # skip sequels with similar base title
        sims.append((j, _cosine(idx, j)))

    sims.sort(key=lambda x: x[1], reverse=True)
    top = [j for j, _ in sims[:k]]
    return movies_df.iloc[top][["title"]]

