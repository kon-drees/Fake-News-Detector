import pandas as pd

from app.core.config import Settings
from app.pipelines.base_pipeline import BaseDataPipeline

settings = Settings()


class GermanFakeNCPipeline(BaseDataPipeline):
    def _load_data(self) -> pd.DataFrame:
        csv_path = (
                settings.BASE_DIR.parent
                / "rawdata"
                / "GermanFakeNC"
                / "scraped"
                / "germanfakenc_training_articles.csv"
        )
        return pd.read_csv(csv_path)

    def _run_processing(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        df["text"] = (
            df["text"]
            .astype(str)
            .str.strip()
            .str.replace(r"\s+", " ", regex=True)
        )

        df["title"] = df["title"].astype(str)
        df.loc[df["title"].str.strip() == "", "title"] = pd.NA
        df["publish_date"] = pd.to_datetime(df["publish_date"], errors="coerce")
        df["publish_date"] = df["publish_date"].dt.strftime("%Y-%m-%d")
        df["publish_date"] = df["publish_date"].fillna("")
        df = df.dropna(subset=["text", "label"]).drop_duplicates(subset=["text"])
        df["language"] = "de"
        df["label"] = df["label"].astype(str)
        if "source" in df.columns:
            df["source"] = df["source"].fillna("")
        df = df[["title", "text", "label", "source", "publish_date", "language"]]

        return df
