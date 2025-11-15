from dataclasses import dataclass
from datetime import datetime
from enum import Enum
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


class Label(str, Enum):
    FAKE = "fake"
    REAL = "real"

    @classmethod
    def from_number(cls, value: int):
        if value == 0:
            return cls.FAKE
        elif value == 1:
            return cls.REAL
        else:
            raise ValueError(f"Invalid value for Label: {value}")


@dataclass
class TrainingArticle:
    dataset: str
    title: Optional[str]
    text: str
    label: Label
    source: Optional[str]
    publish_date: Optional[datetime]
