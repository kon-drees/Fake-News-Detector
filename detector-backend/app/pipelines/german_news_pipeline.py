import pandas as pd

from app.core.config import Settings
from app.pipelines.base_pipeline import BaseDataPipeline
from app.domain import Label, Language

settings = Settings()


class GermanNewsPipeline(BaseDataPipeline):

    @staticmethod
    def _normalize_whitespace(s: pd.Series) -> pd.Series:
        return (
            s.astype(str)
             .str.replace(r"\r\n|\r|\n", " ", regex=True)
             .str.replace(r"\s+", " ", regex=True)
             .str.strip()
        )

    @staticmethod
    def _remove_html_and_urls(s: pd.Series) -> pd.Series:
        s = s.str.replace(r"http\S+|www\.\S+", " ", regex=True)
        s = s.str.replace(r"<[^>]+>", " ", regex=True)
        return s

    @staticmethod
    def _normalize_quotes_and_dashes(s: pd.Series) -> pd.Series:
        repl = {
            "„": "\"", "“": "\"",
            "‚": "'", "‘": "'", "’": "'",
            "´": "'", "`": "'",
            "–": "-", "—": "-",
            "…": "...",
        }
        for old, new in repl.items():
            s = s.str.replace(old, new)
        return s

    @staticmethod
    def _cleanup_boundaries(s: pd.Series) -> pd.Series:
        strip_chars = ' "\'„“‚‘’«»›‹|[](){}-–—'
        return s.str.strip(strip_chars)

    @staticmethod
    def _clean_text_column(s: pd.Series) -> pd.Series:
        s = s.fillna("")
        s = GermanNewsPipeline._remove_html_and_urls(s)
        s = GermanNewsPipeline._normalize_quotes_and_dashes(s)
        s = GermanNewsPipeline._normalize_whitespace(s)
        s = GermanNewsPipeline._cleanup_boundaries(s)
        return s

    @staticmethod
    def _clean_title_column(s: pd.Series) -> pd.Series:
        s = s.astype(str)

        placeholder_values = {
            "nan", "NaN", "None", "none",
            "null", "Null", "-", "--"
        }
        s = s.replace(list(placeholder_values), "")

        s = GermanNewsPipeline._remove_html_and_urls(s)
        s = GermanNewsPipeline._normalize_quotes_and_dashes(s)
        s = GermanNewsPipeline._normalize_whitespace(s)
        s = GermanNewsPipeline._cleanup_boundaries(s)
        s = s.str.replace(r"[!?]{3,}", "!!", regex=True)
        s = s.mask(s.str.len() < 3, "")
        s = s.fillna("")
        return s


    def _load_data(self) -> pd.DataFrame:
        csv_path = (
            settings.BASE_DIR.parent
            / "rawdata"
            / "German_News_Dataset"
            / "data.csv"
        )
        return pd.read_csv(csv_path)

    def _run_processing(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        drop_cols = [c for c in df.columns if c.lower().startswith("unnamed")]
        if drop_cols:
            df = df.drop(columns=drop_cols)
        df["text"] = self._clean_text_column(df["text"])
        if "title" in df.columns:
            df["title"] = self._clean_title_column(df["title"])
        else:
            df["title"] = ""
        if "published" in df.columns:
            published_num = pd.to_numeric(df["published"], errors="coerce")

            df["publish_date"] = pd.to_datetime(
                published_num,
                errors="coerce",
                unit="s",
            )

            df["publish_date"] = (
                df["publish_date"]
                .dt.strftime("%Y-%m-%d")
                .fillna("")
            )
        else:
            df["publish_date"] = ""

        if "source" in df.columns:
            df["source"] = df["source"].fillna("")
        else:
            df["source"] = ""

        df = df.dropna(subset=["text"])
        df = df[df["text"].str.strip() != ""]
        df = df.drop_duplicates(subset=["text"])
        df["language"] = Language.DE.value
        df["label"] = Label.REAL.value
        df = df[["title", "text", "label", "source", "publish_date", "language"]]
        return df
