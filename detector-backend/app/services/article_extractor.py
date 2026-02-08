"""
Article Extraction Module
---------------------------------------

Dieses Modul implementiert die Extraktion eines einzelnen Nachrichtenartikels
mithilfe der Python-Bibliothek Fundus. Fundus enthält spezialisierte Parser
für viele große Nachrichtenportale (z. B. Golem.de, Heise.de, Spiegel.de).

ZIEL:
- Eine URL entgegennehmen
- Publisher anhand der Domain erkennen
- Falls Publisher nicht unterstützt → Fehler zurückgeben
- Falls unterstützt → Artikel über Fundus extrahieren
- Keine Website-Crawls (keine RSS-/Sitemap-Verarbeitung), sondern gezielte
  Extraktion einzelner, vom Nutzer übergebener URLs
- Plaintext zurückgeben (für spätere Klassifikation im KI-Modul)
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse

import tldextract
import validators

from fundus.publishers import PublisherCollection, Publisher, PublisherGroup
from fundus.scraping.article import Article
from fundus.scraping.html import HTML, SourceInfo
from fundus.scraping.session import session_handler


class ArticleExtractor:
    def __init__(self, supported_languages: set) -> None:
        """
        Initialisiert den ArticleExtractor.

        Beim Erzeugen der Instanz wird einmalig eine Lookup-Struktur aufgebaut,
        welche registrierbare Domains (z. B. 'spiegel.de') den entsprechenden
        FUNDUS-Publishern zuordnet. Zudem werden nur Publisher berücksichtigt,
        die auch Artikel in unterstützten Sprachen des Detectors veröffentlichen.
        """
        self._supported_languages = supported_languages
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
                if publisher.languages.isdisjoint(self._supported_languages):
                    continue

                domains = publisher.domain

                # Fundus erlaubt Domains sowohl als String als auch als Liste
                if isinstance(domains, str):
                    domains = [domains]

                for domain in domains:
                    if not domain:
                        continue

                    extracted = tldextract.extract(domain)

                    # Ungültige oder unvollständige Domains überspringen
                    if not extracted.domain or not extracted.suffix:
                        continue

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

        # Falls Domain oder Suffix fehlen, kann keine gültige Root-Domain gebildet werden
        if not extracted.domain or not extracted.suffix:
            return None

        root_domain = f"{extracted.domain}.{extracted.suffix}"

        # Direkter Lookup im Dictionary (O(1))
        return self._publisher_map.get(root_domain)


    def _extract_article_with_fundus(self, url: str) -> Dict[str, Any]:
        """
        Extrahiert einen einzelnen Artikel mithilfe des FUNDUS-Parsers.

        Hinweis:
        Dieses Projekt verwendet FUNDUS hier *nicht* als Crawler. Stattdessen wird die
        konkrete URL direkt abgerufen und anschließend mit dem passenden Publisher-Parser
        verarbeitet.

        Ablauf:
        1. URL parsen → Publisher-Domain bestimmen
        2. Publisher in FUNDUS identifizieren
        3. robots.txt prüfen
        4. Artikel-HTML direkt abrufen
        5. Passenden Parser anwenden
        6. Extrahierten Artikel zurückgeben

        :param url: Vollständige URL eines Nachrichtenartikels.
        :return: Dict[str, Any]:
                {
                    "success": bool,
                    "input_type": "url",
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
        # 2. robots.txt prüfen (Fundus nutzt ebenfalls robots-Regeln)
        # ---------------------------------------------------------
        user_agent = publisher.request_header.get("user-agent") or "*"
        if publisher.robots and not publisher.robots.can_fetch(user_agent, url):
            return {
                "success": False,
                "input_type": "url",
                "publisher": publisher.name,
                "title": None,
                "text": None,
                "error": "robots.txt erlaubt das Abrufen dieser URL nicht.",
            }

        # ---------------------------------------------------------
        # 3. HTML direkt laden (kein Crawling durch RSS/Sitemaps)
        # ---------------------------------------------------------
        session = session_handler.get_session()
        try:
            response = session.get_with_interrupt(url, headers=publisher.request_header)
        except Exception as exc:
            return {
                "success": False,
                "input_type": "url",
                "publisher": publisher.name,
                "title": None,
                "text": None,
                "error": f"Artikel konnte nicht geladen werden: {exc}",
            }

        html = HTML(
            requested_url=url,
            responded_url=str(response.url),
            content=response.text,
            crawl_date=datetime.now(timezone.utc),
            source_info=SourceInfo(publisher.name),
        )

        # ---------------------------------------------------------
        # 4. Parser auf Basis der neuesten Version anwenden
        # ---------------------------------------------------------
        try:
            parser = publisher.parser()
            extraction = parser.parse(html.content, error_handling="raise")
        except Exception as exc:
            return {
                "success": False,
                "input_type": "url",
                "publisher": publisher.name,
                "title": None,
                "text": None,
                "error": f"Artikel konnte nicht extrahiert werden: {exc}",
            }

        article = Article(html=html, **extraction)
        if not article.plaintext:
            return {
                "success": False,
                "input_type": "url",
                "publisher": publisher.name,
                "title": None,
                "text": None,
                "error": "Artikel konnte nicht extrahiert werden.",
            }

        return {
            "success": True,
            "input_type": "url",
            "publisher": publisher.name,
            "title": article.title,
            "text": article.plaintext,
            "error": None,
        }


    def process(self, user_input: str) -> Dict[str, Any]:
        """
        Zentrale Einstiegsmethode für die Verarbeitung von Nutzereingaben.

        Diese Methode entscheidet, ob es sich bei der Eingabe um:
        - eine reine URL zu einem Nachrichtenartikel,
        - mehrere URLs (zeilenweise) oder
        - bereits vorliegenden Artikeltext

        handelt und leitet entsprechend die weitere Verarbeitung ein.

        Ablauf:
        1. Prüfung, ob der Input ausschließlich aus einer URL besteht
        2. Falls URL: Extraktion über FUNDUS
        3. Falls mehrere URLs (zeilenweise): jede URL extrahieren und Texte kombinieren
        4. Falls kein Link: Behandlung als Rohtext
        5. Rückgabe eines einheitlichen Ergebnisobjekts

        :param user_input: Eingabetext aus dem Frontend (URL(s) oder Artikeltext)
        :return: Dict[str, Any]:
                {
                    "success": bool,
                    "input_type": "url" | "multi_url" | "text" | None,
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
        lines = [line.strip() for line in user_input.splitlines() if line.strip()]

        # ---------------------------------------------------------
        # Fall 1: Mehrere Zeilen → prüfen, ob alle Zeilen URLs sind
        # (Hinweis: Der Code erzwingt aktuell NICHT, dass alle URLs zum selben Publisher gehören.)
        # ---------------------------------------------------------
        if len(lines) > 1 and all(self._is_pure_url(line) for line in lines):
            combined_text = []
            errors = []
            title = None
            publisher = None
            result = None

            for line in lines:
                result = self._extract_article_with_fundus(line)

                if result["success"] and result["text"]:

                    if title is None and publisher is None:
                        title = result["title"]
                        publisher = result["publisher"]

                    combined_text.append(result["text"])

                if result["error"]:
                    errors.append(f"{line}: {result['error']}")

            return {
                "success": (len(combined_text) > 0 and len(errors) == 0),
                "input_type": "multi_url",
                "publisher": publisher,
                "title": title,
                "text": "\n\n".join(combined_text) if combined_text else None,
                "error": "\n".join(errors) if errors else None,
            }

        # ---------------------------------------------------------
        # Fall 2: Einzelne URL
        # ---------------------------------------------------------
        if self._is_pure_url(user_input):
            return self._extract_article_with_fundus(user_input)

        # ---------------------------------------------------------
        # Fall 3: Eingabe ist kein Link → als Artikeltext behandeln
        # ---------------------------------------------------------
        return {
            "success": True,
            "input_type": "text",
            "publisher": None,
            "title": None,
            "text": user_input,
            "error": None,
        }