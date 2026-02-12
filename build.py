#!/usr/bin/env python3
"""Génère un site statique à partir de data/events.md."""

import re
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).parent
EVENTS_FILE = ROOT / "data" / "events.md"
OUTPUT_FILE = ROOT / "public" / "index.html"


def fetch_title(url: str) -> str:
    """Récupère le titre d'une page web."""
    # Validate URL scheme to prevent SSRF
    if urlparse(url).scheme not in ("http", "https"):
        return url
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            match = re.search(r"<title[^>]*>([^<]+)</title>", html, re.IGNORECASE)
            return match.group(1).strip() if match else url
    except (urllib.error.URLError, TimeoutError, OSError):
        return url


def parse_events() -> list[tuple[date, str]]:
    """Parse events.md (format: YYYY-MM-DD URL)."""
    if not EVENTS_FILE.exists():
        return []
    events = []
    for line in EVENTS_FILE.read_text().splitlines():
        parts = line.strip().split(maxsplit=1)
        if len(parts) == 2:
            try:
                events.append((date.fromisoformat(parts[0]), parts[1]))
            except ValueError:
                pass
    return events


def generate_html(today: date, events: list[tuple[date, str]]) -> str:
    """Génère le HTML."""
    has_event = any(d == today for d, _ in events)
    latest = max(events, key=lambda e: e[0]) if events else None
    days = max(0, (today - latest[0]).days) if latest else 0
    title = fetch_title(latest[1]) if latest else ""

    body = "<h1>Est-ce que Trump a encore dit une connerie aujourd'hui ?</h1></br>"
    f"<h1>{'Oui' if has_event else 'Non'}</h1>"
    if latest:
        body += f"""<p>Jours sans nouvelle entrée : {days}</p>
    <hr>
    <h2>Dernière entrée</h2>
    <p><a href="{latest[1]}">{title}</a></p>
    <p>Date : {latest[0].strftime('%d/%m/%Y')}</p>"""
    else:
        body += "<p>Aucune entrée enregistrée.</p>"

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Est-ce que Trump a encore dit une connerie aujourd'hui ?</title>
</head>
<body style="margin:0;min-height:100vh;display:flex;justify-content:center;align-items:center">
<div style="text-align:center">
{body}
</div>
</body>
</html>"""

if __name__ == "__main__":
    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    events = parse_events()
    OUTPUT_FILE.write_text(generate_html(date.today(), events))
    print(f"Generated {OUTPUT_FILE} ({len(events)} events)")
