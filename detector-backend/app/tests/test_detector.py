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


def test_merge_tokens_to_words(detector):
    original = "Donald Trump left the office."

    highlights = [
        TokenContribution("Donald", 0.1, 0.1),
        TokenContribution("Tr", 0.1, 0.1),
        TokenContribution("ump", 0.2, 0.2),
        TokenContribution("left", 0.1, 0.1),
        TokenContribution("the", 0.1, 0.1),
        TokenContribution("of", 0.1, 0.1),
        TokenContribution("fice", -0.1, -0.1),
        TokenContribution(".", 0.3, 0.3),
    ]

    result = detector.merge_tokens_to_words(original, highlights)

    assert isinstance(result, list)
    assert len(result) == len(original.split(" "))
    assert result[1].score == pytest.approx(0.15) and result[
        1
    ].score_normalized == pytest.approx(0.15)
    assert result[4].score == pytest.approx(0.1) and result[
        4
    ].score_normalized == pytest.approx(0.1)
