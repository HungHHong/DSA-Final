import pandas as pd
import os

def load_data():
    base_path = os.path.dirname(os.path.dirname(__file__))  # go up from /src
    data_path = os.path.join(base_path, "data")

    ratings_file = os.path.join(data_path, "ratings_sample.csv")
    movies_file = os.path.join(data_path, "movies.csv")
    tags_file = os.path.join(data_path, "tags.csv")

    ratings = pd.read_csv(ratings_file)
    movies = pd.read_csv(movies_file)
    tags = pd.read_csv(tags_file, encoding='ISO-8859-1')


    return ratings, movies, tags

def merge_movie_tags(movies, tags):
    # Simple tag aggregation
    tags_grouped = tags.groupby('movieId')['tag'].apply(lambda x: ' '.join(str(i) for i in x)).reset_index()
    movies_with_tags = pd.merge(movies, tags_grouped, on='movieId', how='left')
    movies_with_tags['tag'] = movies_with_tags['tag'].fillna('')  # fill missing tags

    return movies_with_tags
