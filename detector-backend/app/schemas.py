from typing import Annotated, List

from fastapi import Query
from pydantic import BaseModel, Field

from app.domain import PredictionResult, TokenContribution


class TextRequest(BaseModel):
    text: Annotated[
        str,
        Query(
            min_length=5,
            description="Plain text content or one/multiple article URLs (one per line).",
        ),
    ]


# /predict
class PredictionResponse(BaseModel):
    prediction_result: PredictionResult
    confidence_fake: float
    confidence_real: float


# /highlight
class HighlightResponse(BaseModel):
    highlights: List[TokenContribution]


# /fact-check
class ClaimCheck(BaseModel):
    claim: str = Field(description="A specific claim extracted from the text.")
    assessment: str = Field(description="Assessment: True, False or Misleading.")
    reasoning: str = Field(description="Brief reasoning behind the assessment.")


class FactCheckResponse(BaseModel):
    fake_score: float = Field(
        description="A score ranging from 0.0 to 1.0 representing the likelihood of the article being fake.",
    )
    summary_analysis: str = Field(
        description="A concise summary analyzing the credibility, style, and potential bias of the text."
    )
    checked_claims: List[ClaimCheck] = Field(
        description="A list of specific claims found in the text and their fact-check results."
    )
