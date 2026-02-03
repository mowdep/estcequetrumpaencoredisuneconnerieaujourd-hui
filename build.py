#!/usr/bin/env python3
"""
Build script for the static website generator.
Reads events from data/events.md and generates index.html.
"""

import os
import sys
from datetime import datetime, date
from pathlib import Path


def parse_events(events_file: Path) -> list[dict]:
    """Parse events from the events.md file.
    
    Format: YYYY-MM-DD|URL|Title|OptionalThumbnailURL
    """
    events = []
    
    if not events_file.exists():
        return events
    
    with open(events_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            
            parts = line.split('|')
            if len(parts) < 3:
                print(f"Warning: Line {line_num} has invalid format, skipping: {line}", file=sys.stderr)
                continue
            
            try:
                event_date = datetime.strptime(parts[0].strip(), '%Y-%m-%d').date()
            except ValueError:
                print(f"Warning: Line {line_num} has invalid date format, skipping: {line}", file=sys.stderr)
                continue
            
            event = {
                'date': event_date,
                'url': parts[1].strip(),
                'title': parts[2].strip(),
                'thumbnail': parts[3].strip() if len(parts) > 3 else None
            }
            events.append(event)
    
    return events


def get_latest_event(events: list[dict]) -> dict | None:
    """Get the most recent event by date."""
    if not events:
        return None
    return max(events, key=lambda e: e['date'])


def calculate_days_since(event_date: date, today: date) -> int:
    """Calculate number of days since the event."""
    return (today - event_date).days


def has_event_today(events: list[dict], today: date) -> bool:
    """Check if there's an event on today's date."""
    return any(e['date'] == today for e in events)


def generate_html(has_event: bool, days_count: int, latest_event: dict | None) -> str:
    """Generate the static HTML page."""
    indicator = "Oui" if has_event else "Non"
    
    html_parts = [
        '<!DOCTYPE html>',
        '<html lang="fr">',
        '<head>',
        '<meta charset="UTF-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
        '<title>Est-ce que Trump a encore dit une connerie aujourd\'hui ?</title>',
        '</head>',
        '<body>',
        f'<h1>{indicator}</h1>',
    ]
    
    if latest_event:
        html_parts.append(f'<p>Jours sans nouvelle entrée : {days_count}</p>')
        html_parts.append('<hr>')
        html_parts.append('<h2>Dernière entrée</h2>')
        
        if latest_event.get('thumbnail'):
            html_parts.append(f'<img src="{latest_event["thumbnail"]}" alt="Miniature">')
        
        html_parts.append(f'<p><a href="{latest_event["url"]}">{latest_event["title"]}</a></p>')
        html_parts.append(f'<p>Date : {latest_event["date"].strftime("%d/%m/%Y")}</p>')
    else:
        html_parts.append('<p>Aucune entrée enregistrée.</p>')
    
    html_parts.extend([
        '</body>',
        '</html>',
    ])
    
    return '\n'.join(html_parts)


def main():
    # Get the script directory
    script_dir = Path(__file__).parent.resolve()
    
    # Paths
    events_file = script_dir / 'data' / 'events.md'
    output_dir = script_dir / 'public'
    output_file = output_dir / 'index.html'
    
    # Ensure output directory exists
    output_dir.mkdir(exist_ok=True)
    
    # Get today's date
    today = date.today()
    
    # Parse events
    events = parse_events(events_file)
    print(f"Parsed {len(events)} events from {events_file}")
    
    # Get latest event
    latest_event = get_latest_event(events)
    
    # Calculate days since last event (cap at 0 for future dates)
    if latest_event:
        days_count = max(0, calculate_days_since(latest_event['date'], today))
    else:
        days_count = 0
    
    # Check if there's an event today
    has_event = has_event_today(events, today)
    
    # Generate HTML
    html_content = generate_html(has_event, days_count, latest_event)
    
    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Generated {output_file}")
    print(f"Today: {today}")
    print(f"Has event today: {has_event}")
    print(f"Days since last event: {days_count}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
