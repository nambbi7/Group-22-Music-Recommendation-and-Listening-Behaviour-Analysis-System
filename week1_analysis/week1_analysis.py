import pandas as pd

df = pd.read_csv("dataset.csv/music.csv")

print(df.head())
print("Rows:", df.shape[0])
print("Columns:", df.shape[1])
print(df.columns.tolist())
print(df.isnull().sum())
print("Duplicates:", df.duplicated().sum())
print(df.dtypes)

import pandas as pd

df = pd.read_csv("dataset.csv/music.csv")

print(df.head())
print("Rows:", df.shape[0])
print("Columns:", df.shape[1])
print(df.columns.tolist())
print(df.isnull().sum())
print("Duplicates:", df.duplicated().sum())
print(df.dtypes)

print("\nTop 10 Genres:")
print(df["track_genre"].value_counts().head(10))

print("\nTop 10 Artists:")
print(df["artists"].value_counts().head(10))

print("\nTop 10 Popular Songs:")
print(df[["track_name", "artists", "popularity"]]
      .sort_values("popularity", ascending=False)
      .head(10))