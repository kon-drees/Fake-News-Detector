import datetime
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
    label: str
    probabilities: Dict[str, float]
    highlights: Optional[List[HighlightTokenSchema]]
    meta: Optional[dict] = None
