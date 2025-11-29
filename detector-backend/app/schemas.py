from typing import Annotated, List

from fastapi import Query
from pydantic import BaseModel

from app.domain import PredictionResult, TokenContribution


class TextRequest(BaseModel):
    text: Annotated[str, Query(min_length=10)]


class PredictionResponse(BaseModel):
    prediction_result: PredictionResult
    confidence_fake: float
    confidence_real: float


class HighlightResponse(BaseModel):
    highlights: List[TokenContribution]
