import json
import os

from lingua import LanguageDetectorBuilder
import pandas as pd

from app.core.config import Settings
from app.pipelines.base_pipeline import BaseDataPipeline
from app.domain import Label

settings = Settings()


class WebzioPipeline(BaseDataPipeline):
    def _load_data(self) -> pd.DataFrame:
        domains = []
        titles = []
        texts = []
        publish_dates = []
        for root, dirs, files in os.walk(
            settings.BASE_DIR.parent / "rawdata" / "webz_io_Dataset"
        ):
            for file in files:
                if file.endswith(".json"):
                    file_path = os.path.join(root, file)

                    with open(file_path, "r") as f:
                        article_data = json.load(f)

                        domains.append(
                            article_data.get("thread", pd.NA).get("site", pd.NA)
                        )
                        titles.append(article_data.get("title", pd.NA))
                        texts.append(article_data.get("text", pd.NA))
                        publish_dates.append(article_data.get("published", pd.NA))

        df = pd.DataFrame(
            {
                "source": domains,
                "title": titles,
                "text": texts,
                "publish_date": publish_dates,
            }
        )

        return df

    def _run_processing(self, df: pd.DataFrame) -> pd.DataFrame | None:
        df = df.copy()

        df["label"] = Label.FAKE.value
        df["text"] = df["text"].str.strip().str.replace(r"\s+", " ", regex=True)
        df["publish_date"] = pd.to_datetime(
            df["publish_date"], errors="coerce", utc=True
        )
        df.loc[df["title"] == "", "title"] = pd.NA

        df = df.dropna(subset=["text", "label"]).drop_duplicates(subset=["text"])

        detector = LanguageDetectorBuilder.from_all_spoken_languages().build()
        df["language"] = df["text"].apply(
            lambda x: detector.detect_language_of(x).iso_code_639_1.name
        )
        df = df[df["language"] == "EN"]

        return df
