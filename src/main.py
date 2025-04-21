'''from src.preprocess import load_data, merge_movie_tags

ratings, movies, tags = load_data()
movies_with_tags = merge_movie_tags(movies, tags)

print(movies_with_tags.head())'''


import tkinter as tk
from pathlib import Path
import pandas as pd
from ui import Application

here = Path(__file__).resolve().parent
Root = here.parent
data_path = Root / 'data'

ratings_df = pd.read_csv(data_path / 'ratings_sample.csv', usecols=['userId', 'movieId', 'rating'])
movies_df = pd.read_csv(data_path / 'movies.csv', usecols=['movieId', 'title', 'genres'])
all_genres = sorted({i for cell in movies_df["genres"].dropna() for i in cell.split("|")})

if __name__ == "__main__":
    Application(ratings_df, movies_df, all_genres).mainloop()
