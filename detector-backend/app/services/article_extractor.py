"""
Article Extraction Module (Fundus-based)
---------------------------------------

Dieses Modul implementiert die Extraktion eines einzelnen Nachrichtenartikels
mithilfe der Python-Bibliothek FUNDUS. FUNDUS enthält spezialisierte Parser
für viele große Nachrichtenportale (z. B. Golem.de, Heise.de, Spiegel.de).

ZIEL:
- Eine URL entgegennehmen
- Publisher anhand der Domain erkennen
- Falls Publisher nicht unterstützt → Fehler zurückgeben
- Falls unterstützt → Artikel über FUNDUS extrahieren
- Nur den einen Artikel extrahieren (kein Crawling kompletter Websites!)
- Plaintext zurückgeben (für spätere Klassifikation im KI-Modul)
"""

from __future__ import annotations

import re
from urllib.parse import urlparse
from typing import Optional, Dict, Any, List

from fundus import Crawler
from fundus.scraping.filter import inverse, regex_filter
from fundus.publishers import PublisherCollection, Publisher, PublisherGroup


class ArticleExtractor:

    def _find_publisher_for_url(self, hostname: str) -> Optional[Publisher]:
        """
        Bestimmt den passenden FUNDUS-Publisher für eine gegebene Host-Domain.

        FUNDUS strukturiert Publisher entweder:
        - als Einzelobjekt vom Typ Publisher oder
        - als Gruppe (PublisherGroup), welche mehrere Publisher zusammenfasst.

        Jeder Publisher besitzt eine oder mehrere definierte Domains. Diese Funktion
        führt eine normalisierte, domainbasierte Übereinstimmung durch.

        :param hostname: Die Host-Komponente einer URL.
        :return: Optional[Publisher]:
                - passender Publisher bei Erfolg
                - None, falls FUNDUS diese Domain nicht unterstützt
        """

        if not hostname:
            return None

        # Alle Publisher in FUNDUS durchlaufen
        for entry in PublisherCollection:
            # PublisherCollection enthält einzelne Publisher
            # ODER PublisherGroup, die mehrere Publisher umfasst.
            if isinstance(entry, PublisherGroup):
                publishers: List[Publisher] = entry.publishers
            else:
                publishers = [entry]

            # Domains prüfen
            for publisher in publishers:
                domains = publisher.domain

                # Publisher.domain kann str ODER List[str] sein
                if isinstance(domains, str):
                    domains = [domains]

                # Wenn die Domain der URL zu einem Publisher passt → Treffer
                for domain in domains:
                    if hostname in domain:
                        return publisher

        return None


    def extract_article_with_fundus(self, url: str) -> Dict[str, Any]:
        """
         Extrahiert einen einzelnen Artikel mithilfe des FUNDUS-Crawlers.

        Obwohl FUNDUS als generalisierbarer Crawler ausgelegt ist, kann durch
        geschickte Nutzung eines inversen Regex-Filters erreicht werden, dass
        ausschließlich *eine spezifische URL* extrahiert wird. Dies ermöglicht den
        Einsatz als zielgerichteten Artikel-Extractor.

        Ablauf:
        1. URL parsen → Publisher-Domain bestimmen
        2. Publisher in FUNDUS identifizieren
        3. Falls unbekannt → Fehlerobjekt zurückgeben
        4. Inversen URL-Filter aufbauen (beschränkt Crawling auf die Ziel-URL)
        5. Crawler initialisieren (threading=False → deterministisches Verhalten)
        6. Extrahierten Artikel zurückgeben

        :param url: Vollständige URL eines Nachrichtenartikels.
        :return: Dict[str, Any]:
                {
                    "success": bool,
                    "publisher": str | None,
                    "title": str | None,
                    "text": str | None,
                    "error": str | None
                }
        """
        # ---------------------------------------------------------
        # 1. Publisher aus URL bestimmen
        # ---------------------------------------------------------
        parsed = urlparse(url)
        hostname = parsed.hostname

        publisher = self._find_publisher_for_url(hostname)

        if publisher is None:
            return {
                "success": False,
                "publisher": None,
                "title": None,
                "text": None,
                "error": (
                    "Publisher wird von Fundus nicht unterstützt. "
                    "Extraktion für diese Domain ist nicht möglich."
                ),
            }

        # ---------------------------------------------------------
        # 2. URL-Filter definieren
        #
        # Der regex_filter lässt *alle anderen* URLs zu.
        # Mit inverse erhält FUNDUS effektiv nur die eine gewünschte Artikel-URL.
        # ---------------------------------------------------------
        escaped_path = re.escape(parsed.path)
        url_filter = inverse(regex_filter(escaped_path))

        # ---------------------------------------------------------
        # 3. FUNDUS-Crawler vorbereiten
        # threading=False verhindert parallele Konflikte
        # ---------------------------------------------------------
        crawler = Crawler(publisher, threading=False)

        # ---------------------------------------------------------
        # 4. Crawl-Vorgang ausführen
        #
        # Es wird nur der Artikel zurückgegeben, der mit der übergebenen URL übereinstimmt.
        # ---------------------------------------------------------
        for article in crawler.crawl(
                url_filter=url_filter,
                only_complete=False,  # unvollständige Artikel sind erlaubt
        ):
            return {
                "success": True,
                "publisher": publisher.name,
                "title": article.title,
                "text": article.plaintext,
                "error": None,
            }

        # ---------------------------------------------------------
        # 5. Falls FUNDUS keinen Artikel extrahieren konnte (z. B. Consent-Seite)
        # ---------------------------------------------------------
        return {
            "success": False,
            "publisher": publisher.name,
            "title": None,
            "text": None,
            "error": "Artikel konnte nicht extrahiert werden.",
        }

# Test Extraktion eines Artikels
extractor = ArticleExtractor()
print(extractor.extract_article_with_fundus('https://www.golem.de/news/science-fiction-neuer-star-trek-film-von-den-dungeons-dragons-machern-2511-202218.html'))
