from typing import List
from pydantic import BaseModel


class Song(BaseModel):
    track_name: str
    artists: str
    album_name: str

    class ConfigDict:
        json_schema_extra = {
            "example": {
                "track_name": "Time",
                "artists": "Pink Floyd",
                "album_name": "The Dark Side of the Moon",
            }
        }


class RecommendationResponse(BaseModel):
    requested_track: str
    recommendations: List[Song]
    similarity_scores: List[float]

    class ConfigDict:
        json_schema_extra = {
            "example": {
                "requested_track": "Time",
                "recommendations": [
                    {
                        "track_name": "Time",
                        "artists": "Pink Floyd",
                        "album_name": "The Dark Side of the Moon",
                    }
                ],
                "similarity_scores": [1.0],
            }
        }
