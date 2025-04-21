import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from collaborative_filter import user_Recs
from content_filter import use_content_filter

sns.set_theme(style="darkgrid")

def draw_chart(frame, titles, scores, x_label, title, palette):
    for j in frame.winfo_children():
        j.destroy()
    fig, ax = plt.subplots(figsize=(6, 3))
    sns.barplot(x=scores, y=titles, ax=ax, palette=palette, legend=False)
    ax.set_xlabel(x_label)
    ax.set_title(title, pad=14)
    fig.tight_layout()
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

class Application(tk.Tk):
    def __init__(self, ratings_df, movies_df, all_genres):
        super().__init__()
        self.title("🎬 Reelgorithm — Movie Recommender")
        self.geometry("1100x700")
        self.configure(bg="white")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.ratings_df = ratings_df
        self.movies_df = movies_df
        self.all_genres = all_genres
        self.current_titles = []

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 11), padding=8, background="#3F51B5", foreground="white")
        style.map("TButton", background=[("active", "#303F9F")])
        style.configure("TLabel", font=("Segoe UI", 11))
        style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"), foreground="#333")
        style.configure("TCombobox", font=("Segoe UI", 11))
        style.configure("TEntry", font=("Segoe UI", 11))

        container = tk.Frame(self, bg="#F5F5F5", bd=0)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        left = tk.Frame(container, bg="white", bd=1, relief="groove")
        left.pack(fill=tk.BOTH, expand=True)

        ttk.Label(left, text="🎯 Select Genre", style="Header.TLabel").pack(anchor="w", padx=16, pady=(16, 4))
        self.genre_cb = ttk.Combobox(left, values=self.all_genres, state="readonly")
        self.genre_cb.pack(fill=tk.X, padx=16, pady=(0, 12))
        self.genre_cb.bind("<<ComboboxSelected>>", self.populate_seen)

        ttk.Label(left, text="🎬 Pick Movies You Like", style="Header.TLabel").pack(anchor="w", padx=16)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(left, textvariable=self.search_var)
        self.search_entry.pack(fill=tk.X, padx=16, pady=(0, 8))
        self.search_entry.bind("<KeyRelease>", self.filter_seed)

        self.seed_list = tk.Listbox(left, selectmode=tk.MULTIPLE, bg="#ECEFF1", bd=0, height=6, relief="solid")
        self.seed_list.pack(fill=tk.BOTH, expand=False, padx=16, pady=(0, 12))

        ttk.Label(left, text="🧠 Choose Recommendation Method", style="Header.TLabel").pack(anchor="w", padx=16, pady=(0, 4))
        self.algo_var = tk.StringVar(value="Collaborative")
        self.algo_cb = ttk.Combobox(left, textvariable=self.algo_var, values=["Collaborative", "Content-Based"], state="readonly")
        self.algo_cb.pack(fill=tk.X, padx=16, pady=(0, 12))

        ttk.Button(left, text="🔍 Get Recommendations", command=self.on_recommend).pack(padx=16, pady=(0, 12))

        ttk.Label(left, text="🎁 Recommended Movies", style="Header.TLabel").pack(anchor="w", padx=16, pady=(0, 4))
        self.result_list = tk.Listbox(left, bg="#FFFFFF", bd=0, height=6, relief="solid")
        self.result_list.pack(fill=tk.BOTH, expand=False, padx=16, pady=(0, 12))

        self.chart = tk.Frame(left, bg="white", bd=1, relief="ridge")
        self.chart.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 16))

    def populate_seen(self, _evt=None):
        genre = self.genre_cb.get()
        self.seed_list.delete(0, tk.END)
        if not genre:
            self.current_titles = []
            return
        new_movies = self.movies_df["genres"].str.contains(genre, case=False, na=False)
        titles = self.movies_df.loc[new_movies, "title"].tolist()
        self.current_titles = titles
        for t in titles:
            self.seed_list.insert(tk.END, t)

    def filter_seed(self, _evt=None):
        term = self.search_var.get().lower()
        filtered = [i for i in self.current_titles if term in i.lower()]
        self.seed_list.delete(0, tk.END)
        for i in filtered:
            self.seed_list.insert(tk.END, i)

    def on_recommend(self):
        genre = self.genre_cb.get()
        if not genre:
            return messagebox.showerror("Error", "Please select a genre")
        selected = self.seed_list.curselection()
        if not selected:
            return messagebox.showerror("Error", "Pick at least one movie")
        seen = [self.seed_list.get(i) for i in selected]

        algo = self.algo_var.get()
        temp_ratings = self.ratings_df.copy()
        id_map = self.movies_df.set_index("title")["movieId"].to_dict()
        seed_df = pd.DataFrame({
            "userId": 0, "movieId": [id_map[i] for i in seen], "rating": 5.0
        })

        temp_ratings = pd.concat([temp_ratings, seed_df], ignore_index=True)

        if algo == "Collaborative":
            recs = user_Recs(temp_ratings, self.movies_df, user_id=0, k=30, top_Movie=8, genre=genre)
        else:
            rec_titles = []
            for m in seen:
                try:
                    results = use_content_filter(m, self.movies_df, k=5)
                    rec_titles.extend(results["title"].tolist())
                except:
                    continue
            rec_titles = list(dict.fromkeys(rec_titles))[:8]
            recs = [(title, 4.5) for title in rec_titles]

        self.result_list.delete(0, tk.END)
        titles, scores = [], []
        for title, score in recs:
            self.result_list.insert(tk.END, f"{score:.2f} · {title}")
            titles.append(title)
            scores.append(score)

        draw_chart(
            self.chart,
            titles,
            scores,
            x_label="Predicted rating",
            title="Your Personalized Picks",
            palette="Spectral"
        )

    def on_close(self):
        print("Manual close")
        self.destroy()
