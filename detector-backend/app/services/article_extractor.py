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
import tldextract
import validators
from urllib.parse import urlparse
from typing import Optional, Dict, Any, List

from fundus import Crawler
from fundus.scraping.filter import inverse, regex_filter
from fundus.publishers import PublisherCollection, Publisher, PublisherGroup


class ArticleExtractor:
    def __init__(self) -> None:
        """
        Initialisiert den ArticleExtractor.

        Beim Erzeugen der Instanz wird einmalig eine Lookup-Struktur aufgebaut,
        welche registrierbare Domains (z. B. 'spiegel.de') den entsprechenden
        FUNDUS-Publishern zuordnet. Diese Vorverarbeitung ermöglicht eine
        effiziente Publisher-Erkennung mit konstanter Zugriffszeit (O(1))
        bei späteren Anfragen.
        """
        self._publisher_map: Dict[str, Publisher] = {}
        self._build_publisher_map()

    def _build_publisher_map(self) -> None:
        """
        Erstellt eine Mapping-Struktur von Domains zu FUNDUS-Publishern.

        FUNDUS organisiert Publisher teilweise in PublisherGroups. Diese Funktion
        normalisiert die Struktur, indem alle Publisher – unabhängig von ihrer
        Gruppierung – iteriert werden.

        Für jede Publisher-Domain wird die registrierbare Root-Domain
        (z. B. 'spiegel.de') extrahiert und als Schlüssel im Dictionary verwendet.
        Dadurch können unterschiedliche Subdomains (z. B. 'www.', 'm.', 'amp.')
        zuverlässig dem gleichen Publisher zugeordnet werden.
        """

        for entry in PublisherCollection:
            # PublisherCollection kann einzelne Publisher oder PublisherGroups enthalten
            if isinstance(entry, PublisherGroup):
                publishers = entry.publishers
            else:
                publishers = [entry]

            for publisher in publishers:
                domains = publisher.domain

                # FUNDUS erlaubt Domains sowohl als String als auch als Liste
                if isinstance(domains, str):
                    domains = [domains]

                for domain in domains:
                    # Extraktion der registrierbaren Root-Domain
                    extracted = tldextract.extract(domain)

                    # Zusammensetzen der Root-Domain (z. B. 'spiegel.de')
                    root_domain = f"{extracted.domain}.{extracted.suffix}"

                    # Speicherung im Lookup-Dictionary
                    self._publisher_map[root_domain] = publisher


    def _is_pure_url(self, text: str) -> bool:
        """
        Prüft, ob ein String ausschließlich aus einer URL besteht.

        Akzeptiert:
        - http://example.com
        - https://example.com
        - example.com/news/article

        Lehnt ab:
        - "Hier ist ein Link https://example.com"
        - "example.com und mehr Text"
        """

        if not text or not text.strip():
            return False

        text = text.strip()

        # Leerzeichen bedeutet kein reiner Link
        if " " in text:
            return False

        # Schema ergänzen, falls nicht vorhanden
        normalized = text
        if not re.match(r"^https?://", text):
            normalized = "https://" + text

        # URL-Syntax prüfen
        if not validators.url(normalized):
            return False

        parsed = urlparse(normalized)

        # Keine Domain
        if not parsed.netloc:
            return False

        # TLD prüfen
        extracted = tldextract.extract(parsed.netloc)
        if not extracted.domain or not extracted.suffix:
            return False

        return True

    def _find_publisher_for_url(self, hostname: str) -> Optional[Publisher]:
        """
        Bestimmt den passenden FUNDUS-Publisher anhand der Host-Domain einer URL.

        Die übergebene Host-Domain wird zunächst auf ihre registrierbare
        Root-Domain normalisiert. Anschließend erfolgt ein direkter Lookup
        im vorverarbeiteten Dictionary.

        Diese Vorgehensweise vermeidet wiederholte lineare Durchläufe über
        die PublisherCollection und ist insbesondere für den Einsatz in
        Webanwendungen effizient.

        :param hostname: Hostname einer URL (z. B. 'www.spiegel.de')
        :return:
            - Publisher, falls die Domain von FUNDUS unterstützt wird
            - None, falls kein passender Publisher existiert
        """

        if not hostname:
            return None

        # Normalisierung der Host-Domain auf registrierbare Root-Domain
        extracted = tldextract.extract(hostname)
        root_domain = f"{extracted.domain}.{extracted.suffix}"

        # Direkter Lookup im Dictionary (O(1))
        return self._publisher_map.get(root_domain)


    def _extract_article_with_fundus(self, url: str) -> Dict[str, Any]:
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
                "input_type": "url",
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
                "input_type": "url",
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
            "input_type": "url",
            "publisher": publisher.name,
            "title": None,
            "text": None,
            "error": "Artikel konnte nicht extrahiert werden.",
        }


    def process(self, user_input: str) -> Dict[str, Any]:
        """
        Zentrale Einstiegsmethode für die Verarbeitung von Nutzereingaben.

        Diese Methode entscheidet, ob es sich bei der Eingabe um:
        - eine reine URL zu einem Nachrichtenartikel oder
        - um bereits vorliegenden Artikeltext

        handelt und leitet entsprechend die weitere Verarbeitung ein.

        Ablauf:
        1. Prüfung, ob der Input ausschließlich aus einer URL besteht
        2. Falls URL: Extraktion über FUNDUS
        3. Falls kein Link: Behandlung als Rohtext
        4. Rückgabe eines einheitlichen Ergebnisobjekts

        :param user_input: Eingabetext aus dem Frontend (URL oder Artikeltext)
        :return: Dict[str, Any]:
                {
                    "success": bool,
                    "input_type": "url" | "text",
                    "publisher": str | None,
                    "title": str | None,
                    "text": str | None,
                    "error": str | None
                }
        """

        if not user_input or not user_input.strip():
            return {
                "success": False,
                "input_type": None,
                "publisher": None,
                "title": None,
                "text": None,
                "error": "Leere Eingabe.",
            }

        user_input = user_input.strip()

        # ---------------------------------------------------------
        # Fall 1: Eingabe ist ein reiner Link → Artikel extrahieren
        # ---------------------------------------------------------
        if self._is_pure_url(user_input):
            return self._extract_article_with_fundus(user_input)

        # ---------------------------------------------------------
        # Fall 2: Eingabe ist kein Link → als Artikeltext behandeln
        # ---------------------------------------------------------
        return {
            "success": True,
            "input_type": "text",
            "publisher": None,
            "title": None,
            "text": user_input,
            "error": None,
        }


# Test Extraktion eines Artikels
extractor = ArticleExtractor()
print(extractor.process('https://www.golem.de/news/science-fiction-neuer-star-trek-film-von-den-dungeons-dragons-machern-2511-202218.html'))

