import json
import pandas as pd

from app.core.config import Settings
from app.pipelines.base_pipeline import BaseDataPipeline

settings = Settings()

# HF: Human written and false, HR: Human written and true/real
LABEL_MAP = {
    "HF": "0",
    "HR": "1",
}

class GossipCopPipeline(BaseDataPipeline):
    def _load_data(self) -> pd.DataFrame:
        json_path = (
            settings.BASE_DIR.parent
            / "rawdata"
            / "gossipcop"
        )
        all_rows = []

        for label in ["HF", "HR"]:
            folder = json_path / label
            if not folder.exists():
                print(f"Folder {folder} not found.")
                continue

            for file_path in folder.glob("*.json"):
                print(f"processing file: {file_path}")
                try:
                    with open(file_path, "r", encoding="utf-8") as file:
                        data = json.load(file)
                        for entry in data.values():
                            all_rows.append(
                                {
                                    "title": entry.get("title", ""),
                                    "text": entry.get("text", entry.get("content", "")),
                                    "label": LABEL_MAP[label],
                                }
                            )
                except Exception as e:
                    print(f"[Error] Failed to load {file_path}: {e}")

        df = pd.DataFrame(all_rows)
        print(df)
        return df



    def _run_processing(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Clean text and title
        df["text"] = (
            df["text"]
            .astype(str)
            .str.strip()
            .str.replace(r"\s+", " ", regex=True)
        )
        df["title"] = df["title"].astype(str).str.strip()
        df.loc[df["title"] == "", "title"] = pd.NA

        # Drop duplicates and missing text/label rows
        df = df.dropna(subset=["text", "label"]).drop_duplicates(subset=["text"])

        # Add static metadata columns
        df["publish_date"] = ""  # No publish date available
        df["language"] = "en"

        # Keep only relevant columns: title, text, label, language
        df = df[["title", "text", "label", "language"]]

        return df