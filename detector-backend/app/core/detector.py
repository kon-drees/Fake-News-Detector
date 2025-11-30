from typing import List, Literal

from fastapi import HTTPException
from shap import Explainer
import torch
from transformers import pipeline, Pipeline

from app.domain import PredictionResult, TokenContribution
from app.services.language_service import LanguageDetectionService
from app.domain import Label


class FakeNewsDetector:
    def __init__(self):
        # TODO: Change URI for own models
        self.pipe_en = pipeline("text-classification", "Pulk17/Fake-News-Detection", device=0 if torch.cuda.is_available() else -1)
        self.pipe_de = pipeline("text-classification", "Pulk17/Fake-News-Detection", device=0 if torch.cuda.is_available() else -1)
        self.explainer_en = Explainer(self.pipe_en)
        self.explainer_de = Explainer(self.pipe_de)
        self.language_detector = LanguageDetectionService()

    def choose_language(
        self, text: str, return_element: Literal["pipe", "explainer"]
    ) -> Pipeline | Explainer:
        if self.language_detector.is_english(text):
            pipe = self.pipe_en
            explainer = self.explainer_en
        elif self.language_detector.is_german(text):
            pipe = self.pipe_de
            explainer = self.explainer_de
        else:
            language = self.language_detector.detect_code(text)
            raise HTTPException(
                status_code=422,
                detail=f"Language has to be either German or English. Got {language}.",
            )

        return pipe if return_element == "pipe" else explainer

    def predict(self, text: str) -> PredictionResult:
        pipe = self.choose_language(text, return_element="pipe")

        result = pipe(text, truncation=True, max_length=512)
        top_result = max(result, key=lambda x: x["score"])

        label = Label.from_number(int(top_result["label"].split("_")[1]))
        score = top_result["score"]

        return PredictionResult(label=label, score=score)

    def highlight(self, text: str) -> List[TokenContribution]:
        explainer = self.choose_language(text, return_element="explainer")
        shap_values = explainer([text])

        # Always explain the values for label fake -> Positive value: fake, Negative value: real
        target_class = 0

        tokens = shap_values.data[0]
        values = shap_values.values[0, :, target_class]

        highlights = []
        for token, value in zip(tokens, values):
            highlights.append(TokenContribution(token, value))

        return highlights
