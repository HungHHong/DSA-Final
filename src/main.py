from src.preprocess import load_data, merge_movie_tags

ratings, movies, tags = load_data()
movies_with_tags = merge_movie_tags(movies, tags)

print(movies_with_tags.head())
