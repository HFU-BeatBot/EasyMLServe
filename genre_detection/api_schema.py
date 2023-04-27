from typing import List
from pydantic import BaseModel


class APIRequest(BaseModel):
    music_array: List[float]


class APIResponse(BaseModel):
    genre: str
    confidence: float
