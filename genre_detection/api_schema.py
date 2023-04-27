from typing import List
from pydantic import BaseModel


class APIRequest(BaseModel):
    use_python_model: bool = False
    music_array: List[float]


class APIResponse(BaseModel):
    genre: str
    confidence: float
