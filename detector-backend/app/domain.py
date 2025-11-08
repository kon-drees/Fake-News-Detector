from dataclasses import dataclass
from typing import Dict


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



