import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List

import requests
from bs4 import BeautifulSoup

from app.domain import Label, ScrapedArticle, TrainingArticle, Language

HERE = Path(__file__).resolve()
BACKEND_DIR = HERE.parents[2]
JSON_PATH = BACKEND_DIR / "rawdata" / "GermanFakeNC" / "GermanFakeNC.json"
OUTPUT_DIR = BACKEND_DIR / "rawdata" / "GermanFakeNC" / "scraped"



class GermanFakeNCScraper:
    def __init__(
        self,
        json_path: Path = JSON_PATH,
        output_dir: Path = OUTPUT_DIR,
    ) -> None:
        self.json_path = json_path
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        # Faking a header so we can bypass some filters....
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
        }

    @staticmethod
    def _map_overall_rating_to_label(overall: Optional[str]) -> Optional[Label]:
        if overall is None or overall == "":
            return None
        try:
            value = float(overall)
        except ValueError:
            return None

        if value > 0.5:
            return Label.FAKE
        else:
            return Label.REAL

    @staticmethod
    def _parse_date(date_str: Optional[str]) -> Optional[datetime]:
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return None

    def _scrape_url(self, url: str) -> ScrapedArticle:
        resp = requests.get(url, headers=self.headers, timeout=15)
        resp.raise_for_status()
        html = resp.text

        soup = BeautifulSoup(html, "html.parser")
        title = soup.title.string.strip() if soup.title and soup.title.string else None

        paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
        text = "\n".join(p for p in paragraphs if p)

        return ScrapedArticle(url=url, title=title, text=text or None)

    def load_raw_metadata(self) -> list[dict]:
        with self.json_path.open(encoding="utf-8") as f:
            return json.load(f)

    def scrape_all(self) -> List[TrainingArticle]:
        records = self.load_raw_metadata()
        total = len(records)

        articles: List[TrainingArticle] = []
        errors = 0
        no_text = 0
        skipped_label_or_url = 0

        for i, rec in enumerate(records, start=1):
            url = rec.get("URL")
            overall = rec.get("Overall_Rating")
            date_str = rec.get("Date")

            label = self._map_overall_rating_to_label(overall)
            if label is None or not url:
                skipped_label_or_url += 1
                continue

            try:
                scraped = self._scrape_url(url)
            except Exception as e:
                errors += 1
                print(f"[{i}/{total}] Fehler bei {url}: {e}")
                continue

            if not scraped.text:
                no_text += 1
                print(f"[{i}/{total}] Kein Text für {url}")
                continue

            publish_date = self._parse_date(date_str)

            ta = TrainingArticle(
                dataset="GermanFakeNC",
                title=scraped.title,
                text=scraped.text,
                label=label,
                source=url,
                publish_date=publish_date,
                language=Language.DE,
            )
            articles.append(ta)


        csv_path = self.output_dir / "germanfakenc_training_articles.csv"
        with csv_path.open("w", encoding="utf-8", newline="") as f:
            import csv
            writer = csv.writer(f)
            writer.writerow(["dataset", "title", "text", "label", "source", "publish_date"])
            for a in articles:
                writer.writerow(
                    [
                        a.dataset,
                        a.title or "",
                        a.text.replace("\n", " "),
                        a.label.value,
                        a.source or "",
                        a.publish_date.strftime("%Y-%m-%d") if a.publish_date else "",
                    ]
                )

        usable = len(articles)
        lost = total - usable
        perc_usable = usable / total * 100 if total else 0.0
        perc_lost= 100 - perc_usable

        summary_lines = [
            f"Gesamt:              {total} Artikel im JSON",
            f"Nutzbare Artikel:    {usable}",
            f"  -> davon Fehler:   {errors}",
            f"  -> ohne Text:      {no_text}",
            f"  -> Label/URL skip: {skipped_label_or_url}",
            f"Verlust absolut:     {lost}",
            f"Vorhanden:           {perc_usable:.1f} %",
            f"Verlust:             {perc_lost:.1f} %",
        ]
        summary_text = "\n".join(summary_lines)

        stats_path = self.output_dir / "germanfakenc_scrape_stats.txt"
        with stats_path.open("w", encoding="utf-8") as f:
            f.write(summary_text + "\n")

        print(summary_text)

        return articles



def main() -> None:
    scraper = GermanFakeNCScraper()
    scraper.scrape_all()


if __name__ == "__main__":
    main()








