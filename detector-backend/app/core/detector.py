from typing import List, Literal

from fastapi import HTTPException
from shap import Explainer
import torch
from transformers import pipeline, Pipeline

from app.domain import PredictionResult, TokenContribution
from app.services.language_service import LanguageDetectionService
from app.domain import Label


class FakeNewsDetector:
    """
    Core detector service providing multi-language fake news classification
    and token-level interpretability via SHAP explainers.
    """

    def __init__(self):
        # Initialize pipelines for each supported language.
        self.pipe_en = pipeline(
            "text-classification",
            "Lennywinks/fake-news-detector-english",
            device=0 if torch.cuda.is_available() else -1,
        )
        self.pipe_de = pipeline(
            "text-classification",
            "Lennywinks/fake-news-detector-german",
            device=0 if torch.cuda.is_available() else -1,
        )
        # SHAP Explainers take the pipeline as input to calculate feature importance for specific text tokens.
        self.explainer_en = Explainer(self.pipe_en)
        self.explainer_de = Explainer(self.pipe_de)
        self.language_detector = LanguageDetectionService()

    def choose_language(
        self, text: str, return_element: Literal["pipe", "explainer"]
    ) -> Pipeline | Explainer:
        """
        Routes the input text to the appropriate model based on language detection.
        Strictly enforces English or German support. If a different language is
        detected, a 422 error is raised to prevent invalid inference results.
        """
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
        """
        Executes a classification pass on the input text.
        """
        pipe = self.choose_language(text, return_element="pipe")

        result = pipe(text, truncation=True, max_length=512)
        top_result = max(result, key=lambda x: x["score"])

        label = Label.from_number(int(top_result["label"].split("_")[1]))
        score = top_result["score"]

        return PredictionResult(label=label, score=score)

    def highlight(self, text: str) -> List[TokenContribution]:
        """
        Calculates the contribution of each token to the classification result.

        Uses SHAP (SHapley Additive exPlanations) to assign importance scores.
        Scores are normalized against the maximum absolute value to allow for
        consistent heatmapping in the frontend.
        """
        explainer = self.choose_language(text, return_element="explainer")

        # This call is computationally expensive as it requires multiple inference passes to calculate Shapley values.
        try:
            shap_values = explainer([text])
        except Exception as exc:
            raise HTTPException(
                status_code=500, detail=f"Could not generate highlights: {exc}"
            ) from exc

        # Get the predicted label
        prediction = self.predict(text)
        target_class = 0 if prediction.label == Label.FAKE else 1

        tokens = shap_values.data[0]
        values = shap_values.values[0, :, target_class]
        # Find max value for normalization
        max_abs_value = max([abs(v) for v in values])

        highlights = []
        for token, score in zip(tokens, values):
            if token.strip() == "":
                continue
            # 0.0 / 0.0 = nan -> Might be the case for small text inputs and causes a crash later on.
            score_normalized = score / max_abs_value if max_abs_value > 0 else 0.0
            highlights.append(TokenContribution(token, score, score_normalized))

        highlights = FakeNewsDetector.merge_tokens_to_words(
            original_text=text, highlights=highlights
        )

        return highlights

    @staticmethod
    def merge_tokens_to_words(
        original_text: str, highlights: List[TokenContribution]
    ) -> List[TokenContribution]:
        words = original_text.split()
        merged_results = []
        token_ptr = 0

        for word in words:
            buffer = []
            accumulated_str = ""

            # Match each to token, till the word is complete
            while token_ptr < len(highlights):
                h = highlights[token_ptr]
                clean_token = h.token.strip()

                # Skip if token is empty
                if not clean_token and h.token:
                    token_ptr += 1
                    continue

                accumulated_str += clean_token
                buffer.append(h)
                token_ptr += 1

                if len(accumulated_str) >= len(word):
                    break

            # Aggregate TokenContributions
            if buffer:
                avg_score = sum(t.score for t in buffer) / len(buffer)
                avg_norm = sum(t.score_normalized for t in buffer) / len(buffer)

                merged_results.append(
                    TokenContribution(word, float(avg_score), float(avg_norm))
                )

        return merged_results
