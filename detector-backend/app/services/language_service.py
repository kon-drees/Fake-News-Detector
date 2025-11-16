from __future__ import annotations

from typing import Optional

from lingua import Language, LanguageDetectorBuilder


class LanguageDetectionService:
    def __init__(self, restrict_to: Optional[list[str]] = None) -> None:
        if restrict_to:
            langs = []
            for code in restrict_to:
                code = code.lower()
                if code == "en":
                    langs.append(Language.ENGLISH)
                elif code == "de":
                    langs.append(Language.GERMAN)
            self._detector = LanguageDetectorBuilder.from_languages(*langs).build()
        else:
            self._detector = LanguageDetectorBuilder.from_all_spoken_languages().build()

    def detect_code(self, text: str) -> Optional[str]:
        if not isinstance(text, str):
            return None
        text = text.strip()
        if not text:
            return None
        lang = self._detector.detect_language_of(text)
        if lang is None:
            return None
        return lang.iso_code_639_1.name.lower()

    def is_english(self, text: str) -> bool:
        return self.detect_code(text) == "en"

    def is_german(self, text: str) -> bool:
        return self.detect_code(text) == "de"
