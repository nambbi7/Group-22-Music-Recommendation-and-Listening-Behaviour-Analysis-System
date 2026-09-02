import pandas as pd
df = pd.read_csv("dataset.csv/music.csv")
print("Original rows:", len(df))
print("Original columns:", len(df.columns))
print("\nMissing Values:")
print(df.isnull().sum())

df["artists"] = df["artists"].fillna("Unknown Artist")
df["album_name"] = df["album_name"].fillna("Unknown Album")
df["track_name"] = df["track_name"].fillna("Unknown Track")
print("\nMissing Values After Cleaning:")
print(df.isnull().sum())

print("\nDuplicate Rows:")
print(df.duplicated().sum())

print("\nNumerical Data Summary:")
print(df[["popularity", "danceability", "energy", "valence", "tempo"]].describe())

df.to_csv("cleaned_data/clean_music.csv", index=False)

print("\nCleaned dataset saved successfully.")