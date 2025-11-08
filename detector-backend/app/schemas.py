from typing import Dict, List, Optional
from pydantic import BaseModel


class PredictTextRequest(BaseModel):
    text: str

class HighlightTokenSchema(BaseModel):
    text: str
    start: int
    end: int
    score: float

class PredictionResponse(BaseModel):
    text: str
    probabilities: Dict[str, float]
    highlights: Optional[List[HighlightTokenSchema]]

