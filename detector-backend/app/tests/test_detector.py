import pytest

from app.core.detector import FakeNewsDetector
from app.domain import Label, TokenContribution, PredictionResult


@pytest.fixture(scope="module")
def detector():
    return FakeNewsDetector()


def test_predict_structure(detector):
    text = "Donald Trump left the office."
    result = detector.predict(text)

    assert isinstance(result, PredictionResult)
    assert isinstance(result.label, Label)
    assert 0.0 <= result.score <= 1.0


def test_highlight_structure(detector):
    text = "Donald Trump left the office."

    highlights = detector.highlight(text)

    assert isinstance(highlights, list)
    assert len(highlights) > 0

    first_token = highlights[0]

    assert isinstance(first_token, TokenContribution)
    assert first_token.token.strip() == "Donald"
    assert isinstance(first_token.score, float)
    assert isinstance(first_token.score_normalized, float)
