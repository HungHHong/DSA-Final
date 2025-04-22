import pandas as pd
import os

def load_data():
    """
    Loads the dataset files into pandas DataFrames.
    - Tries to load 'ratings.csv' if it exists.
    - Falls back to 'ratings_sample.csv' if 'ratings.csv' is missing.
    """
    base_path = os.path.dirname(os.path.dirname(__file__))
    data_path = os.path.join(base_path, "data")

    # Try to use the full dataset if available, otherwise use the sample
    ratings_file = os.path.join(data_path, "ratings.csv")
    if not os.path.exists(ratings_file):
        ratings_file = os.path.join(data_path, "ratings_sample.csv")

    print("Reading from:", ratings_file)
    ratings = pd.read_csv(ratings_file)

    movies_file = os.path.join(data_path, "movies.csv")
    tags_file = os.path.join(data_path, "tags.csv")

    ratings = pd.read_csv(ratings_file)
    movies = pd.read_csv(movies_file)
    tags = pd.read_csv(tags_file, encoding='ISO-8859-1')

    return ratings, movies, tags

def merge_movie_tags(movies, tags):
    """
    Combines movie metadata with associated tags for content-based filtering.
    Returns a new DataFrame where each movie includes a combined 'tag' string.
    """
    # Group tags by movieId and join them into a single string per movie
    tags_grouped = tags.groupby('movieId')['tag'].apply(lambda x: ' '.join(str(i) for i in x)).reset_index()
    movies_with_tags = pd.merge(movies, tags_grouped, on='movieId', how='left')
    movies_with_tags['tag'] = movies_with_tags['tag'].fillna('')  # Fill missing tags with empty strings

    return movies_with_tags
