from abc import ABC, abstractmethod

import pandas as pd

from services.language_service import LanguageDetectionService


class BaseDataPipeline(ABC):
    def __init__(self, dataset_name: str):
        self.dataset_name = dataset_name
        self.lang_service = LanguageDetectionService()

    @abstractmethod
    def _load_data(self) -> pd.DataFrame:
        pass

    @abstractmethod
    def _run_processing(self, df: pd.DataFrame) -> pd.DataFrame:
        pass

    def process_data(self) -> pd.DataFrame | None:
        print(
            f"[{self.__class__.__name__}] Starting processing for {self.dataset_name} dataset."
        )

        try:
            df = self._load_data()
        except FileNotFoundError:
            print(
                f"[{self.__class__.__name__}] Could not find the file for {self.dataset_name}."
            )
            return None

        processed_df = self._run_processing(df)

        processed_df["dataset"] = self.dataset_name

        print(
            f"[{self.__class__.__name__}] Finished processing for {self.dataset_name} dataset."
        )

        return processed_df
