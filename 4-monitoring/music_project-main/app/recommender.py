from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler


class RecommenderModel:
    def __init__(self):
        self.data_encoded = None
        self.similarity_matrix = None

    def fit(self, df: pd.DataFrame, df_year: pd.DataFrame):
        df_year["track_id"] = df_year["id"]
        df_year.drop(columns="id", inplace=True)

        df = pd.merge(df, df_year, on="track_id")

        xtab_song = pd.crosstab(df["track_id"], df["track_genre"]) * 2
        xtab_song.reset_index(inplace=True)

        df_distinct = (
            df.drop_duplicates("track_id")
            .sort_values("track_id")
            .reset_index(drop=True)
        )
        data_encoded = pd.concat(
            [df_distinct, xtab_song.drop(columns=["track_id"])], axis=1
        )

        numerical_features = [
            "explicit",
            "danceability",
            "energy",
            "loudness",
            "speechiness",
            "acousticness",
            "instrumentalness",
            "liveness",
            "valence",
            "year",
        ]
        scaler = MinMaxScaler()
        data_encoded[numerical_features] = scaler.fit_transform(
            data_encoded[numerical_features]
        )

        self.data_encoded = data_encoded
        self.similarity_matrix = cosine_similarity(
            data_encoded[numerical_features + list(xtab_song.columns[1:])]
        )

    def recommend(self, track_title: str, N: int = 5):
        indices = pd.Series(
            self.data_encoded.index, index=self.data_encoded["track_name"]
        ).drop_duplicates()

        if track_title not in indices:
            return []

        idx = indices[track_title]
        if isinstance(idx, pd.Series):
            idx = idx.iloc[0]

        sim_scores = list(enumerate(self.similarity_matrix[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1 : N + 1]

        song_indices = [i[0] for i in sim_scores]
        recommended = self.data_encoded[["track_name", "artists", "album_name"]].iloc[
            song_indices
        ]

        return recommended.to_dict(orient="records"), [round(float(i[1]),2) for i in sim_scores]


def load_model() -> object:
    return joblib.load(Path(__file__).resolve().parent / "model.pkl")


def recommend_songs(model, track_title: str, N: int = 5) -> list[dict[str, str]]:
    return model.recommend(track_title, N)


if __name__ == "__main__":

    def sample_tracks_df():
        return pd.DataFrame(
            [
                {
                    "track_id": "t1",
                    "track_name": "Song A",
                    "artists": "Artist 1",
                    "album_name": "Album 1",
                    "track_genre": "rock",
                    "explicit": 0,
                    "danceability": 0.5,
                    "energy": 0.7,
                    "loudness": -5,
                    "speechiness": 0.1,
                    "acousticness": 0.2,
                    "instrumentalness": 0.1,
                    "liveness": 0.3,
                    "valence": 0.6,
                },
                {
                    "track_id": "t2",
                    "track_name": "Song B",
                    "artists": "Artist 2",
                    "album_name": "Album 2",
                    "track_genre": "pop",
                    "explicit": 1,
                    "danceability": 0.8,
                    "energy": 0.9,
                    "loudness": -3,
                    "speechiness": 0.2,
                    "acousticness": 0.1,
                    "instrumentalness": 0.0,
                    "liveness": 0.2,
                    "valence": 0.8,
                },
            ]
        )

    def sample_years_df():
        return pd.DataFrame(
            [
                {"id": "t1", "year": 2020},
                {"id": "t2", "year": 2021},
            ]
        )

    model = RecommenderModel()
    model.fit(sample_tracks_df(), sample_years_df())
    recommend_songs(model=model, track_title="Song A")
