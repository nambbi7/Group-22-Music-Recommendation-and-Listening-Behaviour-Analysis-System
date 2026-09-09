import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("cleaned_data/clean_music.csv")

print("Dataset loaded successfully")
print("Rows:", len(df))
print("Columns:", len(df.columns))

print("\nTop 10 Genres:")
print(df["track_genre"].value_counts().head(10))

print("\nTop 10 Artists:")
print(df["artists"].value_counts().head(10))

print("\nTop 10 Popular Songs:")

top_songs = df[
    ["track_name", "artists", "popularity"]
].sort_values(
    "popularity",
    ascending=False
).head(10)

print(top_songs)

print("\nAverage Popularity by Genre:")

genre_popularity = (
    df.groupby("track_genre")["popularity"]
    .mean()
    .sort_values(ascending=False)
    .head(10)
)

print(genre_popularity)

print("\nAverage Audio Features:")

features = [
    "danceability",
    "energy",
    "valence",
    "acousticness",
    "instrumentalness",
    "speechiness",
    "tempo"
]

print(df[features].mean())

genre_counts = df["track_genre"].value_counts().head(10)

plt.figure(figsize=(10, 6))
genre_counts.plot(kind="bar")

plt.title("Top 10 Music Genres")
plt.xlabel("Genre")
plt.ylabel("Number of Songs")
plt.xticks(rotation=45)

plt.tight_layout()
plt.show()

top_popular = df.nlargest(10, "popularity")

plt.figure(figsize=(10, 6))
plt.bar(top_popular["track_name"], top_popular["popularity"])

plt.title("Top 10 Most Popular Songs")
plt.xlabel("Song")
plt.ylabel("Popularity")

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()