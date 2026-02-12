#!/usr/bin/env python3
"""Surveille les flux RSS de sources francophones pour détecter les nouvelles
sorties controversées de Donald Trump et les ajouter dans data/events.md.

Seuls les articles dont Trump est le *sujet* (il a dit ou fait quelque chose)
sont retenus ; les événements externes (votes, réactions, poursuites par des
tiers…) sont filtrés.
"""

import re
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).parent
EVENTS_FILE = ROOT / "data" / "events.md"

# ── Flux RSS à surveiller ──────────────────────────────────────────────
RSS_FEEDS: list[str] = [
    # Le Monde – International
    "https://www.lemonde.fr/international/rss_full.xml",
    # France Info – Donald Trump
    "https://www.franceinfo.fr/monde/usa/presidentielle/donald-trump.rss",
    # Ouest-France – Donald Trump
    "https://www.ouest-france.fr/monde/etats-unis/donald-trump/rss",
]

# ── Mots-clés : Trump doit être le sujet ───────────────────────────────
# Verbes / tournures indiquant que Trump *agit* ou *parle*
SUBJECT_PATTERNS: list[re.Pattern[str]] = [
    re.compile(p, re.IGNORECASE)
    for p in (
        r"trump\s+(a |va |veut |menace |annonce |signe |ordonne |décide "
        r"|affirme |déclare |accuse |réclame |impose |retire |supprime "
        r"|abroge |lance |propose |prévoit |promet |exige |qualifie "
        r"|insulte |attaque |dénonce |rejette |refuse |suspend "
        r"|interdit |bloque |critique |revendique |envisage |souhaite )",
        r"trump\s+dit\b",
        r"trump\s+fait\b",
        r"trump\s+prend\b",
        r"trump\s+met\b",
        r"trump\s+abrogera\b",
        r"donald\s+trump\s+(a |va |veut |menace |annonce |signe |ordonne "
        r"|décide |affirme |déclare |accuse |réclame |impose |retire "
        r"|supprime |abroge |lance |propose |prévoit |promet |exige "
        r"|qualifie |insulte |attaque |dénonce |rejette |refuse |suspend "
        r"|interdit |bloque |critique |revendique |envisage |souhaite )",
    )
]

# Motifs d'exclusion : articles où Trump n'est pas le sujet principal
EXCLUDE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(p, re.IGNORECASE)
    for p in (
        r"(vote|voté|réagi|répondu|condamné|critiqué|poursuivi|accusé"
        r"|manifesté|protesté|dénoncé)\s.*(contre|envers)\s.*trump",
        r"(face à|en réponse à|contre)\s+(donald\s+)?trump",
        r"(anti[- ]?trump|opposition\s+à\s+trump)",
    )
]

USER_AGENT = (
    "Mozilla/5.0 (compatible; TrumpEventBot/1.0; "
    "+https://github.com/mowdep/EstCeQueTrumpAEncoreDitUneConnerieAujourdhui)"
)


# ── Fonctions utilitaires ──────────────────────────────────────────────
def _fetch_xml(url: str) -> ET.Element | None:
    """Télécharge et parse un flux RSS/Atom."""
    if urlparse(url).scheme not in ("http", "https"):
        return None
    try:
        req = Request(url, headers={"User-Agent": USER_AGENT})
        with urlopen(req, timeout=15) as resp:
            return ET.fromstring(resp.read())
    except Exception:
        return None


def _is_trump_subject(text: str) -> bool:
    """Renvoie True si le texte indique que Trump est le sujet de l'action."""
    if any(pat.search(text) for pat in EXCLUDE_PATTERNS):
        return False
    return any(pat.search(text) for pat in SUBJECT_PATTERNS)


def _existing_urls() -> set[str]:
    """Lit les URLs déjà présentes dans events.md."""
    if not EVENTS_FILE.exists():
        return set()
    urls: set[str] = set()
    for line in EVENTS_FILE.read_text().splitlines():
        parts = line.strip().split(maxsplit=1)
        if len(parts) == 2:
            urls.add(parts[1])
    return urls


def _parse_rss_items(root: ET.Element) -> list[tuple[str, str, str]]:
    """Extrait (titre, lien, date_str) depuis un flux RSS 2.0 ou Atom."""
    items: list[tuple[str, str, str]] = []

    # RSS 2.0
    for item in root.iter("item"):
        title_el = item.find("title")
        link_el = item.find("link")
        pub_el = item.find("pubDate")
        if title_el is not None and link_el is not None:
            title = (title_el.text or "").strip()
            link = (link_el.text or "").strip()
            pub = (pub_el.text if pub_el is not None else "") or ""
            items.append((title, link, pub))

    # Atom
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    for entry in root.findall("atom:entry", ns):
        title_el = entry.find("atom:title", ns)
        link_el = entry.find("atom:link", ns)
        pub_el = entry.find("atom:published", ns) or entry.find(
            "atom:updated", ns
        )
        if title_el is not None and link_el is not None:
            title = (title_el.text or "").strip()
            link = link_el.get("href", "").strip()
            pub = (pub_el.text if pub_el is not None else "") or ""
            items.append((title, link, pub))

    return items


def _extract_date(pub_date: str, link: str) -> date | None:
    """Essaye d'extraire une date ISO depuis pubDate RFC-2822 ou l'URL."""
    # Tente d'abord d'extraire depuis l'URL (format courant /2026/02/03/)
    m = re.search(r"/(\d{4})/(\d{2})/(\d{2})/", link)
    if m:
        try:
            return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            pass
    # Depuis pubDate RFC-2822 : "Mon, 03 Feb 2026 …"
    m = re.search(r"(\d{1,2})\s+(\w{3})\s+(\d{4})", pub_date)
    if m:
        months = {
            "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
            "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
            "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12,
        }
        month = months.get(m.group(2))
        if month:
            try:
                return date(int(m.group(3)), month, int(m.group(1)))
            except ValueError:
                pass
    return None


# ── Point d'entrée ─────────────────────────────────────────────────────
def fetch_new_events() -> list[tuple[date, str]]:
    """Parcourt les flux RSS et renvoie les nouveaux événements détectés."""
    existing = _existing_urls()
    new_events: list[tuple[date, str]] = []

    for feed_url in RSS_FEEDS:
        root = _fetch_xml(feed_url)
        if root is None:
            continue
        for title, link, pub in _parse_rss_items(root):
            if not link or link in existing:
                continue
            if urlparse(link).scheme not in ("http", "https"):
                continue
            if _is_trump_subject(title):
                d = _extract_date(pub, link)
                if d is not None:
                    new_events.append((d, link))
                    existing.add(link)

    return sorted(new_events)


def append_events(new_events: list[tuple[date, str]]) -> int:
    """Ajoute les événements à events.md et renvoie le nombre ajouté."""
    if not new_events:
        return 0

    lines = EVENTS_FILE.read_text().splitlines() if EVENTS_FILE.exists() else []
    # Supprime les lignes vides en fin de fichier
    while lines and not lines[-1].strip():
        lines.pop()

    for d, url in new_events:
        lines.append(f"{d.isoformat()} {url}")

    EVENTS_FILE.write_text("\n".join(lines) + "\n")
    return len(new_events)


if __name__ == "__main__":
    new = fetch_new_events()
    added = append_events(new)
    if added:
        print(f"✅ {added} nouvel(s) événement(s) ajouté(s) :")
        for d, url in new:
            print(f"   {d} {url}")
    else:
        print("ℹ️  Aucun nouvel événement trouvé.")
