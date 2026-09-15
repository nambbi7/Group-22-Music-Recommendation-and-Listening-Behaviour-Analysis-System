import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors


# ==========================================
# 1. LOAD CLEANED DATASET
# ==========================================

df = pd.read_csv("cleaned_data/clean_music.csv")

print("Dataset loaded successfully")
print("Rows:", len(df))
print("Columns:", len(df.columns))


# ==========================================
# 2. SELECT MUSIC FEATURES
# ==========================================

features = [
    "danceability",
    "energy",
    "loudness",
    "speechiness",
    "acousticness",
    "instrumentalness",
    "liveness",
    "valence",
    "tempo"
]

print("\nSelected features:")
print(features)


# ==========================================
# 3. PREPARE FEATURES
# ==========================================

feature_data = df[features]

# Handle missing numerical values
feature_data = feature_data.fillna(feature_data.mean())

# Scale the features
scaler = StandardScaler()
feature_matrix = scaler.fit_transform(feature_data)

print("\nFeatures prepared successfully")
print("Feature matrix shape:", feature_matrix.shape)


# ==========================================
# 4. CREATE RECOMMENDATION MODEL
# ==========================================

model = NearestNeighbors(
    n_neighbors=15,
    metric="cosine"
)

model.fit(feature_matrix)

print("\nRecommendation model created successfully")


# ==========================================
# 5. RECOMMENDATION FUNCTION
# ==========================================

def recommend_songs(song_name, number_of_recommendations=5):

    # Find the song
    matches = df[
        df["track_name"].str.lower() == song_name.lower()
    ]

    # If song is not found
    if matches.empty:
        print("\nSong not found.")
        print("Please check the song name and try again.")
        return

    # Get the first matching song
    song_index = matches.index[0]

    # Find similar songs
    distances, indices = model.kneighbors(
        feature_matrix[song_index].reshape(1, -1),
        n_neighbors=15
    )

    print("\nRecommended songs for:", df.loc[song_index, "track_name"])
    print("----------------------------------------")

    recommended_songs = set()
    count = 0

    for index in indices[0]:

        # Skip the original song
        if index == song_index:
            continue

        track_name = df.loc[index, "track_name"]

        # Skip duplicate songs
        if track_name in recommended_songs:
            continue

        recommended_songs.add(track_name)

        print(
            f"{count + 1}. "
            f"{track_name} - "
            f"{df.loc[index, 'artists']}"
        )

        count += 1

        if count == number_of_recommendations:
            break


# ==========================================
# 6. USER INPUT
# ==========================================

print("\n========================================")
print("       MUSIC RECOMMENDATION SYSTEM")
print("========================================")

song = input("\nEnter a song name: ")

recommend_songs(song)