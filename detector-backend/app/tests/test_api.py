from typing import List

from fastapi.testclient import TestClient
import pytest
from unittest.mock import patch


from app.main import app, model
from app.domain import Label, PredictionResult, TokenContribution
from app.schemas import FactCheckResponse


class MockArticleExtractor:
    def __init__(self, *args, **kwargs):
        self.calls = []

    def process(self, user_input: str):
        self.calls.append(user_input)
        if "fail" in user_input:
            return {
                "success": False,
                "input_type": "url",
                "publisher": None,
                "title": None,
                "text": None,
                "error": "Extraction failed",
            }

        if user_input.startswith("http"):
            return {
                "success": True,
                "input_type": "url",
                "publisher": "Example News",
                "title": "Example Title",
                "text": "Extracted article body",
                "error": None,
            }

        return {
            "success": True,
            "input_type": "text",
            "publisher": None,
            "title": None,
            "text": user_input,
            "error": None,
        }


class MockFakeNewsDetector:
    def __init__(self):
        self.last_predict_input = None
        self.last_highlight_input = None

    def predict(self, text: str) -> PredictionResult:
        self.last_predict_input = text
        return PredictionResult(label=Label.FAKE, score=0.95)

    def highlight(self, text: str) -> List[TokenContribution]:
        self.last_highlight_input = text
        return [
            TokenContribution("Fake", 0.9, 0.9),
            TokenContribution("Article", 0.1, 0.1),
        ]


class MockFactCheckAgent:
    def __init__(self):
        self.last_text = None

    async def run_fact_check(self, text: str) -> FactCheckResponse:
        self.last_text = text
        return FactCheckResponse(
            fake_score=0.4,
            summary_analysis="Checked content",
            checked_claims=[],
        )


@pytest.fixture(scope="module")
def client():
    with patch("app.main.FakeNewsDetector", new=MockFakeNewsDetector):
        with patch("app.main.FactCheckAgent", new=MockFactCheckAgent):
            with patch("app.main.ArticleExtractor", new=MockArticleExtractor):
                with TestClient(app) as c:
                    yield c

    model.clear()


def test_predict_endpoint_success(client):
    payload = {"text": "Fake Article."}

    response = client.post("/api/predict", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert "prediction_result" in data
    assert "label" in data["prediction_result"]
    assert "score" in data["prediction_result"]
    assert "confidence_fake" in data
    assert data["prediction_result"]["label"] == Label.FAKE
    assert data["confidence_fake"] == pytest.approx(0.95)
    assert data["confidence_real"] == pytest.approx(0.05)


def test_highlight_endpoint_success(client):
    payload = {"text": "Fake Article."}

    response = client.post("/api/highlight", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert "highlights" in data
    assert isinstance(data["highlights"], list)
    assert len(data["highlights"]) == 2
    assert data["highlights"][0]["token"] == "Fake"


def test_fact_check_endpoint_success(client):
    payload = {"text": "Fake Article."}
    response = client.post("/api/fact-check", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert "fake_score" in data
    assert "summary_analysis" in data
    assert "checked_claims" in data
    assert isinstance(data["checked_claims"], list)


def test_predict_validation_error(client):
    response = client.post("/api/predict", json={})

    assert response.status_code == 422
    assert "detail" in response.json()


def test_predict_empty_string(client):
    response = client.post("/api/predict", json={"text": ""})

    assert response.status_code == 422


def test_predict_longer_string(client):
    response = client.post("/api/predict", json={"text": "A longer string."})

    assert response.status_code == 200


def test_predict_with_url_uses_extractor(client):
    response = client.post("/api/predict", json={"text": "https://example.com/article"})

    assert response.status_code == 200
    assert model["detector"].last_predict_input == "Extracted article body"


def test_predict_extraction_failure_returns_error(client):
    response = client.post("/api/predict", json={"text": "fail-url"})

    assert response.status_code == 400
    assert "detail" in response.json()


def test_fact_check_uses_extracted_text(client):
    response = client.post("/api/fact-check", json={"text": "https://example.com/article"})

    assert response.status_code == 200
    assert model["fact_checker"].last_text == "Extracted article body"
