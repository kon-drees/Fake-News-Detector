import pandas as pd

from app.core.config import Settings
from app.db import Database
from app.pipelines.base_pipeline import BaseDataPipeline
from app.pipelines.webzio_pipeline import WebzioPipeline
from app.pipelines.welfake_pipeline import WelfakePipeline
from pipelines.germa_pipeline import GermaPipeline
from pipelines.german_news_pipeline import GermanNewsPipeline
from pipelines.germanfakenc_pipeline import GermanFakeNCPipeline


class DataService:
    PIPELINES = {
        "germannews": GermanNewsPipeline,
        "germanfakenc": GermanFakeNCPipeline,
        "welfake": WelfakePipeline,
        "webzio": WebzioPipeline,
        "germa": GermaPipeline,
    }

    def __init__(self) -> None:
        self.db = Database(Settings())

    @staticmethod
    def validate_df(df: pd.DataFrame, dataset: str) -> None:
        if df is None or df.empty:
            raise ValueError(f"[DataService] No data found for {dataset}")

        required_cols = {"title", "text", "label", "language"}
        if not required_cols.issubset(df.columns):
            raise ValueError(
                f"[DataService] Dataframe of {dataset} is missing at least on of {required_cols} Columns."
            )

    def import_to_mongo(self, pipeline: BaseDataPipeline) -> None:
        df = pipeline.process_data()
        dataset = pipeline.dataset_name

        try:
            DataService.validate_df(df, dataset)
        except ValueError as e:
            print(f"[DataService] Validation failed for {dataset}: {e}")
            return

        print(f"[DataService] Starting import for {dataset}")

        coll = self.db.get_articles_collection()
        coll.delete_many({"dataset": dataset})
        coll.insert_many(df.to_dict("records"))

        print(
            f"[DataService] Finished import for {dataset}. Inserted {len(df)} documents into 'articles' collection."
        )

    def run_and_import_all_pipelines(self) -> None:
        for name, pipeline in DataService.PIPELINES.items():
            self.import_to_mongo(pipeline(name))


if __name__ == "__main__":
    data_service = DataService()
    data_service.run_and_import_all_pipelines()
    data_service.db.close()
