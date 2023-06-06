from typing import List
from pydantic import BaseModel


class APIRequest(BaseModel):
    model_to_use: int = (
        2  # 0 = "Librosa - GTZAN", 1 = "Librosa - FMA", 2 = "JLibrosa - GTZAN"
    )
    music_array: List[float]


class APIResponse(BaseModel):
    genre: str
    confidences: dict
