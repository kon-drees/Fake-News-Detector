import os
import re
from typing import Iterable, List
from dataclasses import asdict
import pandas as pd

from app.db import get_articles_collection
from app.domain import TrainingArticle
from app.domain import Label

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

def clean_text_welfake(raw: str) -> str:
    if not isinstance(raw, str):
        return ""
    txt = raw.strip()
    txt = RE_NEWSWIRE_PREFIX.sub("", txt)
    txt = re.sub(r"\s+", " ", txt)
    return txt.strip()



def import_welfake_to_mongo():
    csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "rawdata", "WELFake_Dataset","WELFake_Dataset.csv"))
    df = pd.read_csv(csv_path)

    coll = get_articles_collection()
    coll.delete_many({"dataset": "welfake"})

    docs: List[dict] = []
    print("Start clean and import...")
    for _, row in df.iterrows():
        raw_text = row.get("text", "")
        clean_text = clean_text_welfake(raw_text)
        if not clean_text:
            continue

        title = row.get("title")
        if not isinstance(title, str):
            title = None

        label = Label(int(row.get("label", 0)))

        sample = TrainingArticle(
            dataset="welfake",
            title=title,
            text=clean_text,
            label=label.value
        )
        docs.append(asdict(sample))

    if docs:
        coll.insert_many(docs)

    print(f"Inserted {len(docs)} documents into 'articles' collection.")


if __name__ == "__main__":
    import_welfake_to_mongo()