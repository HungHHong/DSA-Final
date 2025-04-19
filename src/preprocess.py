import pandas as pd
import os

def fix_encoding(text):
    try:
        return text.encode('latin1').decode('utf-8')
    except:
        return text

def load_data():
    base_path = os.path.dirname(os.path.dirname(__file__))  # go up from /src
    data_path = os.path.join(base_path, "data")

    ratings = pd.read_csv(os.path.join(data_path, "ratings_sample.csv"))
    movies = pd.read_csv(os.path.join(data_path, "movies.csv"))
    tags = pd.read_csv(os.path.join(data_path, "tags.csv"), encoding='ISO-8859-1')

    # Step 1: Attempt to decode any improperly read strings
    tags['tag'] = tags['tag'].apply(lambda x: fix_encoding(x) if isinstance(x, str) else x)

    # Step 2: Replace known corrupted values
    corrupted_map = {
        'CiarÃ¡n Hinds': 'Ciarán Hinds',
        'TÃ©a Leoni': 'Téa Leoni',
        'comedinha de velhinhos engraÃ§ada': 'comedinha de velhinhos engraçada',
        'comedinha de velhinhos engraÃƒÂ§ada': 'comedinha de velhinhos engraçada',
        'Gael GarcÃ­a Bernal': 'Gael García Bernal',
        # ... Add the rest of the mappings you printed here
    }
    tags['tag'] = tags['tag'].replace(corrupted_map)

    # Optional: Remove exact duplicates
    tags.drop_duplicates(subset=['movieId', 'tag'], inplace=True)

    return ratings, movies, tags

def merge_movie_tags(movies, tags):
    tags_grouped = tags.groupby('movieId')['tag'].apply(
        lambda x: ' '.join(dict.fromkeys(str(i) for i in x))
    ).reset_index()

    tags_grouped['tag'] = tags_grouped['tag'].apply(lambda x: fix_encoding(x) if isinstance(x, str) else x)

    movies_with_tags = pd.merge(movies, tags_grouped, on='movieId', how='left')
    movies_with_tags['tag'] = movies_with_tags['tag'].fillna('')

    return movies_with_tags
