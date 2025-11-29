from typing import List

from fastapi.testclient import TestClient
import pytest
from unittest.mock import patch


from app.main import app, model
from app.domain import Label, PredictionResult, TokenContribution


class MockFakeNewsDetector:
    def predict(self, text: str) -> PredictionResult:
        return PredictionResult(label=Label.FAKE, score=0.95)

    def highlight(self, text: str) -> List[TokenContribution]:
        return [TokenContribution("Fake", 0.9), TokenContribution("Article", 0.1)]


@pytest.fixture(scope="module")
def client():
    model["detector"] = MockFakeNewsDetector()

    with patch("app.main.FakeNewsDetector", new=MockFakeNewsDetector):
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
