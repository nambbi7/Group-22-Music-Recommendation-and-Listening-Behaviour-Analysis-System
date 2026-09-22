import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors

df = pd.read_csv("cleaned_data/clean_music.csv")

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

feature_data = df[features].copy()
feature_data = feature_data.fillna(feature_data.mean())

scaler = StandardScaler()
feature_matrix = scaler.fit_transform(feature_data)

model = NearestNeighbors(
    n_neighbors=15,
    metric="cosine"
)

model.fit(feature_matrix)


def recommend_songs_by_id(
    track_id,
    number_of_recommendations=5
):

    matches = df[
        df["track_id"].astype(str) == str(track_id)
    ]

    if matches.empty:
        return []

    song_index = matches.index[0]

    neighbours = model.kneighbors(
        feature_matrix[song_index].reshape(1, -1),
        n_neighbors=15
    )

    distances = neighbours[0][0]
    indices = neighbours[1][0]

    recommendations = []
    used_tracks = set()

    for distance, index in zip(distances, indices):

        if index == song_index:
            continue

        recommended_track_id = str(
            df.loc[index, "track_id"]
        )

        if recommended_track_id in used_tracks:
            continue

        used_tracks.add(
            recommended_track_id
        )
        print("DISTANCE:", distance)
        print("SIMILARITY:", (1 - float(distance)) * 100)
       

        recommendations.append({
            "track_id": recommended_track_id,
            "track_name": str(df.loc[index, "track_name"]),
            "artists": str(df.loc[index, "artists"]),
            "album_name": str(df.loc[index, "album_name"]),
            "similarity": round(1 - float(distance), 4),
            "similarity_percent": round((1 - float(distance)) * 100, 2)
        })

        if len(recommendations) >= number_of_recommendations:
            break

    return recommendations
 


def recommend_songs_by_name(
    song_name,
    number_of_recommendations=5
):

    matches = df[
        df["track_name"].astype(str).str.lower()
        == song_name.lower()
    ]

    if matches.empty:
        return []

    track_id = matches.iloc[0]["track_id"]

    return recommend_songs_by_id(
        track_id,
        number_of_recommendations
    )

def recommend_songs_with_fallback(
    track_id,
    song_name=None,
    artist=None,
    number_of_recommendations=3
):

    recommendations = recommend_songs_by_id(
        track_id,
        number_of_recommendations
    )

    if recommendations:
        return recommendations

    if song_name:

        matches = df[
            df["track_name"].astype(str).str.lower()
            == song_name.lower()
        ]

        if not matches.empty:

            dataset_track_id = matches.iloc[0]["track_id"]

            return recommend_songs_by_id(
                dataset_track_id,
                number_of_recommendations
            )

    if artist:

        artist_matches = df[
            df["artists"].astype(str).str.lower()
            .str.contains(
                artist.lower(),
                na=False
            )
        ]

        if not artist_matches.empty:

            artist_index = artist_matches.index[0]

            neighbours = model.kneighbors(
                feature_matrix[artist_index].reshape(1, -1),
                n_neighbors=15
            )

            distances = neighbours[0][0]
            indices = neighbours[1][0]

            recommendations = []
            used_tracks = set()

            for distance, index in zip(distances, indices):

                recommended_track_id = str(
                    df.loc[index, "track_id"]
                )

                if recommended_track_id == str(track_id):
                    continue

                if recommended_track_id in used_tracks:
                    continue

                used_tracks.add(
                    recommended_track_id
                )

                recommendations.append({

                    "track_id":
                        recommended_track_id,

                    "track_name":
                        str(
                            df.loc[index, "track_name"]
                        ),

                    "artists":
                        str(
                            df.loc[index, "artists"]
                        ),

                    "album_name":
                        str(
                            df.loc[index, "album_name"]
                        ),

                    "similarity":
                        round(
                            1 - float(distance),
                            4
                        ),

                        "similarity_percent": round(
                            (1 - float(distance)) * 100,
                           2
                        
)

                })

                if len(recommendations) >= number_of_recommendations:
                    break

            return recommendations

    return []






if __name__ == "__main__":
    results = recommend_songs_by_name("Shape Of You")

    for song in results:
        print(
            song["track_name"],
            "-",
            song["similarity_percent"],
            "%"
        )