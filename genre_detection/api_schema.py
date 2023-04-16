from typing import List
from pydantic import BaseModel


class APIRequest(BaseModel):
    music_array: str


class Histogram(BaseModel):
    counts: List[int]
    rel_counts: List[float]
    bins: List[float]


class APIResponse(BaseModel):
    genre: str
