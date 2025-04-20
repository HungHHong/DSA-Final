#Referenced Website: https://www.geeksforgeeks.org/recommendation-system-in-python/,
# https://numpy.org/doc/stable/reference/routines.datetime.html,
# and https://pandas.pydata.org/docs/reference/index.html

#Used NumPy and pandas to implement algorithm
import numpy as np
import pandas as pd


#Builds the movie_Matrix which is user x item
def movie_Matrix(ratings_df: pd.DataFrame) -> pd.DataFrame:
# Uses pandas to create the pivot: rows = userId, cols = movieId, and values = rating
    matrix = ratings_df.pivot(index= 'userId', columns='movieId', values='rating')
    return matrix.fillna(0).astype(float) #fillna is a pandas call which replaces anything empty with a 0 in this case.

#computed the cosine similarity between users
def user_similarityRating(Row: np.ndarray) -> np.ndarray:

    rows = np.linalg.norm(Row, axis = 1, keepdims = True) # np.linalg.norm computes the L2 of each row
    normal_Rows = Row / np.where(rows == 0, 1, rows) # Where is used to avoid division by 0.
    return normal_Rows @ normal_Rows.T # @ is used for matrix-multiplication to get the cosine similarity

def movie_predictor(Row: np.ndarray, col: np.ndarray, u_index: int, i_index: int, k: int = 30) -> float:
    similar_Movies = col[u_index]

    next_Movie = np.argsort(similar_Movies)[::-1][1:k+1] #Uses slicing to pick the top-k neighbors.
    row_k = Row[next_Movie, i_index] # Extracts the neighbors ratings
    col_k = similar_Movies[next_Movie]

    valid_Rating = row_k > 0
    if not valid_Rating.any():
        return 0.0
    return np.dot(row_k[valid_Rating], col_k[valid_Rating] / col_k[valid_Rating].sum()) #np.dot is used to find the weighted average



def user_Recs(ratings_df: pd.DataFrame, movies_df: pd.DataFrame, user_id: int, k: int = 30, top_Movie: int = 10) -> list[tuple[str,float]]:
    Row_df = movie_Matrix(ratings_df) # movie_Matrix returns a pandas DataFrame
    if user_id not in Row_df.index:
        raise KeyError('userID not found')
    Rows = Row_df.values #values yields NumPy array
    Cols = user_similarityRating(Rows) # computes similarity on NumPy array
    u_idx = Row_df.index.get_loc(user_id) # get_loc finds the integer location of user_id

    no_Rating = np.where(Rows[u_idx] == 0)[0] # np.where is used to find indices of unrated movies.
    prediction = [(col, movie_predictor(Rows, Cols, u_idx, col, k)) for col in no_Rating]
    prediction.sort(key=lambda x: x[1], reverse=True) ## .sort on python list of tuples

    movie_ids = Row_df.columns.to_numpy()
#.loc and .iloc are used to map movieId -> title
    return [
        (
            movies_df.loc[movies_df.movieId == movie_ids[col], 'title']. iloc[0], round(score, 2)
        )
        for col, score in prediction[:top_Movie]


    ]
