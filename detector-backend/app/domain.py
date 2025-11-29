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
    score: float


@dataclass
class TokenContribution:
    token: str
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


class Language(str, Enum):
    DE = "de"
    EN = "en"


@dataclass
class ScrapedArticle:
    url: str
    title: Optional[str]
    text: Optional[str]


@dataclass
class TrainingArticle:
    dataset: str
    title: Optional[str]
    text: str
    label: Label
    source: Optional[str]
    publish_date: Optional[datetime]
    language: Language
