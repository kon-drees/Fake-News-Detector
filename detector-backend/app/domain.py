from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class Article:
    text: str


@dataclass
class PredictionResult:
    label: str
    probabilities: Dict[str, float]


@dataclass
class HighlightToken:
    text: str
    start: int
    end: int
    score: float


@dataclass
class TrainingArticle:
    dataset: str
    title: Optional[str]
    text: str
    label: int


