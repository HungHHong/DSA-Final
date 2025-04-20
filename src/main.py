'''from src.preprocess import load_data, merge_movie_tags

ratings, movies, tags = load_data()
movies_with_tags = merge_movie_tags(movies, tags)

print(movies_with_tags.head())'''

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collaborative_filter import user_Recs

sns.set_theme(style="darkgrid")

here = Path(__file__). resolve().parent
Root = here.parent
data_path = Root / 'data'
ratings_df = pd.read_csv(data_path/'ratings_sample.csv', usecols= ['userId', 'movieId', 'rating'])
movies_df = pd.read_csv(data_path/'movies.csv', usecols= ['movieId', 'title', 'genres'])
all_genres = sorted({i for cell in movies_df["genres"].dropna() for i in cell.split("|")})

#Chart helper function

def draw_chart(frame, titles, scores, x_label, title, palette):
    for j in frame.winfo_children():
        j.destroy()

    fig, ax = plt.subplots(figsize=(5, 3))
    sns.barplot(x = scores, y = titles, ax= ax, palette = palette, hue = None, legend = False)
    ax.set_xlabel(x_label)
    ax.set_title(title, pad = 14)
    fig.tight_layout()
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill= tk.BOTH, expand= True)

#Main application

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Personalized Movie Recommender 🎥")
        self.geometry("920x600")
        self.configure(bg="white")

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TButton", font = ("Helvetica", 12), padding = 6, cursor = "hand", background = "009688", foreground = "white")
        style.map( "TButton", background = [("active", "#00796B"), ("pressed", "#004D40")], foreground =[("disabled", '#aaaaa')])
        style.configure("Header.TLabel", font = ("Helvetica", 16, "bold"), foreground = "#4a148C")
        style.configure("TCombobox", font = ("Helvetica", 12), padding = 4, fieldbackground = "pink", background ="FFF59D")
        style.configure("TEntry", font = ("Helvetica",11), fieldbackground = "white", background="E0F7FA")

        #left side

        left = tk.Frame(self, bg = "#151ded", bd = 1, relief = "ridge")
        left.place(relx= 0.02, rely = 0.02, relwidth = 0.90, relheight = 0.96)
        ttk.Label(left,text=" Select Genre", style = "Header.TLabel", font = ("Helvetica"), background = "#e39529") \
            .pack(anchor='w', padx=12, pady=(12, 0))
        self.genre_cb = ttk.Combobox(left, values =all_genres, state = "readonly")
        self.genre_cb.pack(fill=tk.X, padx=12, pady=(4,8))
        self.genre_cb.bind("<<ComboboxSelected>>", self.populate_seen)

        #Search bar implementation
        ttk.Label(left, text=" Select movies that interest you", style = "Header.TLabel", background = '#e39529')\
            .pack(anchor="w", padx=12)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(left, textvariable = self.search_var)
        self.search_entry.pack(fill=tk.X, padx=12, pady=(4,8))
        self.search_entry.bind("<KeyRelease>", self.filter_seed)

        #User's liked mvovies
        self.seed_list = tk.Listbox(
            left, selectmode = tk.MULTIPLE, bg = "#EDE7F6", bd=0, highlightthickness = 1, relief="solid"
        )

        self.seed_list.pack(fill=tk.BOTH, expand= False, padx=12, pady=(0,8))
        ttk.Button(left, text=" Get Recommendations", command = self.on_recommend).pack(pady=(0,12))

        ttk.Label(left, text=" Recommended movies for you", style = "Header.TLabel", background="#e39529")\
            .pack(anchor="w", padx=12)
        self.result_list = tk.Listbox(
            left, bg = "white", bd=0, highlightthickness = 1, relief="solid"
        )
        self.result_list.pack(fill=tk.BOTH, expand = False, padx = 12, pady=(4,8))
        self.chart = tk.Frame(left, bg='white', bd=1, relief="solid")
        self.chart.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0,12))
    def populate_seen(self, _evt=None):
        genre = self.genre_cb.get()
        self.seed_list.delete(0, tk.END)
        if not genre:
            self.current_titles = []
            return

        new_movies = movies_df["genres"].str.contains(genre, case = False, na = False)
        titles = movies_df.loc[new_movies, "title"].tolist()
        self.current_titles = titles
        for t in titles:
            self.seed_list.insert(tk.END, t)
    def filter_seed(self, _evt=None):
        term = self.search_var.get().lower()
        filtered = [i for i in getattr(self, "current_titles", []) if term in i.lower()]
        self.seed_list.delete(0, tk.END)
        for i in filtered:
            self.seed_list.insert(tk.END, i)

    def on_recommend(self):
        genre = self.genre_cb.get()
        if not genre:
            return messagebox.showerror("Error", "Please select a genre")
        Self = self.seed_list.curselection()
        if not Self:
            return messagebox.showerror("Error", "Pick at least one movie")
        seen = [self.seed_list.get(i) for i in Self]

        tempRatings = ratings_df.copy()
        id_map = movies_df.set_index("title")["movieId"].to_dict()
        seed_df = pd.DataFrame({
            "userId": 0, "movieId": [id_map[i] for i in seen], "rating": 5.0})


        tempRatings = pd.concat([tempRatings, seed_df], ignore_index = True)
        recs = user_Recs(tempRatings, movies_df, user_id = 0, k = 30, top_Movie = 8, genre = genre)

        self.result_list.delete(0, tk.END)
        titles, scores = [], []
        for i, j in recs:
            self.result_list.insert(tk.END, f"{j: .2f} · {i}")
            titles.append(i); scores.append(j)

            draw_chart(
                self.chart, titles, scores, x_label ="Predicted rating", title = "Your Personalized Picks", palette = "Spectral")

if __name__ == "__main__":
    Application().mainloop()














