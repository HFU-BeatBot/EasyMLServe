from typing import List
from pydantic import BaseModel


class APIRequest(BaseModel):
    use_legacy_model: bool = False
    music_array: List[float]


class APIResponse(BaseModel):
    genre: str
    confidences: dict
