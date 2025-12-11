import re

import pandas as pd

from app.core.config import Settings
from app.domain import Label
from app.pipelines.base_pipeline import BaseDataPipeline

settings = Settings()


class WelfakePipeline(BaseDataPipeline):
    RE_NEWSWIRE_PREFIX = re.compile(
        r"""^                      
            [A-Z][A-Za-z0-9 /,.-]* # Ort(e): z.B. BAGHDAD/LONDON oder NEW YORK
            \s*                    # optionales Leerzeichen
            \(
            (?:Reuters|REUTERS|AP|AFP)
            \)
            \s*-\s*                # Bindestrich mit evtl. Spaces
        """,
        re.VERBOSE,
    )

    def _load_data(self) -> pd.DataFrame:
        csv_path = (
                settings.BASE_DIR.parent
                / "rawdata"
                / "WELFake_Dataset"
                / "WELFake_Dataset.csv"
        )

        return pd.read_csv(csv_path, index_col=0)

    def _run_processing(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["text"] = (
            df["text"]
            .astype(str)
            .str.strip()
            .str.replace(self.RE_NEWSWIRE_PREFIX, "", regex=True)
            .str.replace(r"\s+", " ", regex=True)
        )
        df["title"] = df["title"].astype(str)
        df.loc[df["title"].str.strip() == "", "title"] = pd.NA
        df = df.dropna(subset=["text", "label"]).drop_duplicates(subset=["text"])
        #labels sind vertauscht!!!!
        df["label"] = df["label"].astype(int)
        df["label"] = df["label"].map({
            0: Label.REAL.value,
            1: Label.FAKE.value,
        })
        df["language"] = df["text"].apply(self.lang_service.detect_code)
        df = df[df["language"] == "en"]
        return df
